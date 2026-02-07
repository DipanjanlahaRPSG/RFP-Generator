/**
 * API Client for RFP Generator Backend
 * Connects Next.js frontend to FastAPI backend
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Types for API requests/responses
interface AnalyzeRequest {
    prompt: string;
}

interface AnalyzeResponse {
    rfp_type: string;
    entities: Record<string, any>;
    questions: string[];
    session_id: string;
}

interface GenerateRequest {
    session_id: string;
    context: Record<string, any>;
}

interface GenerateResponse {
    session_id: string;
    sections: {
        new: any[];
        old: any[];
        rules: any[];
    };
}

interface RegenerateRequest {
    session_id: string;
    section_name: string;
    context: Record<string, any>;
    iteration: number;
    additional_context?: string;
}

interface RegenerateResponse {
    section: any;
}

/**
 * Analyze initial RFP request and get adaptive questions
 */
export async function analyzeRequest(prompt: string): Promise<AnalyzeResponse> {
    const response = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
}

/**
 * Discover relevant context from RAG system
 * Called after user answers questions, before generation
 */
export async function discoverContext(
    sessionId: string,
    context: Record<string, any>
): Promise<{
    session_id: string;
    relevant_rfps: Array<{
        doc_name: string;
        similarity: number;
        rfp_type: string;
        sections_found: string[];
        summary: string;
    }>;
    extracted_insights: Record<string, any>;
    search_query: string;
    total_found: number;
}> {
    const response = await fetch(`${API_BASE}/discover-context`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: sessionId,
            context,
        }),
    });

    if (!response.ok) {
        throw new Error(`Failed to discover context: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
}

/**
 * Generate all RFP sections
 */
export async function generateSections(
    sessionId: string,
    context: Record<string, any>
): Promise<GenerateResponse> {
    const response = await fetch(`${API_BASE}/generate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: sessionId,
            context,
        }),
    });

    if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
}

/**
 * Regenerate a single section
 */
export async function regenerateSection(
    sessionId: string,
    sectionName: string,
    context: Record<string, any>,
    iteration: number,
    additionalContext?: string
): Promise<RegenerateResponse> {
    const response = await fetch(`${API_BASE}/regenerate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: sessionId,
            section_name: sectionName,
            context,
            iteration,
            additional_context: additionalContext,
        }),
    });

    if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
}

/**
 * Export RFP as Word document
 */
export async function exportRFP(sessionId: string): Promise<Blob> {
    const response = await fetch(`${API_BASE}/export?session_id=${sessionId}`, {
        method: 'GET',
    });

    if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
    }

    return response.blob();
}

/**
 * Download exported RFP
 */
export function downloadRFP(blob: Blob, filename: string = 'RFP.docx') {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

/**
 * Health check
 */
export async function healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${API_BASE.replace('/api', '')}/health`);
    return response.json();
}
