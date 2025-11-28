/** Utilities for character-level diff highlighting. */

// Note: diff-match-patch is loaded dynamically in the component to avoid
// Turbopack/Next.js CommonJS module issues

export interface DiffChunk {
  text: string;
  type: "added" | "removed" | "unchanged";
}

/**
 * Compute character-level diff between two strings.
 * Returns chunks with their change type for highlighting.
 * Uses dynamic import to load diff-match-patch (CommonJS module).
 */
export async function computeCharDiff(oldText: string, newText: string): Promise<DiffChunk[]> {
  if (typeof window === "undefined") {
    // Server-side fallback
    return [{ text: oldText || newText || "", type: "unchanged" }];
  }

  try {
    // Dynamic import for CommonJS module compatibility
    const DiffMatchPatchModule = await import("diff-match-patch");
    const DiffMatchPatch = (DiffMatchPatchModule as any).default || DiffMatchPatchModule;
    const dmp = new DiffMatchPatch();

    const diffs = dmp.diff_main(oldText, newText);
    dmp.diff_cleanupSemantic(diffs);

    const chunks: DiffChunk[] = [];

    for (const [operation, text] of diffs) {
      if (operation === 0) {
        // Unchanged
        chunks.push({ text, type: "unchanged" });
      } else if (operation === -1) {
        // Removed
        chunks.push({ text, type: "removed" });
      } else if (operation === 1) {
        // Added
        chunks.push({ text, type: "added" });
      }
    }

    return chunks;
  } catch (error) {
    // Fallback on error
    console.error("Error computing diff:", error);
    return [{ text: oldText || newText || "", type: "unchanged" }];
  }
}

/**
 * Format marker path as a readable string.
 */
export function formatMarkerPath(path: string[] | null): string {
  if (!path || path.length === 0) {
    return "(root)";
  }
  return path.join(" → ");
}

/**
 * Line-level diff information for a single line.
 */
export interface LineDiff {
  lineNumber: number; // 1-indexed
  content: string;
  type: "added" | "removed" | "unchanged" | "modified";
  oldLineNumber?: number; // For modified/removed lines in old file
  newLineNumber?: number; // For modified/added lines in new file
}

/**
 * Compute line-by-line diff between two texts.
 * Returns arrays of line diffs for both old and new versions.
 * Uses dynamic import to load diff-match-patch (CommonJS module).
 */
