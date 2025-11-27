"use client";

import { DocumentDiff } from "@/lib/types";
import { useDiscussionsStore } from "@/stores/discussions";

interface ExportButtonProps {
  diff: DocumentDiff | null;
  disabled?: boolean;
}

export default function ExportButton({ diff, disabled }: ExportButtonProps) {
  const discussions = useDiscussionsStore((state) => state.discussions);

  const handleExport = () => {
    if (!diff) return;

    const exportData = {
      exported_at: new Date().toISOString(),
      diff,
      discussions,
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `yaml-diff-${new Date().toISOString().replace(/[:.]/g, "-")}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <button
      onClick={handleExport}
      disabled={disabled || !diff}
      className="px-3 sm:px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors text-sm sm:text-base"
    >
      <span className="hidden sm:inline">Export JSON</span>
      <span className="sm:hidden">Export</span>
    </button>
  );
}
