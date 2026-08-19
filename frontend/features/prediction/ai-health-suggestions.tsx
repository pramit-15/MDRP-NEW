"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sparkles,
  Heart,
  Activity,
  Brain,
  Apple,
  Dumbbell,
  Stethoscope,
  Moon,
  Target,
  CheckCircle2,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  Zap,
  Info,
  CheckSquare,
  Square,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { AISuggestionsResult, LifestyleSuggestion } from "@/types";

const CATEGORY_ICONS: Record<string, React.ElementType> = {
  "Diet & Nutrition": Apple,
  "Physical Activity": Dumbbell,
  "Routine Monitoring": Stethoscope,
  "Daily Habits & Wellness": Moon,
  "Daily Habits": Moon,
  Nutrition: Apple,
  Exercise: Dumbbell,
};

function getCategoryIcon(category: string, defaultIconName?: string): React.ElementType {
  if (CATEGORY_ICONS[category]) return CATEGORY_ICONS[category];
  if (defaultIconName === "Apple") return Apple;
  if (defaultIconName === "Dumbbell") return Dumbbell;
  if (defaultIconName === "Stethoscope") return Stethoscope;
  if (defaultIconName === "Moon") return Moon;
  return Activity;
}

function getPriorityBadge(priority: "High" | "Medium" | "Low") {
  switch (priority) {
    case "High":
      return (
        <Badge className="bg-red-500/10 text-red-600 border-red-200 dark:border-red-800 dark:text-red-400 text-[11px]">
          High Priority
        </Badge>
      );
    case "Medium":
      return (
        <Badge className="bg-amber-500/10 text-amber-600 border-amber-200 dark:border-amber-800 dark:text-amber-400 text-[11px]">
          Recommended
        </Badge>
      );
    case "Low":
    default:
      return (
        <Badge className="bg-emerald-500/10 text-emerald-600 border-emerald-200 dark:border-emerald-800 dark:text-emerald-400 text-[11px]">
          Maintenance
        </Badge>
      );
  }
}

interface AIHealthSuggestionsProps {
  suggestions?: AISuggestionsResult;
  isLoading?: boolean;
}

