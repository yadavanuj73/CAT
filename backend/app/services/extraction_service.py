"""
Historical Question Extraction and Classification Service.
Parses raw extracted text from authentic CAT papers into structured questions,
options, answers, sections (VARC, DILR, QA), and assigns initial classifications.
Never silently marks uncertain extractions as verified.
"""

import re
import uuid
from typing import Dict, List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.paper import Paper, PaperStatus
from app.models.question import (
    AnswerKey,
    Difficulty,
    Question,
    QuestionOption,
    QuestionType,
    Section,
    Solution,
    VerificationStatus,
)
from app.models.topic import Topic, QuestionClassification, ClassifiedBy
from app.services.ocr_service import extract_pages_from_pdf, compute_overall_confidence
from app.services.ai import get_ai_provider, ExtractedPaperBatchSchema, AIProviderError

# Section keyword heuristics
VARC_KEYWORDS = ["reading comprehension", "verbal ability", "para jumble", "sentence completion", "passage", "summary"]
DILR_KEYWORDS = ["data interpretation", "logical reasoning", "table", "graph", "seating arrangement", "puzzle"]
QA_KEYWORDS = ["quantitative aptitude", "arithmetic", "algebra", "geometry", "number system", "modern math"]

# Option parsing regex patterns
OPTION_PATTERN = re.compile(r"(?:\n|^)\s*(?:\(?([A-Da-d1-4])\)?[\.\:\-\)]\s*)([^\n]+)")
QUESTION_SPLIT_PATTERN = re.compile(r"(?:\n|^)\s*(?:Q(?:uestion)?\.?\s*(\d+)|\b(\d+)\.\s+)", re.IGNORECASE)


def detect_section(text: str, default: str = "QA") -> str:
    """Detect exam section from question or page context."""
    text_lower = text.lower()
    varc_score = sum(1 for kw in VARC_KEYWORDS if kw in text_lower)
    dilr_score = sum(1 for kw in DILR_KEYWORDS if kw in text_lower)
    qa_score = sum(1 for kw in QA_KEYWORDS if kw in text_lower)

    if varc_score > dilr_score and varc_score > qa_score:
        return "VARC"
    elif dilr_score > varc_score and dilr_score > qa_score:
        return "DILR"
    elif qa_score > 0:
        return "QA"
    return default


def parse_raw_text_into_questions(pages: List[Dict]) -> List[Dict]:
    """
    Parse paginated text into individual structured questions.
    Preserves Reading Comprehension passages and options.
    """
    full_text = "\n\n".join(p["text"] for p in pages)
    avg_confidence = compute_overall_confidence(pages)

    raw_chunks = QUESTION_SPLIT_PATTERN.split(full_text)
    questions_data = []

    # If simple splitting didn't find clear question numbers, split by double newlines
    if len(raw_chunks) <= 2:
        paragraphs = [p.strip() for p in full_text.split("\n\n") if len(p.strip()) > 30]
        for idx, para in enumerate(paragraphs, start=1):
            q_type = "MCQ" if OPTION_PATTERN.search(para) else "TITA"
            questions_data.append({
                "number": idx,
                "text": para,
                "type": q_type,
                "confidence": avg_confidence,
            })
    else:
        # Structured parse
        idx = 1
        i = 1
        while i < len(raw_chunks):
            q_num_str = raw_chunks[i] or raw_chunks[i+1] if (i+1 < len(raw_chunks)) else str(idx)
            try:
                q_num = int(q_num_str) if q_num_str and q_num_str.isdigit() else idx
            except Exception:
                q_num = idx

            content = raw_chunks[i+2] if (i+2 < len(raw_chunks)) else ""
            if content.strip():
                # Detect options
                options_matches = list(OPTION_PATTERN.finditer(content))
                q_type = "MCQ" if len(options_matches) >= 3 else "TITA"
                
                questions_data.append({
                    "number": q_num,
                    "text": content.strip(),
                    "type": q_type,
                    "confidence": avg_confidence,
                })
                idx += 1
            i += 3

    return questions_data


