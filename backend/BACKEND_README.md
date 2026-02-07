# RFP Generator Backend Server

Backend API server that connects the Next.js frontend with the RAG system for AI-powered RFP generation.

## Architecture

```
Backend Server (FastAPI)
├── server.py              # Main FastAPI application
├── api/
│   ├── routes.py          # API endpoints
│   └── schemas.py         # Pydantic models
├── services/
│   ├── section_generator.py    # NEW/OLD/RULES generation
│   ├── question_generator.py   # Adaptive questions
│   └── ai_evaluator.py         # AI evaluation metrics
├── database/
│   └── db.py              # SQLite database
└── templates/             # RULES section templates (11 files)
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/analyze` | POST | Analyze initial RFP request, generate questions |
| `/api/questions` | POST | Get next question (returns completion status) |
| `/api/generate` | POST | Generate all 25 RFP sections |
| `/api/regenerate` | POST | Regenerate single section with context |
| `/api/export` | GET | Export RFP as Word document |

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the `backend` directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o
```

### 3. Run the Server

```bash
cd backend
python server.py
```

Or using uvicorn directly:

```bash
uvicorn server:app --reload --port 8000
```

The server will start at `http://localhost:8000`

## Database

SQLite database (`rfp_generator.db`) with 3 tables:

- **rfp_sessions**: RFP generation sessions
- **sections**: Generated sections (NEW/OLD/RULES)
- **generation_traces**: Langfuse-ready traces for future observability

Database is automatically initialized on server startup.

## Three-Source Architecture

### NEW Sections (6) - LLM Generated
- Scope of Work
- Deliverables
- Technical Requirements
- Evaluation Criteria
- Timeline & Milestones
- Budget & Payment Terms

### OLD Sections (8) - RAG Retrieved
- Background & Context
- Vendor Qualifications
- Proposal Format
- Submission Instructions
- Contract Terms
- Insurance Requirements
- Warranty & Support
- References Required

### RULES Sections (11) - Fixed Templates
- General Terms & Conditions
- Safety & Compliance
- Intellectual Property
- Confidentiality
- Termination Clause
- Dispute Resolution
- Force Majeure
- Indemnification
- Liability Limitations
- Governing Law
- Amendment Procedures

## Testing

### Health Check

```bash
curl http://localhost:8000/health
```

### Analyze Request

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create RFP for UI/UX designer, 6 months"}'
```

### Generate Sections

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "context": {
      "service": "UI/UX Designer",
      "duration": "6 months"
    }
  }'
```

## Integration with Frontend

Update the Next.js frontend to call these endpoints instead of using mock data:

```typescript
// Replace mock data in src/lib/mock-data.ts
const API_BASE = 'http://localhost:8000/api';

export async function analyzeRequest(prompt: string) {
  const response = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
  return response.json();
}

export async function generateSections(sessionId: string, context: Record<string, any>) {
  const response = await fetch(`${API_BASE}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, context }),
  });
  return response.json();
}
```

## Future Enhancements

- [ ] Integrate actual RAG retrieval for OLD sections (currently uses LLM)
- [ ] Add Langfuse observability integration
- [ ] Implement user authentication
- [ ] Add multi-organization support
- [ ] Enhance Word export with better formatting
