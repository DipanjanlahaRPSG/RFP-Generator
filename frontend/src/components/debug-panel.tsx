"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "@/components/ui/accordion";
import {
    Brain,
    Database,
    FileText,
    Sparkles,
    Clock,
    Zap,
    FileSearch,
} from "lucide-react";
import { Section } from "@/lib/types";

interface DebugPanelProps {
    section: Section;
    sectionType: "new" | "old" | "rules";
}

export function DebugPanel({ section, sectionType }: DebugPanelProps) {
    const aiEval = section.aiEval;

    // Determine generation method
    const getGenerationMethod = () => {
        switch (sectionType) {
            case "new":
                return {
                    icon: Brain,
                    label: "AI Generated",
                    color: "text-purple-600",
                    bgColor: "bg-purple-50 dark:bg-purple-950",
                    borderColor: "border-purple-200 dark:border-purple-800",
                    description: "Generated using GPT-4o based on your input",
                };
            case "old":
                return {
                    icon: Database,
                    label: "RAG Retrieved",
                    color: "text-blue-600",
                    bgColor: "bg-blue-50 dark:bg-blue-950",
                    borderColor: "border-blue-200 dark:border-blue-800",
                    description: "Retrieved from historical RFPs using semantic search",
                };
            case "rules":
                return {
                    icon: FileText,
                    label: "Template",
                    color: "text-green-600",
                    bgColor: "bg-green-50 dark:bg-green-950",
                    borderColor: "border-green-200 dark:border-green-800",
                    description: "Fixed template from CESC standards",
                };
        }
    };

    const method = getGenerationMethod();
    const Icon = method.icon;

    return (
        <Card className={`${method.borderColor} border-2`}>
            <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-amber-500" />
                    Debug Information
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                {/* Generation Method */}
                <div className={`p-3 rounded-lg ${method.bgColor} ${method.borderColor} border`}>
                    <div className="flex items-center gap-2 mb-2">
                        <Icon className={`h-5 w-5 ${method.color}`} />
                        <span className={`font-semibold ${method.color}`}>{method.label}</span>
                    </div>
                    <p className="text-sm text-muted-foreground">{method.description}</p>
                </div>

                {/* Performance Metrics */}
                {aiEval && (
                    <div className="space-y-2">
                        <h4 className="text-sm font-semibold flex items-center gap-2">
                            <Zap className="h-4 w-4" />
                            Performance Metrics
                        </h4>
                        <div className="grid grid-cols-2 gap-2">
                            {aiEval.latencyMs !== undefined && (
                                <div className="p-2 bg-muted rounded-md">
                                    <div className="flex items-center gap-1 text-xs text-muted-foreground mb-1">
                                        <Clock className="h-3 w-3" />
                                        Latency
                                    </div>
                                    <div className="text-sm font-semibold">{aiEval.latencyMs}ms</div>
                                </div>
                            )}
                            {aiEval.tokenCount !== undefined && (
                                <div className="p-2 bg-muted rounded-md">
                                    <div className="flex items-center gap-1 text-xs text-muted-foreground mb-1">
                                        <FileText className="h-3 w-3" />
                                        Tokens
                                    </div>
                                    <div className="text-sm font-semibold">{aiEval.tokenCount}</div>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* RAG Sources */}
                {sectionType === "old" && aiEval?.sources && aiEval.sources.length > 0 && (
                    <div className="space-y-2">
                        <h4 className="text-sm font-semibold flex items-center gap-2">
                            <FileSearch className="h-4 w-4" />
                            RAG Sources ({aiEval.sources.length})
                        </h4>
                        <Accordion type="single" collapsible className="w-full">
                            {aiEval.sources.map((source, idx) => (
                                <AccordionItem key={idx} value={`source-${idx}`} className="border rounded-md mb-2">
                                    <AccordionTrigger className="px-3 py-2 hover:no-underline">
                                        <div className="flex items-center justify-between w-full pr-2">
                                            <span className="text-xs font-medium truncate">{source.docName}</span>
                                            <Badge variant="secondary" className="ml-2">
                                                {source.similarity}% match
                                            </Badge>
                                        </div>
                                    </AccordionTrigger>
                                    <AccordionContent className="px-3 pb-2">
                                        <div className="space-y-1 text-xs">
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">Section:</span>
                                                <span className="font-medium">{source.section}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">Similarity:</span>
                                                <span className="font-medium">{source.similarity}%</span>
                                            </div>
                                            {source.chunk && (
                                                <div className="mt-2 p-2 bg-muted rounded text-xs">
                                                    <div className="text-muted-foreground mb-1">Content Preview:</div>
                                                    <div className="line-clamp-3">{source.chunk}</div>
                                                </div>
                                            )}
                                        </div>
                                    </AccordionContent>
                                </AccordionItem>
                            ))}
                        </Accordion>
                    </div>
                )}

                {/* AI Evaluation Scores */}
                {aiEval && (
                    <div className="space-y-2">
                        <h4 className="text-sm font-semibold">AI Quality Scores</h4>
                        <div className="space-y-2">
                            <div>
                                <div className="flex justify-between text-xs mb-1">
                                    <span className="text-muted-foreground">Coherence</span>
                                    <span className="font-medium">{aiEval.coherence}/10</span>
                                </div>
                                <div className="h-2 bg-muted rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-blue-500 transition-all"
                                        style={{ width: `${(aiEval.coherence / 10) * 100}%` }}
                                    />
                                </div>
                            </div>
                            <div>
                                <div className="flex justify-between text-xs mb-1">
                                    <span className="text-muted-foreground">RAG Confidence</span>
                                    <span className="font-medium">{aiEval.ragConfidence}%</span>
                                </div>
                                <div className="h-2 bg-muted rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-green-500 transition-all"
                                        style={{ width: `${aiEval.ragConfidence}%` }}
                                    />
                                </div>
                            </div>
                            <div>
                                <div className="flex justify-between text-xs mb-1">
                                    <span className="text-muted-foreground">Format Compliance</span>
                                    <span className="font-medium">{aiEval.formatCompliance}%</span>
                                </div>
                                <div className="h-2 bg-muted rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-purple-500 transition-all"
                                        style={{ width: `${aiEval.formatCompliance}%` }}
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Assumptions (for NEW sections) */}
                {sectionType === "new" && section.assumptions && section.assumptions.length > 0 && (
                    <div className="space-y-2">
                        <h4 className="text-sm font-semibold">AI Assumptions</h4>
                        <ul className="space-y-1">
                            {section.assumptions.map((assumption, idx) => (
                                <li key={idx} className="text-xs text-muted-foreground flex items-start gap-2">
                                    <span className="text-amber-500 mt-0.5">•</span>
                                    <span>{assumption}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
