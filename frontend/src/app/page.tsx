"use client";

import { useState } from "react";
import { ChatScreen } from "@/components/chat-screen";
import { ReviewScreen } from "@/components/review-screen";
import { ChatMessage, RFPSections } from "@/lib/types";

export default function Home() {
  const [screen, setScreen] = useState<"chat" | "review">("chat");
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [sections, setSections] = useState<RFPSections | null>(null);
  const [context, setContext] = useState<Record<string, string>>({});
  const [rfpTitle, setRfpTitle] = useState("");
  const [sessionId, setSessionId] = useState("");

  const handleSectionsGenerated = (newSections: RFPSections, newContext: Record<string, string>) => {
    setSections(newSections);
    setContext(newContext);
    setSessionId(newContext.sessionId || "");
    // Generate title from context
    const service = newContext.service || "Professional Services";
    setRfpTitle(`${service} - Service RFP`);
  };

  if (screen === "review" && sections) {
    return (
      <ReviewScreen
        sections={sections}
        onBack={() => setScreen("chat")}
        rfpTitle={rfpTitle}
        setRfpTitle={setRfpTitle}
        sessionId={sessionId}
        context={context}
      />
    );
  }

  return (
    <ChatScreen
      chatHistory={chatHistory}
      setChatHistory={setChatHistory}
      onSectionsGenerated={handleSectionsGenerated}
      onNavigateToReview={() => setScreen("review")}
      hasGeneratedSections={sections !== null}
    />
  );
}
