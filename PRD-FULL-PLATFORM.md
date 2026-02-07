# PRD: RPSG AI-Powered RFP Workspace

**Version**: 2.0
**Last Updated**: 2026-02-02
**Author**: Benison Joseph
**Status**: Draft

---

## 1. Context

### 1.1 Problem Statement

**Who**: CESC (and RPSG group companies) business users across all functions
**Problem**: Manual RFP creation is slow, inconsistent, and error-prone
**Context**: Any business user—from legal, operations, IT, or other functions—may need to create RFPs for services, supplies, or projects. Each RFP requires searching historical documents, copy-pasting sections, ensuring compliance with templates, and manual formatting.
**Impact**:
- 8-12 hours per RFP (2-3 days of a business user's time)
- Risk of missing critical clauses (legal, safety, compliance)
- Inconsistent quality across RFPs
- No institutional memory - knowledge trapped in documents

### 1.2 User Scenario Context

| Source | Scenario/Observation | Insight |
|--------|----------------------|---------|
| Business User (CESC Kolkata) | "I spend 2-3 days creating each RFP manually" | Primary pain is time consumption |
| Business User | "I struggle to find relevant past RFPs for reference" | Search/retrieval is a major friction |
| Business User | "I worry about missing critical clauses or compliance requirements" | Quality/compliance anxiety is high |
| 19 RFP Corpus Analysis | Mix of Service (9), Supply (7), EPC (3) RFPs with varying structures | Need for template standardization |
| Annexure Templates | 3 fixed templates for legal/safety terms | Some sections are truly immutable (RULES) |

### 1.3 Corpus & Repository Context

**Starting Point**: The POC uses 19 existing CESC RFPs as the initial corpus for RAG retrieval. This represents the current baseline for one company.

**Growth Expectation**: As adoption increases, the repository will expand significantly:
- More RFPs from additional RPSG entities (CPDL, MPSL, etc.)
- New categories and service types not in current corpus
- Company-specific clauses and terminology
- Domain-specific requirements (new industries, compliance standards)

**System Flexibility Requirements**:
- Architecture must support dynamic section discovery (new sections beyond current 25)
- Vector database must scale with corpus growth
- RAG retrieval quality improves with corpus size—more historical RFPs = better output confidence
- Templates and rules must be organization-configurable

**Critical Insight**: Prior RFP upload is essential for output quality. The system's confidence in generated content directly correlates with corpus depth. Users should understand: *"The more historical RFPs you provide, the better the outputs become."*

### 1.4 Opportunity/Job

**Job Story (JTBD)**:
- **When** I need to create an RFP for a new service, supply, or EPC requirement
- **I want to** describe my needs in plain language and have a system generate a complete draft
- **So I can** finalize and issue the RFP in under 1 hour instead of 2-3 days

**Forces**:
| Force | Evidence |
|-------|----------|
| Push (pain of current) | "I spend 2-3 days creating each RFP manually", risk of missing clauses |
| Pull (attraction of new) | <1 hour generation, 95%+ accuracy, consistent quality |
| Anxiety (fear of change) | "What if AI hallucinates legal clauses?", adoption resistance |
| Habit (comfort with current) | Familiar with Word docs, existing templates, known process |

---

## 2. Solution

### 2.1 Solution Hypothesis

We believe that an **AI-powered RFP generation system** with three-source architecture (NEW + OLD + RULES) will **reduce RFP creation time by 85%** for **RPSG business users**.

We'll know we're right when:
- RFP creation time drops from 8-12 hours to <1 hour
- Users approve NEW sections in <3 regenerations on average
- 80%+ of target users actively use the tool

### 2.2 Platform Vision (Phased)

| Phase | Name | Scope | Focus |
|-------|------|-------|-------|
| **Phase 1** | POC | Chat-based RFP generation + review + Word export (CESC only) | Prove generation quality |
| **Phase 2** | Platform | Multi-organization, repository UI, approval workflows, user management | Scale to RPSG entities |
| **Phase 3** | Learning & Analytics | Human feedback loop, AI-powered RFP analytics, fine-tuning | Continuous improvement |

### 2.3 User Stories

#### Phase 1: POC (Priority P0)

| ID | As a... | I want to... | So that... | Priority |
|----|---------|--------------|------------|----------|
| US-1.1 | Business User | Describe my RFP need in plain English | I can quickly generate a draft without filling forms | P0 |
| US-1.2 | Business User | Answer adaptive questions one at a time | The system gathers context conversationally | P0 |
| US-1.3 | Business User | Review and approve critical sections (NEW) | I ensure the RFP matches my exact requirements | P0 |
| US-1.4 | Business User | Regenerate sections with additional context | I can refine output without starting over | P0 |
| US-1.5 | Business User | Download approved RFP as Word document | I can share with vendors via standard process | P0 |

#### Phase 2: Platform (Priority P1)

| ID | As a... | I want to... | So that... | Priority |
|----|---------|--------------|------------|----------|
| US-2.1 | Business User | Select my organization (CESC/CPDL/MPSL) | RFP uses correct templates and branding | P1 |
| US-2.2 | Business User | Upload historical RFPs to improve the system | Future generations are more accurate for my domain | P1 |
| US-2.3 | Approver | Review and approve/reject RFPs assigned to me | I can fulfill my approval responsibility | P1 |
| US-2.4 | Business User | Search and chat with existing RFPs | I can find relevant past work without manual search | P1 |
| US-2.5 | Admin | Manage templates and update RULES sections | Templates stay current with policy changes | P1 |

#### Phase 3: Learning & Analytics (Priority P2)

| ID | As a... | I want to... | So that... | Priority |
|----|---------|--------------|------------|----------|
| US-3.1 | Business User | Submit the final RFP I actually sent | The system learns from my edits and improves | P2 |
| US-3.2 | Commercial Team | Analyze active RFPs and patterns | I can identify trends and optimize procurement | P2 |
| US-3.3 | Admin | View AI performance metrics and quality trends | I can monitor and improve system quality | P2 |

### 2.4 Acceptance Criteria (Phase 1 POC)

#### US-1.1: Natural Language RFP Creation

**Given** a business user opens the tool
**When** they type a single sentence describing RFP need
**Then** system initiates generation flow

**Acceptance Criteria**:
- [ ] User can type free-form text: "Create services RFP for product designer, 6 months"
- [ ] System classifies RFP type (Service/Supply/EPC)
- [ ] System extracts entities (role, duration, budget if provided)
- [ ] No form fields required - pure conversational input

#### US-1.2: Adaptive Question Generation (One at a Time)

**Given** system has analyzed user's initial request
**When** information is missing for NEW sections
**Then** system generates contextual questions asked one at a time

**Acceptance Criteria**:
- [ ] Questions adapt based on context richness (2-5 questions max)
- [ ] Rich context → fewer questions; Vague input → more questions
- [ ] Questions asked **one at a time** in conversational flow
- [ ] Never asks for information user already provided
- [ ] Each question completes in <5 seconds
- [ ] **Encourage detailed input**: Messaging prompts users to provide as much context as possible, copy/paste relevant text, or attach supporting files

**Messaging Guidance**:
- "Feel free to paste any existing requirements, specifications, or notes you have"
- "The more detail you provide, the better the output will be"
- "You can attach files or paste text for additional context"

**Edge Cases**:
- [ ] User provides extensive detail → System asks 0-2 questions
- [ ] User provides only "RFP for catering" → System asks 4-5 questions

#### US-1.3: Three-Source Content Generation

**Given** user has answered questions
**When** system generates RFP
**Then** 25 sections are created from appropriate sources

**Acceptance Criteria**:
- [ ] NEW sections (6): Generated from user input + LLM
- [ ] OLD sections (8): Retrieved via RAG from historical RFP corpus
- [ ] RULES sections (11): Pulled from fixed templates
- [ ] Generation completes in <90 seconds
- [ ] NEW sections flagged as "requires approval"
- [ ] Assumptions made by AI are explicitly flagged

#### US-1.4: Section Regeneration

**Given** user is reviewing a NEW or OLD section
**When** they click Regenerate and provide context
**Then** section is regenerated with heavier RAG weighting

**Acceptance Criteria**:
- [ ] User can regenerate up to 5 times per section
- [ ] User can add context in text box
- [ ] Regeneration completes in <30 seconds
- [ ] Each iteration shows count: "Regeneration 2/5"
- [ ] RAG weighting increases: 60% → 70% → 80% → 85% → 90%
- [ ] Previous version used as baseline

#### US-1.5: Document Export

**Given** all 6 NEW sections are approved
**When** user clicks Download
**Then** Word document is generated

**Acceptance Criteria**:
- [ ] Download button disabled until all NEW sections approved
- [ ] Output is .docx format
- [ ] CESC formatting preserved (fonts, spacing, numbering)
- [ ] All 25 sections in standard order
- [ ] File naming: `RFP_{Service_Type}_{Date}_{TenderNo}.docx`
- [ ] Download completes in <10 seconds

### 2.5 AI Evaluation Strategy (Langfuse)

Given that RFP generation is a non-deterministic AI system, traditional unit tests are insufficient. We implement continuous AI evaluation using **Langfuse** (open-source observability platform).

#### Why Langfuse

- **Full Observability**: Every LLM call traced with inputs, outputs, latency, cost
- **Evaluation Scores**: Attach quality scores to generations for tracking over time
- **Dataset Management**: Build evaluation datasets from real user interactions
- **Self-hosted**: Data stays internal, unlimited traces, no external dependencies

#### Implementation Plan

**Phase 1: Tracing (POC)**
```
RFP Generation Session
├─ Trace: question_generation
│   └─ metadata: {input_richness, question_count}
├─ Trace: section_generation (×25)
│   └─ metadata: {section_name, source_type, rag_hits}
├─ Trace: regeneration (if any)
│   └─ metadata: {section_name, iteration, additional_context}
└─ Score: user_approval_rate
    └─ value: approved_sections / total_new_sections
```

**Phase 2: Evaluation Datasets**
- Collect traces where users regenerated >3 times (quality issues)
- Collect traces where users approved on first generation (good quality)
- Build labeled dataset: {input, output, quality_score}

**Phase 3: Automated Evals**
- Run evals on each deployment
- Track quality metrics over time:
  - First-pass approval rate (target: >70%)
  - Average regenerations per section (target: <2)
  - Section quality scores (model-graded)

#### Evaluation Metrics

| Metric | Measurement | Target |
|--------|-------------|--------|
| Section Coherence | LLM-as-judge scoring | >8/10 |
| Factual Accuracy | RAG attribution score | >85% |
| Format Compliance | Template adherence check | 100% |
| User Satisfaction | First-pass approval rate | >70% |
| Regeneration Rate | Avg regens per section | <2 |

#### Experimentation Workflow

Section regeneration will involve extensive experimentation:
1. **Run generation** with current prompts
2. **Review traces** in Langfuse UI
3. **Leave remarks** on problematic outputs
4. **Iterate prompts** based on trace analysis
5. **Compare versions** using A/B evaluation datasets

### 2.6 Multi-Organization Architecture (Phase 2)

**Post-login, users belong to one organization**:
- Most users are assigned to a single organization (CESC, CPDL, MPSL)
- Super admins can access multiple organizations

**Organization-scoped resources**:
- RFP document repository (vectorized corpus per org)
- Templates and RULES sections
- Approval workflows
- User permissions

**RFP generation is organization-specific**:
- RAG retrieval pulls from that organization's corpus only
- Templates match organization branding and policies
- Cross-org patterns may be shared at admin level (future)

### 2.7 Out of Scope

**Explicitly NOT included**:
- Outreach automation (vendor communication, bid collection) - Not planned
- Real-time collaboration (simultaneous editing) - Not planned
- ERP/procurement system integration - Future consideration

**Phase 3 / Future Considerations** (only after generation quality is proven):
- AI-powered RFP analytics ("Analyze your active RFPs", trend analysis)
- RFP lifecycle management (post-creation workflow between business user and commercial team)
- Fine-tuning on organization-specific data

---

## 3. Prototype Specification

### 3.1 Tech Stack (POC)

| Layer | Technology |
|-------|------------|
| Framework | Streamlit (Python) |
| Backend | Python 3.10+ |
| RAG Orchestration | LangChain |
| LLM | OpenAI GPT-4o or Gemini 1.5 Pro |
| Vector DB | ChromaDB |
| Document Export | python-docx |
| Observability | Langfuse (self-hosted) |
| Hosting (POC) | Local development |

### 3.2 Build Phases

**Phase 1A: Infrastructure**
- Vector DB setup with RFP corpus
- Template store with RULES sections
- LLM integration
- Langfuse tracing setup

**Phase 1B: Generation Engine**
- Question generation module (one-at-a-time flow)
- NEW section generator
- OLD section generator with RAG
- RULES section retriever

**Phase 1C: User Interface**
- Chat interface with conversational questions
- Section review UI
- Regeneration flow
- Approval mechanism
- Word export

### 3.3 Visual References

| Reference | Path | Purpose |
|-----------|------|---------|
| UI Prototype | `rfp-generator-prototype.tsx` | React mockup of 2-screen flow |
| POC Code | `rfp-generator-poc/` | Working Streamlit implementation |
| PRD Spec | `PRD-rfp-gen-poc.md` | Original detailed requirements |
| RFP Corpus | `/RFP Documents/` | Training data for RAG |

---

## 4. Success Metrics

| Metric | Type | Baseline | Target | Measurement |
|--------|------|----------|--------|-------------|
| Time to create RFP | Leading | 8-12 hours | <1 hour | Timer in app |
| NEW section approval rate | Leading | N/A | >70% first-pass | Langfuse tracking |
| Regenerations per RFP | Leading | N/A | <3 average | App analytics |
| RAG relevance | Leading | N/A | >85% | Langfuse eval scores |
| User adoption | Lagging | 0% | 80% of target users | Active user count |

---

## 5. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| LLM hallucinates legal clauses | Medium | High | RULES sections only for legal (no LLM) |
| RAG retrieves irrelevant sections | Medium | Medium | Langfuse tracing + manual validation + tune embeddings |
| User provides insufficient context | High | Medium | Encourage detailed input, show assumption flags |
| Generation takes >2 minutes | Low | Medium | Async processing, progress bar, parallel gen |
| Adoption resistance | Medium | High | UAT with real users, iterate on feedback |
| Corpus too small for good RAG | Medium | High | Encourage historical RFP uploads, set expectations |

---

## 6. Eng Handoff Notes

### 6.1 Technical Decisions (Locked)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Three-source architecture | NEW + OLD + RULES | Balances creativity (NEW), consistency (OLD), compliance (RULES) |
| Vector DB | ChromaDB | Lightweight, local, sufficient for initial corpus |
| Section approval gate | All 6 NEW sections | Quality control - prevents premature download |
| Regeneration limit | 5 per section | Prevents infinite loops, forces user decision |
| Question flow | One at a time | More conversational, less overwhelming |
| Observability | Langfuse | AI-specific evals, self-hosted, traces every LLM call |

### 6.2 Open Questions

| Question | Context | Needed By |
|----------|---------|-----------|
| GPT-4o vs Gemini 1.5 Pro? | Cost/performance tradeoff | Week 1 |
| Embedding model choice? | OpenAI ada-002 vs open-source | Week 1 |
| Hosting for UAT? | Streamlit Cloud vs EC2 vs local | Week 2 |

---

## Appendix

### A. Glossary

| Term | Definition |
|------|------------|
| NEW sections | 6 sections generated by LLM from user input |
| OLD sections | 8 sections retrieved via RAG from historical RFPs |
| RULES sections | 11 fixed template sections (legal, compliance) |
| RAG | Retrieval-Augmented Generation |
| Langfuse | Open-source LLM observability and evaluation platform |
| Business User | Any employee who needs to create an RFP (not limited to procurement) |

### B. Phase 3: Human Feedback Loop (Future)

**Concept**: Reinforce learning from human feedback (RLHF-lite)

**Flow**:
1. User generates RFP through system
2. User makes edits, regenerates sections
3. User downloads and sends final RFP
4. User (or commercial team) uploads the **actual final version** they sent
5. System compares generated vs final → captures the "gap"
6. Gap data used to improve prompts, RAG, or fine-tune models

**Value**: Continuous quality improvement based on real user behavior, not just test datasets.

### C. Phase 3: AI-Powered Analytics (Future)

**Concept**: Ask questions about your RFP portfolio

**Examples**:
- "What are our most common RFP categories this quarter?"
- "Which vendors bid on multiple RFPs?"
- "What's the average time from RFP creation to vendor selection?"
- "Show me RFPs with budget overruns"

**Requires**: RFP lifecycle tracking, structured metadata, analytics engine

### D. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-02 | Benison Joseph | Initial version |
| 2.0 | 2026-02-02 | Benison Joseph | User scenario context, business user focus, Langfuse AI evals, multi-org architecture, Phase 3 learning loop, removed contract management |

---

## PRD Checklist

- [x] All user stories have acceptance criteria
- [x] Success metrics have baselines and targets
- [x] At least 2 risks identified with mitigations
- [x] Tech stack decisions documented
- [x] Out of scope explicitly stated
- [x] AI evaluation strategy defined (Langfuse)
- [x] Corpus growth expectations set
- [x] Multi-organization architecture outlined
