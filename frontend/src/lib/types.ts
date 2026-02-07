// RFP Generator Types

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

// AI Evaluation scores (from Langfuse)
export interface AIEvalScores {
  coherence: number;        // LLM-as-judge score (0-10)
  ragConfidence: number;    // RAG attribution score (0-100%)
  formatCompliance: number; // Template adherence (0-100%)
  sources?: RAGSource[];    // Source documents used
  latencyMs?: number;       // Generation time
  tokenCount?: number;      // Tokens used
}

export interface RAGSource {
  docName: string;
  section: string;
  similarity: number;       // 0-100%
  chunk?: string; // Optional content preview
}

export interface Section {
  name: string;
  content: string;
  assumptions?: string[];
  aiEval?: AIEvalScores;    // AI evaluation metrics
}

export interface RFPSections {
  new: Section[];
  old: Section[];
  rules: Section[];
}

export interface AppState {
  screen: "chat" | "review";
  chatHistory: ChatMessage[];
  sections: RFPSections | null;
  approved: Set<string>;
  regenCounts: Record<string, number>;
  context: Record<string, string>;
  rfpTitle: string;
  pendingQuestions: string[];
  currentQuestionIndex: number;
  collectedAnswers: string[];
  isGenerating: boolean;
}

// Section names
export const NEW_SECTIONS = [
  "Scope of Work",
  "Deliverables",
  "Technical Requirements",
  "Evaluation Criteria",
  "Timeline & Milestones",
  "Budget & Payment Terms",
] as const;

export const OLD_SECTIONS = [
  "Background & Context",
  "Vendor Qualifications",
  "Proposal Format",
  "Submission Instructions",
  "Contract Terms",
  "Insurance Requirements",
  "Warranty & Support",
  "References Required",
] as const;

export const RULES_SECTIONS = [
  "General Terms & Conditions",
  "Safety & Compliance",
  "Intellectual Property",
  "Confidentiality",
  "Termination Clause",
  "Dispute Resolution",
  "Force Majeure",
  "Indemnification",
  "Liability Limitations",
  "Governing Law",
  "Amendment Procedures",
] as const;
