"use client";

import React from "react";
import { RecommendationResponse } from "@/types/coach";
import { useCoachStore } from "@/lib/store";
import { CheckSquare, Square, ListTodo } from "lucide-react";

interface ActionChecklistCardProps {
  data: RecommendationResponse;
}

export const ActionChecklistCard: React.FC<ActionChecklistCardProps> = ({ data }) => {
  const { completedChecklistItems, toggleChecklistItem } = useCoachStore();

  const items =
    data.explanation.explanation.priority_checklist?.length > 0
      ? data.explanation.explanation.priority_checklist
      : data.actionable_checklist;

  const completedCount = items.filter((item) => completedChecklistItems[item]).length;
  const progressPct = items.length > 0 ? Math.round((completedCount / items.length) * 100) : 0;

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 sm:p-5 shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            <ListTodo className="w-4 h-4" />
          </div>
          <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wide">
            In-Game Action Checklist
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-emerald-400 font-bold">
            {completedCount} / {items.length} Done ({progressPct}%)
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full h-1.5 bg-slate-950 rounded-full overflow-hidden mb-4 border border-slate-800">
        <div
          style={{ width: `${progressPct}%` }}
          className="h-full bg-emerald-500 transition-all duration-300 rounded-full"
        />
      </div>

      {/* Checklist Items */}
      <div className="space-y-2">
        {items.map((item, idx) => {
          const isDone = Boolean(completedChecklistItems[item]);
          return (
            <button
              key={idx}
              type="button"
              onClick={() => toggleChecklistItem(item)}
              className={`w-full flex items-start gap-3 p-3 rounded-xl border text-left transition-all ${
                isDone
                  ? "bg-slate-950/40 border-slate-800/60 text-slate-500 line-through"
                  : "bg-slate-950 border-slate-800 hover:border-amber-500/50 text-slate-200"
              }`}
            >
              <div className="mt-0.5 shrink-0 text-amber-400">
                {isDone ? (
                  <CheckSquare className="w-4 h-4 text-emerald-400" />
                ) : (
                  <Square className="w-4 h-4 text-slate-600 hover:text-amber-400" />
                )}
              </div>
              <div className="flex-1 text-xs leading-relaxed font-medium">
                <span className="font-mono text-amber-400 font-bold mr-1.5">{idx + 1}.</span>
                {item}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
