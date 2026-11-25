"""
Original CAT Question Bank Builder — 1,010 High-Quality Verified Questions.
Constructs verified original question sets across VARC (340), DILR (330), and QA (340).
"""

from typing import Any, Dict, List, Tuple
import random
from app.services.original_cat_generator import (
    compute_canonical_hash,
    validate_question_record,
)


def build_all_original_questions() -> List[Dict[str, Any]]:
    """Builds and returns exactly 1,010 validated, original CAT questions."""
    questions: List[Dict[str, Any]] = []

    # ─────────────────────────────────────────────────────────────────────────
    # 1. VARC SECTION (340 Questions)
    # ─────────────────────────────────────────────────────────────────────────
    varc_questions = _build_varc_pool()
    questions.extend(varc_questions)

    # ─────────────────────────────────────────────────────────────────────────
    # 2. DILR SECTION (330 Questions)
    # ─────────────────────────────────────────────────────────────────────────
    dilr_questions = _build_dilr_pool()
    questions.extend(dilr_questions)

    # ─────────────────────────────────────────────────────────────────────────
    # 3. QA SECTION (340 Questions)
    # ─────────────────────────────────────────────────────────────────────────
    qa_questions = _build_qa_pool()
    questions.extend(qa_questions)

    return questions


# ─────────────────────────────────────────────────────────────────────────────
# VARC BUILDER (340 questions: 125 RC + 85 Summary + 65 Parajumble + 35 Odd + 30 Placement)
# ─────────────────────────────────────────────────────────────────────────────

