import React, { useEffect, useState } from 'react';
import { sharedApi } from '../services/api';
import type { SharedCorpusStats, SharedQuestion } from '../types';
import {
  Database,
  Search,
  CheckCircle2,
  Layers,
  FileText,
  AlertCircle,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

const PAGE_SIZE = 20;

export const SharedQuestionBank: React.FC = () => {
  const [stats, setStats] = useState<SharedCorpusStats | null>(null);
  const [questions, setQuestions] = useState<SharedQuestion[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  // Filters & Pagination
  const [section, setSection] = useState<string>('');
  const [topic, setTopic] = useState<string>('');
  const [year, setYear] = useState<string>('');
  const [difficulty, setDifficulty] = useState<string>('');
  const [qType, setQType] = useState<string>('');
  const [searchInput, setSearchInput] = useState<string>('');
  const [debouncedSearch, setDebouncedSearch] = useState<string>('');
  const [page, setPage] = useState<number>(0);

  // Debounce server-side search input and reset pagination to page 0
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchInput.trim());
      setPage(0);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchInput]);

  useEffect(() => {
    let active = true;
    sharedApi
      .getStats()
      .then((data) => {
        if (active) setStats(data);
      })
      .catch((err) => {
        console.error('Failed to load shared stats', err);
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;
    const fetchQuestions = async () => {
      setIsLoading(true);
      try {
        const params: Record<string, any> = {
          limit: PAGE_SIZE,
          offset: page * PAGE_SIZE,
        };
        if (section) params.section = section;
        if (topic) params.topic = topic;
        if (year) params.year = Number(year);
        if (difficulty) params.difficulty = difficulty;
        if (qType) params.question_type = qType;
        if (debouncedSearch) params.search = debouncedSearch;

        const res = await sharedApi.listQuestions(params);
        if (active) {
          setQuestions(res.items || []);
          setTotal(res.total || 0);
        }
      } catch (err) {
        console.error('Failed to load shared questions', err);
      } finally {
        if (active) setIsLoading(false);
      }
    };
    fetchQuestions();
    return () => {
      active = false;
    };
  }, [section, topic, year, difficulty, qType, debouncedSearch, page]);

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const startIdx = total === 0 ? 0 : page * PAGE_SIZE + 1;
  const endIdx = Math.min((page + 1) * PAGE_SIZE, total);

  const availableTopics: string[] = (stats?.topic_breakdown || [])
    .map((t: Record<string, any>) => String(t.topic || ''))
    .filter(Boolean);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <Database className="w-5 h-5 text-blue-600" />
          <h1 className="text-xl font-bold text-gray-900 tracking-tight">
            Global Shared Question Bank
          </h1>
        </div>
        <p className="text-sm text-gray-500 mt-1">
          A self-growing, verified CAT 2026 preparation bank of original authored questions. Every record is mathematically verified, deduplicated at the database level, and available to all users.
        </p>
      </div>

      {/* Real Live Database Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white border border-gray-200 rounded p-4">
          <div className="flex items-center justify-between text-gray-500 text-xs font-semibold uppercase">
            <span>Verified Papers</span>
            <FileText className="w-4 h-4 text-blue-500" />
          </div>
          <div className="mt-2 text-2xl font-bold text-gray-900">
            {stats ? stats.total_verified_papers : '—'}
          </div>
          <p className="text-[11px] text-gray-400 mt-1">Verified corpus pools</p>
        </div>

        <div className="bg-white border border-gray-200 rounded p-4">
          <div className="flex items-center justify-between text-gray-500 text-xs font-semibold uppercase">
            <span>Unique Questions</span>
            <CheckCircle2 className="w-4 h-4 text-green-500" />
          </div>
          <div className="mt-2 text-2xl font-bold text-gray-900">
            {stats ? stats.total_unique_verified_questions : '—'}
          </div>
          <p className="text-[11px] text-gray-400 mt-1">100% verified & deduplicated</p>
        </div>

        <div className="bg-white border border-gray-200 rounded p-4">
          <div className="flex items-center justify-between text-gray-500 text-xs font-semibold uppercase">
            <span>Duplicates Prevented</span>
            <Layers className="w-4 h-4 text-purple-500" />
          </div>
          <div className="mt-2 text-2xl font-bold text-gray-900">
            {stats ? stats.total_duplicates_prevented : '—'}
          </div>
          <p className="text-[11px] text-gray-400 mt-1">Database-level uniqueness enforced</p>
        </div>

        <div className="bg-white border border-gray-200 rounded p-4">
          <div className="flex items-center justify-between text-gray-500 text-xs font-semibold uppercase">
            <span>Source Links</span>
            <ExternalLink className="w-4 h-4 text-amber-500" />
          </div>
          <div className="mt-2 text-2xl font-bold text-gray-900">
            {stats ? stats.total_sources_linked : '—'}
          </div>
          <p className="text-[11px] text-gray-400 mt-1">Verified provenance links</p>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white border border-gray-200 rounded p-4 space-y-3">
        <div className="flex flex-col lg:flex-row gap-3">
          <div className="flex-1 relative">
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search all verified questions by keywords (e.g. train, speed, logarithm, circular track)..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs border border-gray-200 rounded focus:outline-none focus:border-blue-600"
            />
          </div>

          <div className="flex flex-wrap gap-2">
            <select
              value={section}
              onChange={(e) => {
                setSection(e.target.value);
                setPage(0);
              }}
              className="px-2.5 py-1.5 text-xs border border-gray-200 rounded bg-white text-gray-700 focus:outline-none focus:border-blue-600"
            >
              <option value="">All Sections</option>
              <option value="QA">QA (Quantitative Aptitude)</option>
              <option value="DILR">DILR (Data Interpretation & LR)</option>
              <option value="VARC">VARC (Verbal Ability & RC)</option>
            </select>

            <select
              value={topic}
              onChange={(e) => {
                setTopic(e.target.value);
                setPage(0);
              }}
              className="px-2.5 py-1.5 text-xs border border-gray-200 rounded bg-white text-gray-700 focus:outline-none focus:border-blue-600"
            >
              <option value="">All Topics</option>
              {availableTopics.map((tName) => (
                <option key={tName} value={tName}>
                  {tName}
                </option>
              ))}
            </select>

            <select
              value={year}
              onChange={(e) => {
                setYear(e.target.value);
                setPage(0);
              }}
              className="px-2.5 py-1.5 text-xs border border-gray-200 rounded bg-white text-gray-700 focus:outline-none focus:border-blue-600"
            >
              <option value="">All Years</option>
              {Array.from({ length: 26 }, (_, i) => 2025 - i).map((y) => (
                <option key={y} value={y}>
                  CAT {y}
                </option>
              ))}
            </select>

            <select
              value={difficulty}
              onChange={(e) => {
                setDifficulty(e.target.value);
                setPage(0);
              }}
              className="px-2.5 py-1.5 text-xs border border-gray-200 rounded bg-white text-gray-700 focus:outline-none focus:border-blue-600"
            >
              <option value="">All Difficulties</option>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>

            <select
              value={qType}
              onChange={(e) => {
                setQType(e.target.value);
                setPage(0);
              }}
              className="px-2.5 py-1.5 text-xs border border-gray-200 rounded bg-white text-gray-700 focus:outline-none focus:border-blue-600"
            >
              <option value="">All Formats</option>
              <option value="MCQ">MCQ</option>
              <option value="TITA">TITA (Non-MCQ)</option>
            </select>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] text-gray-500 pt-1 border-t border-gray-100">
          <span>
            Showing <strong className="text-gray-900">{startIdx}–{endIdx}</strong> of{' '}
            <strong className="text-gray-900">{total}</strong> verified questions
          </span>
          <span className="text-gray-400">
            Page {page + 1} of {totalPages} • Duplicates prevented at database level
          </span>
        </div>
      </div>

      {/* Questions List */}
      <div className="space-y-3">
        {isLoading ? (
          <div className="bg-white border border-gray-200 rounded p-8 text-center text-xs text-gray-400">
            Querying shared verified database...
          </div>
        ) : questions.length === 0 ? (
          <div className="bg-white border border-gray-200 rounded p-8 text-center text-xs text-gray-400 space-y-2">
            <AlertCircle className="w-6 h-6 text-gray-300 mx-auto" />
            <p className="font-medium text-gray-600">No verified questions match current filter criteria.</p>
            <p>Adjust search/filters or upload a CAT paper to expand the shared question bank.</p>
          </div>
        ) : (
          questions.map((q) => {
            const isExpanded = expandedId === q.id;
            return (
              <div
                key={q.id}
                className="bg-white border border-gray-200 rounded p-4 space-y-3 hover:border-gray-300 transition-colors"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-blue-50 text-blue-700 border border-blue-200">
                      {q.section}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-gray-100 text-gray-700">
                      {q.primary_slot || `CAT ${q.primary_year}`}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded text-[11px] font-medium capitalize ${
                        q.difficulty === 'easy'
                          ? 'bg-green-50 text-green-700'
                          : q.difficulty === 'hard'
                          ? 'bg-red-50 text-red-700'
                          : 'bg-amber-50 text-amber-700'
                      }`}
                    >
                      {q.difficulty}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-purple-50 text-purple-700">
                      {q.question_type}
                    </span>
                    {q.topic && (
                      <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                        {q.topic}{q.subtopic ? ` · ${q.subtopic}` : ''}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-3 text-xs text-gray-400">
                    <span title="Level 2 Canonical Hash Fingerprint" className="font-mono text-[10px]">
                      FP: {q.canonical_hash.substring(0, 10)}...
                    </span>
                    <button
                      onClick={() => setExpandedId(isExpanded ? null : q.id)}
                      className="text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-1 text-xs"
                    >
                      <span>{isExpanded ? 'Hide Solution' : 'View Answer & Sources'}</span>
                      {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>

                {/* Passage if applicable */}
                {q.has_passage && q.passage_text && (
                  <div className="bg-gray-50 border-l-2 border-blue-400 p-3 rounded text-xs text-gray-700 italic whitespace-pre-wrap">
                    <strong className="block text-[10px] text-gray-500 uppercase not-italic mb-1">
                      Reading Comprehension Passage:
                    </strong>
                    {q.passage_text}
                  </div>
                )}

                {/* DILR Dataset if applicable */}
                {q.dataset_text && !q.question_text.includes(q.dataset_text) && (
                  <div className="bg-slate-50 border-l-2 border-indigo-400 p-3 rounded text-xs text-gray-700 whitespace-pre-wrap font-mono">
                    <strong className="block text-[10px] text-gray-500 uppercase font-sans mb-1">
                      DILR Caselet & Dataset:
                    </strong>
                    {q.dataset_text}
                  </div>
                )}

                {/* Question Text */}
                <div className="text-sm text-gray-900 leading-relaxed font-normal whitespace-pre-wrap">
                  <span className="font-semibold text-gray-500 mr-2">Q{q.question_number}.</span>
                  {q.question_text}
                </div>

                {/* Options for MCQ */}
                {q.question_type === 'MCQ' && q.options && q.options.length > 0 && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
                    {q.options.map((opt) => (
                      <div
                        key={opt.id}
                        className={`p-2.5 rounded text-xs border flex items-center gap-2 ${
                          isExpanded && (opt.is_correct || opt.option_label === q.correct_answer)
                            ? 'bg-green-50 border-green-300 text-green-900 font-medium'
                            : 'bg-gray-50 border-gray-200 text-gray-700'
                        }`}
                      >
                        <span className="w-5 h-5 rounded-full bg-white border border-gray-300 flex items-center justify-center font-bold text-[11px] shrink-0">
                          {opt.option_label}
                        </span>
                        <span>{opt.option_text}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Expanded Details: Solution & Multi-Source Provenance */}
                {isExpanded && (
                  <div className="pt-3 border-t border-gray-100 space-y-3">
                    <div className="bg-blue-50/50 border border-blue-100 rounded p-3 text-xs space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-blue-900">Verified Answer:</span>
                        <span className="font-mono font-bold text-green-700 bg-white px-2 py-0.5 rounded border border-green-200">
                          {q.correct_answer || 'Validated in official key'}
                        </span>
                      </div>
                      {q.solution_text && (
                        <div className="mt-2 text-gray-700">
                          <strong className="block text-[11px] text-gray-500 uppercase mb-1">
                            Deterministic Solution:
                          </strong>
                          <p className="whitespace-pre-wrap">{q.solution_text}</p>
                        </div>
                      )}
                    </div>

                    {/* Source Provenance */}
                    {q.sources && q.sources.length > 0 && (
                      <div className="text-[11px] text-gray-500 flex flex-wrap items-center gap-2">
                        <strong className="text-gray-700">Source Provenance:</strong>
                        {q.sources.map((src) => (
                          <span
                            key={src.id}
                            className="bg-gray-100 text-gray-700 px-2 py-0.5 rounded border border-gray-200"
                          >
                            {src.source_name || `CAT ${src.year}`} ({src.source_type})
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Pagination Footer */}
      {total > PAGE_SIZE && (
        <div className="bg-white border border-gray-200 rounded p-3 flex items-center justify-between text-xs text-gray-600">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0 || isLoading}
            className="flex items-center gap-1 px-3 py-1.5 rounded border border-gray-200 bg-white hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed font-medium"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
            <span>Previous</span>
          </button>

          <span className="font-medium text-gray-700">
            Page {page + 1} of {totalPages}
          </span>

          <button
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1 || isLoading}
            className="flex items-center gap-1 px-3 py-1.5 rounded border border-gray-200 bg-white hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed font-medium"
          >
            <span>Next</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}
    </div>
  );
};