export function AIHealthSuggestions({ suggestions, isLoading }: AIHealthSuggestionsProps) {
  const [completedItems, setCompletedItems] = useState<Record<string, boolean>>({});
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  if (isLoading) {
    return (
      <Card className="border-blue-200/60 dark:border-blue-800/40 animate-pulse">
        <CardHeader>
          <div className="h-6 w-48 bg-muted rounded-md mb-2" />
          <div className="h-4 w-72 bg-muted rounded-md" />
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="h-20 bg-muted rounded-xl" />
          <div className="grid sm:grid-cols-2 gap-4">
            <div className="h-36 bg-muted rounded-xl" />
            <div className="h-36 bg-muted rounded-xl" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!suggestions || !suggestions.summary) {
    return null;
  }

  const toggleItem = (key: string) => {
    setCompletedItems((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const isAiPowered = suggestions.generated_by === "gemini_ai";

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="space-y-6"
    >
      <Card className="border-2 border-blue-500/20 bg-gradient-to-b from-blue-500/5 via-card to-card shadow-sm overflow-hidden">
        <CardHeader className="pb-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="flex items-center gap-2.5">
              <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-blue-600 to-emerald-500 flex items-center justify-center text-white shadow-sm shadow-blue-500/20">
                <Sparkles className="h-5 w-5" />
              </div>
              <div>
                <CardTitle className="text-lg flex items-center gap-2">
                  AI Health Insights & Suggestions
                </CardTitle>
                <CardDescription className="text-xs">
                  Personalized improvement strategies tailored to your biomarker & risk profile
                </CardDescription>
              </div>
            </div>

            <Badge variant="outline" className="self-start sm:self-center gap-1.5 py-1 px-2.5 text-xs font-normal border-blue-200 dark:border-blue-800 bg-background/80">
              <Sparkles className="h-3.5 w-3.5 text-blue-500" />
              {isAiPowered ? "Gemini 2.0 AI" : "Clinical Rule Engine"}
            </Badge>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Executive Risk Summary */}
          <div className="p-4 sm:p-5 rounded-xl bg-card border border-border/80 shadow-2xs space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
              <ShieldCheck className="h-4 w-4 text-blue-600" />
              <span>Risk Understanding & Assessment Overview</span>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {suggestions.summary}
            </p>

            {/* Disease breakdown pills */}
            {suggestions.risk_breakdown && (
              <div className="grid sm:grid-cols-3 gap-3 pt-2">
                {suggestions.risk_breakdown.heart && (
                  <div className="p-3 rounded-lg bg-red-500/5 border border-red-200/40 dark:border-red-900/30 text-xs space-y-1">
                    <div className="font-semibold text-red-600 dark:text-red-400 flex items-center gap-1.5">
                      <Heart className="h-3.5 w-3.5" /> Heart Risk
                    </div>
                    <p className="text-muted-foreground leading-normal">
                      {suggestions.risk_breakdown.heart}
                    </p>
                  </div>
                )}
                {suggestions.risk_breakdown.diabetes && (
                  <div className="p-3 rounded-lg bg-amber-500/5 border border-amber-200/40 dark:border-amber-900/30 text-xs space-y-1">
                    <div className="font-semibold text-amber-600 dark:text-amber-400 flex items-center gap-1.5">
                      <Activity className="h-3.5 w-3.5" /> Diabetes Risk
                    </div>
                    <p className="text-muted-foreground leading-normal">
                      {suggestions.risk_breakdown.diabetes}
                    </p>
                  </div>
                )}
                {suggestions.risk_breakdown.kidney && (
                  <div className="p-3 rounded-lg bg-blue-500/5 border border-blue-200/40 dark:border-blue-900/30 text-xs space-y-1">
                    <div className="font-semibold text-blue-600 dark:text-blue-400 flex items-center gap-1.5">
                      <Brain className="h-3.5 w-3.5" /> Kidney Health
                    </div>
                    <p className="text-muted-foreground leading-normal">
                      {suggestions.risk_breakdown.kidney}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Top Priority Action Banner */}
          {suggestions.top_priority && (
            <div className="p-4 rounded-xl bg-gradient-to-r from-amber-500/10 via-orange-500/10 to-amber-500/5 border border-amber-300/60 dark:border-amber-700/40 flex items-start gap-3.5">
              <div className="h-9 w-9 rounded-lg bg-amber-500/20 text-amber-700 dark:text-amber-400 flex items-center justify-center shrink-0 mt-0.5">
                <Target className="h-5 w-5" />
              </div>
              <div className="space-y-0.5">
                <span className="text-xs font-bold uppercase tracking-wider text-amber-700 dark:text-amber-400">
                  Top Priority Health Action
                </span>
                <p className="text-sm font-medium text-foreground leading-snug">
                  {suggestions.top_priority}
                </p>
              </div>
            </div>
          )}

          {/* Categorized Suggestions Grid */}
          {suggestions.lifestyle_suggestions && suggestions.lifestyle_suggestions.length > 0 && (
            <div className="space-y-3">
              <div className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                Actionable Improvement Plan
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                {suggestions.lifestyle_suggestions.map((item: LifestyleSuggestion, idx: number) => {
                  const Icon = getCategoryIcon(item.category, item.icon);
                  const isExpanded = expandedIndex === idx;

                  return (
                    <div
                      key={idx}
                      className="p-4 rounded-xl border border-border/80 bg-card hover:border-blue-300 dark:hover:border-blue-800 transition-all flex flex-col justify-between"
                    >
                      <div className="space-y-2.5">
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex items-center gap-2">
                            <div className="h-8 w-8 rounded-lg bg-blue-600/10 text-blue-600 dark:text-blue-400 flex items-center justify-center shrink-0">
                              <Icon className="h-4 w-4" />
                            </div>
                            <div>
                              <span className="text-xs text-muted-foreground font-medium block">
                                {item.category}
                              </span>
                              <h4 className="text-sm font-semibold leading-tight">
                                {item.title}
                              </h4>
                            </div>
                          </div>
                          {getPriorityBadge(item.priority)}
                        </div>

                        <p className="text-xs text-muted-foreground leading-relaxed pt-1">
                          {item.advice}
                        </p>

                        {/* Action Checklist */}
                        {item.action_items && item.action_items.length > 0 && (
                          <div className="space-y-1.5 pt-2 border-t border-border/40">
                            <span className="text-[11px] font-semibold text-foreground/80 block mb-1">
                              Action Items:
                            </span>
                            {item.action_items.map((action: string, aIdx: number) => {
                              const actionKey = `${idx}-${aIdx}`;
                              const isChecked = !!completedItems[actionKey];

                              return (
                                <button
                                  key={aIdx}
                                  type="button"
                                  onClick={() => toggleItem(actionKey)}
                                  className="w-full flex items-start gap-2 text-left p-1.5 rounded-lg hover:bg-muted/50 transition-colors group cursor-pointer"
                                >
                                  {isChecked ? (
                                    <CheckSquare className="h-3.5 w-3.5 text-emerald-500 shrink-0 mt-0.5" />
                                  ) : (
                                    <Square className="h-3.5 w-3.5 text-muted-foreground group-hover:text-foreground shrink-0 mt-0.5" />
                                  )}
                                  <span
                                    className={`text-xs leading-tight transition-all ${
                                      isChecked
                                        ? "line-through text-muted-foreground opacity-70"
                                        : "text-foreground"
                                    }`}
                                  >
                                    {action}
                                  </span>
                                </button>
                              );
                            })}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Clinical Disclaimer */}
          <div className="flex items-start gap-2.5 p-3 rounded-lg bg-muted/40 border border-border/40 text-muted-foreground text-xs leading-relaxed">
            <Info className="h-4 w-4 shrink-0 text-muted-foreground mt-0.5" />
            <p>
              {suggestions.disclaimer ||
                "These suggestions are AI-generated for general wellness purposes and do not replace formal clinical consultation. Please review with your doctor before implementing major dietary or physical activity changes."}
            </p>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
