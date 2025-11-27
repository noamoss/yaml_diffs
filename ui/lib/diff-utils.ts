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

    // Mark modified lines (lines that appear in both but with different content)
    // This is a simplified approach - for true modified detection, we'd need
    // more sophisticated matching. For now, we'll treat adjacent removed+added
    // as potentially modified.
    for (let i = 0; i < oldLines.length; i++) {
      const oldLine = oldLines[i];
      if (oldLine.type === "removed" && i + 1 < oldLines.length) {
        const nextOldLine = oldLines[i + 1];
        // Look for corresponding added line in newLines
        for (let j = 0; j < newLines.length; j++) {
          const newLine = newLines[j];
          if (newLine.type === "added" && newLine.newLineNumber === oldLineNum) {
            // Mark as modified if content is similar but different
            oldLine.type = "modified";
            newLine.type = "modified";
            oldLine.newLineNumber = newLine.newLineNumber;
            newLine.oldLineNumber = oldLine.oldLineNumber;
            break;
          }
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
