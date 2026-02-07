"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  FileText,
  Send,
  RotateCcw,
  Loader2,
  ChevronRight,
  Bot,
  User,
} from "lucide-react";
import { ChatMessage, RFPSections } from "@/lib/types";
import { analyzeRequest, generateSections, discoverContext } from "@/lib/api-client";

interface ChatScreenProps {
  chatHistory: ChatMessage[];
  setChatHistory: (history: ChatMessage[]) => void;
  onSectionsGenerated: (sections: RFPSections, context: Record<string, string>) => void;
  onNavigateToReview: () => void;
  hasGeneratedSections: boolean;
}

export function ChatScreen({
  chatHistory,
  setChatHistory,
  onSectionsGenerated,
  onNavigateToReview,
  hasGeneratedSections,
}: ChatScreenProps) {
  const [input, setInput] = useState("");
  const [pendingQuestions, setPendingQuestions] = useState<string[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [collectedAnswers, setCollectedAnswers] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [context, setContext] = useState<Record<string, string>>({});
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [chatHistory]);

  const addMessage = (role: "user" | "assistant", content: string) => {
    setChatHistory([...chatHistory, { role, content }]);
  };

  const handleSend = async () => {
    if (!input.trim() || isGenerating) return;

    const userInput = input.trim();
    setInput("");

    // Add user message
    const newHistory = [...chatHistory, { role: "user" as const, content: userInput }];
    setChatHistory(newHistory);

    // First input - analyze and start questions
    if (pendingQuestions.length === 0 && currentQuestionIndex === 0) {
      try {
        // Call analyze API
        setIsGenerating(true);
        const analysisResult = await analyzeRequest(userInput);
        setIsGenerating(false);

        // Store session ID and context
        const newContext = {
          sessionId: analysisResult.session_id,
          originalRequest: userInput,
          rfpType: analysisResult.rfp_type,
          ...analysisResult.entities,
        };
        setContext(newContext);

        // Check if we have questions
        if (analysisResult.questions && analysisResult.questions.length > 0) {
          setPendingQuestions(analysisResult.questions);

          const total = analysisResult.questions.length;
          setChatHistory([
            ...newHistory,
            {
              role: "assistant",
              content: `Thanks! I have ${total} quick question${total > 1 ? "s" : ""} to help create a better RFP.\n\n**Question 1/${total}:** ${analysisResult.questions[0]}`,
            },
          ]);
          setCurrentQuestionIndex(1);
        } else {
          // No questions - skip to generation
          await startGeneration(newHistory, newContext);
        }
      } catch (error) {
        setIsGenerating(false);
        setChatHistory([
          ...newHistory,
          {
            role: "assistant",
            content: `Error analyzing request: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`,
          },
        ]);
      }
    } else if (pendingQuestions.length > 0) {
      // Answering questions one at a time
      const newAnswers = [...collectedAnswers, userInput];
      setCollectedAnswers(newAnswers);

      const total = pendingQuestions.length;
      const current = currentQuestionIndex;

      if (current < total) {
        // Ask next question
        setChatHistory([
          ...newHistory,
          {
            role: "assistant",
            content: `**Question ${current + 1}/${total}:** ${pendingQuestions[current]}`,
          },
        ]);
        setCurrentQuestionIndex(current + 1);
      } else {
        // All questions answered - generate
        const updatedContext = {
          ...context,
          answers: pendingQuestions.map((q, i) => `Q: ${q}\nA: ${newAnswers[i]}`).join("\n\n"),
        };
        await startGeneration(newHistory, updatedContext);
      }
    }
  };

  const startGeneration = async (history: ChatMessage[], ctx: Record<string, string>) => {
    setIsGenerating(true);

    setChatHistory([
      ...history,
      {
        role: "assistant",
        content: "Perfect! Generating your RFP now... This may take up to 90 seconds.",
      },
    ]);

    try {
      // Call generate API
      // Step 1: Discover relevant context from RAG
      setChatHistory([
        ...history,
        {
          role: "assistant",
          content: "Searching historical RFPs for relevant context...",
        },
      ]);

      const discovery = await discoverContext(ctx.sessionId, ctx);

      // Add discovered context metadata to session context
      ctx = {
        ...ctx,
        rag_discovery_count: discovery.total_found.toString(),
        rag_discovery_query: discovery.search_query
      };

      setChatHistory([
        ...history,
        {
          role: "assistant",
          content: "Searching historical RFPs for relevant context...",
        },
        {
          role: "assistant",
          content: `Found ${discovery.total_found} relevant historical RFPs! Using insights to generate your RFP...`,
        },
      ]);

      // Step 2: Generate sections with RAG context
      const result = await generateSections(ctx.sessionId, ctx);

      const newCount = result.sections.new.length;
      const oldCount = result.sections.old.length;
      const rulesCount = result.sections.rules.length;

      setChatHistory([
        ...history,
        {
          role: "assistant",
          content: "Searching historical RFPs for relevant context...",
        },
        {
          role: "assistant",
          content: `Found ${discovery.total_found} relevant historical RFPs! Using insights to generate your RFP...`,
        },
        {
          role: "assistant",
          content: `**RFP Generated Successfully!**\n\n**Sections Created:**\n- **${newCount} Critical sections** (need your approval)\n- **${oldCount} RAG-generated sections** (from historical RFPs)\n- **${rulesCount} Template sections** (standard clauses)\n\nClick **Review & Approve Sections** below to review the critical sections.`,
        },
      ]);

      setIsGenerating(false);
      onSectionsGenerated(result.sections as RFPSections, ctx);
    } catch (error) {
      setIsGenerating(false);
      setChatHistory([
        ...history,
        {
          role: "assistant",
          content: `Error generating RFP: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`,
        },
      ]);
    }
  };

  const handleReset = () => {
    setChatHistory([]);
    setPendingQuestions([]);
    setCurrentQuestionIndex(0);
    setCollectedAnswers([]);
    setContext({});
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <header className="border-b px-6 py-4 flex items-center justify-between bg-card">
        <div className="flex items-center gap-3">
          <FileText className="h-6 w-6 text-primary" />
          <div>
            <h1 className="text-xl font-semibold">RFP Generator</h1>
            <p className="text-sm text-muted-foreground">CESC Procurement Tool</p>
          </div>
        </div>
        <Button variant="outline" size="sm" onClick={handleReset}>
          <RotateCcw className="h-4 w-4 mr-2" />
          Start Over
        </Button>
      </header>

      {/* Chat Area */}
      <ScrollArea className="flex-1 p-6" ref={scrollRef}>
        <div className="max-w-3xl mx-auto space-y-4">
          {/* Welcome message */}
          {chatHistory.length === 0 && (
            <Card className="p-6 bg-muted/50">
              <div className="flex items-start gap-3">
                <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
                  <Bot className="h-4 w-4 text-primary-foreground" />
                </div>
                <div className="space-y-3">
                  <p className="font-medium">Welcome to the RFP Generator!</p>
                  <p className="text-muted-foreground">
                    I'll help you create a professional RFP document. Just describe what you need to procure.
                  </p>
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Examples:</p>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li className="cursor-pointer hover:text-foreground" onClick={() => setInput("I need an RFP for hiring a UI/UX designer for 6 months")}>
                        → "I need an RFP for hiring a UI/UX designer for 6 months"
                      </li>
                      <li className="cursor-pointer hover:text-foreground" onClick={() => setInput("Create an RFP for procuring 500 energy meters")}>
                        → "Create an RFP for procuring 500 energy meters"
                      </li>
                      <li className="cursor-pointer hover:text-foreground" onClick={() => setInput("RFP for construction of a new substation")}>
                        → "RFP for construction of a new substation"
                      </li>
                    </ul>
                  </div>
                  <p className="text-sm text-muted-foreground mt-4 p-3 bg-background rounded-md border">
                    💡 <strong>Tip:</strong> The more detail you provide, the better the output. Feel free to paste existing requirements or specifications.
                  </p>
                </div>
              </div>
            </Card>
          )}

          {/* Chat messages */}
          {chatHistory.map((msg, i) => (
            <div
              key={i}
              className={`flex items-start gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
            >
              <div
                className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === "user" ? "bg-secondary" : "bg-primary"
                  }`}
              >
                {msg.role === "user" ? (
                  <User className="h-4 w-4" />
                ) : (
                  <Bot className="h-4 w-4 text-primary-foreground" />
                )}
              </div>
              <Card
                className={`p-4 max-w-[80%] ${msg.role === "user" ? "bg-secondary" : "bg-muted/50"
                  }`}
              >
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  {msg.content.split("\n").map((line, j) => (
                    <p key={j} className="mb-2 last:mb-0">
                      {line.startsWith("**") ? (
                        <strong>{line.replace(/\*\*/g, "")}</strong>
                      ) : line.startsWith("- ") ? (
                        <span className="block ml-2">{line}</span>
                      ) : (
                        line
                      )}
                    </p>
                  ))}
                </div>
              </Card>
            </div>
          ))}

          {/* Generating indicator */}
          {isGenerating && (
            <div className="flex items-start gap-3">
              <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
                <Bot className="h-4 w-4 text-primary-foreground" />
              </div>
              <Card className="p-4 bg-muted/50">
                <div className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Generating 25 sections in parallel...</span>
                </div>
              </Card>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Transition to Review */}
      {hasGeneratedSections && (
        <>
          <Separator />
          <div className="p-4 bg-muted/30">
            <div className="max-w-3xl mx-auto">
              <Button
                size="lg"
                className="w-full"
                onClick={onNavigateToReview}
              >
                Review & Approve Sections
                <ChevronRight className="h-4 w-4 ml-2" />
              </Button>
            </div>
          </div>
        </>
      )}

      {/* Input Area */}
      <div className="border-t p-4 bg-card">
        <div className="max-w-3xl mx-auto flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe your RFP need..."
            disabled={isGenerating}
            className="flex-1"
          />
          <Button onClick={handleSend} disabled={!input.trim() || isGenerating}>
            {isGenerating ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

// Helper functions
function simulateDelay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function extractService(input: string): string {
  const match = input.match(/(?:for|hiring|need)\s+(?:a\s+)?(.+?)(?:\s+for|\s+services?|\s*$)/i);
  return match ? match[1] : "Professional Services";
}

function extractDuration(input: string): string {
  const match = input.match(/(\d+)\s*(months?|years?|weeks?)/i);
  return match ? `${match[1]} ${match[2]}` : "6 months";
}