async def extract_questions_with_gemini(
    raw_text: str,
    year: int,
    slot: Optional[str] = None,
    api_key: Optional[str] = None,
) -> ExtractedPaperBatchSchema:
    """
    Extract structured questions from raw CAT paper text using Google Gemini (gemini-2.5-flash).
    Extracts question text, section, type, options, and reading passages.
    Guarantees extracted items remain UNVERIFIED until passed through independent deterministic gates.
    """
    provider = get_ai_provider("gemini", api_key=api_key)
    system_prompt = (
        "You are an expert CAT examination digitizer. Extract questions from authentic CAT examination papers. "
        "Strictly adhere to the three official CAT sections: VARC, DILR, and QA. Questions must be either MCQ (with 4 distinct options) "
        "or TITA (Type In The Answer with no options). For Reading Comprehension (VARC) or Caselets (DILR), preserve the shared passage."
    )
    user_prompt = f"Extract all authentic CAT examination questions from the following text for CAT {year} {slot or ''}:\n\n{raw_text[:25000]}"
    return await provider.generate_structured(
        prompt=user_prompt,
        response_schema=ExtractedPaperBatchSchema,
        system_instruction=system_prompt,
        temperature=0.1,
    )


async def extract_and_store_paper_questions(
    db: AsyncSession,
    paper: Paper,
) -> int:
    """
    Execute full extraction pipeline on an uploaded authentic CAT paper.
    Updates paper status and creates unverified question records.
    """
    paper.status = PaperStatus.EXTRACTING
    await db.commit()

    try:
        pages = extract_pages_from_pdf(paper.file_path)
        overall_conf = compute_overall_confidence(pages)
        paper.extraction_confidence = overall_conf

        parsed_questions = parse_raw_text_into_questions(pages)

        # Default section distribution across paper if not explicit
        current_section = Section.VARC

        count = 0
        for q_item in parsed_questions:
            # Detect section
            sec_str = detect_section(q_item["text"], default=current_section.value)
            try:
                section_enum = Section(sec_str)
            except Exception:
                section_enum = Section.QA

            has_passage = "passage" in q_item["text"].lower() or len(q_item["text"]) > 600

            # Extraction confidence: if confidence < 0.70, verification_status must be NEEDS_REVIEW
            status = VerificationStatus.NEEDS_REVIEW if q_item["confidence"] < 0.75 else VerificationStatus.UNVERIFIED

            question = Question(
                paper_id=paper.id,
                user_id=paper.user_id,
                question_number=q_item["number"],
                question_text=q_item["text"],
                question_type=QuestionType(q_item["type"]),
                section=section_enum,
                difficulty=Difficulty.MEDIUM,
                marks_positive=3.0,
                marks_negative=1.0 if q_item["type"] == "MCQ" else 0.0,
                has_passage=has_passage,
                extraction_confidence=q_item["confidence"],
                verification_status=status,
                year=paper.year,
                slot=paper.slot,
            )
            db.add(question)
            await db.flush()

            # Parse and insert options for MCQ
            if q_item["type"] == "MCQ":
                options = list(OPTION_PATTERN.finditer(q_item["text"]))
                labels = ["A", "B", "C", "D"]
                for o_idx, opt_match in enumerate(options[:4]):
                    lbl = labels[o_idx] if o_idx < 4 else f"Opt{o_idx+1}"
                    opt_text = opt_match.group(2).strip()
                    opt = QuestionOption(
                        question_id=question.id,
                        option_label=lbl,
                        option_text=opt_text,
                        is_correct=False,
                    )
                    db.add(opt)

            count += 1

        paper.status = PaperStatus.EXTRACTED
        paper.total_questions = count
        await db.commit()
        await db.refresh(paper)
        return count

    except Exception as e:
        paper.status = PaperStatus.FAILED
        paper.notes = f"Extraction failed: {str(e)}"
        await db.commit()
        raise e
