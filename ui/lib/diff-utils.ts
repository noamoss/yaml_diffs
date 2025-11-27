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
