// Mock data for visual prototype
import { RFPSections, NEW_SECTIONS, OLD_SECTIONS, RULES_SECTIONS, AIEvalScores, RAGSource } from "./types";

// Mock RAG sources (historical RFPs)
const MOCK_RAG_SOURCES: RAGSource[] = [
  { docName: "RFP_IT_Services_2024.docx", section: "Scope of Work", similarity: 92 },
  { docName: "RFP_Design_Agency_2023.docx", section: "Deliverables", similarity: 87 },
  { docName: "RFP_Consulting_2024.docx", section: "Technical Requirements", similarity: 84 },
  { docName: "RFP_Software_Dev_2023.docx", section: "Evaluation Criteria", similarity: 89 },
  { docName: "RFP_EPC_Substation_2024.docx", section: "Timeline", similarity: 78 },
];

function generateMockAIEval(sectionName: string, sourceType: "new" | "old" | "rules"): AIEvalScores {
  // Generate realistic but varied scores
  const baseScores: Record<string, Partial<AIEvalScores>> = {
    "Scope of Work": { coherence: 8.7, ragConfidence: 91, formatCompliance: 100 },
    "Deliverables": { coherence: 8.2, ragConfidence: 87, formatCompliance: 95 },
    "Technical Requirements": { coherence: 9.1, ragConfidence: 84, formatCompliance: 100 },
    "Evaluation Criteria": { coherence: 8.9, ragConfidence: 92, formatCompliance: 100 },
    "Timeline & Milestones": { coherence: 7.8, ragConfidence: 78, formatCompliance: 90 },
    "Budget & Payment Terms": { coherence: 8.4, ragConfidence: 89, formatCompliance: 100 },
  };

  const defaults = baseScores[sectionName] || { coherence: 8.0, ragConfidence: 85, formatCompliance: 100 };

  // Pick 2-3 random sources for this section
  const numSources = sourceType === "new" ? 3 : sourceType === "old" ? 2 : 0;
  const shuffled = [...MOCK_RAG_SOURCES].sort(() => Math.random() - 0.5);
  const sources = shuffled.slice(0, numSources).map(s => ({
    ...s,
    similarity: Math.floor(s.similarity + (Math.random() * 10 - 5)) // Add some variance
  }));

  return {
    coherence: defaults.coherence || 8.0,
    ragConfidence: defaults.ragConfidence || 85,
    formatCompliance: defaults.formatCompliance || 100,
    sources: sources.length > 0 ? sources : undefined,
    latencyMs: Math.floor(800 + Math.random() * 2000),
    tokenCount: Math.floor(200 + Math.random() * 500),
  };
}

export const MOCK_QUESTIONS = [
  "What specific skills or certifications should the designer have?",
  "What is the approximate budget range for this engagement?",
  "Are there any specific tools or design systems they need to work with?",
  "Will they need to collaborate with an existing team?",
];

export function generateMockSections(context: Record<string, string>): RFPSections {
  const serviceName = context.service || "UI/UX Designer";
  const duration = context.duration || "6 months";

  return {
    new: NEW_SECTIONS.map((name) => ({
      name,
      content: getMockContent(name, serviceName, duration),
      assumptions: getMockAssumptions(name),
      aiEval: generateMockAIEval(name, "new"),
    })),
    old: OLD_SECTIONS.map((name) => ({
      name,
      content: getMockOldContent(name),
      aiEval: generateMockAIEval(name, "old"),
    })),
    rules: RULES_SECTIONS.map((name) => ({
      name,
      content: getMockRulesContent(name),
      aiEval: generateMockAIEval(name, "rules"),
    })),
  };
}

