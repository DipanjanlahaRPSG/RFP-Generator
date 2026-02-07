"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import {
  Brain,
  Database,
  FileCheck,
  Clock,
  Coins,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Sparkles,
  TrendingUp,
  AlertTriangle,
} from "lucide-react";
import { AIEvalScores } from "@/lib/types";

interface AIEvalPanelProps {
  eval: AIEvalScores;
  sectionType: "new" | "old" | "rules";
  compact?: boolean;
}

export function AIEvalPanel({ eval: aiEval, sectionType, compact = false }: AIEvalPanelProps) {
  const [expanded, setExpanded] = useState(false);

  // Determine quality level
  const getQualityLevel = (coherence: number) => {
    if (coherence >= 8.5) return { label: "Excellent", color: "bg-green-500", textColor: "text-green-700" };
    if (coherence >= 7.5) return { label: "Good", color: "bg-blue-500", textColor: "text-blue-700" };
    if (coherence >= 6.5) return { label: "Fair", color: "bg-amber-500", textColor: "text-amber-700" };
    return { label: "Needs Review", color: "bg-red-500", textColor: "text-red-700" };
  };

  const quality = getQualityLevel(aiEval.coherence);

  // Compact inline badges view
  if (compact) {
    return (
      <div className="flex items-center gap-2 flex-wrap">
        <Badge variant="outline" className="text-xs gap-1">
          <Brain className="h-3 w-3" />
          {aiEval.coherence.toFixed(1)}/10
        </Badge>
        {sectionType !== "rules" && (
          <Badge variant="outline" className="text-xs gap-1">
            <Database className="h-3 w-3" />
            {aiEval.ragConfidence}%
          </Badge>
        )}
        <Badge variant="outline" className="text-xs gap-1">
          <FileCheck className="h-3 w-3" />
          {aiEval.formatCompliance}%
        </Badge>
      </div>
    );
  }

  return (
    <div className="bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
      {/* Header - Always visible */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors rounded-lg"
      >
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
            <Sparkles className="h-4 w-4 text-white" />
          </div>
          <div className="text-left">
            <div className="text-sm font-medium flex items-center gap-2">
              AI Evaluation
              <Badge className={`${quality.color} text-white text-xs`}>
                {quality.label}
              </Badge>
            </div>
            <div className="text-xs text-muted-foreground">
              Langfuse quality metrics
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {/* Quick stats */}
          <div className="hidden sm:flex items-center gap-2 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <Brain className="h-3 w-3" />
              {aiEval.coherence.toFixed(1)}
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <Database className="h-3 w-3" />
              {aiEval.ragConfidence}%
            </span>
          </div>
          {expanded ? (
            <ChevronUp className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          )}
        </div>
      </button>

      {/* Expanded content */}
      {expanded && (
        <div className="px-4 pb-4 space-y-4">
          <Separator />

          {/* Main metrics grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Coherence Score */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="flex items-center gap-1.5 text-muted-foreground">
                  <Brain className="h-4 w-4" />
                  Coherence
                </span>
                <span className={`font-semibold ${quality.textColor}`}>
                  {aiEval.coherence.toFixed(1)}/10
                </span>
              </div>
              <Progress value={aiEval.coherence * 10} className="h-2" />
              <p className="text-xs text-muted-foreground">
                LLM-as-judge quality score
              </p>
            </div>

            {/* RAG Confidence */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="flex items-center gap-1.5 text-muted-foreground">
                  <Database className="h-4 w-4" />
                  RAG Confidence
                </span>
                <span className={`font-semibold ${aiEval.ragConfidence >= 85 ? "text-green-700" : aiEval.ragConfidence >= 70 ? "text-amber-700" : "text-red-700"}`}>
                  {aiEval.ragConfidence}%
                </span>
              </div>
              <Progress value={aiEval.ragConfidence} className="h-2" />
              <p className="text-xs text-muted-foreground">
                Attribution to corpus
              </p>
            </div>

            {/* Format Compliance */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="flex items-center gap-1.5 text-muted-foreground">
                  <FileCheck className="h-4 w-4" />
                  Format
                </span>
                <span className={`font-semibold ${aiEval.formatCompliance === 100 ? "text-green-700" : "text-amber-700"}`}>
                  {aiEval.formatCompliance}%
                </span>
              </div>
              <Progress value={aiEval.formatCompliance} className="h-2" />
              <p className="text-xs text-muted-foreground">
                Template compliance
              </p>
            </div>
          </div>

          {/* Sources used */}
          {aiEval.sources && aiEval.sources.length > 0 && (
            <div className="space-y-2">
              <div className="text-sm font-medium flex items-center gap-1.5">
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
                RAG Sources Used
              </div>
              <div className="space-y-1">
                {aiEval.sources.map((source, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between text-xs bg-white dark:bg-slate-800 rounded px-3 py-2 border"
                  >
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-primary">
                        {source.docName}
                      </span>
                      <span className="text-muted-foreground">
                        → {source.section}
                      </span>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {source.similarity}% match
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Performance metrics */}
          <div className="flex items-center gap-4 text-xs text-muted-foreground pt-2 border-t">
            {aiEval.latencyMs && (
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {(aiEval.latencyMs / 1000).toFixed(1)}s latency
              </span>
            )}
            {aiEval.tokenCount && (
              <span className="flex items-center gap-1">
                <Coins className="h-3 w-3" />
                {aiEval.tokenCount} tokens
              </span>
            )}
            <Button
              variant="ghost"
              size="sm"
              className="h-6 text-xs ml-auto"
              onClick={(e) => {
                e.stopPropagation();
                // In real app, this would open Langfuse trace
                alert("Opens Langfuse trace view for this generation");
              }}
            >
              <ExternalLink className="h-3 w-3 mr-1" />
              View in Langfuse
            </Button>
          </div>

          {/* Quality warnings */}
          {(aiEval.coherence < 7.5 || aiEval.ragConfidence < 80) && (
            <div className="flex items-start gap-2 p-3 bg-amber-50 dark:bg-amber-950 rounded-md border border-amber-200 dark:border-amber-800">
              <AlertTriangle className="h-4 w-4 text-amber-600 mt-0.5" />
              <div className="text-xs">
                <p className="font-medium text-amber-800 dark:text-amber-200">
                  Quality Review Recommended
                </p>
                <p className="text-amber-700 dark:text-amber-300 mt-0.5">
                  {aiEval.coherence < 7.5 && "Coherence score below target (8.0). "}
                  {aiEval.ragConfidence < 80 && "RAG confidence below target (85%). "}
                  Consider regenerating with more specific context.
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Summary component for header
interface AIEvalSummaryProps {
  sections: { aiEval?: AIEvalScores }[];
}

export function AIEvalSummary({ sections }: AIEvalSummaryProps) {
  const validEvals = sections.filter(s => s.aiEval).map(s => s.aiEval!);

  if (validEvals.length === 0) return null;

  const avgCoherence = validEvals.reduce((sum, e) => sum + e.coherence, 0) / validEvals.length;
  const avgRagConfidence = validEvals.reduce((sum, e) => sum + e.ragConfidence, 0) / validEvals.length;
  const avgFormat = validEvals.reduce((sum, e) => sum + e.formatCompliance, 0) / validEvals.length;

  return (
    <div className="flex items-center gap-4 text-sm">
      <div className="flex items-center gap-1.5">
        <Brain className="h-4 w-4 text-violet-500" />
        <span className="text-muted-foreground">Avg Quality:</span>
        <span className="font-semibold">{avgCoherence.toFixed(1)}/10</span>
      </div>
      <div className="flex items-center gap-1.5">
        <Database className="h-4 w-4 text-blue-500" />
        <span className="text-muted-foreground">RAG:</span>
        <span className="font-semibold">{avgRagConfidence.toFixed(0)}%</span>
      </div>
      <div className="flex items-center gap-1.5">
        <FileCheck className="h-4 w-4 text-green-500" />
        <span className="text-muted-foreground">Format:</span>
        <span className="font-semibold">{avgFormat.toFixed(0)}%</span>
      </div>
    </div>
  );
}
