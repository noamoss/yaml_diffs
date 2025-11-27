"use client";

import { DocumentDiff } from "@/lib/types";

interface DiffSummaryProps {
  diff: DocumentDiff;
}

export default function DiffSummary({ diff }: DiffSummaryProps) {
  return (
    <div className="bg-gray-50 border-b border-gray-200 px-4 sm:px-6 py-4">
      <div className="flex flex-wrap items-center gap-3 sm:gap-6 text-sm">
        <span className="font-semibold text-gray-700">Changes Summary:</span>
        <div className="flex items-center gap-2">
          <span className="text-green-600 font-medium">
            +{diff.added_count} added
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-red-600 font-medium">
            -{diff.deleted_count} removed
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-yellow-600 font-medium">
            ~{diff.modified_count} modified
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-purple-600 font-medium">
            ↔{diff.moved_count} moved
          </span>
        </div>
        <div className="ml-auto text-gray-500">
          Total: {diff.changes.length} changes
        </div>
      </div>
    </div>
  );
}
