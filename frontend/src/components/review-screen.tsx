"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  ArrowLeft,
  Check,
  RefreshCw,
  Download,
  AlertCircle,
  FileText,
  Loader2,
  Undo2,
  Clock,
  CheckCircle2,
  BookOpen,
  FileCheck,
  Sparkles,
} from "lucide-react";
import { RFPSections, Section, NEW_SECTIONS } from "@/lib/types";
import { AIEvalPanel, AIEvalSummary } from "@/components/ai-eval-panel";
import { DebugPanel } from "@/components/debug-panel";
import { regenerateSection, exportRFP, downloadRFP } from "@/lib/api-client";

interface ReviewScreenProps {
  sections: RFPSections;
  onBack: () => void;
  rfpTitle: string;
  setRfpTitle: (title: string) => void;
  sessionId: string;
  context: Record<string, string>;
}

export function ReviewScreen({
  sections,
  onBack,
  rfpTitle,
  setRfpTitle,
  sessionId,
  context,
}: ReviewScreenProps) {
  const [approved, setApproved] = useState<Set<string>>(new Set());
  const [regenCounts, setRegenCounts] = useState<Record<string, number>>(
    Object.fromEntries(NEW_SECTIONS.map((s) => [s, 1]))
  );
  const [regeneratingSection, setRegeneratingSection] = useState<string | null>(null);
  const [regenContext, setRegenContext] = useState<Record<string, string>>({});
  const [debugMode, setDebugMode] = useState(false);

  const totalRequired = NEW_SECTIONS.length;
  const approvedCount = approved.size;
  const progressPercent = (approvedCount / totalRequired) * 100;

  const handleApprove = (sectionName: string) => {
    setApproved(new Set([...approved, sectionName]));
  };

  const handleUnapprove = (sectionName: string) => {
    const newApproved = new Set(approved);
    newApproved.delete(sectionName);
    setApproved(newApproved);
  };

  const handleRegenerate = async (sectionName: string) => {
    if (regenCounts[sectionName] >= 5) return;

    setRegeneratingSection(sectionName);

    try {
      const iteration = regenCounts[sectionName] + 1;
      const additionalContext = regenContext[sectionName];

      // Call regenerate API
      const result = await regenerateSection(
        sessionId,
        sectionName,
        context,
        iteration,
        additionalContext
      );

      // Update section in sections (would need to update parent state in real app)
      // For now, just update counts
      setRegenCounts((prev) => ({
        ...prev,
        [sectionName]: iteration,
      }));
      setRegenContext((prev) => ({ ...prev, [sectionName]: "" }));
    } catch (error) {
      alert(`Error regenerating section: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setRegeneratingSection(null);
    }
  };

  const handleDownload = async () => {
    try {
      const blob = await exportRFP(sessionId);
      downloadRFP(blob, `${rfpTitle.replace(/\s+/g, '_')}.docx`);
    } catch (error) {
      alert(`Error exporting RFP: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <header className="border-b px-6 py-4 bg-card">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={onBack}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Chat
            </Button>
            <Separator orientation="vertical" className="h-6" />
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary" />
              <h1 className="text-lg font-semibold">Review & Refine</h1>
            </div>
          </div>
          {/* AI Eval Summary */}
          <div className="hidden md:flex items-center gap-4">
            <AIEvalSummary sections={sections.new} />
            <Separator orientation="vertical" className="h-6" />
            <Button
              variant={debugMode ? "default" : "outline"}
              size="sm"
              onClick={() => setDebugMode(!debugMode)}
              className="gap-2"
            >
              <Sparkles className="h-4 w-4" />
              {debugMode ? "Hide" : "Show"} Debug Info
            </Button>
          </div>
        </div>
      </header>

      {/* Progress Bar */}
      <div className="px-6 py-4 bg-muted/30 border-b">
        <div className="max-w-4xl mx-auto space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium">
              {approvedCount}/{totalRequired} critical sections approved
            </span>
            <span className="text-muted-foreground">
              {approvedCount < totalRequired
                ? `${totalRequired - approvedCount} remaining`
                : "All approved!"}
            </span>
          </div>
          <Progress value={progressPercent} className="h-2" />
          {approvedCount < totalRequired ? (
            <Alert variant="default" className="mt-3 bg-amber-50 border-amber-200 dark:bg-amber-950 dark:border-amber-800">
              <AlertCircle className="h-4 w-4 text-amber-600" />
              <AlertDescription className="text-amber-800 dark:text-amber-200">
                Approve all {totalRequired} critical sections to enable download
              </AlertDescription>
            </Alert>
          ) : (
            <Alert className="mt-3 bg-green-50 border-green-200 dark:bg-green-950 dark:border-green-800">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800 dark:text-green-200">
                All critical sections approved! You can now download the RFP.
              </AlertDescription>
            </Alert>
          )}
        </div>
      </div>

      {/* Main Content */}
      <ScrollArea className="flex-1">
        <div className={`max-w-4xl mx-auto p-6 ${approvedCount === totalRequired ? "pb-28" : ""}`}>
          <Tabs defaultValue="critical" className="space-y-4">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="critical" className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-red-500" />
                Critical ({approvedCount}/{totalRequired})
              </TabsTrigger>
              <TabsTrigger value="rag" className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-blue-500" />
                RAG-Generated ({sections.old.length})
              </TabsTrigger>
              <TabsTrigger value="templates" className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-green-500" />
                Templates ({sections.rules.length})
              </TabsTrigger>
            </TabsList>

            {/* Critical Sections Tab */}
            <TabsContent value="critical" className="space-y-4">
              <div className="text-sm text-muted-foreground mb-4">
                These sections are generated from your input and need review before download.
              </div>
              <Accordion type="multiple" className="space-y-3">
                {sections.new.map((section) => {
                  const isApproved = approved.has(section.name);
                  const regenCount = regenCounts[section.name] || 1;
                  const isRegenerating = regeneratingSection === section.name;

                  return (
                    <AccordionItem
                      key={section.name}
                      value={section.name}
                      className="border rounded-lg overflow-hidden"
                    >
                      <AccordionTrigger className="px-4 py-3 hover:no-underline hover:bg-muted/50">
                        <div className="flex items-center gap-3 flex-1">
                          {isApproved ? (
                            <CheckCircle2 className="h-5 w-5 text-green-500 shrink-0" />
                          ) : (
                            <Clock className="h-5 w-5 text-amber-500 shrink-0" />
                          )}
                          <span className="font-medium text-left">{section.name}</span>
                          {/* AI Eval compact badges */}
                          {section.aiEval && (
                            <div className="hidden sm:block ml-2">
                              <AIEvalPanel eval={section.aiEval} sectionType="new" compact />
                            </div>
                          )}
                          <Badge variant="outline" className="ml-auto mr-4">
                            v{regenCount}/5
                          </Badge>
                        </div>
                      </AccordionTrigger>
                      <AccordionContent className="px-4 pb-4">
                        {/* Content */}
                        <div className="prose prose-sm dark:prose-invert max-w-none mb-4 p-4 bg-muted/30 rounded-md">
                          {section.content.split("\n").map((line, i) => {
                            if (line.startsWith("## ")) {
                              return (
                                <h2 key={i} className="text-lg font-semibold mt-0 mb-3">
                                  {line.replace("## ", "")}
                                </h2>
                              );
                            }
                            if (line.startsWith("### ")) {
                              return (
                                <h3 key={i} className="text-base font-medium mt-4 mb-2">
                                  {line.replace("### ", "")}
                                </h3>
                              );
                            }
                            if (line.startsWith("| ")) {
                              return (
                                <code key={i} className="block text-xs bg-background p-1 font-mono">
                                  {line}
                                </code>
                              );
                            }
                            if (line.startsWith("- ") || line.startsWith("* ")) {
                              return (
                                <li key={i} className="ml-4">
                                  {line.substring(2)}
                                </li>
                              );
                            }
                            if (line.match(/^\d+\./)) {
                              return (
                                <li key={i} className="ml-4">
                                  {line}
                                </li>
                              );
                            }
                            if (line.trim() === "") {
                              return <br key={i} />;
                            }
                            return (
                              <p key={i} className="mb-2">
                                {line.replace(/\*\*(.+?)\*\*/g, "$1")}
                              </p>
                            );
                          })}
                        </div>

                        {/* AI Evaluation Panel */}
                        {section.aiEval && (
                          <div className="mb-4">
                            <AIEvalPanel eval={section.aiEval} sectionType="new" />
                          </div>
                        )}

                        {/* Debug Panel */}
                        {debugMode && (
                          <div className="mb-4">
                            <DebugPanel section={section} sectionType="new" />
                          </div>
                        )}

                        {/* Assumptions */}
                        {section.assumptions && section.assumptions.length > 0 && (
                          <Alert className="mb-4">
                            <AlertCircle className="h-4 w-4" />
                            <AlertDescription>
                              <strong>Assumptions:</strong>{" "}
                              {section.assumptions.join("; ")}
                            </AlertDescription>
                          </Alert>
                        )}

                        <Separator className="my-4" />

                        {/* Actions */}
                        {!isApproved ? (
                          <div className="space-y-4">
                            {/* Regeneration */}
                            {regenCount < 5 && (
                              <div className="space-y-2">
                                <label className="text-sm font-medium">
                                  Want changes? Add context below:
                                </label>
                                <div className="flex gap-2">
                                  <Textarea
                                    value={regenContext[section.name] || ""}
                                    onChange={(e) =>
                                      setRegenContext((prev) => ({
                                        ...prev,
                                        [section.name]: e.target.value,
                                      }))
                                    }
                                    placeholder="e.g., Include WCAG 2.1 AA accessibility requirements"
                                    className="flex-1 min-h-[60px]"
                                  />
                                  <Button
                                    variant="outline"
                                    onClick={() => handleRegenerate(section.name)}
                                    disabled={isRegenerating}
                                    className="shrink-0"
                                  >
                                    {isRegenerating ? (
                                      <Loader2 className="h-4 w-4 animate-spin" />
                                    ) : (
                                      <RefreshCw className="h-4 w-4" />
                                    )}
                                    <span className="ml-2">Regenerate</span>
                                  </Button>
                                </div>
                              </div>
                            )}
                            {regenCount >= 5 && (
                              <Alert>
                                <AlertCircle className="h-4 w-4" />
                                <AlertDescription>
                                  Maximum regenerations (5) reached for this section.
                                </AlertDescription>
                              </Alert>
                            )}

                            {/* Approve Button */}
                            <Button
                              className="w-full"
                              onClick={() => handleApprove(section.name)}
                            >
                              <Check className="h-4 w-4 mr-2" />
                              Approve This Section
                            </Button>
                          </div>
                        ) : (
                          <Button
                            variant="outline"
                            onClick={() => handleUnapprove(section.name)}
                          >
                            <Undo2 className="h-4 w-4 mr-2" />
                            Unapprove
                          </Button>
                        )}
                      </AccordionContent>
                    </AccordionItem>
                  );
                })}
              </Accordion>
            </TabsContent>

            {/* RAG-Generated Sections Tab */}
            <TabsContent value="rag" className="space-y-4">
              <div className="text-sm text-muted-foreground mb-4">
                These sections are adapted from similar historical RFPs.
              </div>
              <Accordion type="multiple" className="space-y-3">
                {sections.old.map((section) => (
                  <AccordionItem
                    key={section.name}
                    value={section.name}
                    className="border rounded-lg overflow-hidden"
                  >
                    <AccordionTrigger className="px-4 py-3 hover:no-underline hover:bg-muted/50">
                      <div className="flex items-center gap-3 flex-1">
                        <BookOpen className="h-5 w-5 text-blue-500 shrink-0" />
                        <span className="font-medium">{section.name}</span>
                        {/* AI Eval compact badges */}
                        {section.aiEval && (
                          <div className="hidden sm:block ml-auto mr-4">
                            <AIEvalPanel eval={section.aiEval} sectionType="old" compact />
                          </div>
                        )}
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="px-4 pb-4">
                      <div className="prose prose-sm dark:prose-invert max-w-none p-4 bg-muted/30 rounded-md mb-4">
                        {section.content.split("\n").map((line, i) => {
                          if (line.startsWith("## ")) {
                            return (
                              <h2 key={i} className="text-lg font-semibold mt-0 mb-3">
                                {line.replace("## ", "")}
                              </h2>
                            );
                          }
                          if (line.startsWith("### ")) {
                            return (
                              <h3 key={i} className="text-base font-medium mt-4 mb-2">
                                {line.replace("### ", "")}
                              </h3>
                            );
                          }
                          if (line.startsWith("- ") || line.startsWith("* ")) {
                            return (
                              <li key={i} className="ml-4">
                                {line.substring(2)}
                              </li>
                            );
                          }
                          if (line.trim() === "") {
                            return <br key={i} />;
                          }
                          return (
                            <p key={i} className="mb-2">
                              {line}
                            </p>
                          );
                        })}
                      </div>
                      {/* AI Evaluation Panel for RAG sections */}
                      {section.aiEval && (
                        <AIEvalPanel eval={section.aiEval} sectionType="old" />
                      )}
                      {/* Debug Panel */}
                      {debugMode && (
                        <div className="mt-4">
                          <DebugPanel section={section} sectionType="old" />
                        </div>
                      )}
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </TabsContent>

            {/* Template Sections Tab */}
            <TabsContent value="templates" className="space-y-4">
              <div className="text-sm text-muted-foreground mb-4">
                Standard clauses from CESC templates (cannot be modified).
              </div>
              <Accordion type="multiple" className="space-y-3">
                {sections.rules.map((section) => (
                  <AccordionItem
                    key={section.name}
                    value={section.name}
                    className="border rounded-lg overflow-hidden"
                  >
                    <AccordionTrigger className="px-4 py-3 hover:no-underline hover:bg-muted/50">
                      <div className="flex items-center gap-3">
                        <FileCheck className="h-5 w-5 text-green-500 shrink-0" />
                        <span className="font-medium">{section.name}</span>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="px-4 pb-4">
                      <div className="prose prose-sm dark:prose-invert max-w-none p-4 bg-muted/30 rounded-md">
                        {section.content.split("\n").map((line, i) => {
                          if (line.startsWith("## ")) {
                            return (
                              <h2 key={i} className="text-lg font-semibold mt-0 mb-3">
                                {line.replace("## ", "")}
                              </h2>
                            );
                          }
                          if (line.startsWith("- ") || line.match(/^\d+\./)) {
                            return (
                              <li key={i} className="ml-4">
                                {line.replace(/^[-\d.]+\s*/, "")}
                              </li>
                            );
                          }
                          if (line.trim() === "") {
                            return <br key={i} />;
                          }
                          return (
                            <p key={i} className="mb-2">
                              {line}
                            </p>
                          );
                        })}
                      </div>
                      {/* Debug Panel */}
                      {debugMode && (
                        <div className="mt-4">
                          <DebugPanel section={section} sectionType="rules" />
                        </div>
                      )}
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </TabsContent>
          </Tabs>

          {/* Download Section */}
          <Separator className="my-8" />
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Download className="h-5 w-5" />
                Download RFP
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">
                    RFP Title
                  </label>
                  <Input
                    value={rfpTitle}
                    onChange={(e) => setRfpTitle(e.target.value)}
                    placeholder="Enter RFP title"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    This will appear on the cover page
                  </p>
                </div>
                <div className="flex items-end">
                  <Button
                    className="w-full"
                    size="lg"
                    disabled={approvedCount < totalRequired}
                    onClick={handleDownload}
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Download RFP (.docx)
                  </Button>
                </div>
              </div>
              {approvedCount < totalRequired && (
                <p className="text-sm text-muted-foreground">
                  Approve all {totalRequired} critical sections to enable download
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </ScrollArea>

      {/* Fixed Bottom CTA - Shows when all approved */}
      {approvedCount === totalRequired && (
        <div className="fixed bottom-0 left-0 right-0 bg-green-600 text-white border-t shadow-lg animate-in slide-in-from-bottom duration-300">
          <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-white/20 flex items-center justify-center">
                <CheckCircle2 className="h-6 w-6" />
              </div>
              <div>
                <p className="font-semibold">All sections approved!</p>
                <p className="text-sm text-green-100">Your RFP is ready to download</p>
              </div>
            </div>
            <Button
              size="lg"
              variant="secondary"
              className="bg-white text-green-700 hover:bg-green-50 font-semibold shadow-md"
              onClick={handleDownload}
            >
              <Download className="h-5 w-5 mr-2" />
              Download RFP (.docx)
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
