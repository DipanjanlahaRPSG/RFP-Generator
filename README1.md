# RFP Generator - Prototype Handoff

## Live Demo
https://rfp-generator-web.vercel.app

## Overview
Visual prototype for an AI-powered RFP response generator. Uses mock data to demonstrate the full user flow.

## Stack
- Next.js 16
- React + TypeScript
- Tailwind CSS
- shadcn/ui components

## Features

### Chat Screen
- Welcome message with clickable examples
- Adaptive follow-up questions (2-5 based on input richness)
- One question at a time flow
- Simulated generation with loading state

### Review Screen
- Progress bar (X/6 sections approved)
- 3 tabs: Critical (6) / RAG-Generated (8) / Templates (11)
- Accordion sections with formatted markdown
- Assumptions flagged per section
- Regenerate with context (max 5 attempts, shows version)
- Approve/Unapprove flow
- Fixed bottom CTA when all 6 critical sections approved

### AI Evaluation Panel
- Per-section metrics: Coherence, RAG Confidence, Format Compliance
- RAG sources with similarity scores
- Latency & token count
- "View in Langfuse" button (mock)

## Run Locally

```bash
cd rfp-generator-web
npm install
npm run dev
# Opens at http://localhost:3000
```

## To Make Production-Ready

### 1. Replace Mock Data with API Calls
- `generateMockSections()` → call backend LLM/RAG service
- `MOCK_QUESTIONS` → call question generation endpoint
- Mock AI evals → integrate Langfuse SDK

### 2. Add Backend API Routes
```
POST /api/analyze    - Analyze initial request
POST /api/generate   - Generate all 25 sections
POST /api/regenerate - Regenerate single section
GET  /api/export     - Generate Word document
```

### 3. Integrate Langfuse
- Wrap LLM calls with `langfuse.trace()`
- Log section generation with metadata
- Attach evaluation scores to traces

### 4. Add Persistence
- Save RFP drafts to database
- User authentication (Phase 2)
- Organization scoping (Phase 2)

## Key Files

| File | Purpose |
|------|---------|
| `src/app/page.tsx` | Main page with screen switching |
| `src/components/chat-screen.tsx` | Chat interface |
| `src/components/review-screen.tsx` | Review & approve flow |
| `src/components/ai-eval-panel.tsx` | AI evaluation display |
| `src/lib/types.ts` | TypeScript types |
| `src/lib/mock-data.ts` | Mock data generation |

## AI Eval Metrics (Targets)

| Metric | Target |
|--------|--------|
| Section Coherence | >8/10 |
| RAG Confidence | >85% |
| Format Compliance | 100% |
| First-pass approval | >70% |
| Avg regenerations | <2 |

## Related Docs
- `PRD-FULL-PLATFORM.md` - Full PRD
- `ENG-HANDOFF.md` - Engineering decisions
- `PROTOTYPE-SPEC-STREAMLIT.md` - Build specification
