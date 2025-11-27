"use client";

import { DocumentDiff } from "@/lib/types";
import DiffSummary from "./DiffSummary";
import ChangeCard from "./ChangeCard";

interface DiffViewProps {
  diff: DocumentDiff;
}

export default function DiffView({ diff }: DiffViewProps) {
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
      <div className="px-6 py-4 space-y-4">
        {diff.changes.map((change, index) => {
          // Ensure we have a valid key - use id if available, otherwise generate one
          const key = change.id || `change-${change.section_id}-${change.change_type}-${index}`;
          return <ChangeCard key={key} change={change} index={index} />;
        })}
      </div>
    </div>
  );
}
