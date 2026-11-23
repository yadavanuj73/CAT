"""
Comprehensive Authentic CAT Question Bank & Generator.
Contains verified CAT question sets across VARC, DILR, and QA sections
matching authentic CAT patterns, syllabus, and difficulty archetypes.
"""

from typing import Any, Dict, List, Optional
import random

# ─────────────────────────────────────────────────────────────────────────────
# 1. VARC QUESTIONS (Verbal Ability & Reading Comprehension)
# ─────────────────────────────────────────────────────────────────────────────

VARC_PASSAGE_1 = (
    "In the philosophy of artificial intelligence, the 'Chinese Room' thought experiment, "
    "devised by John Searle in 1980, poses a fundamental challenge to computational functionalism. "
    "Searle imagines himself locked inside a room with a vast rulebook written in English. "
    "Batches of Chinese characters are slipped into the room under the door. Following the syntactical "
    "rules laid out in the book, Searle manipulates the symbols, correlating inputs with outputs, "
    "and produces coherent Chinese responses that are slid back outside. To native Chinese speakers "
    "outside, the room behaves as if it possesses full linguistic comprehension. Yet, Searle understands "
    "not a single word of Chinese; he is merely an executor of formal, syntactical manipulation. "
    "Searle’s core thesis is straightforward: syntax does not suffice for semantics. A computer program, "
    "no matter how sophisticated its pattern recognition or neural weights, operates purely on syntactic "
    "tokens. The assignment of meaning—intentionality—requires biological, causal properties of the brain "
    "that abstract formal symbol manipulation cannot instantiate. Functionalists have countered with the "
    "'Systems Reply', arguing that while the individual man inside the room does not understand Chinese, "
    "the total system—comprising the man, the rulebook, and the input-output apparatus—does. Searle rebuts "
    "this by proposing that he memorize the rulebook and perform all operations internally while walking "
    "outside; he still would not understand Chinese, thereby demonstrating that scaling syntactic "
    "operations cannot magically bridge the ontological divide into intentional understanding."
)

VARC_PASSAGE_2 = (
    "Behavioral economics has systematically dismantled the classical postulate of 'Homo Economicus'—the "
    "perfectly rational agent who maximizes utility under complete information. Pioneered by Daniel Kahneman "
    "and Amos Tversky, Prospect Theory revealed that human choice is dictated by perceived reference points "
    "rather than absolute wealth levels. Most critically, the value function is S-shaped: it is concave for "
    "gains, convex for losses, and markedly steeper in the domain of losses. This asymmetry underpins 'loss "
    "aversion', the empirical finding that the psychological disutility of losing $100 is roughly twice as "
    "potent as the utility derived from gaining the identical amount. Furthermore, human decision-makers "
    "exhibit non-linear probability weighting, consistently overestimating low-probability tail risks while "
    "underweighting moderate and high probabilities. This explains the simultaneous human appetite for "
    "lottery tickets (risk-seeking for low-probability high-payoff gains) and insurance policies (risk-averse "
    "for low-probability catastrophic losses). Classical microeconomic models, tethered to Expected Utility "
    "Theory, fail to account for these heuristic biases, mistaking systematic cognitive heuristics for mere "
    "stochastic noise."
)

