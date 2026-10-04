export type ModuleKind = "lean" | "python" | "corpus";

export type RepoModule = {
  name: string;
  path: string;
  kind: ModuleKind;
  color: string;
  summary: string;
  detail: string;
  tags: string[];
};

export type ClaimExample = {
  title: string;
  prompt: string;
  verdict: "proved" | "open" | "caution";
  explanation: string;
  code: string;
};

export const repoFacts = {
  title: "4Leibniz",
  tagline: "A formal laboratory for reason, relation, and proof.",
  repoUrl: "https://github.com/Mega-Therion/4Leibniz",
  branch: "main",
  measured: "2026-09-05",
  modules: 10,
  theorems: 34,
  definitions: 48,
  structures: 16,
  inductives: 10,
  abbrevs: 4,
};

export const repoModules: RepoModule[] = [
  {
    name: "Characteristica",
    path: "Leibniz/Characteristica.lean",
    kind: "lean",
    color: "#E9B872",
    summary: "A universal binary alphabet and its dual tension.",
    detail: "The module formalizes a small vocabulary for signs, truth values, and complementary poles: a computational echo of the characteristica universalis.",
    tags: ["logic", "symbols", "Lean 4"],
  },
  {
    name: "SpatiumRelativum",
    path: "Leibniz/SpatiumRelativum.lean",
    kind: "lean",
    color: "#79A8A9",
    summary: "Relational metrics on bundles of monads.",
    detail: "Space is treated as relation rather than container. The code gives that intuition a typed home through bundles, connections, and holonomy.",
    tags: ["relation", "geometry", "monads"],
  },
  {
    name: "VisViva",
    path: "Leibniz/VisViva.lean",
    kind: "lean",
    color: "#D9795B",
    summary: "Active energy, force, and horizon acceleration.",
    detail: "This chapter turns Leibniz's vis viva into a compact formal vocabulary for active power and a boundary where acceleration changes character.",
    tags: ["physics", "force", "dynamics"],
  },
  {
    name: "LexContinuitatis",
    path: "Leibniz/LexContinuitatis.lean",
    kind: "lean",
    color: "#B9A7D5",
    summary: "The continuity law and its χ-band endpoints.",
    detail: "Continuity is used as a guardrail: the χ floor becomes a typed threshold that later invariants can preserve.",
    tags: ["continuity", "invariants", "threshold"],
  },
  {
    name: "Harmonia",
    path: "Leibniz/Harmonia.lean",
    kind: "lean",
    color: "#C8D46A",
    summary: "An anti-drift stability scaffold around Lindblad notation.",
    detail: "Important epistemic note: this file contains axioms and a deliberately tautological stability definition. It compiles, but compilation alone is not evidence that the physical claim is proved.",
    tags: ["open", "axioms", "caution"],
  },
  {
    name: "Calculemus",
    path: "Leibniz/Calculemus.lean",
    kind: "lean",
    color: "#F28F3B",
    summary: "Claim adjudication and the honest oracle boundary.",
    detail: "The real machine is calculemus.py: claim → IR → proof search → theorem synthesis → Lean kernel. The Lean receipt in this module is explicitly not a measurement.",
    tags: ["oracle", "ledger", "verification"],
  },
  {
    name: "calculemus.py",
    path: "calculemus.py",
    kind: "python",
    color: "#74A7E7",
    summary: "The claim-to-kernel pipeline.",
    detail: "This is the repo's executable center of gravity. It translates natural-language claims into a universal calculus intermediate representation, searches transparent rules, synthesizes Lean, and records adjudications.",
    tags: ["pipeline", "IR", "automation"],
  },
  {
    name: "corpus/",
    path: "corpus/",
    kind: "corpus",
    color: "#E0A458",
    summary: "Witnesses, transcriptions, and translations.",
    detail: "The corpus is where historical materials meet formalization. Treat it as source evidence, not decoration: every formal claim needs a traceable witness.",
    tags: ["sources", "history", "witnesses"],
  },
];

export const lessons = [
  {
    title: "The Monadology in one breath",
    category: "Leibniz 101",
    duration: "4 min",
    accent: "#E9B872",
    body: "Leibniz imagines reality as composed of simple substances—monads—each expressing the whole from its own point of view. The 4Leibniz repo borrows that vocabulary to ask a modern question: can relations, perspectives, and reasons be made explicit enough for a proof assistant to check?",
    prompt: "Why does the repo talk about monads?",
  },
  {
    title: "What 'Calculemus!' really means",
    category: "Method",
    duration: "6 min",
    accent: "#79A8A9",
    body: "Calculemus—'let us calculate'—is a wager that disputes can be transformed into inspectable procedures. In this project, that means no black-box verdicts: the claim is lowered into an intermediate representation, rules are applied transparently, and Lean's kernel checks the generated theorem.",
    prompt: "Walk me through the claim-to-kernel pipeline.",
  },
  {
    title: "Compile clean ≠ prove true",
    category: "Epistemics",
    duration: "5 min",
    accent: "#D9795B",
    body: "The repo makes a valuable distinction: a file can compile while proving very little. A theorem may simply return its hypothesis; an axiom may carry the hard work; a hand-written receipt may be mistaken for a measurement. A good guide must show both the result and its epistemic boundary.",
    prompt: "Which claims in the repo should I treat cautiously?",
  },
];

export const claimExamples: ClaimExample[] = [
  {
    title: "Sufficient reason is transitive",
    prompt: "If A grounds B and B grounds C, does A ground C?",
    verdict: "proved",
    explanation: "The repo's flagship example closes through the transparent transitivity rule, synthesizes a Lean theorem, and accepts it with zero new axioms.",
    code: "theorem sufficientReason_transitivity ... := by\n  exact hAB.trans hBC",
  },
  {
    title: "Harmonia preserves a floor",
    prompt: "Does anti-drift stability establish a physical coherence threshold?",
    verdict: "caution",
    explanation: "Not by itself. The definition harmonia_stabilis u gamma := u ≥ gamma makes the theorem h : P ⊢ P. The file also includes axioms, so compilation is not an empirical validation.",
    code: "def harmonia_stabilis (u gamma : ℝ) : Prop := u ≥ gamma\ntheorem anti_drift_preservation ... (h : harmonia_stabilis u gamma) : u ≥ gamma := h",
  },
  {
    title: "The verification ledger is measured",
    prompt: "Can a VeritasReceipt literal audit the repository?",
    verdict: "open",
    explanation: "No. The receipt is a record literal. Run scripts/measure_kernel.py --check to read the elaborator's output and measure the tree; the repo explicitly warns against citing the receipt as an audit.",
    code: "def execute_calculemus : VeritasReceipt :=\n  { build := true, theoremCount := 34, ... }",
  },
];

export const starterPrompts = [
  "What is 4Leibniz?",
  "Explain the claim → kernel pipeline",
  "Which files are axiomatic?",
  "Teach me about Leibniz's monads",
];
