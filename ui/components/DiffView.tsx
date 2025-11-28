"use client";

import { useState, useEffect } from "react";
import { DocumentDiff } from "@/lib/types";
import DiffSummary from "./DiffSummary";
import ChangeCard from "./ChangeCard";
import SplitDiffView from "./SplitDiffView";

interface DiffViewProps {
  diff: DocumentDiff;
  oldYaml: string;
  newYaml: string;
}

type ViewType = "split" | "cards";

const VIEW_STORAGE_KEY = "yaml-diff-view-preference";

export default function DiffView({ diff, oldYaml, newYaml }: DiffViewProps) {
  const [viewType, setViewType] = useState<ViewType>("split");

  // Load view preference from localStorage
  useEffect(() => {
    const saved = localStorage.getItem(VIEW_STORAGE_KEY);
    if (saved === "split" || saved === "cards") {
      setViewType(saved);
    }
  }, []);

  // Save view preference to localStorage
  const handleViewChange = (newView: ViewType) => {
    setViewType(newView);
    localStorage.setItem(VIEW_STORAGE_KEY, newView);
  };

  if (diff.changes.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">No changes detected between the two versions.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <DiffSummary diff={diff} />

      {/* View toggle */}
      <div className="border-b border-gray-200 bg-white">
        <div className="px-4 sm:px-6">
          <nav className="flex space-x-8">
            <button
              onClick={() => handleViewChange("split")}
              className={`py-3 px-1 border-b-2 font-medium text-sm transition-colors ${
                viewType === "split"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              Split View
            </button>
            <button
              onClick={() => handleViewChange("cards")}
              className={`py-3 px-1 border-b-2 font-medium text-sm transition-colors ${
                viewType === "cards"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              Cards View
            </button>
          </nav>
        </div>
      </div>

      {/* View content */}
      {viewType === "split" ? (
        <SplitDiffView oldYaml={oldYaml} newYaml={newYaml} diff={diff} />
      ) : (
        <div className="px-6 py-4 space-y-4">
          {diff.changes
            .slice() // Create a copy to avoid mutating original
            .sort((a, b) => {
              // Sort by new line number, fall back to old line number for deleted sections
              const aLine = a.new_line_number ?? a.old_line_number ?? Infinity;
              const bLine = b.new_line_number ?? b.old_line_number ?? Infinity;
              return aLine - bLine;
            })
            .map((change, index) => {
              // Ensure we have a valid key - use id if available, otherwise generate one
              const key = change.id || `change-${change.section_id}-${change.change_type}-${index}`;
              return (
                <ChangeCard
                  key={key}
                  change={change}
                  index={index}
                  oldYaml={oldYaml}
                  newYaml={newYaml}
                />
              );
            })}
        </div>
      )}
    </div>
  );
}