function getMockContent(sectionName: string, service: string, duration: string): string {
  const contents: Record<string, string> = {
    "Scope of Work": `## Scope of Work

CESC Limited invites proposals from qualified vendors to provide **${service}** services for a period of **${duration}**.

### Primary Responsibilities
- Lead the design of user interfaces for our digital transformation initiatives
- Create wireframes, prototypes, and high-fidelity mockups
- Conduct user research and usability testing
- Collaborate with development teams to ensure design implementation fidelity
- Establish and maintain design systems and component libraries

### Work Location
- Primary: CESC Head Office, Kolkata
- Hybrid arrangement: 3 days on-site, 2 days remote

### Reporting Structure
The selected vendor will report to the Digital Transformation Lead and work closely with the IT and Operations teams.`,

    "Deliverables": `## Deliverables

The selected vendor shall provide the following deliverables:

### Monthly Deliverables
1. **Design Artifacts**
   - Wireframes for all new features
   - High-fidelity UI mockups
   - Interactive prototypes (Figma)

2. **Documentation**
   - Design specifications
   - Component documentation
   - Handoff notes for developers

### Project Milestones
| Milestone | Deliverable | Timeline |
|-----------|-------------|----------|
| M1 | Design System Foundation | Month 1 |
| M2 | Customer Portal Redesign | Month 2-3 |
| M3 | Mobile App Designs | Month 4-5 |
| M4 | Final Documentation | Month 6 |

### Acceptance Criteria
All deliverables must meet WCAG 2.1 AA accessibility standards and be approved by the project stakeholders.`,

    "Technical Requirements": `## Technical Requirements

### Mandatory Skills
- **Design Tools**: Figma (primary), Adobe Creative Suite
- **Prototyping**: Interactive prototypes with micro-interactions
- **Design Systems**: Experience building and maintaining component libraries
- **Collaboration**: Familiarity with Jira, Confluence, and developer handoff tools

### Preferred Qualifications
- Experience with utility/energy sector applications
- Knowledge of React/React Native design patterns
- Understanding of data visualization best practices
- Accessibility certification (CPACC or equivalent)

### Technical Environment
- Design files must be maintained in CESC's Figma organization
- All assets exported in appropriate formats (SVG, PNG @2x, @3x)
- Version control for all design iterations`,

    "Evaluation Criteria": `## Evaluation Criteria

Proposals will be evaluated based on the following criteria:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Portfolio Quality | 30% | Demonstrated design excellence and relevant experience |
| Technical Expertise | 25% | Proficiency in required tools and methodologies |
| Team Composition | 20% | Qualifications of proposed team members |
| Cost Proposal | 15% | Value for money and budget alignment |
| References | 10% | Past client satisfaction and project success |

### Evaluation Process
1. **Stage 1**: Technical qualification review
2. **Stage 2**: Portfolio presentation (shortlisted vendors)
3. **Stage 3**: Commercial evaluation
4. **Stage 4**: Final selection and negotiation

### Minimum Qualifying Score
Vendors must achieve a minimum of 70% in the technical evaluation to proceed to commercial evaluation.`,

    "Timeline & Milestones": `## Timeline & Milestones

### Project Schedule

| Phase | Activity | Duration | Start | End |
|-------|----------|----------|-------|-----|
| RFP | Proposal Submission | 2 weeks | Week 1 | Week 2 |
| Evaluation | Technical Review | 1 week | Week 3 | Week 3 |
| Selection | Presentations & Negotiation | 1 week | Week 4 | Week 4 |
| Onboarding | Contract & Setup | 1 week | Week 5 | Week 5 |
| Execution | Design Services | ${duration} | Week 6 | Week 30 |

### Key Milestones
- **RFP Issue Date**: Upon approval
- **Query Deadline**: 1 week from issue
- **Submission Deadline**: 2 weeks from issue
- **Vendor Presentations**: Week 3
- **Contract Award**: Week 4
- **Project Kickoff**: Week 6

### Important Dates
All submissions must be received by **5:00 PM IST** on the deadline date. Late submissions will not be considered.`,

    "Budget & Payment Terms": `## Budget & Payment Terms

### Budget Range
The indicative budget for this engagement is **INR 15,00,000 - 25,00,000** for the full ${duration} period, inclusive of all applicable taxes.

### Payment Schedule
| Milestone | Percentage | Trigger |
|-----------|------------|---------|
| Contract Signing | 10% | Upon execution |
| Month 1 Completion | 15% | Deliverables approved |
| Month 3 Completion | 25% | Deliverables approved |
| Month 5 Completion | 25% | Deliverables approved |
| Project Completion | 25% | Final acceptance |

### Payment Terms
- Invoices to be submitted within 5 working days of milestone completion
- Payment within 30 days of invoice approval
- All payments via bank transfer (NEFT/RTGS)

### Cost Breakdown Required
Vendors must provide detailed breakdown of:
- Monthly professional fees
- Tool/license costs (if any)
- Travel expenses (if applicable)
- Any other charges`,
  };

  return contents[sectionName] || `## ${sectionName}\n\nContent for this section will be generated based on your requirements.`;
}

