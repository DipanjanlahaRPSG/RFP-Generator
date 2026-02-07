# Frontend Integration Guide

## Setup

1. **Install dependencies** (if not already done):
```bash
cd frontend
npm install
```

2. **Configure API URL**:
The `.env.local` file is already configured to point to `http://localhost:8000/api`

3. **Start the development server**:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## What Changed

### New Files
- **`src/lib/api-client.ts`**: API client with functions for all backend endpoints

### Updated Files
- **`src/components/chat-screen.tsx`**: 
  - Replaced mock data with real API calls
  - Uses `analyzeRequest()` for question generation
  - Uses `generateSections()` for RFP creation
  
- **`src/components/review-screen.tsx`**:
  - Uses `regenerateSection()` for section regeneration
  - Uses `exportRFP()` and `downloadRFP()` for Word export
  
- **`src/app/page.tsx`**:
  - Added `sessionId` state management
  - Passes sessionId and context to ReviewScreen

## Testing the Integration

### 1. Start Both Servers

**Terminal 1 - Backend:**
```bash
cd backend
start_server.bat
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 2. Test the Flow

1. Open `http://localhost:3000`
2. Enter an RFP request (e.g., "Create RFP for UI/UX designer, 6 months")
3. Answer the adaptive questions
4. Wait for generation (may take 30-90 seconds)
5. Review the generated sections
6. Regenerate any section with additional context
7. Approve all critical sections
8. Download the RFP as a Word document

## API Endpoints Used

| Frontend Action | API Endpoint | Purpose |
|----------------|--------------|---------|
| Initial prompt | `POST /api/analyze` | Get questions and session ID |
| After questions | `POST /api/generate` | Generate all 25 sections |
| Regenerate button | `POST /api/regenerate` | Regenerate single section |
| Download button | `GET /api/export` | Export as .docx |

## Error Handling

All API calls include try-catch blocks with user-friendly error messages. If the backend is not running, you'll see connection errors in the chat.

## Environment Variables

- **`NEXT_PUBLIC_API_URL`**: Backend API base URL (default: `http://localhost:8000/api`)

## Next Steps

- Test the full end-to-end flow
- Verify Word document export
- Check AI evaluation metrics display
- Test regeneration with different contexts