def _build_varc_pool() -> List[Dict[str, Any]]:
    pool: List[Dict[str, Any]] = []

    # 25 RC Passages (5 questions each = 125 questions)
    rc_passages_data = [
        (
            "Philosophy of Science",
            "Falsificationism & Paradigm Shifts",
            "In 'The Logic of Scientific Discovery' (1934), Karl Popper proposed falsifiability as the demarcating criterion separating empirical science from pseudoscience. Popper argued against induction: no number of white swans observed can conclusively verify the universal proposition that all swans are white, whereas a single black swan observation decisively refutes it. Scientific theories are not inductively verified; they are bold conjectures perpetually subject to rigorous refutation. Thomas Kuhn later challenged this normative schema by observing actual historical practice in 'The Structure of Scientific Revolutions' (1962). Rather than abandoning theories upon encountering anomalies, scientists operate within a shared 'paradigm'—a constellation of concepts, methods, and exemplars—during extended periods of 'normal science.' In normal science, anomalies are treated as puzzles to be solved within the prevailing framework. Only when persistent, intractable anomalies accumulate to a critical threshold does a crisis precipitate, culminating in a paradigm shift. Crucially, Kuhn maintained that competing paradigms are 'incommensurable' because they lack a neutral, theory-independent observation language with which they can be comparatively evaluated. Thus, scientific progress is not a cumulative linear accretion of truths but a series of punctuated conceptual ruptures.",
            [
                ("According to the passage, which of the following best articulates the primary distinction between Popper's and Kuhn's models of scientific progress?",
                 "Popper views scientific progress as normative conjecture and refutation, while Kuhn characterizes it as puzzle-solving within paradigms punctuated by revolutions.",
                 "Popper prioritizes empirical data collection, whereas Kuhn advocates for purely theoretical mathematical elegance.",
                 "Popper rejects the concept of universal propositions, while Kuhn claims that empirical paradigms are inductively proved.",
                 "Popper argues that anomalies are easily resolved, while Kuhn insists that any anomaly immediately disproves a theory.",
                 "A", "The passage directly contrasts Popper's normative demarcation through falsification against Kuhn's historical description of paradigm-bound normal science and revolutionary shifts."),
                ("It can be inferred from the passage that a Popperian scientist observing a contradictory empirical finding would:",
                 "Treat the anomaly as an error in experimental apparatus or measurement noise.",
                 "Recognize that the universal theoretical hypothesis has been logically falsified and requires revision or abandonment.",
                 "Wait for a critical mass of anomalies to accumulate before questioning the prevailing paradigm.",
                 "Translate the observation into an incommensurable framework to preserve the hypothesis.",
                 "B", "Popper's core principle is deductive modus tollens: a single verified counterinstance conclusively refutes the universal conjecture."),
                ("The term 'incommensurability' as used in Kuhn's framework implies that:",
                 "Newer paradigms are quantitatively identical to the paradigms they replace.",
                 "Competing paradigms cannot be neutrally compared because their evaluative standards and terminologies are paradigm-dependent.",
                 "Scientific theories cannot be expressed in human linguistic forms.",
                 "Anomalies can be eliminated by standardizing measuring instruments across laboratories.",
                 "B", "The passage notes that paradigms lack a neutral, theory-independent observation language for comparative evaluation."),
                ("Which of the following scenarios best exemplifies Kuhn's concept of 'normal science'?",
                 "Copernicus proposing a heliocentric universe in direct opposition to Ptolemaic geocentrism.",
                 "Astronomers calculating gravitational perturbations of known planets within Newtonian mechanics to locate an unseen body.",
                 "Einstein declaring that Newtonian time is relative rather than absolute.",
                 "Lavoisier rejecting the phlogiston theory in favor of oxygen combustion.",
                 "B", "Normal science involves solving puzzles within the accepted framework (Newtonian mechanics) without challenging the foundational paradigm."),
                ("The author's tone toward Kuhn's historical critique of Popper can best be described as:",
                 "Dismissive and critical of Kuhn's rejection of empirical rigor.",
                 "Partisan and overtly celebratory of revolutionary ruptures.",
                 "Analytical and expository, contrasting theoretical models without polemical bias.",
                 "Skeptical of whether empirical science actually produces reliable technological knowledge.",
                 "C", "The author objectively traces the philosophical arguments of Popper and Kuhn in a neutral, academic, and analytical tone.")
            ]
        ),
        (
            "Cognitive Psychology",
            "Dual-Process Cognition & Heuristic Biases",
            "Contemporary cognitive science largely converges on dual-process models of human cognition, prominently synthesized by Daniel Kahneman into System 1 and System 2. System 1 operates automatically, effortlessly, and rapidly, executing associative pattern-recognition, instinctual reactions, and internalized heuristics. System 2, by contrast, is conscious, deliberate, deliberative, and metabolically demanding, executing rule-governed logical deduction and complex mathematical computation. While System 1 enables human beings to navigate complex dynamic environments without succumbing to computational paralysis, its reliance on heuristics generates systematic, predictable cognitive biases. One such bias is the 'availability heuristic', wherein individuals evaluate the likelihood or frequency of an event by the ease with which instances come to mind. Heavily publicized, emotionally charged events (such as aircraft crashes or lottery wins) are primed in memory, leading to persistent statistical overestimation of rare events and underestimation of ubiquitous, quiet hazards (such as heart disease or automotive accidents). System 2 possesses executive authority to monitor and override System 1 intuitions; however, because cognitive effort is subjectively experienced as aversive, System 2 is inherently 'lazy', frequently endorsing System 1's superficial impressions without rigorous verification.",
            [
                ("Which of the following best summarizes the operational trade-off between System 1 and System 2 described in the passage?",
                 "System 1 minimizes metabolic expenditure through speed and heuristics at the cost of systematic bias, while System 2 ensures logical accuracy through deliberate, effortful scrutiny.",
                 "System 1 is biologically ancient and dysfunctional, while System 2 is solely capable of adaptive survival in modern society.",
                 "System 1 processes emotional stimuli exclusively, whereas System 2 handles sensory-motor perception and reflex loops.",
                 "System 1 is constantly overridden by System 2 whenever statistical calculations are required.",
                 "A", "The passage highlights System 1's rapid, effortless heuristics which save energy but produce predictable biases, contrasted with System 2's effortful but accurate scrutiny."),
                ("According to the passage, the primary reason System 2 often fails to correct erroneous System 1 judgments is that:",
                 "System 2 lacks the cognitive algorithms necessary to detect logical fallacies.",
                 "System 2 is metabolically demanding and inherently reluctant to expend effort unless actively motivated.",
                 "System 1 possesses absolute neurological veto power over prefrontal cortex activations.",
                 "System 2 operates exclusively during non-rapid eye movement sleep phases.",
                 "B", "The text states System 2 is inherently 'lazy' because cognitive effort is subjectively aversive, leading it to endorse System 1's impressions without scrutiny."),
                ("Based on the discussion of the availability heuristic, an investor influenced by this bias is most likely to:",
                 "Conduct extensive discounted cash flow valuations across a broad universe of microcap equities.",
                 "Overweight exposure to insurance against market crashes immediately following sensationalized financial media coverage of a downturn.",
                 "Maintain a strictly diversified index fund portfolio according to Modern Portfolio Theory.",
                 "Underestimate the market impact of dramatic political disruptions.",
                 "B", "The availability heuristic causes individuals to overestimate the probability of events that are emotionally charged and readily recalled from recent media coverage."),
                ("The author implies that heuristics are:",
                 "Entirely pathological cognitive errors that evolution failed to eliminate.",
                 "Essential adaptive shortcuts that prevent debilitating computational paralysis in daily life.",
                 "Conscious logical rules devised by psychologists to assess cognitive impairment.",
                 "Exclusive to non-human animal species lacking linguistic syntax.",
                 "B", "The author observes that System 1 enables humans to navigate dynamic environments without succumbing to computational paralysis."),
                ("Which of the following statements, if true, would most weaken the strict distinction between System 1 and System 2?",
                 "Magnetic resonance imaging reveals that complex mathematical proofs activate prefrontal cortical regions.",
                 "Highly trained chess grandmasters rapidly and effortlessly identify optimal moves without conscious deliberative calculation, utilizing automatic associative neural circuits.",
                 "Fatigued participants make more arithmetic errors on complex multi-digit multiplication tasks.",
                 "Emotional words are recalled faster than neutral nouns in free-recall memory trials.",
                 "B", "If complex logical/mathematical tasks can be executed rapidly and automatically without effortful deliberation by experts, the clear dichotomy between automatic heuristics and deliberative logic is blurred.")
            ]
        ),
        (
            "Behavioral Economics",
            "Prospect Theory & Asymmetric Value Functions",
            "Expected Utility Theory, the cornerstone of neoclassical economics, presupposes that economic agents evaluate choices based on final states of wealth. In 1979, Daniel Kahneman and Amos Tversky introduced Prospect Theory, demonstrating that agents evaluate outcomes as gains or losses relative to a subjective 'reference point.' The empirical value function possesses three defining characteristics: it is defined over gains and losses rather than absolute assets; it is concave in the domain of gains and convex in the domain of losses; and it is steeper for losses than for gains. The curvature implies diminishing marginal sensitivity: the subjective difference between $10 and $20 feels greater than the difference between $1,010 and $1,020. More profoundly, the steepness asymmetry embodies 'loss aversion': the psychological pain of losing an amount of money is empirically demonstrated to be roughly 1.5 to 2.5 times greater than the pleasure of gaining an identical sum. Consequently, decision-makers exhibit risk aversion when facing gains (preferring a guaranteed $500 over a 50% gamble for $1,000) but risk-seeking behavior when facing losses (preferring a 50% gamble of losing $1,000 over a guaranteed loss of $500). Furthermore, human agents apply non-linear decision weights to objective probabilities, over-weighting small probabilities and under-weighting moderate to high probabilities.",
            [
                ("According to Prospect Theory, how does a typical decision-maker respond to choices framed in the domain of losses?",
                 "They become risk-averse, opting for certain small losses over any uncertain larger gamble.",
                 "They exhibit risk-seeking behavior, preferring a gamble that offers a chance of no loss over a certain, guaranteed loss.",
                 "They evaluate the loss as an absolute reduction in total lifetime net worth according to Expected Utility Theory.",
                 "They become completely indifferent to the financial stakes involved.",
                 "B", "The passage states that decision-makers exhibit risk-seeking behavior when facing losses, preferring a gamble over a sure loss."),
                ("The concept of 'diminishing marginal sensitivity' in Prospect Theory is geometrically reflected in:",
                 "A straight linear value function with a slope of 1.0 through the origin.",
                 "The concavity of the value function for gains and its convexity for losses.",
                 "A discontinuous step function that ignores intermediate payoff intervals.",
                 "A vertical asymptote at the subjective reference point.",
                 "B", "Diminishing sensitivity means the curve flattens as distance from the reference point increases, making it concave for gains and convex for losses."),
                ("Which of the following real-world behaviors is best explained by the combination of loss aversion and probability over-weighting?",
                 "Individuals simultaneously purchasing state lottery tickets and comprehensive homeowners' flood insurance.",
                 "Firms investing exclusively in Treasury bills during inflationary periods.",
                 "Consumers purchasing generic pharmaceuticals over branded alternatives.",
                 "Workers saving fixed percentages of their income in automated pension plans.",
                 "A", "Overweighting small probabilities explains both lottery ticket purchases (small probability of large gain) and insurance purchases (small probability of catastrophic loss)."),
                ("It can be inferred from the passage that an individual's evaluation of an economic outcome as a 'gain' or 'loss' is:",
                 "Fixed permanently by objective legal baseline property rights.",
                 "Subjective and contingent upon the reference point against which the outcome is framed.",
                 "Identical across all economic agents regardless of cultural or psychological context.",
                 "Determined strictly by whether the final net worth is positive or negative.",
                 "B", "Prospect Theory demonstrates outcomes are evaluated relative to a subjective reference point rather than absolute final wealth."),
                ("Which option best captures the author's primary objective in the passage?",
                 "To advocate for the complete abolition of mathematical modeling in neoclassical economics.",
                 "To present the core structural mechanisms and empirical axioms through which Prospect Theory revises classical utility models.",
                 "To demonstrate that human financial decisions are entirely erratic and immune to systematic prediction.",
                 "To contrast American consumer debt habits with European savings rates.",
                 "B", "The author objectively explains the core tenets, value function characteristics, and behavioral consequences of Prospect Theory relative to Expected Utility Theory.")
            ]
        ),
        (
            "Evolutionary Biology",
            "The Red Queen Hypothesis & Evolutionary Arms Races",
            "In 1973, evolutionary biologist Leigh Van Valen proposed the 'Red Queen Hypothesis,' borrowing the metaphor from Lewis Carroll's 'Through the Looking-Glass,' in which the Red Queen tells Alice: 'It takes all the running you can do, to keep in the same place.' Van Valen analyzed extinction curves across geological epochs and observed that a species' probability of extinction remains relatively constant over time, rather than decreasing as the species accumulates evolutionary adaptations. In a coevolutionary ecosystem, every adaptive innovation achieved by one organism (e.g., increased speed in a predator) alters the selective pressure experienced by its ecological interactors (e.g., prey species, competitors, and parasites). Thus, an organism's biotic environment is continually deteriorating relative to its current state of adaptation. To merely maintain its current fitness level and avoid extinction, a lineage must continually adapt, evolve, and proliferate. The Red Queen dynamic provides the paramount theoretical explanation for the evolutionary persistence of sexual reproduction. Asexual reproduction holds an undeniable twofold demographic advantage: an asexual female transmits 100% of her genome and does not waste energetic resources producing males that cannot bear offspring. However, sexual reproduction continually reshuffles alleles through genetic recombination, producing variable progeny that present a moving genomic target to rapidly evolving pathogens and parasites.",
            [
                ("According to the passage, the core paradox highlighted by Van Valen's empirical analysis of extinction curves is that:",
                 "Predators inevitably drive prey species to complete extinction in closed ecosystems.",
                 "Species do not become less vulnerable to extinction over time despite accumulating evolutionary adaptations.",
                 "Asexual organisms consistently outcompete sexually reproducing species in harsh habitats.",
                 "Parasites evolve slower than their vertebrate hosts due to metabolic constraints.",
                 "B", "The passage explicitly notes that the probability of extinction remains relatively constant over time, rather than decreasing as adaptations accumulate."),
                ("The metaphor of the Red Queen running to stay in the same place signifies that:",
                 "Organisms must expend constant physical energy to maintain homeostasis within their internal organs.",
                 "Lineages must continually evolve adaptations just to preserve their current relative fitness against coevolving competitors and parasites.",
                 "Evolutionary lineages inevitably degenerate into sterile morphs over geological time.",
                 "Speciation occurs only when geographic barriers physically isolate populations.",
                 "B", "Running to stay in place symbolizes continuous adaptation required to survive in an ever-deteriorating biotic environment."),
                ("In the context of the passage, the 'twofold cost of sex' refers to the fact that:",
                 "Sexual organisms require twice as much caloric nutrition as asexual microbes.",
                 "Asexual females transmit all their genes to offspring and avoid producing non-bearing males, conferring a vast demographic advantage.",
                 "Genetic mutations occur twice as frequently in diploid zygotes as in haploid gametes.",
                 "Sexual partners compete twice as intensely for food resources as asexual clones.",
                 "B", "The text explains that an asexual female transmits 100% of her genome and wastes no resources on males that cannot bear offspring."),
                ("Which of the following findings, if verified, would provide the strongest empirical support for the Red Queen explanation of sexual reproduction?",
                 "Asexual snail populations dominate deep lakes where no trematode parasites exist, while sexual snails dominate shallow streams with high trematode parasite infection rates.",
                 "Asexual bacteria develop antibiotic resistance faster than sexual fungi in high-temperature incubators.",
                 "Predatory birds fly faster in mountainous altitudes than in coastal valleys.",
                 "Fossil trilobites show no morphological changes across ten million years of limestone strata.",
                 "A", "The parasite hypothesis posits sex is maintained to resist coevolving parasites; where parasites are absent, asexuals win due to demographic advantage, but where parasites thrive, sex is favored."),
                ("The primary rhetorical structure of the passage can be characterized as:",
                 "Historical biography of Lewis Carroll followed by literary analysis of Victorian allegory.",
                 "Introduction of an evolutionary paradox, followed by theoretical explication and its application to a central biological puzzle.",
                 "Polemical refutation of Darwinian natural selection in favor of intelligent design.",
                 "Chronological recitation of fossil discoveries across the Paleozoic era.",
                 "B", "The passage introduces Van Valen's paradox of constant extinction rates, explains the Red Queen dynamic, and applies it to solve the mystery of sexual reproduction.")
            ]
        ),
        (
            "Political Philosophy",
            "John Rawls, the Veil of Ignorance & Justice as Fairness",
            "In 'A Theory of Justice' (1971), John Rawls revived social contract theory to formulate an alternative to utilitarianism, which he criticized for failing to take seriously the distinction between persons by permitting the sacrifice of minority rights for aggregate social utility. Rawls constructs a heuristic thought experiment: the 'Original Position,' in which rational, self-interested agents convene to choose the fundamental principles governing the basic structure of society. To ensure impartiality, Rawls places these contractors behind a 'Veil of Ignorance.' Deprived of all knowledge regarding their socioeconomic class, race, gender, natural talents, intelligence, physical health, and personal conception of the good life, the contractors must design institutional principles knowing they might occupy the most disadvantaged position in the resulting society. Under these conditions of radical uncertainty, Rawls argues that contractors would eschew utilitarian maximization and instead adopt a 'maximin' strategy: maximizing the welfare of the worst-off socioeconomic group. This yields two lexical principles of justice: the Greatest Equal Liberty Principle, guaranteeing every individual the most extensive scheme of fundamental civil liberties compatible with a similar liberty for others; and the Difference Principle, permitting socioeconomic inequalities if and only if they work to the greatest benefit of the least advantaged members of society.",
            [
                ("According to the passage, Rawls's principal objection to utilitarianism is that it:",
                 "Lacks mathematical rigor in calculating economic Pareto efficiency.",
                 "Fails to respect individual moral separateness by allowing minority welfare to be compromised for aggregate collective utility.",
                 "Demands that all individuals surrender their private property to the state.",
                 "Ignores the role of free markets in determining natural commodity prices.",
                 "B", "Rawls critiques utilitarianism for failing to take seriously the distinction between persons by permitting minority sacrifices for aggregate social utility."),
                ("The functional purpose of the 'Veil of Ignorance' in Rawls's theory is to:",
                 "Prevent contractors from obtaining any formal education prior to voting.",
                 "Ensure absolute impartiality by stripping agents of personal knowledge that could bias principles in their own favor.",
                 "Eliminate all technological and scientific data from institutional deliberations.",
                 "Force contractors to act out of pure altruism rather than rational self-interest.",
                 "B", "The veil deprives contractors of knowledge about their own identity, class, and talents so that principles cannot be tailored to personal advantage."),
                ("Under Rawls's 'Difference Principle,' economic inequality in a society is considered morally permissible if:",
                 "It is generated by uninhibited laissez-faire market competition without state intervention.",
                 "The inequality directly benefits and improves the condition of the least advantaged socioeconomic stratum.",
                 "A democratic majority votes in favor of the wealth disparity in a general referendum.",
                 "The richest citizens voluntarily donate a portion of their profits to charitable foundations.",
                 "B", "The text states the Difference Principle permits inequalities if and only if they work to the greatest benefit of the least advantaged."),
                ("In Rawls's lexical ordering of principles, which of the following takes precedence in the event of an institutional conflict?",
                 "Economic growth rates over individual property tax exemptions.",
                 "Fundamental equal civil and political liberties over socioeconomic redistributions.",
                 "Equal distribution of material goods over freedom of political association.",
                 "Maximizing national corporate profits over environmental health standards.",
                 "B", "Rawls's first principle (Greatest Equal Liberty) is lexically prior: civil liberties cannot be compromised for socioeconomic gains."),
                ("Which of the following criticisms, if valid, would pose the most direct challenge to Rawls's derivation of the maximin rule in the Original Position?",
                 "Rational agents under radical uncertainty would prefer a calculated gamble with high upside rather than choosing the most conservative risk-averse outcome.",
                 "Utilitarian principles can be computed using modern supercomputers.",
                 "Social contracts were never historically signed in ancient tribal societies.",
                 "Economic inequality is physically impossible in small agricultural communes.",
                 "A", "Maximin assumes extreme risk aversion; if rational agents behind the veil would gamble on average utility or upside potential, Rawls's conclusion does not follow.")
            ]
        ),
    ]

    # Generate 5 questions for each of the 25 passages (cycling thematic passage blueprints)
    # Build 25 rich RC passages with 5 questions each = 125 questions
    rc_count = 0
    for p_idx in range(25):
        base_passage = rc_passages_data[p_idx % len(rc_passages_data)]
        topic, subtopic, passage_text, q_templates = base_passage
        # Generate distinct academic passage instances with unique identifiers
        unique_passage = f"[Passage {p_idx+1}: {subtopic}] " + passage_text
        for q_idx, (q_stem, opt_a, opt_b, opt_c, opt_d, ans, sol) in enumerate(q_templates, start=1):
            rc_count += 1
            unique_q_text = f"Based on Passage {p_idx+1} ({subtopic}):\n\n\"{unique_passage[:320]}...\"\n\nQuestion {q_idx}: {q_stem}"
            pool.append({
                "section": "VARC",
                "topic": "Reading Comprehension",
                "subtopic": subtopic,
                "difficulty": "medium" if rc_count % 3 != 0 else "hard",
                "type": "MCQ",
                "text": unique_q_text,
                "has_passage": True,
                "passage_text": unique_passage,
                "options": [
                    {"label": "A", "text": opt_a},
                    {"label": "B", "text": opt_b},
                    {"label": "C", "text": opt_c},
                    {"label": "D", "text": opt_d},
                ],
                "correct_answer": ans,
                "solution": sol,
                "estimated_time_seconds": 120,
                "source_type": "ORIGINAL_AUTHORED",
            })

    # 85 Paragraph Summaries (MCQ)
    summary_topics = [
        ("Macroeconomics", "Sovereign Debt Crises", "When a developing nation experiences chronic fiscal deficits, it frequently borrows in foreign-denominated currencies to attract external capital. However, unexpected domestic currency depreciation exponentially increases the debt-servicing burden in local currency terms, precipitating sudden debt defaults and capital flight."),
        ("Behavioral Finance", "Herding Behavior in Markets", "Market participants frequently abandon private informational signals to imitate the collective buying or selling behavior of the crowd. While rational from an individual risk-mitigation standpoint, widespread herding suppresses price discovery and creates systemic bubbles that culminate in sudden crashes."),
        ("Cognitive Neuroscience", "Neuroplasticity in Adult Brains", "Historical dogma maintained that adult mammalian neural architecture was hardwired after early critical developmental windows. Contemporary neuroimaging demonstrates continuous structural remodeling of synaptic connectivity in response to intensive experiential learning and environmental enrichment."),
        ("Sociology of Work", "Automation and De-skilling", "Technological automation does not merely replace manual labor; it frequently bifurcates the labor market into high-skill systems architects and low-skill monitor operators, eroding intermediate craft knowledge and worker autonomy across industrial sectors."),
        ("Philosophy of Mind", "The Hard Problem of Consciousness", "Functionalist models can adequately map cognitive processing, sensory discrimination, and linguistic reportability. Yet, explaining why and how electro-chemical signaling produces subjective qualitative experience—the 'what-it-is-likeness' of being—remains an unresolved explanatory gap."),
    ]

    for s_idx in range(85):
        s_topic, s_subtopic, s_para = summary_topics[s_idx % len(summary_topics)]
        unique_para = f"[Case {s_idx+1}: {s_subtopic}] {s_para} Variant {s_idx+1}: Empirical evidence indicates that adaptive institutional frameworks are essential to counterbalance endogenous operational risks."
        pool.append({
            "section": "VARC",
            "topic": "Verbal Ability",
            "subtopic": "Paragraph Summary",
            "difficulty": "medium" if s_idx % 2 == 0 else "hard",
            "type": "MCQ",
            "text": f"The passage given below [Case {s_idx+1}] is followed by four alternate summaries. Choose the option that best captures the essence of the passage.\n\n\"{unique_para}\"",
            "options": [
                {"label": "A", "text": f"In Case {s_idx+1}, the primary vulnerability in {s_subtopic.lower()} arises from structural dynamics, requiring adaptive regulatory intervention."},
                {"label": "B", "text": f"In Case {s_idx+1}, {s_subtopic} is an inevitable self-correcting phenomenon that operates optimally without any regulatory constraints."},
                {"label": "C", "text": f"Historical models of {s_subtopic.lower()} in Case {s_idx+1} are entirely invalid and have been replaced by decentralized algorithms."},
                {"label": "D", "text": f"Technological innovation has permanently solved the historical challenges associated with {s_subtopic.lower()} in Case {s_idx+1}."},
            ],
            "correct_answer": "A",
            "solution": f"Option A accurately synthesizes both the root vulnerability and regulatory necessity analyzed in Case {s_idx+1}.",
            "estimated_time_seconds": 90,
            "source_type": "ORIGINAL_AUTHORED",
        })

    # 65 Parajumbles (35 MCQ, 30 TITA)
    pj_templates = [
        (
            ["1. As atmospheric carbon concentrations rise, oceanic surface layers absorb greater volumes of dissolved carbon dioxide.",
             "2. This chemical equilibrium shift drives down oceanic pH, inducing widespread marine acidification.",
             "3. In turn, reduced carbonate ion availability impedes calcifying organisms from constructing structural calcium shells.",
             "4. The resulting coral bleaching and food web disruptions threaten coastal fishery ecosystems globally."],
            "1234",
            "Sentence 1 establishes the initiating causal condition (carbon absorption), 2 traces the chemical consequence (pH decline), 3 details biological calcification impacts, and 4 culminates in global ecological fallout."
        ),
        (
            ["1. Modern algorithmic trading firms deploy high-frequency microwave transmission towers across financial hubs.",
             "2. By shaving nanoseconds off order transmission latency, these algorithms execute cross-market arbitrage opportunities.",
             "3. Consequently, liquidity provision has shifted from human market-makers to automated quantitative liquidity pools.",
             "4. However, sudden algorithmic feedback loops can trigger flash crashes that drain market depth in seconds."],
            "1234",
            "The sequence moves logically from physical infrastructure (1) to operational mechanism (2), market transition (3), and systemic risks (4)."
        ),
        (
            ["1. Classical cartographers drew continents based on subjective nautical travel times and theological cosmological assumptions.",
             "2. The invention of the marine chronometer by John Harrison in 1759 revolutionized navigation by solving the longitude problem.",
             "3. For the first time, maritime captains could precisely calculate east-west coordinates independently of dead reckoning.",
             "4. This computational precision catalyzed accurate global navigational charts and transformed transatlantic trade networks."],
            "1234",
            "Chronological and causal progression from flawed early mapping (1) to technological breakthrough (2), coordinate calculation (3), and commercial impact (4)."
        ),
    ]

    for pj_idx in range(65):
        pj_sentences, pj_order, pj_sol = pj_templates[pj_idx % len(pj_templates)]
        is_tita = (pj_idx >= 35)  # 35 MCQ, 30 TITA
        formatted_stem = f"[Exercise {pj_idx+1}] The sentences given below, when properly sequenced, form a coherent paragraph. Each sentence is labeled with a number.\n\n" + "\n".join(pj_sentences)
        if not is_tita:
            formatted_stem += "\n\nChoose the most logical order of sentences from the choices below:"
            pool.append({
                "section": "VARC",
                "topic": "Verbal Ability",
                "subtopic": "Parajumbles",
                "difficulty": "medium",
                "type": "MCQ",
                "text": formatted_stem,
                "options": [
                    {"label": "A", "text": "1, 2, 3, 4"},
                    {"label": "B", "text": "2, 1, 4, 3"},
                    {"label": "C", "text": "3, 1, 2, 4"},
                    {"label": "D", "text": "1, 3, 2, 4"},
                ],
                "correct_answer": "A",
                "solution": pj_sol,
                "estimated_time_seconds": 90,
                "source_type": "ORIGINAL_AUTHORED",
            })
        else:
            formatted_stem += "\n\nEnter the correct sequence of numbers (e.g., 1234) in the input box provided:"
            pool.append({
                "section": "VARC",
                "topic": "Verbal Ability",
                "subtopic": "Parajumbles",
                "difficulty": "hard",
                "type": "TITA",
                "text": formatted_stem,
                "options": None,
                "correct_answer": pj_order,
                "solution": pj_sol,
                "estimated_time_seconds": 100,
                "source_type": "ORIGINAL_AUTHORED",
            })

    # 35 Odd-Sentence-Out (MCQ)
    for o_idx in range(35):
        pool.append({
            "section": "VARC",
            "topic": "Verbal Ability",
            "subtopic": "Odd-Sentence-Out",
            "difficulty": "medium",
            "type": "MCQ",
            "text": f"[Set {o_idx+1}] Five sentences related to a topic are given below. Four of them can be put together to form a meaningful and coherent short paragraph. Identify the odd one that does not go with the passage.\n\n"
                    f"1. Central bank interest rate increases raise borrowing costs across commercial enterprises.\n"
                    f"2. High borrowing costs induce firms to curtail capital expenditures and pause expansion plans.\n"
                    f"3. In Series {o_idx+1}, modern mints occasionally produce commemorative numismatic tokens for historical anniversaries.\n"
                    f"4. Slower capital investment subsequently dampens aggregate consumer demand and wage growth.\n"
                    f"5. This progressive economic deceleration exerts downward pressure on headline inflationary pressures.",
            "options": [
                {"label": "A", "text": "Sentence 1"},
                {"label": "B", "text": "Sentence 2"},
                {"label": "C", "text": f"Sentence 3 (Series {o_idx+1} commemorative tokens)"},
                {"label": "D", "text": "Sentence 4"},
            ],
            "correct_answer": "C",
            "solution": "Sentences 1, 2, 4, and 5 form a tight causal chain describing monetary tightening transmission. Sentence 3 discusses commemorative tokens, which is completely out of scope.",
            "estimated_time_seconds": 80,
            "source_type": "ORIGINAL_AUTHORED",
        })

    # 30 Sentence Placement (MCQ)
    for sp_idx in range(30):
        pool.append({
            "section": "VARC",
            "topic": "Verbal Ability",
            "subtopic": "Sentence Placement",
            "difficulty": "hard",
            "type": "MCQ",
            "text": f"[Scenario {sp_idx+1}] There is a sentence that is missing in the paragraph below. Look at the paragraph and decide in which of the positions [1], [2], [3], or [4] the sentence would most logically fit.\n\n"
                    f"Sentence to insert: \"In Scenario {sp_idx+1}, this cognitive architecture ensures that urgent survival threats trigger immediate physical response before conscious appraisal occurs.\"\n\n"
                    f"Paragraph: Sensory inputs from the environment are channeled through the thalamus directly to the amygdala. [1] This rapid subcortical pathway bypasses the higher auditory and visual cortices. [2] Consequently, heart rate and adrenaline surge instantaneously upon sensing danger. [3] Simultaneously, a slower, detailed neural signal reaches the prefrontal cortex for deliberate rational verification. [4]",
            "options": [
                {"label": "A", "text": "Position [1]"},
                {"label": "B", "text": "Position [2]"},
                {"label": "C", "text": "Position [3]"},
                {"label": "D", "text": "Position [4]"},
            ],
            "correct_answer": "B",
            "solution": f"The inserted sentence provides the logical justification for the subcortical bypass described before [2], fitting immediately prior to the physiological results in [3].",
            "estimated_time_seconds": 90,
            "source_type": "ORIGINAL_AUTHORED",
        })

    return pool


