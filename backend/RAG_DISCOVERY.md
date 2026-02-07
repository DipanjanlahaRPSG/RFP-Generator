# RAG Context Discovery Architecture

## Overview
After the user answers adaptive questions, the system now searches historical RFPs in the RAG system to find relevant context before generating new sections.

## Flow

```
1. User enters initial prompt
   ↓
2. System generates adaptive questions
   ↓
3. User answers questions
   ↓
4. **NEW: RAG Context Discovery**
   - Search historical RFPs using semantic search
   - Extract insights using LLM analysis
   - Store discovered context in session
   ↓
5. Generate RFP sections (with RAG context)
   ↓
6. Review & approve
```

## Implementation

### Backend

#### New Service: `rag_context_discovery.py`
- **Purpose**: Search RAG system and extract insights
- **Methods**:
  - `discover_context()`: Main entry point
  - `_build_search_query()`: Constructs semantic search query
  - `_search_historical_rfps()`: Searches vector store (TODO: integrate with actual SearchEngine)
  - `_extract_insights()`: Uses LLM to analyze found RFPs

#### New Endpoint: `POST /api/discover-context`
- **Request**: `{ session_id, context }`
- **Response**: `{ relevant_rfps[], extracted_insights{}, search_query, total_found }`
- **Side Effect**: Updates session context in database with RAG discovery results

### Frontend

#### Updated `api-client.ts`
- Added `discoverContext()` function

#### Updated `chat-screen.tsx`
- Calls `discoverContext()` after user answers questions
- Shows progress: "Searching historical RFPs for relevant context..."
- Shows results: "Found X relevant historical RFPs!"
- Passes enriched context to `generateSections()`

## Benefits

1. **Better Context**: Sections are informed by similar historical RFPs
2. **Consistency**: Maintains patterns from successful past RFPs
3. **Quality**: Leverages proven approaches and language
4. **Transparency**: Debug mode shows which RFPs were used

## TODO

- [ ] Integrate with actual `SearchEngine` from `rag_engine` module
- [ ] Add RAG source attribution to generated sections
- [ ] Show discovered RFPs in debug panel
- [ ] Allow user to review/select which historical RFPs to use