function getMockAssumptions(sectionName: string): string[] {
  const assumptions: Record<string, string[]> = {
    "Scope of Work": [
      "Hybrid work arrangement assumed based on typical CESC requirements",
      "Reporting to Digital Transformation Lead based on project type",
    ],
    "Deliverables": [
      "Figma assumed as primary design tool",
      "Monthly delivery cycle assumed",
    ],
    "Technical Requirements": [
      "React knowledge preferred based on CESC tech stack",
    ],
    "Evaluation Criteria": [],
    "Timeline & Milestones": [
      "Standard 2-week RFP response period assumed",
    ],
    "Budget & Payment Terms": [
      "Budget range estimated based on similar historical RFPs",
      "Standard CESC payment terms applied",
    ],
  };

  return assumptions[sectionName] || [];
}

function getMockOldContent(sectionName: string): string {
  const contents: Record<string, string> = {
    "Background & Context": `## Background & Context

CESC Limited, a flagship company of the RPSG Group, is one of India's leading integrated power utilities. Serving over 3.4 million customers in Kolkata and Howrah, CESC is committed to digital transformation and operational excellence.

### Project Background
As part of our ongoing digital transformation initiative, CESC is enhancing customer-facing applications and internal operational tools. This requires experienced design resources to ensure world-class user experiences.

### Strategic Objectives
- Improve customer satisfaction scores by 20%
- Reduce service request resolution time
- Modernize legacy applications
- Enable mobile-first experiences`,

    "Vendor Qualifications": `## Vendor Qualifications

### Minimum Requirements
- Registered company with minimum 3 years in operation
- Previous experience with enterprise clients
- Team size of at least 5 design professionals
- No active litigation or blacklisting

### Preferred Qualifications
- Experience in utility/energy sector
- ISO 27001 certified or equivalent
- Presence in Eastern India
- Existing relationship with RPSG companies`,

    "Proposal Format": `## Proposal Format

Proposals must be submitted in two separate envelopes:

### Envelope A: Technical Proposal
1. Cover letter with executive summary
2. Company profile and credentials
3. Team composition and CVs
4. Portfolio of relevant work (max 5 projects)
5. Technical approach and methodology
6. Project plan and timeline

### Envelope B: Commercial Proposal
1. Pricing summary
2. Detailed cost breakdown
3. Payment terms acceptance
4. Validity period (minimum 90 days)`,

    "Submission Instructions": `## Submission Instructions

### Submission Method
- Electronic submission via email to procurement@cesc.co.in
- Subject line: "RFP Response - [Vendor Name] - [RFP Number]"
- Maximum attachment size: 25MB per email

### Deadline
All proposals must be received by **5:00 PM IST** on the deadline date.

### Queries
- Submit queries in writing to rfp-queries@cesc.co.in
- Query deadline: 7 days before submission deadline
- Responses will be shared with all participating vendors`,

    "Contract Terms": `## Contract Terms

### Contract Duration
- Initial term: As specified in scope
- Extension: Up to 2 renewals of 6 months each, subject to performance

### Performance Review
- Quarterly performance reviews
- KPIs defined in contract annexure
- Right to terminate with 30 days notice for non-performance`,

    "Insurance Requirements": `## Insurance Requirements

The selected vendor must maintain:
- Professional Liability Insurance: INR 1 Crore minimum
- General Liability Insurance: INR 50 Lakhs minimum
- Cyber Liability Insurance: INR 50 Lakhs minimum

Insurance certificates must be provided before contract execution.`,

    "Warranty & Support": `## Warranty & Support

### Warranty Period
- 30 days warranty on all deliverables post-acceptance
- Defects to be rectified at no additional cost

### Support
- Email support during business hours
- 48-hour response time for queries
- Knowledge transfer at project completion`,

    "References Required": `## References Required

Vendors must provide:
- Minimum 3 references from enterprise clients
- At least 1 reference from utility/infrastructure sector (preferred)
- Reference contact details for verification

CESC reserves the right to contact references directly.`,
  };

  return contents[sectionName] || `## ${sectionName}\n\nThis section is retrieved from historical RFPs and adapted for this requirement.`;
}