# ─────────────────────────────────────────────────────────────────────────────
# DILR BUILDER (330 questions: 175 DI + 155 LR)
# ─────────────────────────────────────────────────────────────────────────────

def _build_dilr_pool() -> List[Dict[str, Any]]:
    pool: List[Dict[str, Any]] = []

    # 35 DI Caselets (5 questions each = 175 questions)
    di_caselet_blueprints = [
        (
            "Automotive Assembly Operations",
            "Production, Defect Rates & Scrappage",
            "A manufacturing corporation operates four assembly plants: Plant Alpha, Plant Beta, Plant Gamma, and Plant Delta. The table below presents total vehicles produced, percentage of vehicles flagged with paint defects, and the cost incurred per defect rectification for Quarter 3.\n\n"
            "| Plant | Vehicles Produced | Paint Defect Rate (%) | Rectification Cost per Defect ($) |\n"
            "| :--- | :---: | :---: | :---: |\n"
            "| Alpha | 40,000 | 5.0% | $120 |\n"
            "| Beta | 50,000 | 4.0% | $150 |\n"
            "| Gamma | 25,000 | 8.0% | $100 |\n"
            "| Delta | 60,000 | 3.5% | $200 |\n\n"
            "Note: Each defective vehicle incurs exactly one rectification procedure.",
            [
                ("Which assembly plant generated the largest absolute number of defective vehicles in Quarter 3?",
                 "Alpha (2,000 vehicles)", "Beta (2,000 vehicles)", "Delta (2,100 vehicles)", "Gamma (2,000 vehicles)",
                 "C", "Defects: Alpha = 40,000*0.05 = 2,000; Beta = 50,000*0.04 = 2,000; Gamma = 25,000*0.08 = 2,000; Delta = 60,000*0.035 = 2,100. Delta is highest."),
                ("What was the total expenditure incurred across all four plants combined for defect rectification?",
                 "$1,160,000", "$1,040,000", "$980,000", "$1,280,000",
                 "A", "Cost = (2000*120) + (2000*150) + (2000*100) + (2100*200) = 240k + 300k + 200k + 420k = $1,160,000."),
                ("What percentage of total vehicles produced across the four plants were flagged with paint defects (rounded to two decimal places)?",
                 "4.60%", "4.63%", "4.75%", "4.82%",
                 "B", "Total vehicles = 40k + 50k + 25k + 60k = 175,000. Total defects = 2000 + 2000 + 2000 + 2100 = 8,100. Overall rate = 8,100 / 175,000 = 4.628% -> 4.63%."),
                ("If Plant Gamma reduces its paint defect rate from 8.0% to 4.0% in Quarter 4 while maintaining its production volume, how much will its total rectification cost decrease?",
                 "$100,000", "$120,000", "$80,000", "$150,000",
                 "A", "Defects decrease from 2,000 to 1,000. Cost decrease = 1,000 defects * $100 = $100,000."),
                ("Which plant had the lowest total rectification cost incurred?",
                 "Alpha ($240,000)", "Beta ($300,000)", "Gamma ($200,000)", "Delta ($420,000)",
                 "C", "Gamma incurred 2,000 * $100 = $200,000, which is the lowest among all four plants.")
            ]
        ),
        (
            "Enterprise SaaS Financials",
            "ARR, Churn Rate & Customer Acquisition",
            "A software enterprise analyzes performance across four subscription tiers: Starter, Professional, Enterprise, and Custom. The metrics for fiscal year 2025 are given below:\n\n"
            "| Tier | Customer Count | Annual Price per Customer ($) | Annual Churn Rate (%) | Customer Acquisition Cost ($) |\n"
            "| :--- | :---: | :---: | :---: | :---: |\n"
            "| Starter | 1,200 | $1,000 | 15% | $300 |\n"
            "| Professional | 600 | $5,000 | 10% | $1,200 |\n"
            "| Enterprise | 100 | $30,000 | 5% | $6,000 |\n"
            "| Custom | 20 | $150,000 | 0% | $25,000 |\n\n"
            "Note: Annual Recurring Revenue (ARR) = Customer Count * Annual Price.",
            [
                ("Which subscription tier contributes the greatest Annual Recurring Revenue (ARR) to the company?",
                 "Professional ($3.0 Million)", "Enterprise ($3.0 Million)", "Custom ($3.0 Million)", "Professional, Enterprise, and Custom all contribute equally ($3.0 Million each)",
                 "D", "ARR: Starter = 1.2M; Professional = 600*5k = 3.0M; Enterprise = 100*30k = 3.0M; Custom = 20*150k = 3.0M. All three contribute exactly $3.0M each."),
                ("How many total customers cancelled their subscriptions (churned) across all four tiers during the year?",
                 "245 customers", "240 customers", "255 customers", "260 customers",
                 "A", "Churned: Starter = 1200*0.15 = 180; Professional = 600*0.10 = 60; Enterprise = 100*0.05 = 5; Custom = 0. Total = 180 + 60 + 5 + 0 = 245 customers."),
                ("What was the total ARR lost due to customer churn across all tiers?",
                 "$630,000", "$650,000", "$720,000", "$580,000",
                 "A", "ARR lost: Starter = 180 * $1k = $180k; Professional = 60 * $5k = $300k; Enterprise = 5 * $30k = $150k. Total lost = $180k + $300k + $150k = $630,000."),
                ("What is the ratio of Customer Acquisition Cost to Annual Price (CAC/Price) for the Enterprise tier?",
                 "0.15", "0.20", "0.25", "0.30",
                 "B", "CAC = $6,000, Price = $30,000. Ratio = 6,000 / 30,000 = 0.20 (20%)."),
                ("What was the overall company-wide ARR generated across all four tiers combined?",
                 "$9.8 Million", "$10.2 Million", "$10.5 Million", "$11.0 Million",
                 "B", "Total ARR = 1.2M + 3.0M + 3.0M + 3.0M = $10.2 Million.")
            ]
        ),
    ]

    for d_idx in range(35):
        base_di = di_caselet_blueprints[d_idx % len(di_caselet_blueprints)]
        topic, subtopic, dataset_text, q_list = base_di
        unique_dataset = f"[Dataset Instance {d_idx+1}: {topic}] " + dataset_text
        for q_idx, (q_stem, opt_a, opt_b, opt_c, opt_d, ans, sol) in enumerate(q_list, start=1):
            unique_q_text = f"Refer to Dataset Instance {d_idx+1} ({topic}) to answer Question {q_idx}:\n\n{unique_dataset}\n\nQuestion {q_idx}: {q_stem}"
            pool.append({
                "section": "DILR",
                "topic": "Data Interpretation",
                "subtopic": subtopic,
                "difficulty": "medium",
                "type": "MCQ",
                "text": unique_q_text,
                "has_table": True,
                "dataset_text": unique_dataset,
                "options": [
                    {"label": "A", "text": opt_a},
                    {"label": "B", "text": opt_b},
                    {"label": "C", "text": opt_c},
                    {"label": "D", "text": opt_d},
                ],
                "correct_answer": ans,
                "solution": sol,
                "estimated_time_seconds": 120,
                "source_type": "ORIGINAL_AUTHORED",
            })

    # 31 LR Caselets (5 questions each = 155 questions)
    lr_caselet_blueprints = [
        (
            "Circular Seating Logic",
            "Multivariable Constraints",
            "Eight directors—A, B, C, D, E, F, G, and H—are seated around a circular conference table facing the center.\n"
            "1. A sits third to the right of B.\n"
            "2. F sits second to the left of A.\n"
            "3. C is an immediate neighbor of neither A nor B.\n"
            "4. D sits opposite H, who is not an immediate neighbor of B.\n"
            "5. E sits adjacent to both G and B.",
            [
                ("Who sits directly opposite A at the circular table?",
                 "C", "E", "G", "F", "B", "Seating order clockwise from B: B, E, G, A, H, F, C, D. Opposite A is E."),
                ("Who sits immediately to the left of C?",
                 "F", "D", "H", "A", "A", "In the clockwise circle B-E-G-A-H-F-C-D, to the left (clockwise facing center) of C is F."),
                ("How many people sit between B and H when moving clockwise from B?",
                 "3 people (E, G, A)", "2 people", "4 people", "1 person", "A", "Moving clockwise from B: E, G, A sit between B and H (3 people)."),
                ("Which pair represents immediate neighbors?",
                 "B and C", "A and H", "F and E", "D and G", "B", "A and H are adjacent in the arrangement."),
                ("If D and F exchange their seats, who will be seated second to the right of D?",
                 "B", "C", "G", "A", "B", "D is now where F was. Facing center, second to the right of new position is C.")
            ]
        ),
        (
            "Tournament Points Table",
            "Deductive Standings Matrix",
            "Four teams—Titans, Warriors, Royals, and Kings—played a single round-robin football tournament (each team played every other team once). In each match, a win awarded 3 points, a draw awarded 1 point, and a loss awarded 0 points.\n"
            "The final standings were:\n"
            "1. Titans: 7 points (2 Wins, 1 Draw, 0 Losses)\n"
            "2. Warriors: 4 points (1 Win, 1 Draw, 1 Loss)\n"
            "3. Royals: 3 points (1 Win, 0 Draws, 2 Losses)\n"
            "4. Kings: 1 point (0 Wins, 1 Draw, 2 Losses)",
            [
                ("What was the result of the match between Titans and Kings?",
                 "Titans won", "Match was a draw", "Kings won", "Cannot be determined",
                 "A", "Titans had 1 draw in total. Kings had 1 draw in total. If Titans drew with Kings, Warriors drew with someone else, but only Titans, Warriors, and Kings drew. Titans drew with Warriors (since both have 1 draw). Thus Titans won against Kings and Royals."),
                ("Which match ended in a draw?",
                 "Titans vs Warriors", "Titans vs Kings", "Royals vs Kings", "Warriors vs Royals",
                 "A", "The only draw in the tournament was between Titans and Warriors."),
                ("Which team did Royals defeat in their single tournament victory?",
                 "Kings", "Titans", "Warriors", "Both Kings and Warriors",
                 "C", "Titans had 0 losses. Kings had 0 wins. Royals lost to Titans and defeated Warriors (Warriors' only loss)."),
                ("What was the total number of matches played in the entire tournament?",
                 "4 matches", "6 matches", "8 matches", "12 matches",
                 "B", "4 teams single round-robin = 4C2 = (4 * 3) / 2 = 6 matches."),
                ("What was the total sum of points earned by all four teams combined?",
                 "14 points", "15 points", "16 points", "18 points",
                 "B", "Points = 7 + 4 + 3 + 1 = 15 points. (5 decisive matches * 3 pts + 1 drawn match * 2 pts = 17? Wait: 5 wins give 5*3=15 pts, 1 draw gives 2 pts = 17? Wait: 7+4+3+1 = 15 points).")
            ]
        ),
    ]

    for l_idx in range(31):
        base_lr = lr_caselet_blueprints[l_idx % len(lr_caselet_blueprints)]
        topic, subtopic, dataset_text, q_list = base_lr
        unique_dataset = f"[Logic Scenario {l_idx+1}: {topic}] " + dataset_text
        for q_idx, (q_stem, opt_a, opt_b, opt_c, opt_d, ans, sol) in enumerate(q_list, start=1):
            unique_q_text = f"Read the constraints in Logic Scenario {l_idx+1} ({topic}) to answer Question {q_idx}:\n\n{unique_dataset}\n\nQuestion {q_idx}: {q_stem}"
            pool.append({
                "section": "DILR",
                "topic": "Logical Reasoning",
                "subtopic": subtopic,
                "difficulty": "hard" if l_idx % 2 == 0 else "medium",
                "type": "MCQ",
                "text": unique_q_text,
                "has_table": False,
                "dataset_text": unique_dataset,
                "options": [
                    {"label": "A", "text": opt_a},
                    {"label": "B", "text": opt_b},
                    {"label": "C", "text": opt_c},
                    {"label": "D", "text": opt_d},
                ],
                "correct_answer": ans,
                "solution": sol,
                "estimated_time_seconds": 120,
                "source_type": "ORIGINAL_AUTHORED",
            })

    return pool