export async function computeLineDiff(
  oldText: string,
  newText: string
): Promise<{ oldLines: LineDiff[]; newLines: LineDiff[] }> {
  if (typeof window === "undefined") {
    // Server-side fallback
    const oldLines = oldText.split("\n").map((line, i) => ({
      lineNumber: i + 1,
      content: line,
      type: "unchanged" as const,
      oldLineNumber: i + 1,
    }));
    const newLines = newText.split("\n").map((line, i) => ({
      lineNumber: i + 1,
      content: line,
      type: "unchanged" as const,
      newLineNumber: i + 1,
    }));
    return { oldLines, newLines };
  }

  try {
    // Dynamic import for CommonJS module compatibility
    const DiffMatchPatchModule = await import("diff-match-patch");
    const DiffMatchPatch = (DiffMatchPatchModule as any).default || DiffMatchPatchModule;
    const dmp = new DiffMatchPatch();

    const diffs = dmp.diff_main(oldText, newText);
    dmp.diff_cleanupSemantic(diffs);

    const oldLines: LineDiff[] = [];
    const newLines: LineDiff[] = [];

    let oldLineNum = 1;
    let newLineNum = 1;

    for (const [operation, text] of diffs) {
      const lines = text.split("\n");
      // Remove empty last line if text doesn't end with newline
      if (text && !text.endsWith("\n") && lines.length > 0) {
        // Last line is not empty, keep it
      } else if (lines.length > 0 && lines[lines.length - 1] === "") {
        // Remove trailing empty line
        lines.pop();
      }

      if (operation === 0) {
        // Unchanged
        for (const line of lines) {
          oldLines.push({
            lineNumber: oldLineNum,
            content: line,
            type: "unchanged",
            oldLineNumber: oldLineNum,
            newLineNumber: newLineNum,
          });
          newLines.push({
            lineNumber: newLineNum,
            content: line,
            type: "unchanged",
            oldLineNumber: oldLineNum,
            newLineNumber: newLineNum,
          });
          oldLineNum++;
          newLineNum++;
        }
      } else if (operation === -1) {
        // Removed
        for (const line of lines) {
          oldLines.push({
            lineNumber: oldLineNum,
            content: line,
            type: "removed",
            oldLineNumber: oldLineNum,
          });
          oldLineNum++;
        }
      } else if (operation === 1) {
        // Added
        for (const line of lines) {
          newLines.push({
            lineNumber: newLineNum,
            content: line,
            type: "added",
            newLineNumber: newLineNum,
          });
          newLineNum++;
        }
      }
    }

    // Post-process to better match lines and avoid false positives
    // Comprehensive matching: match ALL identical lines regardless of position

    // Build maps of all lines by exact content (for precise matching)
    const oldContentMap = new Map<string, number[]>();
    const newContentMap = new Map<string, number[]>();

    oldLines.forEach((line, idx) => {
      const content = line.content;
      if (!oldContentMap.has(content)) {
        oldContentMap.set(content, []);
      }
      oldContentMap.get(content)!.push(idx);
    });

    newLines.forEach((line, idx) => {
      const content = line.content;
      if (!newContentMap.has(content)) {
        newContentMap.set(content, []);
      }
      newContentMap.get(content)!.push(idx);
    });

    // Match all identical lines: for each content that appears in both versions,
    // match removed lines with added lines
    const matchedOldIndices = new Set<number>();
    const matchedNewIndices = new Set<number>();

    // First pass: match removed lines with added lines (greedy, prefer closest positions)
    for (const [content, oldIndices] of oldContentMap.entries()) {
      const newIndices = newContentMap.get(content);
      if (!newIndices || newIndices.length === 0) continue;

      // For each old line with this content that's marked as removed/modified
      for (const oldIdx of oldIndices) {
        if (matchedOldIndices.has(oldIdx)) continue;

        const oldLine = oldLines[oldIdx];
        if (oldLine.type !== "removed" && oldLine.type !== "modified") continue;

        // Find best matching new line (prefer closest position, prefer added over modified)
        let bestMatch: number | null = null;
        let bestScore = Infinity;

        for (const newIdx of newIndices) {
          if (matchedNewIndices.has(newIdx)) continue;

          const newLine = newLines[newIdx];
          if (newLine.type !== "added" && newLine.type !== "modified") continue;

          // Score: distance + preference for added over modified
          const distance = Math.abs(newIdx - oldIdx);
          const typePenalty = newLine.type === "added" ? 0 : 1000;
          const score = distance + typePenalty;

          if (score < bestScore) {
            bestScore = score;
            bestMatch = newIdx;
          }
        }

        if (bestMatch !== null) {
          const newLine = newLines[bestMatch];
          // Mark both as unchanged and link them
          oldLine.type = "unchanged";
          newLine.type = "unchanged";
          oldLine.newLineNumber = newLine.lineNumber;
          newLine.oldLineNumber = oldLine.lineNumber;

          matchedOldIndices.add(oldIdx);
          matchedNewIndices.add(bestMatch);
        }
      }
    }

    // Second pass: catch any remaining unmatched lines (for cases where order matters less)
    for (const [content, newIndices] of newContentMap.entries()) {
      const oldIndices = oldContentMap.get(content);
      if (!oldIndices || oldIndices.length === 0) continue;

      // For each new line with this content that's marked as added/modified
      for (const newIdx of newIndices) {
        if (matchedNewIndices.has(newIdx)) continue;

        const newLine = newLines[newIdx];
        if (newLine.type !== "added" && newLine.type !== "modified") continue;

        // Find best matching old line
        let bestMatch: number | null = null;
        let bestScore = Infinity;

        for (const oldIdx of oldIndices) {
          if (matchedOldIndices.has(oldIdx)) continue;

          const oldLine = oldLines[oldIdx];
          if (oldLine.type !== "removed" && oldLine.type !== "modified") continue;

          const distance = Math.abs(oldIdx - newIdx);
          const typePenalty = oldLine.type === "removed" ? 0 : 1000;
          const score = distance + typePenalty;

          if (score < bestScore) {
            bestScore = score;
            bestMatch = oldIdx;
          }
        }

        if (bestMatch !== null) {
          const oldLine = oldLines[bestMatch];
          // Mark both as unchanged and link them
          oldLine.type = "unchanged";
          newLine.type = "unchanged";
          oldLine.newLineNumber = newLine.lineNumber;
          newLine.oldLineNumber = oldLine.lineNumber;

          matchedOldIndices.add(bestMatch);
          matchedNewIndices.add(newIdx);
        }
      }
    }

    return { oldLines, newLines };
  } catch (error) {
    // Fallback on error
    console.error("Error computing line diff:", error);
    const oldLines = oldText.split("\n").map((line, i) => ({
      lineNumber: i + 1,
      content: line,
      type: "unchanged" as const,
      oldLineNumber: i + 1,
    }));
    const newLines = newText.split("\n").map((line, i) => ({
      lineNumber: i + 1,
      content: line,
      type: "unchanged" as const,
      newLineNumber: i + 1,
    }));
    return { oldLines, newLines };
  }
}