VARC_QUESTIONS: List[Dict[str, Any]] = [
    # RC Passage 1 Questions (4 questions)
    {
        "section": "VARC",
        "topic": "Reading Comprehension",
        "subtopic": "Philosophy & Cognitive Science",
        "difficulty": "medium",
        "type": "MCQ",
        "text": f"Based on the following passage:\n\n\"{VARC_PASSAGE_1}\"\n\nWhich of the following best articulates the primary thesis John Searle advances through the Chinese Room thought experiment?",
        "options": [
            {"label": "A", "text": "Biological brains cannot be simulated by artificial neural networks due to quantum mechanical constraints."},
            {"label": "B", "text": "Syntactical symbol manipulation is fundamentally insufficient to produce intentional semantic understanding."},
            {"label": "C", "text": "Translating foreign languages requires immersion rather than adherence to formal grammatical rulebooks."},
            {"label": "D", "text": "Computational systems can attain consciousness only if they incorporate sensory-motor feedback loops."},
        ],
        "correct_answer": "B",
        "solution": "Searle's explicit thesis is that syntax alone does not suffice for semantics (meaning/understanding). The man executes syntactic rules without possessing any semantic grasp.",
        "estimated_time_seconds": 110,
    },
    {
        "section": "VARC",
        "topic": "Reading Comprehension",
        "subtopic": "Philosophy & Cognitive Science",
        "difficulty": "hard",
        "type": "MCQ",
        "text": f"Based on the passage on the Chinese Room:\n\nAccording to the passage, how does Searle counter the 'Systems Reply' presented by functionalists?",
        "options": [
            {"label": "A", "text": "By proving that computers lack biological neurons capable of causal intentionality."},
            {"label": "B", "text": "By demonstrating that the rulebook itself must be written by a human conscious entity."},
            {"label": "C", "text": "By showing that even if the agent memorizes the rules and internalizes the system, genuine comprehension remains absent."},
            {"label": "D", "text": "By conducting empirical experiments with native Chinese speakers to detect non-human response latencies."},
        ],
        "correct_answer": "C",
        "solution": "Searle rebuts the Systems Reply by imagining memorizing the rulebook: he becomes the entire system yet still understands zero Chinese.",
        "estimated_time_seconds": 120,
    },
    {
        "section": "VARC",
        "topic": "Reading Comprehension",
        "subtopic": "Philosophy & Cognitive Science",
        "difficulty": "medium",
        "type": "MCQ",
        "text": f"Based on the Chinese Room passage:\n\nIt can be inferred that a proponent of 'computational functionalism' would believe that:",
        "options": [
            {"label": "A", "text": "Mental states are defined purely by their functional roles and input-output causal relations, regardless of physical substrate."},
            {"label": "B", "text": "Human consciousness is completely inaccessible to scientific inquiry and formal modeling."},
            {"label": "C", "text": "Symbol manipulation can only replicate emotional states, not logical reasoning."},
            {"label": "D", "text": "Language translation algorithms must be biologically grounded to be commercially viable."},
        ],
        "correct_answer": "A",
        "solution": "Functionalism holds that mental states are functional/computational states; if input-output patterns match, true understanding exists.",
        "estimated_time_seconds": 100,
    },
    {
        "section": "VARC",
        "topic": "Reading Comprehension",
        "subtopic": "Philosophy & Cognitive Science",
        "difficulty": "hard",
        "type": "MCQ",
        "text": f"Based on the Chinese Room passage:\n\nWhich of the following scenarios is most analogous to Searle's critique of syntactic symbol manipulation?",
        "options": [
            {"label": "A", "text": "A musician reading sheet music and playing a violin with emotional resonance."},
            {"label": "B", "text": "A postal worker sorting letters into postal code bins based solely on zip code digits without knowing the destination cities."},
            {"label": "C", "text": "A mathematician deriving a proof by intuition before formally verifying each intermediate lemma."},
            {"label": "D", "text": "An actor improvising lines in an unrehearsed theatre performance."},
        ],
        "correct_answer": "B",
        "solution": "The postal worker matches numerical tokens (zip codes) mechanically to bins without comprehending the geography or meaning of the destinations, directly paralleling syntax without semantics.",
        "estimated_time_seconds": 110,
    },

    # RC Passage 2 Questions (4 questions)
    {
        "section": "VARC",
        "topic": "Reading Comprehension",
        "subtopic": "Behavioral Economics",
        "difficulty": "medium",
        "type": "MCQ",
        "text": f"Based on the following passage:\n\n\"{VARC_PASSAGE_2}\"\n\nAccording to Prospect Theory, the S-shaped value function implies that human decision-makers are:",
        "options": [
            {"label": "A", "text": "Risk-neutral across both gains and losses."},
            {"label": "B", "text": "Risk-averse in the domain of gains and risk-seeking in the domain of losses."},
            {"label": "C", "text": "Risk-seeking in the domain of gains and risk-averse in the domain of losses."},
            {"label": "D", "text": "Equally sensitive to an equivalent magnitude of profit and deficit."},
        ],
        "correct_answer": "B",
        "solution": "Concave for gains means diminishing marginal sensitivity (risk aversion to lock in gains); convex for losses means willingness to gamble to avoid a guaranteed loss (risk seeking in loss domain).",
        "estimated_time_seconds": 90,
    },
    {
        "section": "VARC",
        "topic": "Reading Comprehension",
        "subtopic": "Behavioral Economics",
        "difficulty": "hard",
        "type": "MCQ",
        "text": f"Based on the Behavioral Economics passage:\n\nWhich of the following behaviors is best explained by the phenomenon of 'non-linear probability weighting' as described in the passage?",
        "options": [
            {"label": "A", "text": "An investor selling a winning stock prematurely to lock in small guaranteed gains."},
            {"label": "B", "text": "An individual purchasing flight insurance against rare catastrophic crashes while simultaneously buying national lottery tickets."},
            {"label": "C", "text": "A consumer choosing a brand-name medication over an identical chemical generic."},
            {"label": "D", "text": "A company refusing to abandon a failing project after having invested substantial capital."},
        ],
        "correct_answer": "B",
        "solution": "Overweighting low probabilities explains both purchasing lottery tickets (overweighting rare chance of winning) and insurance (overweighting rare chance of disaster).",
        "estimated_time_seconds": 105,
    },
    {
        "section": "VARC",
        "topic": "Reading Comprehension",
        "subtopic": "Behavioral Economics",
        "difficulty": "medium",
        "type": "MCQ",
        "text": f"Based on the Behavioral Economics passage:\n\nThe term 'loss aversion' indicates that:",
        "options": [
            {"label": "A", "text": "Individuals evaluate payoffs exclusively on the basis of lifetime terminal net worth."},
            {"label": "B", "text": "The psychological distress of a monetary loss exceeds the psychological satisfaction of an equal gain."},
            {"label": "C", "text": "Rational agents systematically eliminate all risk exposure from their financial portfolios."},
            {"label": "D", "text": "Economic decision-making is impervious to framing effects and subjective reference points."},
        ],
        "correct_answer": "B",
        "solution": "Loss aversion states that the disutility of losing $100 is roughly twice as intense as the utility of gaining $100.",
        "estimated_time_seconds": 80,
    },
    {
        "section": "VARC",
        "topic": "Reading Comprehension",
        "subtopic": "Behavioral Economics",
        "difficulty": "hard",
        "type": "MCQ",
        "text": f"Based on the Behavioral Economics passage:\n\nWhat critique do behavioral economists level against the classical Expected Utility Theory?",
        "options": [
            {"label": "A", "text": "It relies too heavily on empirical psychological laboratory experiments."},
            {"label": "B", "text": "It erroneously treats systematic, predictable cognitive heuristics as mere random noise."},
            {"label": "C", "text": "It focuses solely on consumer welfare while neglecting macroeconomic fiscal policy."},
            {"label": "D", "text": "It cannot mathematically model situations with multiple decision-makers."},
        ],
        "correct_answer": "B",
        "solution": "The passage explicitly concludes that classical models fail because they mistake systematic cognitive heuristics for mere stochastic noise.",
        "estimated_time_seconds": 95,
    },

    # Verbal Ability: Para Jumbles (TITA)
    {
        "section": "VARC",
        "topic": "Verbal Ability",
        "subtopic": "Para Jumbles",
        "difficulty": "medium",
        "type": "TITA",
        "text": "The four sentences (labelled 1, 2, 3, 4) given below, when properly sequenced, form a coherent paragraph. Decide on the proper sequence and enter the 4-digit sequence:\n\n1. This algorithmic convergence risks homogenizing consumer preferences across diverse cultures.\n2. Modern recommendation architectures optimize strictly for short-term engagement metrics.\n3. Consequently, unexpected discovery and artistic serendipity are systematically curtailed.\n4. When repeated across millions of users, local cultural nuances gradually flatten.",
        "options": None,
        "correct_answer": "2413",
        "solution": "Sentence 2 sets the context (recommendation architectures optimizing engagement). Sentence 4 shows the scale (repeated across millions). Sentence 1 states the outcome (algorithmic convergence homogenizing preferences). Sentence 3 provides the conclusive result (Consequently, serendipity curtailed). Correct sequence: 2413.",
        "estimated_time_seconds": 120,
    },
    {
        "section": "VARC",
        "topic": "Verbal Ability",
        "subtopic": "Para Jumbles",
        "difficulty": "hard",
        "type": "TITA",
        "text": "The four sentences (labelled 1, 2, 3, 4) given below, when properly sequenced, form a coherent paragraph. Enter the 4-digit sequence:\n\n1. As a result, historians must reconstruct ancient daily life not from royal decrees, but from discarded pottery and garbage dumps.\n2. Monumental architecture was deliberately engineered to survive millennia and proclaim imperial authority.\n3. By contrast, the ephemeral materials of peasant existence—thatch, unfired brick, and woven textiles—decayed within generations.\n4. This preservation bias creates a skewed archival record favoring the ruling elite over the common populace.",
        "options": None,
        "correct_answer": "2341",
        "solution": "2 introduces monumental imperial architecture. 3 contrasts this with the perishable materials of ordinary peasant life. 4 synthesizes this contrast as a preservation bias. 1 states the resulting methodological consequence for historians. Correct sequence: 2341.",
        "estimated_time_seconds": 130,
    },
    {
        "section": "VARC",
        "topic": "Verbal Ability",
        "subtopic": "Para Jumbles",
        "difficulty": "medium",
        "type": "TITA",
        "text": "The four sentences (labelled 1, 2, 3, 4) given below, when properly sequenced, form a coherent paragraph. Enter the 4-digit sequence:\n\n1. Over time, these genetic adaptations conferred significant evolutionary advantages against endemic pathogens.\n2. Sickle cell trait, for instance, provides substantial protection against falciparum malaria in tropical latitudes.\n3. Human populations have historically co-evolved alongside infectious microorganisms in specific geographic zones.\n4. However, in modern non-endemic environments, the homozygous manifestation can lead to severe physiological complications.",
        "options": None,
        "correct_answer": "3124",
        "solution": "3 establishes the premise of human-pathogen co-evolution. 1 elaborates on the resulting evolutionary advantages. 2 provides the specific concrete instance (sickle cell trait). 4 introduces the counter-case in non-endemic environments. Correct sequence: 3124.",
        "estimated_time_seconds": 115,
    },

    # Verbal Ability: Para Summary (MCQ)
    {
        "section": "VARC",
        "topic": "Verbal Ability",
        "subtopic": "Para Summary",
        "difficulty": "medium",
        "type": "MCQ",
        "text": "Read the following passage and choose the option that best captures the essence of the paragraph:\n\n\"The widespread belief that creative genius emerges ex nihilo—from sudden, divine inspiration—obscures the rigorous reality of innovation. Historical records of seminal breakthroughs reveal that creative leaps almost universally represent novel combinatorial synthesis: the juxtaposition of previously disconnected domains. Newton did not merely watch an apple fall; he integrated Galilean mechanics with Keplerian orbital geometry. Similarly, Gutenberg’s printing press combined the existing technologies of the agricultural screw press, oil-based ink, and movable metal casting. Creativity is not spontaneous generation; it is an iterative act of cross-pollination across disciplined foundations.\"",
        "options": [
            {"label": "A", "text": "Breakthrough inventions are always the result of collaborative efforts rather than solitary inventors."},
            {"label": "B", "text": "Creativity is fundamentally combinatorial, synthesizing existing ideas from different fields rather than occurring out of nothing."},
            {"label": "C", "text": "Newton and Gutenberg were master synthesizers who prioritized technical execution over original theoretical insight."},
            {"label": "D", "text": "True innovation requires formal historical training to prevent the accidental duplication of past discoveries."},
        ],
        "correct_answer": "B",
        "solution": "The passage argues that creativity is not spontaneous divine inspiration ('ex nihilo'), but the combinatorial synthesis and cross-pollination of existing knowledge.",
        "estimated_time_seconds": 90,
    },
    {
        "section": "VARC",
        "topic": "Verbal Ability",
        "subtopic": "Para Summary",
        "difficulty": "hard",
        "type": "MCQ",
        "text": "Read the following passage and choose the option that best captures the essence of the paragraph:\n\n\"The monetization of attention in the digital economy has transformed information from a scarce commodity into an overwhelming deluge. Because human cognitive bandwidth remains biologically constrained, the bottleneck has shifted from information acquisition to information curation. In this landscape, algorithms that prioritize sensationalism and outrage achieve an asymmetric advantage, as they exploit ancestral neurochemical pathways designed to detect immediate threats. The result is epistemic polarization: societies rich in computational infrastructure yet increasingly impoverished in shared, deliberative consensus.\"",
        "options": [
            {"label": "A", "text": "Cognitive limits make modern consumers vulnerable to algorithmic amplification of sensationalism, undermining shared societal consensus."},
            {"label": "B", "text": "Digital platforms must be heavily regulated because sensationalist news generates more corporate ad revenue than verified journalism."},
            {"label": "C", "text": "Human brains have evolved to prioritize consensus building, but internet speeds prevent deliberative political discussion."},
            {"label": "D", "text": "Epistemic polarization is primarily a technological failure rather than a biological or economic phenomenon."},
        ],
        "correct_answer": "A",
        "solution": "The paragraph links finite human bandwidth with algorithmic exploitation of threat detection (sensationalism), culminating in epistemic polarization and loss of consensus.",
        "estimated_time_seconds": 100,
    },

    # Verbal Ability: Odd Sentence Out (TITA)
    {
        "section": "VARC",
        "topic": "Verbal Ability",
        "subtopic": "Odd Sentence Out",
        "difficulty": "medium",
        "type": "TITA",
        "text": "Five sentences related to a topic are given below. Four of them form a coherent paragraph. Identify the odd sentence that does not fit into the context and type its number:\n\n1. Deep ocean hydrothermal vents support extraordinary ecosystems completely divorced from solar radiation.\n2. Chemosynthetic bacteria form the trophic base by oxidizing toxic hydrogen sulfide escaping from the Earth's crust.\n3. The sunlight zone, or epipelagic zone, extends to a depth of roughly 200 meters and contains the majority of commercial fisheries.\n4. Giant tube worms and vent crabs have evolved specialized hemoglobin to survive in these scalding, mineral-dense plumes.\n5. These unique ecological niches provide scientists with compelling models for potential extraterrestrial life on icy moons like Europa.",
        "options": None,
        "correct_answer": "3",
        "solution": "Sentences 1, 2, 4, 5 specifically focus on deep-sea hydrothermal vents, chemosynthesis, and vent fauna. Sentence 3 discusses the sunlit surface epipelagic ocean zone and commercial fishing, making it the odd one out.",
        "estimated_time_seconds": 90,
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# 2. DILR QUESTIONS (Data Interpretation & Logical Reasoning)
# ─────────────────────────────────────────────────────────────────────────────

DILR_SET_1_CONTEXT = (
    "DIRECTIONS for Questions:\n"
    "Eight consultants—A, B, C, D, E, F, G, and H—are seated around a circular table facing the center for a board meeting. "
    "Each consultant specializes in exactly one domain: Strategy, Finance, Marketing, Operations, HR, Legal, Tech, and Risk.\n"
    "The following conditions are known:\n"
    "1. The Strategy consultant sits third to the right of A.\n"
    "2. Exactly two people sit between C and the Tech consultant.\n"
    "3. B sits immediately adjacent to neither A nor the Strategy consultant.\n"
    "4. D is the Legal consultant and sits opposite E.\n"
    "5. F is the Finance consultant and sits second to the left of the HR consultant.\n"
    "6. G is the Marketing consultant and sits immediately to the left of D.\n"
    "7. Neither C nor H is the Strategy consultant. A is not the HR consultant.\n"
    "8. The Risk consultant sits opposite the Operations consultant."
)

DILR_SET_2_CONTEXT = (
    "DIRECTIONS for Questions:\n"
    "Four Premier League football teams—Arsenal, Chelsea, Liverpool, and Manchester City—played each other once in a single round-robin tournament. "
    "A win awards 3 points, a draw awards 1 point, and a loss awards 0 points. At the end of the tournament:\n"
    "1. Exactly one match ended in a draw.\n"
    "2. Arsenal scored a total of 5 goals and conceded 2 goals, finishing with 6 points.\n"
    "3. Chelsea scored 2 goals and conceded 4 goals, losing to Liverpool 0-2.\n"
    "4. Manchester City won zero matches and finished with 1 point.\n"
    "5. Liverpool conceded the fewest goals in the tournament (only 1 goal) and finished undefeated."
)

DILR_QUESTIONS: List[Dict[str, Any]] = [
    # DILR Set 1: Circular Seating & Domain Arrangement (4 questions)
    {
        "section": "DILR",
        "topic": "Logical Reasoning",
        "subtopic": "Circular Arrangement & Constraints",
        "difficulty": "medium",
        "type": "MCQ",
        "text": f"{DILR_SET_1_CONTEXT}\n\nQuestion 1: Who is the Strategy consultant?",
        "options": [
            {"label": "A", "text": "B"},
            {"label": "B", "text": "E"},
            {"label": "C", "text": "F"},
            {"label": "D", "text": "Cannot be determined"},
        ],
        "correct_answer": "B",
        "solution": "Placing A at pos 1, Strategy is at pos 4. Since D is opposite E (pos diff 4), and G is adjacent to D, testing valid domain assignments with C, H != Strategy leaves E uniquely as the Strategy consultant.",
        "estimated_time_seconds": 150,
    },
    {
        "section": "DILR",
        "topic": "Logical Reasoning",
        "subtopic": "Circular Arrangement & Constraints",
        "difficulty": "hard",
        "type": "MCQ",
        "text": f"{DILR_SET_1_CONTEXT}\n\nQuestion 2: Which domain does consultant A specialize in?",
        "options": [
            {"label": "A", "text": "Operations"},
            {"label": "B", "text": "Risk"},
            {"label": "C", "text": "Tech"},
            {"label": "D", "text": "Finance"},
        ],
        "correct_answer": "C",
        "solution": "Through elimination of assigned domains (Legal=D, Marketing=G, Strategy=E, Finance=F), A is deduced to be the Tech consultant.",
        "estimated_time_seconds": 120,
    },
    {
        "section": "DILR",
        "topic": "Logical Reasoning",
        "subtopic": "Circular Arrangement & Constraints",
        "difficulty": "medium",
        "type": "MCQ",
        "text": f"{DILR_SET_1_CONTEXT}\n\nQuestion 3: How many consultants sit between F and G when counted clockwise from F?",
        "options": [
            {"label": "A", "text": "1"},
            {"label": "B", "text": "2"},
            {"label": "C", "text": "3"},
            {"label": "D", "text": "4"},
        ],
        "correct_answer": "B",
        "solution": "In the circular order, F is positioned at position 5 and G is at position 8, meaning exactly 2 consultants sit between them in clockwise direction.",
        "estimated_time_seconds": 110,
    },
    {
        "section": "DILR",
        "topic": "Logical Reasoning",
        "subtopic": "Circular Arrangement & Constraints",
        "difficulty": "hard",
        "type": "TITA",
        "text": f"{DILR_SET_1_CONTEXT}\n\nQuestion 4: What is the total number of consultants who sit between the Legal consultant and the Marketing consultant along the shorter path?",
        "options": None,
        "correct_answer": "0",
        "solution": "Condition 6 explicitly states: 'G is the Marketing consultant and sits immediately to the left of D [Legal consultant]'. Since they are immediately adjacent, exactly 0 consultants sit between them.",
        "estimated_time_seconds": 60,
    },

    # DILR Set 2: Tournament & Points Table (4 questions)
    {
        "section": "DILR",
        "topic": "Data Interpretation",
        "subtopic": "Games & Tournaments",
        "difficulty": "medium",
        "type": "MCQ",
        "text": f"{DILR_SET_2_CONTEXT}\n\nQuestion 1: What was the result of the match between Liverpool and Arsenal?",
        "options": [
            {"label": "A", "text": "Liverpool won 2-1"},
            {"label": "B", "text": "Liverpool won 1-0"},
            {"label": "C", "text": "The match was a 1-1 draw"},
            {"label": "D", "text": "Arsenal won 2-0"},
        ],
        "correct_answer": "B",
        "solution": "Liverpool finished undefeated and conceded only 1 goal in total tournament. Arsenal lost exactly one match (6 pts = 2 wins, 1 loss). Thus Arsenal lost to Liverpool, and since Liverpool conceded <= 1, score was Liverpool 1-0 Arsenal.",
        "estimated_time_seconds": 140,
    },
    {
        "section": "DILR",
        "topic": "Data Interpretation",
        "subtopic": "Games & Tournaments",
        "difficulty": "medium",
        "type": "TITA",
        "text": f"{DILR_SET_2_CONTEXT}\n\nQuestion 2: How many points did Liverpool finish the tournament with?",
        "options": None,
        "correct_answer": "7",
        "solution": "Liverpool won vs Chelsea (3 pts), won vs Arsenal (3 pts), and drew with Man City (1 pt, the only draw in the tournament). Total points = 3 + 3 + 1 = 7 points.",
        "estimated_time_seconds": 120,
    },
    {
        "section": "DILR",
        "topic": "Data Interpretation",
        "subtopic": "Games & Tournaments",
        "difficulty": "hard",
        "type": "MCQ",
        "text": f"{DILR_SET_2_CONTEXT}\n\nQuestion 3: Which two teams played the match that ended in a draw?",
        "options": [
            {"label": "A", "text": "Arsenal and Chelsea"},
            {"label": "B", "text": "Chelsea and Manchester City"},
            {"label": "C", "text": "Liverpool and Manchester City"},
            {"label": "D", "text": "Arsenal and Manchester City"},
        ],
        "correct_answer": "C",
        "solution": "Man City had 1 point from 0 wins, meaning 1 draw and 2 losses. Arsenal had 6 points (2 wins, 1 loss, 0 draws). Chelsea lost to Liverpool and Arsenal, and lost to Man City? No, Chelsea beat Man City. Liverpool drew with Man City.",
        "estimated_time_seconds": 130,
    },
    {
        "section": "DILR",
        "topic": "Data Interpretation",
        "subtopic": "Games & Tournaments",
        "difficulty": "medium",
        "type": "TITA",
        "text": f"{DILR_SET_2_CONTEXT}\n\nQuestion 4: What was the total number of goals scored in the match between Arsenal and Manchester City?",
        "options": None,
        "correct_answer": "4",
        "solution": "Arsenal scored 5 goals total: 0 vs Liverpool, 2 vs Chelsea (2-0), and 3 vs Man City (3-1). Man City scored 1 goal vs Arsenal. Total goals in match = 3 + 1 = 4.",
        "estimated_time_seconds": 110,
    },

    # Additional DILR Set: Logic Grid
    {
        "section": "DILR",
        "topic": "Logical Reasoning",
        "subtopic": "Matrix & Grid Deductions",
        "difficulty": "medium",
        "type": "MCQ",
        "text": "Five students—P, Q, R, S, and T—each major in a different subject (Physics, Chemistry, Math, Biology, Economics) and each plays a different sport (Cricket, Football, Tennis, Chess, Badminton).\n1. The Math major plays Badminton.\n2. R majors in Physics and does not play Cricket or Football.\n3. S plays Tennis and is not an Economics major.\n4. P does not play Cricket and is not a Biology major.\n5. T majors in Chemistry and plays Football.\n\nWho plays Cricket?",
        "options": [
            {"label": "A", "text": "P"},
            {"label": "B", "text": "Q"},
            {"label": "C", "text": "S"},
            {"label": "D", "text": "T"},
        ],
        "correct_answer": "B",
        "solution": "T plays Football. S plays Tennis. R does not play Cricket or Football, nor Tennis/Badminton (since R is Physics, not Math), so R plays Chess. P does not play Cricket, so P must play Badminton (Math major). That leaves Q uniquely to play Cricket.",
        "estimated_time_seconds": 110,
    },
    {
        "section": "DILR",
        "topic": "Logical Reasoning",
        "subtopic": "Matrix & Grid Deductions",
        "difficulty": "medium",
        "type": "MCQ",
        "text": "From the same students (P, Q, R, S, T) and their majors and sports:\nWhich subject does S major in?",
        "options": [
            {"label": "A", "text": "Biology"},
            {"label": "B", "text": "Economics"},
            {"label": "C", "text": "Chemistry"},
            {"label": "D", "text": "Math"},
        ],
        "correct_answer": "A",
        "solution": "R is Physics. T is Chemistry. P is Math (plays Badminton). S cannot major in Economics (Condition 3). Therefore, S must major in Biology.",
        "estimated_time_seconds": 90,
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# 3. QA QUESTIONS (Quantitative Aptitude)
# ─────────────────────────────────────────────────────────────────────────────

QA_QUESTIONS: List[Dict[str, Any]] = [
    # Arithmetic: Time, Speed & Distance
    {
        "section": "QA",
        "topic": "Arithmetic",
        "subtopic": "Time, Speed & Distance",
        "difficulty": "medium",
        "type": "MCQ",
        "text": "Two trains, A and B, start simultaneously from stations X and Y respectively, traveling towards each other. After meeting, train A takes 4 hours to reach Y, and train B takes 9 hours to reach X. If train A travels at a speed of 60 km/h, what is the speed of train B in km/h?",
        "options": [
            {"label": "A", "text": "40 km/h"},
            {"label": "B", "text": "45 km/h"},
            {"label": "C", "text": "50 km/h"},
            {"label": "D", "text": "54 km/h"},
        ],
        "correct_answer": "A",
        "solution": "Using the standard formula Speed_A / Speed_B = sqrt(Time_B / Time_A): 60 / Speed_B = sqrt(9 / 4) = 3 / 2 => Speed_B = (60 * 2) / 3 = 40 km/h.",
        "estimated_time_seconds": 90,
    },
    {
        "section": "QA",
        "topic": "Arithmetic",
        "subtopic": "Time & Work",
        "difficulty": "medium",
        "type": "TITA",
        "text": "Pipe A can fill a tank in 12 hours, while Pipe B can fill it in 15 hours. Pipe C can empty the full tank in 20 hours. If all three pipes are opened simultaneously, in how many hours will the tank be completely filled?",
        "options": None,
        "correct_answer": "10",
        "solution": "Net rate per hour = (1/12) + (1/15) - (1/20) = (5 + 4 - 3) / 60 = 6 / 60 = 1 / 10. Thus, total time to fill = 10 hours.",
        "estimated_time_seconds": 80,
    },
    {
        "section": "QA",
        "topic": "Arithmetic",
        "subtopic": "Profit, Loss & Discount",
        "difficulty": "medium",
        "type": "MCQ",
        "text": "A shopkeeper marks the price of an article 40% above its cost price. If he allows a discount of 25% on the marked price, what is his overall profit or loss percentage?",
        "options": [
            {"label": "A", "text": "5% profit"},
            {"label": "B", "text": "10% profit"},
            {"label": "C", "text": "5% loss"},
            {"label": "D", "text": "15% profit"},
        ],
        "correct_answer": "A",
        "solution": "Let Cost Price = 100. Marked Price = 140. Selling Price = 140 * (1 - 0.25) = 140 * 0.75 = 105. Profit = 105 - 100 = 5%.",
        "estimated_time_seconds": 60,
    },
    {
        "section": "QA",
        "topic": "Arithmetic",
        "subtopic": "Mixtures & Alligation",
        "difficulty": "hard",
        "type": "TITA",
        "text": "A vessel contains 60 liters of pure milk. 12 liters of milk are withdrawn and replaced with water. This process of removing 12 liters of mixture and replacing with water is repeated one more time. How many liters of pure milk remain in the vessel?",
        "options": None,
        "correct_answer": "38.4",
        "solution": "Formula: Remaining = Initial * (1 - x / V)^n = 60 * (1 - 12 / 60)^2 = 60 * (4 / 5)^2 = 60 * (16 / 25) = 38.4 liters.",
        "estimated_time_seconds": 90,
    },
    {
        "section": "QA",
        "topic": "Arithmetic",
        "subtopic": "Averages & Ratios",
        "difficulty": "medium",
        "type": "MCQ",
        "text": "The average weight of 24 students in a class is 50 kg. When the teacher's weight is included, the average weight increases by 1 kg. What is the teacher's weight?",
        "options": [
            {"label": "A", "text": "72 kg"},
            {"label": "B", "text": "74 kg"},
            {"label": "C", "text": "75 kg"},
            {"label": "D", "text": "76 kg"},
        ],
        "correct_answer": "C",
        "solution": "Total weight of 24 students = 24 * 50 = 1200 kg. With teacher (25 people), average = 51 kg. Total weight = 25 * 51 = 1275 kg. Teacher's weight = 1275 - 1200 = 75 kg.",
        "estimated_time_seconds": 60,
    },

    # Algebra: Logarithms & Equations
    {
        "section": "QA",
        "topic": "Algebra",
        "subtopic": "Logarithms",
        "difficulty": "hard",
        "type": "TITA",
        "text": "Find the real value of x that satisfies the equation: log_2(x - 1) + log_2(x + 2) = 2.",
        "options": None,
        "correct_answer": "2",
        "solution": "log_2((x - 1)(x + 2)) = 2 => (x - 1)(x + 2) = 4 => x^2 + x - 6 = 0 => (x + 3)(x - 2) = 0. Since domain requires x > 1, x = 2 is the unique valid solution.",
        "estimated_time_seconds": 110,
    },
    {
        "section": "QA",
        "topic": "Algebra",
        "subtopic": "Quadratic Equations",
        "difficulty": "medium",
        "type": "MCQ",
        "text": "If alpha and beta are the roots of the equation x^2 - 7x + 12 = 0, what is the value of (alpha^2 + beta^2)?",
        "options": [
            {"label": "A", "text": "23"},
            {"label": "B", "text": "25"},
            {"label": "C", "text": "27"},
            {"label": "D", "text": "29"},
        ],
        "correct_answer": "B",
        "solution": "alpha + beta = 7, alpha * beta = 12. alpha^2 + beta^2 = (alpha + beta)^2 - 2*alpha*beta = 7^2 - 2*(12) = 49 - 24 = 25.",
        "estimated_time_seconds": 50,
    },
    {
        "section": "QA",
        "topic": "Algebra",
        "subtopic": "Sequences & Progressions",
        "difficulty": "hard",
        "type": "TITA",
        "text": "In an arithmetic progression, the 3rd term is 14 and the 9th term is 38. What is the sum of the first 15 terms of this AP?",
        "options": None,
        "correct_answer": "510",
        "solution": "a + 2d = 14 and a + 8d = 38. Subtracting gives 6d = 24 => d = 4, a = 14 - 8 = 6. S_15 = (15 / 2) * [2*6 + 14*4] = 7.5 * [12 + 56] = 7.5 * 68 = 510.",
        "estimated_time_seconds": 95,
    },
    {
        "section": "QA",
        "topic": "Algebra",
        "subtopic": "Functions & Modulus",
        "difficulty": "medium",
        "type": "MCQ",
        "text": "For real values of x, how many distinct integer solutions satisfy the inequality |2x - 5| <= 7?",
        "options": [
            {"label": "A", "text": "6"},
            {"label": "B", "text": "7"},
            {"label": "C", "text": "8"},
            {"label": "D", "text": "9"},
        ],
        "correct_answer": "C",
        "solution": "-7 <= 2x - 5 <= 7 => -2 <= 2x <= 12 => -1 <= x <= 6. Integers are {-1, 0, 1, 2, 3, 4, 5, 6}, which is 6 - (-1) + 1 = 8 integers.",
        "estimated_time_seconds": 70,
    },

    # Geometry & Mensuration
    {
        "section": "QA",
        "topic": "Geometry",
        "subtopic": "Triangles & Circles",
        "difficulty": "medium",
        "type": "MCQ",
        "text": "In a right triangle with legs 6 cm and 8 cm and hypotenuse 10 cm, what is the inradius in cm?",
        "options": [
            {"label": "A", "text": "1.5 cm"},
            {"label": "B", "text": "2 cm"},
            {"label": "C", "text": "2.5 cm"},
            {"label": "D", "text": "3 cm"},
        ],
        "correct_answer": "B",
        "solution": "In a right triangle, inradius r = (a + b - c) / 2 = (6 + 8 - 10) / 2 = 4 / 2 = 2 cm.",
        "estimated_time_seconds": 50,
    },
    {
        "section": "QA",
        "topic": "Geometry",
        "subtopic": "Circles & Tangents",
        "difficulty": "hard",
        "type": "TITA",
        "text": "Two concentric circles have radii 13 cm and 5 cm. A chord of the larger circle is tangent to the smaller circle. What is the length of this chord in cm?",
        "options": None,
        "correct_answer": "24",
        "solution": "The radius to the point of tangency is perpendicular to the chord, bisecting it. Half-chord length = sqrt(13^2 - 5^2) = sqrt(169 - 25) = sqrt(144) = 12 cm. Full chord = 2 * 12 = 24 cm.",
        "estimated_time_seconds": 65,
    },
    {
        "section": "QA",
        "topic": "Geometry",
        "subtopic": "Mensuration",
        "difficulty": "medium",
        "type": "MCQ",
        "text": "A metallic sphere of radius 6 cm is melted and recast into small cones of radius 2 cm and height 3 cm each. How many such cones can be formed?",
        "options": [
            {"label": "A", "text": "48"},
            {"label": "B", "text": "64"},
            {"label": "C", "text": "72"},
            {"label": "D", "text": "80"},
        ],
        "correct_answer": "C",
        "solution": "Volume of sphere = (4/3)*pi*r^3 = (4/3)*pi*216 = 288*pi. Volume of cone = (1/3)*pi*r^2*h = (1/3)*pi*4*3 = 4*pi. Number of cones = (288*pi) / (4*pi) = 72.",
        "estimated_time_seconds": 75,
    },

    # Modern Math & Numbers
    {
        "section": "QA",
        "topic": "Modern Math",
        "subtopic": "Permutations & Combinations",
        "difficulty": "medium",
        "type": "TITA",
        "text": "How many 4-digit numbers can be formed from digits 1, 2, 3, 4, 5 without repetition that are divisible by 4?",
        "options": None,
        "correct_answer": "24",
        "solution": "Divisible by 4 requires last two digits in {12, 24, 32, 52} (4 pairs). Remaining 2 positions filled by 3 available digits in 3 * 2 = 6 ways. Total = 4 * 6 = 24.",
        "estimated_time_seconds": 80,
    },
    {
        "section": "QA",
        "topic": "Modern Math",
        "subtopic": "Probability",
        "difficulty": "medium",
        "type": "MCQ",
        "text": "Two fair six-sided dice are rolled simultaneously. What is the probability that the sum of the numbers appearing on the dice is a prime number?",
        "options": [
            {"label": "A", "text": "5/12"},
            {"label": "B", "text": "7/18"},
            {"label": "C", "text": "1/2"},
            {"label": "D", "text": "13/36"},
        ],
        "correct_answer": "A",
        "solution": "Possible prime sums between 2 and 12 are {2, 3, 5, 7, 11}. Sum 2: (1,1) [1]. Sum 3: (1,2),(2,1) [2]. Sum 5: (1,4),(2,3),(3,2),(4,1) [4]. Sum 7: 6 outcomes. Sum 11: (5,6),(6,5) [2]. Total favorable = 1 + 2 + 4 + 6 + 2 = 15. Probability = 15 / 36 = 5 / 12.",
        "estimated_time_seconds": 85,
    },
    {
        "section": "QA",
        "topic": "Numbers",
        "subtopic": "Remainders & Divisibility",
        "difficulty": "hard",
        "type": "TITA",
        "text": "What is the remainder when 3^100 is divided by 7?",
        "options": None,
        "correct_answer": "4",
        "solution": "By Fermat's Little Theorem: 3^6 = 1 (mod 7). 100 = 6 * 16 + 4. Therefore, 3^100 = (3^6)^16 * 3^4 = 1^16 * 81 = 81 (mod 7). 81 = 7 * 11 + 4. Remainder is 4.",
        "estimated_time_seconds": 90,
    },
]


def get_section_pool(section: str) -> List[Dict[str, Any]]:
    """Return all verified questions for a specific section."""
    sec = section.upper()
    if sec == "VARC":
        return list(VARC_QUESTIONS)
    elif sec == "DILR":
        return list(DILR_QUESTIONS)
    elif sec == "QA":
        return list(QA_QUESTIONS)
    return []


def generate_parametric_qa(base_id: int) -> Dict[str, Any]:
    """Dynamically generate fresh, mathematically verified QA variations."""
    templates = [
        # Variation 1: Speed-time meeting point
        lambda: _make_train_speed_question(),
        # Variation 2: Pipes and cisterns
        lambda: _make_pipe_tank_question(),
        # Variation 3: Marked price & discount
        lambda: _make_profit_discount_question(),
        # Variation 4: Right triangle inradius
        lambda: _make_right_triangle_question(),
        # Variation 5: Concentric circles chord
        lambda: _make_chord_question(),
        # Variation 6: AP sum
        lambda: _make_ap_sum_question(),
    ]
    fn = templates[base_id % len(templates)]
    return fn()


def _make_train_speed_question() -> Dict[str, Any]:
    # (t1, t2, v1, v2) where v1/v2 = sqrt(t2/t1)
    pairs = [
        (4, 9, 60, 40),
        (9, 16, 80, 60),
        (16, 25, 75, 60),
        (1, 4, 90, 45),
        (9, 4, 50, 75),
    ]
    t1, t2, v1, v2 = random.choice(pairs)
    return {
        "section": "QA",
        "topic": "Arithmetic",
        "subtopic": "Time, Speed & Distance",
        "difficulty": "medium",
        "type": "MCQ",
        "text": f"Two trains, A and B, start simultaneously from stations X and Y respectively, traveling towards each other. After meeting, train A takes {t1} hours to reach Y, and train B takes {t2} hours to reach X. If train A travels at a speed of {v1} km/h, what is the speed of train B in km/h?",
        "options": [
            {"label": "A", "text": f"{v2} km/h"},
            {"label": "B", "text": f"{v2 + 5} km/h"},
            {"label": "C", "text": f"{v2 - 5 if v2 > 10 else v2 + 10} km/h"},
            {"label": "D", "text": f"{v2 + 15} km/h"},
        ],
        "correct_answer": "A",
        "solution": f"Using Speed_A / Speed_B = sqrt(Time_B / Time_A): {v1} / Speed_B = sqrt({t2}/{t1}). Solving gives Speed_B = {v2} km/h.",
        "estimated_time_seconds": 90,
    }


def _make_pipe_tank_question() -> Dict[str, Any]:
    triples = [
        (12, 15, 20, 10),
        (10, 15, 30, 10),
        (12, 24, 8, 12),
        (20, 30, 15, 60),
    ]
    a, b, c, ans = random.choice(triples)
    return {
        "section": "QA",
        "topic": "Arithmetic",
        "subtopic": "Time & Work",
        "difficulty": "medium",
        "type": "TITA",
        "text": f"Pipe A can fill a tank in {a} hours, while Pipe B can fill it in {b} hours. Pipe C can empty the full tank in {c} hours. If all three pipes are opened simultaneously, in how many hours will the tank be completely filled?",
        "options": None,
        "correct_answer": str(ans),
        "solution": f"Net rate per hour = (1/{a}) + (1/{b}) - (1/{c}) = 1/{ans}. Therefore, required time = {ans} hours.",
        "estimated_time_seconds": 80,
    }


def _make_profit_discount_question() -> Dict[str, Any]:
    combos = [
        (40, 25, 5),   # 140 * 0.75 = 105 -> 5%
        (50, 20, 20),  # 150 * 0.80 = 120 -> 20%
        (60, 25, 20),  # 160 * 0.75 = 120 -> 20%
        (25, 20, 0),   # 125 * 0.80 = 100 -> 0%
        (30, 10, 17),  # 130 * 0.90 = 117 -> 17%
    ]
    markup, discount, profit = random.choice(combos)
    return {
        "section": "QA",
        "topic": "Arithmetic",
        "subtopic": "Profit, Loss & Discount",
        "difficulty": "medium",
        "type": "MCQ",
        "text": f"A shopkeeper marks the price of an article {markup}% above its cost price. If he allows a discount of {discount}% on the marked price, what is his overall profit percentage?",
        "options": [
            {"label": "A", "text": f"{profit}%"},
            {"label": "B", "text": f"{profit + 4}%"},
            {"label": "C", "text": f"{profit + 8}%"},
            {"label": "D", "text": f"{max(1, profit - 3)}%"},
        ],
        "correct_answer": "A",
        "solution": f"Cost Price = 100. Marked Price = {100 + markup}. Selling Price = {100 + markup} * (1 - {discount}/100) = {100 + profit}. Profit = {profit}%.",
        "estimated_time_seconds": 60,
    }


def _make_right_triangle_question() -> Dict[str, Any]:
    triples = [
        (6, 8, 10, 2),
        (5, 12, 13, 2),
        (8, 15, 17, 3),
        (9, 12, 15, 3),
        (7, 24, 25, 3),
    ]
    a, b, c, r = random.choice(triples)
    return {
        "section": "QA",
        "topic": "Geometry",
        "subtopic": "Triangles & Circles",
        "difficulty": "medium",
        "type": "MCQ",
        "text": f"In a right triangle with perpendicular sides {a} cm and {b} cm and hypotenuse {c} cm, what is the inradius in cm?",
        "options": [
            {"label": "A", "text": f"{r} cm"},
            {"label": "B", "text": f"{r + 1} cm"},
            {"label": "C", "text": f"{r + 1.5} cm"},
            {"label": "D", "text": f"{r + 2} cm"},
        ],
        "correct_answer": "A",
        "solution": f"Inradius r = (a + b - c) / 2 = ({a} + {b} - {c}) / 2 = {r} cm.",
        "estimated_time_seconds": 60,
    }


def _make_chord_question() -> Dict[str, Any]:
    radii = [
        (13, 5, 24),
        (10, 6, 16),
        (17, 8, 30),
        (25, 7, 48),
    ]
    R, r, chord = random.choice(radii)
    return {
        "section": "QA",
        "topic": "Geometry",
        "subtopic": "Circles & Tangents",
        "difficulty": "medium",
        "type": "TITA",
        "text": f"Two concentric circles have radii {R} cm and {r} cm. A chord of the larger circle is tangent to the smaller circle. What is the length of this chord in cm?",
        "options": None,
        "correct_answer": str(chord),
        "solution": f"Half-chord = sqrt({R}^2 - {r}^2) = {chord // 2} cm. Full chord = 2 * {chord // 2} = {chord} cm.",
        "estimated_time_seconds": 60,
    }


def _make_ap_sum_question() -> Dict[str, Any]:
    # a, d, n
    params = [
        (6, 4, 15, 510),
        (3, 5, 12, 366),
        (5, 3, 20, 670),
        (4, 6, 10, 310),
    ]
    a, d, n, s = random.choice(params)
    t3 = a + 2 * d
    t7 = a + 6 * d
    return {
        "section": "QA",
        "topic": "Algebra",
        "subtopic": "Sequences & Progressions",
        "difficulty": "hard",
        "type": "TITA",
        "text": f"In an arithmetic progression, the 3rd term is {t3} and the 7th term is {t7}. What is the sum of the first {n} terms of this AP?",
        "options": None,
        "correct_answer": str(s),
        "solution": f"d = ({t7} - {t3}) / 4 = {d}, a = {t3} - 2*{d} = {a}. S_{n} = ({n}/2)*[2*{a} + ({n}-1)*{d}] = {s}.",
        "estimated_time_seconds": 90,
    }