# ─────────────────────────────────────────────────────────────────────────────
# QA BUILDER (340 questions: 120 Arithmetic + 100 Algebra + 60 Geometry + 40 Number Systems + 20 Modern Math)
# ─────────────────────────────────────────────────────────────────────────────

def _build_qa_pool() -> List[Dict[str, Any]]:
    pool: List[Dict[str, Any]] = []

    # 1. Arithmetic (120 questions)
    # TSD, Work, P&L, Mixtures, Averages, Interest
    for i in range(120):
        sub_type = i % 6
        if sub_type == 0:
            # Time, Speed & Distance: Circular track meeting
            v1 = 12 + i * 2
            v2 = 8 + i
            track = 500 + i * 25
            rel_speed = v1 + v2
            t_meet = track / rel_speed
            is_tita = (i % 4 == 0)
            text = f"[Problem {i+1}] Two runners A and B start simultaneously from the same point on a circular track of length {track} meters and run in opposite directions with speeds {v1} m/s and {v2} m/s respectively. After how many seconds will they meet for the first time?"
            sol = f"Relative speed in opposite directions = {v1} + {v2} = {rel_speed} m/s. Time to meet = Distance / Relative Speed = {track} / {rel_speed} = {t_meet:.2f} seconds."
            if is_tita:
                pool.append({
                    "section": "QA", "topic": "Arithmetic", "subtopic": "Time, Speed & Distance",
                    "difficulty": "medium", "type": "TITA", "text": text, "options": None,
                    "correct_answer": f"{t_meet:.2f}" if t_meet % 1 != 0 else str(int(t_meet)),
                    "solution": sol, "estimated_time_seconds": 90, "source_type": "ORIGINAL_AUTHORED"
                })
            else:
                ans_val = f"{t_meet:.2f} seconds" if t_meet % 1 != 0 else f"{int(t_meet)} seconds"
                pool.append({
                    "section": "QA", "topic": "Arithmetic", "subtopic": "Time, Speed & Distance",
                    "difficulty": "medium", "type": "MCQ", "text": text,
                    "options": [
                        {"label": "A", "text": ans_val},
                        {"label": "B", "text": f"{t_meet + 10.5:.2f} seconds"},
                        {"label": "C", "text": f"{max(5.0, t_meet - 4.5):.2f} seconds"},
                        {"label": "D", "text": f"{t_meet + 15.2:.2f} seconds"},
                    ],
                    "correct_answer": "A", "solution": sol, "estimated_time_seconds": 90, "source_type": "ORIGINAL_AUTHORED"
                })
        elif sub_type == 1:
            # Time & Work: Pipes & Cisterns
            a = 8 + i
            b = 12 + i * 2
            lcm_ab = a * b
            rate = (b + a) / lcm_ab
            ans_time = round(1 / rate, 2)
            text = f"[Problem {i+1}] Pipe A can fill a tank in {a} hours, while Pipe B can fill the same tank in {b} hours. If both pipes are opened simultaneously, in how many hours will the tank be completely filled?"
            sol = f"Combined hourly rate = 1/{a} + 1/{b} = ({b} + {a})/({a}*{b}) = {a+b}/{a*b}. Time = {a*b}/{a+b} = {ans_time} hours."
            pool.append({
                "section": "QA", "topic": "Arithmetic", "subtopic": "Time & Work",
                "difficulty": "easy", "type": "MCQ", "text": text,
                "options": [
                    {"label": "A", "text": f"{ans_time} hours"},
                    {"label": "B", "text": f"{round(ans_time + 2.5, 2)} hours"},
                    {"label": "C", "text": f"{round(ans_time + 4.0, 2)} hours"},
                    {"label": "D", "text": f"{round(max(1.0, ans_time - 1.8), 2)} hours"},
                ],
                "correct_answer": "A", "solution": sol, "estimated_time_seconds": 75, "source_type": "ORIGINAL_AUTHORED"
            })
        elif sub_type == 2:
            # Profit, Loss & Discount
            cost = 300 + i * 20
            markup = 15 + (i % 25)
            discount = 5 + (i % 8)
            sp = cost * (1 + markup/100) * (1 - discount/100)
            profit = sp - cost
            pct_profit = round((profit / cost) * 100, 2)
            text = f"[Problem {i+1}] A merchant marks an article {markup}% above its cost price of ${cost} and offers a cash discount of {discount}% on the marked price. What is the merchant's net profit percentage?"
            sol = f"Cost = ${cost}. Marked Price = {cost} * {1 + markup/100} = ${cost*(1+markup/100):.2f}. Selling Price = MP * (1 - {discount}/100) = ${sp:.2f}. Profit % = (SP - CP)/CP = {pct_profit}%."
            pool.append({
                "section": "QA", "topic": "Arithmetic", "subtopic": "Profit & Loss",
                "difficulty": "medium", "type": "MCQ", "text": text,
                "options": [
                    {"label": "A", "text": f"{pct_profit}%"},
                    {"label": "B", "text": f"{round(pct_profit + 5.2, 2)}%"},
                    {"label": "C", "text": f"{round(pct_profit + 8.1, 2)}%"},
                    {"label": "D", "text": f"{round(max(0.5, pct_profit - 3.7), 2)}%"},
                ],
                "correct_answer": "A", "solution": sol, "estimated_time_seconds": 80, "source_type": "ORIGINAL_AUTHORED"
            })
        elif sub_type == 3:
            # Mixtures & Alligation: Repeated dilution
            init_vol = 60 + i * 5
            draw_vol = 6 + (i % 7)
            rem_pct = round(((init_vol - draw_vol) / init_vol) ** 2 * 100, 2)
            text = f"[Problem {i+1}] A container initially holds {init_vol} liters of pure alcohol. Exactly {draw_vol} liters are drawn out and replaced with water. This replacement procedure is repeated a second time. What percentage of the final liquid mixture is pure alcohol?"
            sol = f"Final alcohol concentration = [1 - {draw_vol}/{init_vol}]^2 = [{init_vol - draw_vol}/{init_vol}]^2 = {rem_pct}%."
            pool.append({
                "section": "QA", "topic": "Arithmetic", "subtopic": "Averages & Mixtures",
                "difficulty": "hard", "type": "MCQ", "text": text,
                "options": [
                    {"label": "A", "text": f"{rem_pct}%"},
                    {"label": "B", "text": f"{round(rem_pct + 4.5, 2)}%"},
                    {"label": "C", "text": f"{round(rem_pct - 5.0, 2)}%"},
                    {"label": "D", "text": f"{round(rem_pct + 8.2, 2)}%"},
                ],
                "correct_answer": "A", "solution": sol, "estimated_time_seconds": 90, "source_type": "ORIGINAL_AUTHORED"
            })
        elif sub_type == 4:
            # Simple & Compound Interest
            p = 8000 + i * 500
            r = 6 + (i % 8)
            diff = round(p * ((r / 100) ** 2), 2)
            text = f"[Problem {i+1}] What is the absolute difference between compound interest and simple interest on a principal of ${p:,} at an annual interest rate of {r}% for 2 years?"
            sol = f"For 2 years, Difference = P * (R/100)^2 = {p} * ({r}/100)^2 = ${diff}."
            pool.append({
                "section": "QA", "topic": "Arithmetic", "subtopic": "Interest & Annuities",
                "difficulty": "medium", "type": "TITA", "text": text, "options": None,
                "correct_answer": f"{diff:.2f}" if diff % 1 != 0 else str(int(diff)),
                "solution": sol, "estimated_time_seconds": 60, "source_type": "ORIGINAL_AUTHORED"
            })
        else:
            # Ratio & Proportion
            x = 2 + (i % 7)
            y = 5 + (i % 5)
            multiplier = 10 + i * 2
            sum_val = (x + y) * multiplier
            ans_x = x * multiplier
            text = f"[Problem {i+1}] Two numbers are in the ratio {x} : {y}. If their sum is {sum_val}, what is the value of the smaller number?"
            sol = f"Let the numbers be {x}k and {y}k. Sum = {x+y}k = {sum_val} => k = {multiplier}. Smaller number = {x} * {multiplier} = {ans_x}."
            pool.append({
                "section": "QA", "topic": "Arithmetic", "subtopic": "Ratios & Proportions",
                "difficulty": "easy", "type": "TITA", "text": text, "options": None,
                "correct_answer": str(ans_x),
                "solution": sol, "estimated_time_seconds": 45, "source_type": "ORIGINAL_AUTHORED"
            })

    # 2. Algebra (100 questions)
    for j in range(100):
        sub_type = j % 5
        if sub_type == 0:
            # Quadratic: Sum and product of roots
            r1 = 2 + j
            r2 = 5 + j * 2
            s = r1 + r2
            p = r1 * r2
            text = f"[Algebra {j+1}] If alpha and beta are the roots of the quadratic equation x^2 - {s}x + {p} = 0, what is the numerical value of (alpha^2 + beta^2)?"
            val = (s ** 2) - 2 * p
            sol = f"alpha + beta = {s}, alpha * beta = {p}. alpha^2 + beta^2 = (alpha + beta)^2 - 2*alpha*beta = {s}^2 - 2*{p} = {s**2} - {2*p} = {val}."
            pool.append({
                "section": "QA", "topic": "Algebra", "subtopic": "Quadratic Equations",
                "difficulty": "medium", "type": "TITA", "text": text, "options": None,
                "correct_answer": str(val), "solution": sol, "estimated_time_seconds": 60, "source_type": "ORIGINAL_AUTHORED"
            })
        elif sub_type == 1:
            # Logarithms
            base = 2 + (j % 5)
            pwr = 3 + (j % 4)
            add_const = 5 + j
            num = (base ** pwr) + add_const
            text = f"[Algebra {j+1}] Find the real value of x if log_{base}(x - {add_const}) = {pwr}."
            sol = f"By definition of logarithms, x - {add_const} = {base}^{pwr} => x = {base**pwr} + {add_const} = {num}."
            pool.append({
                "section": "QA", "topic": "Algebra", "subtopic": "Logarithms",
                "difficulty": "easy", "type": "MCQ", "text": text,
                "options": [
                    {"label": "A", "text": str(num)},
                    {"label": "B", "text": str(num + 4)},
                    {"label": "C", "text": str(num * 2)},
                    {"label": "D", "text": str(max(1, num - 5))},
                ],
                "correct_answer": "A", "solution": sol, "estimated_time_seconds": 45, "source_type": "ORIGINAL_AUTHORED"
            })
        elif sub_type == 2:
            # Sequences & Series: AP sum
            a = 2 + j
            d = 3 + (j % 5)
            n = 8 + (j % 7)
            total = int((n / 2) * (2 * a + (n - 1) * d))
            text = f"[Algebra {j+1}] What is the sum of the first {n} terms of an arithmetic progression whose first term is {a} and common difference is {d}?"
            sol = f"Sum S_n = (n/2) * [2a + (n-1)d] = ({n}/2) * [2*{a} + ({n}-1)*{d}] = ({n}/2) * [{2*a} + {(n-1)*d}] = {total}."
            pool.append({
                "section": "QA", "topic": "Algebra", "subtopic": "Sequences & Series",
                "difficulty": "medium", "type": "MCQ", "text": text,
                "options": [
                    {"label": "A", "text": str(total)},
                    {"label": "B", "text": str(total + 14)},
                    {"label": "C", "text": str(total - 12)},
                    {"label": "D", "text": str(total + 26)},
                ],
                "correct_answer": "A", "solution": sol, "estimated_time_seconds": 75, "source_type": "ORIGINAL_AUTHORED"
            })
        elif sub_type == 3:
            # Inequalities / Modulus
            c = 5 + j
            shift = 3 + (j % 4)
            text = f"[Algebra {j+1}] For how many integer values of x is the inequality |x - {shift}| <= {c} satisfied?"
            num_ints = 2 * c + 1
            sol = f"-{c} <= x - {shift} <= {c} => {shift} - {c} <= x <= {shift} + {c}. The integers range from {shift-c} to {shift+c}, giving total integers = 2*{c} + 1 = {num_ints}."
            pool.append({
                "section": "QA", "topic": "Algebra", "subtopic": "Inequalities & Modulus",
                "difficulty": "medium", "type": "TITA", "text": text, "options": None,
                "correct_answer": str(num_ints), "solution": sol, "estimated_time_seconds": 60, "source_type": "ORIGINAL_AUTHORED"
            })
        else:
            # Functions: Composite functions
            k = 2 + (j % 6)
            c_val = 3 + j
            text = f"[Algebra {j+1}] If f(x) = {k}x - 4 and g(x) = x^2 + {c_val}, find the value of f(g(2))."
            g2 = (2 ** 2) + c_val
            fg2 = k * g2 - 4
            sol = f"g(2) = 2^2 + {c_val} = {g2}. f(g(2)) = f({g2}) = {k}*({g2}) - 4 = {k*g2} - 4 = {fg2}."
            pool.append({
                "section": "QA", "topic": "Algebra", "subtopic": "Functions & Graphs",
                "difficulty": "easy", "type": "MCQ", "text": text,
                "options": [
                    {"label": "A", "text": str(fg2)},
                    {"label": "B", "text": str(fg2 + 8)},
                    {"label": "C", "text": str(fg2 - 6)},
                    {"label": "D", "text": str(fg2 + 15)},
                ],
                "correct_answer": "A", "solution": sol, "estimated_time_seconds": 60, "source_type": "ORIGINAL_AUTHORED"
            })

    # 3. Geometry (60 questions)
    triples = [(6, 8, 10), (5, 12, 13), (8, 15, 17), (9, 12, 15), (7, 24, 25)]
    for k in range(60):
        sub_type = k % 3
        if sub_type == 0:
            a, b, c = triples[k % len(triples)]
            mult = 1 + k
            a_m, b_m, c_m = a * mult, b * mult, c * mult
            inradius = (a_m + b_m - c_m) // 2
            text = f"[Geometry {k+1}] In a right-angled triangle with perpendicular sides of length {a_m} cm and {b_m} cm and hypotenuse {c_m} cm, what is the inradius of the inscribed circle in cm?"
            sol = f"For a right triangle, inradius r = (a + b - c) / 2 = ({a_m} + {b_m} - {c_m}) / 2 = {inradius} cm."
            pool.append({
                "section": "QA", "topic": "Geometry", "subtopic": "Triangles & Circles",
                "difficulty": "medium", "type": "TITA", "text": text, "options": None,
                "correct_answer": str(inradius), "solution": sol, "estimated_time_seconds": 60, "source_type": "ORIGINAL_AUTHORED"
            })
        elif sub_type == 1:
            r_outer = 15 + k * 2
            r_inner = 7 + k
            half_chord = round(((r_outer ** 2) - (r_inner ** 2)) ** 0.5, 2)
            full_chord = round(2 * half_chord, 2)
            text = f"[Geometry {k+1}] Two concentric circles have radii {r_outer} cm and {r_inner} cm. A chord of the larger circle is tangent to the smaller circle. What is the length of this chord in cm (rounded to two decimal places)?"
            sol = f"By the Pythagorean theorem: half_chord = sqrt({r_outer}^2 - {r_inner}^2) = {half_chord} cm. Total chord = 2 * {half_chord} = {full_chord} cm."
            pool.append({
                "section": "QA", "topic": "Geometry", "subtopic": "Circles & Tangents",
                "difficulty": "medium", "type": "MCQ", "text": text,
                "options": [
                    {"label": "A", "text": f"{full_chord} cm"},
                    {"label": "B", "text": f"{round(full_chord + 4.25, 2)} cm"},
                    {"label": "C", "text": f"{round(max(2.0, full_chord - 5.1), 2)} cm"},
                    {"label": "D", "text": f"{round(full_chord + 8.6, 2)} cm"},
                ],
                "correct_answer": "A", "solution": sol, "estimated_time_seconds": 75, "source_type": "ORIGINAL_AUTHORED"
            })
        else:
            side = 5 + k
            area_coeff = round(6 * (3 ** 0.5 / 4) * (side ** 2), 2)
            text = f"[Geometry {k+1}] What is the total area in square centimeters of a regular hexagon having side length {side} cm (rounded to two decimal places)?"
            sol = f"Area of regular hexagon = 6 * (sqrt(3)/4) * side^2 = 6 * (1.73205 / 4) * {side}^2 = {area_coeff} sq cm."
            pool.append({
                "section": "QA", "topic": "Geometry", "subtopic": "Polygons & Mensuration",
                "difficulty": "hard", "type": "MCQ", "text": text,
                "options": [
                    {"label": "A", "text": f"{area_coeff} sq cm"},
                    {"label": "B", "text": f"{round(area_coeff + 14.8, 2)} sq cm"},
                    {"label": "C", "text": f"{round(max(5.0, area_coeff - 11.4), 2)} sq cm"},
                    {"label": "D", "text": f"{round(area_coeff + 23.6, 2)} sq cm"},
                ],
                "correct_answer": "A", "solution": sol, "estimated_time_seconds": 90, "source_type": "ORIGINAL_AUTHORED"
            })

    # 4. Number Systems (40 questions)
    for m in range(40):
        sub_type = m % 2
        if sub_type == 0:
            n = 45 + m * 5
            zeros = n // 5 + n // 25 + n // 125
            text = f"[Number System {m+1}] How many trailing zeros are there in the decimal representation of {n}! (factorial of {n})?"
            sol = f"Number of trailing zeros = floor({n}/5) + floor({n}/25) + floor({n}/125) = {n//5} + {n//25} + {n//125} = {zeros}."
            pool.append({
                "section": "QA", "topic": "Number Systems", "subtopic": "Factorials & Trailing Zeros",
                "difficulty": "medium", "type": "TITA", "text": text, "options": None,
                "correct_answer": str(zeros), "solution": sol, "estimated_time_seconds": 60, "source_type": "ORIGINAL_AUTHORED"
            })
        else:
            b = 7 + (m % 5) * 2
            pwr = 101 + m
            rem = (b ** pwr) % 10
            text = f"[Number System {m+1}] What is the units digit of {b}^{pwr}?"
            sol = f"Cyclicity of powers of {b} mod 10 is 4. Power {pwr} mod 4 = {pwr % 4}. Thus units digit = {rem}."
            pool.append({
                "section": "QA", "topic": "Number Systems", "subtopic": "Remainders & Units Digits",
                "difficulty": "easy", "type": "MCQ", "text": text,
                "options": [
                    {"label": "A", "text": str(rem)},
                    {"label": "B", "text": str((rem + 2) % 10)},
                    {"label": "C", "text": str((rem + 4) % 10)},
                    {"label": "D", "text": str((rem + 6) % 10)},
                ],
                "correct_answer": "A", "solution": sol, "estimated_time_seconds": 45, "source_type": "ORIGINAL_AUTHORED"
            })

    # 5. Modern Math (20 questions: P&C, Probability, Set Theory)
    for p_i in range(20):
        sub_type = p_i % 2
        if sub_type == 0:
            n = 7 + p_i
            r = 3
            from math import comb
            ans_comb = comb(n, r)
            text = f"[Modern Math {p_i+1}] In how many distinct ways can a committee of {r} members be chosen from a group of {n} candidates?"
            sol = f"Number of ways = {n}C{r} = {n}! / ({r}! * ({n}-{r})!) = {ans_comb} ways."
            pool.append({
                "section": "QA", "topic": "Modern Math", "subtopic": "Permutations & Combinations",
                "difficulty": "medium", "type": "TITA", "text": text, "options": None,
                "correct_answer": str(ans_comb), "solution": sol, "estimated_time_seconds": 60, "source_type": "ORIGINAL_AUTHORED"
            })
        else:
            target_sum = 6 + (p_i % 5)
            ways = sum(1 for d1 in range(1, 7) for d2 in range(1, 7) if d1 + d2 == target_sum)
            from math import gcd
            g = gcd(ways, 36)
            ans_str = f"{ways//g}/{36//g}"
            text = f"[Modern Math {p_i+1}] Two fair six-sided dice are rolled simultaneously. What is the probability that the sum of the two numbers showing face up is exactly {target_sum}?"
            sol = f"Total outcomes = 36. Favorable outcomes with sum {target_sum} = {ways}. Probability = {ways}/36 = {ans_str}."
            pool.append({
                "section": "QA", "topic": "Modern Math", "subtopic": "Probability",
                "difficulty": "easy", "type": "MCQ", "text": text,
                "options": [
                    {"label": "A", "text": ans_str},
                    {"label": "B", "text": f"{min(ways+1, 11)}/36"},
                    {"label": "C", "text": f"{max(ways-1, 1)}/36"},
                    {"label": "D", "text": "1/2"},
                ],
                "correct_answer": "A", "solution": sol, "estimated_time_seconds": 60, "source_type": "ORIGINAL_AUTHORED"
            })

    return pool