function getMockRulesContent(sectionName: string): string {
  const contents: Record<string, string> = {
    "General Terms & Conditions": `## General Terms & Conditions

1. This RFP does not constitute a commitment by CESC to award a contract.
2. CESC reserves the right to accept or reject any or all proposals.
3. All proposals become the property of CESC upon submission.
4. Vendors bear all costs associated with proposal preparation.
5. CESC may seek clarifications from vendors during evaluation.
6. The decision of CESC shall be final and binding.`,

    "Safety & Compliance": `## Safety & Compliance

All vendors must comply with:
- Applicable labor laws and regulations
- CESC safety protocols when on premises
- Data protection and privacy regulations
- Environmental guidelines as applicable

Non-compliance may result in immediate contract termination.`,

    "Intellectual Property": `## Intellectual Property

- All work product created shall be the exclusive property of CESC
- Vendor grants perpetual, royalty-free license to CESC
- Pre-existing IP remains with respective owners
- Vendor warrants no infringement of third-party IP`,

    "Confidentiality": `## Confidentiality

- Vendors must maintain strict confidentiality of all CESC information
- NDA required before sharing detailed requirements
- Information cannot be used for any purpose other than this engagement
- Confidentiality obligations survive contract termination`,

    "Termination Clause": `## Termination Clause

CESC may terminate the contract:
- For convenience with 30 days written notice
- Immediately for material breach
- Immediately for insolvency or bankruptcy
- Immediately for violation of laws or ethical standards`,

    "Dispute Resolution": `## Dispute Resolution

- Good faith negotiation for 30 days
- Mediation by mutually agreed mediator
- Arbitration under Indian Arbitration Act if mediation fails
- Arbitration seat: Kolkata`,

    "Force Majeure": `## Force Majeure

Neither party liable for failure due to:
- Natural disasters
- War, terrorism, civil unrest
- Government actions
- Pandemic or epidemic

Notice within 7 days required. Contract may be terminated if force majeure exceeds 90 days.`,

    "Indemnification": `## Indemnification

Vendor shall indemnify CESC against:
- Third-party IP infringement claims
- Personal injury or property damage caused by vendor
- Breach of confidentiality
- Violation of applicable laws`,

    "Liability Limitations": `## Liability Limitations

- Total liability limited to contract value
- No liability for indirect, consequential, or punitive damages
- Exceptions: Fraud, gross negligence, IP infringement, confidentiality breach`,

    "Governing Law": `## Governing Law

- Contract governed by laws of India
- Courts of Kolkata shall have exclusive jurisdiction
- English language governs all communications`,

    "Amendment Procedures": `## Amendment Procedures

- All amendments must be in writing
- Signed by authorized representatives of both parties
- No oral modifications valid
- Change requests follow defined change control process`,
  };

  return contents[sectionName] || `## ${sectionName}\n\nStandard CESC clause.`;
}
