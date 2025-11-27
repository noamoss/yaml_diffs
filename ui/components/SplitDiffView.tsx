"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { EditorView, lineNumbers, Decoration } from "@codemirror/view";
import { EditorState, Extension, Range } from "@codemirror/state";
import { syntaxHighlighting, defaultHighlightStyle } from "@codemirror/language";
import { yaml } from "@codemirror/lang-yaml";
import { DocumentDiff, DiffResult } from "@/lib/types";
import { computeLineDiff, LineDiff } from "@/lib/diff-utils";
import ChangePopover from "./ChangePopover";

interface SplitDiffViewProps {
  oldYaml: string;
  newYaml: string;
  diff: DocumentDiff;
}


export default function SplitDiffView({ oldYaml, newYaml, diff }: SplitDiffViewProps) {
  const oldEditorRef = useRef<HTMLDivElement>(null);
  const newEditorRef = useRef<HTMLDivElement>(null);
  const oldViewRef = useRef<EditorView | null>(null);
  const newViewRef = useRef<EditorView | null>(null);
  const [oldLineDiffs, setOldLineDiffs] = useState<LineDiff[]>([]);
  const [newLineDiffs, setNewLineDiffs] = useState<LineDiff[]>([]);
  const [selectedChangeId, setSelectedChangeId] = useState<string | null>(null);
  const [popoverPosition, setPopoverPosition] = useState<{ x: number; y: number } | null>(null);
  const scrollSyncRef = useRef<boolean>(true);

  // Compute line diffs
  useEffect(() => {
    let cancelled = false;
    computeLineDiff(oldYaml, newYaml).then(({ oldLines, newLines }) => {
      if (!cancelled) {
        setOldLineDiffs(oldLines);
        setNewLineDiffs(newLines);
      }
    });
    return () => {
      cancelled = true;
    };
  }, [oldYaml, newYaml]);

  // Map changes to line ranges (simplified - find first occurrence of marker/content)
  const mapChangesToLines = useCallback((changes: DiffResult[], oldLines: LineDiff[], newLines: LineDiff[]) => {
    const changeMap = new Map<string, { oldLine?: number; newLine?: number }>();

    for (const change of changes) {
      // Try to find the line containing the marker or content
      let oldLine: number | undefined;
      let newLine: number | undefined;

      // Search in old lines
      if (change.old_content || change.old_title) {
        const searchText = change.old_content || change.old_title || "";
        for (let i = 0; i < oldLines.length; i++) {
          if (oldLines[i].content.includes(searchText) || oldLines[i].content.includes(change.marker)) {
            oldLine = i + 1;
            break;
          }
        }
      }

      // Search in new lines
      if (change.new_content || change.new_title) {
        const searchText = change.new_content || change.new_title || "";
        for (let i = 0; i < newLines.length; i++) {
          if (newLines[i].content.includes(searchText) || newLines[i].content.includes(change.marker)) {
            newLine = i + 1;
            break;
          }
        }
      }

      if (oldLine || newLine) {
        changeMap.set(change.id, { oldLine, newLine });
      }
    }

    return changeMap;
  }, []);

  const changeLineMap = mapChangesToLines(diff.changes, oldLineDiffs, newLineDiffs);

  // Create decorations for old editor
  const createOldDecorations = useCallback((state: EditorState) => {
    const decorations: Range<Decoration>[] = [];

    const maxLines = Math.min(oldLineDiffs.length, state.doc.lines);

    for (let i = 0; i < maxLines; i++) {
      const lineDiff = oldLineDiffs[i];
      const line = state.doc.line(i + 1);
      if (!line) continue;

      // Add background decoration
      if (lineDiff.type === "removed" || lineDiff.type === "modified") {
        const deco = Decoration.line({
          class: lineDiff.type === "removed" ? "cm-line-removed" : "cm-line-modified",
          attributes: {
            "data-line-number": (i + 1).toString(),
            "data-side": "old",
          },
        });
        decorations.push(deco.range(line.from));
      }
    }

    return Decoration.set(decorations);
  }, [oldLineDiffs]);

  // Create decorations for new editor
  const createNewDecorations = useCallback((state: EditorState) => {
    const decorations: Range<Decoration>[] = [];

    const maxLines = Math.min(newLineDiffs.length, state.doc.lines);

    for (let i = 0; i < maxLines; i++) {
      const lineDiff = newLineDiffs[i];
      const line = state.doc.line(i + 1);
      if (!line) continue;

      // Add background decoration
      if (lineDiff.type === "added" || lineDiff.type === "modified") {
        const deco = Decoration.line({
          class: lineDiff.type === "added" ? "cm-line-added" : "cm-line-modified",
          attributes: {
            "data-line-number": (i + 1).toString(),
            "data-side": "new",
          },
        });
        decorations.push(deco.range(line.from));
      }
    }

    return Decoration.set(decorations);
  }, [newLineDiffs]);

  // Setup old editor
  useEffect(() => {
    if (!oldEditorRef.current) return;

    const extensions: Extension[] = [
      lineNumbers(),
      yaml(),
      syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
      EditorState.readOnly.of(true),
      EditorView.theme({
        "&": {
          height: "100%",
          fontSize: "14px",
        },
        ".cm-content": {
          padding: "12px",
          fontFamily: "var(--font-mono), 'Fira Code', monospace",
        },
        ".cm-scroller": {
          overflow: "auto",
        },
        ".cm-gutters": {
          backgroundColor: "#f6f8fa",
          borderRight: "1px solid #e1e4e8",
        },
        ".cm-line": {
          position: "relative",
        },
        ".cm-line-removed": {
          backgroundColor: "#ffeef0",
        },
        ".cm-line-modified": {
          backgroundColor: "#fff5b1",
        },
        ".cm-line-removed:hover, .cm-line-modified:hover": {
          cursor: "pointer",
          opacity: 0.95,
        },
        ".cm-line-removed::before": {
          content: '""',
          position: "absolute",
          left: 0,
          top: 0,
          bottom: 0,
          width: "4px",
          backgroundColor: "#d1242f",
        },
      }),
      EditorView.decorations.of((view) => createOldDecorations(view.state)),
      EditorView.scrollMargins.of({ top: 0, bottom: 0 }),
    ];

    const state = EditorState.create({
      doc: oldYaml,
      extensions,
    });

    const view = new EditorView({
      state,
      parent: oldEditorRef.current,
    });

    // Sync scrolling
    const scrollListener = () => {
      if (!scrollSyncRef.current || !newViewRef.current) return;
      scrollSyncRef.current = false;
      const scrollTop = view.scrollDOM.scrollTop;
      newViewRef.current.scrollDOM.scrollTop = scrollTop;
      setTimeout(() => {
        scrollSyncRef.current = true;
      }, 50);
    };

    view.scrollDOM.addEventListener("scroll", scrollListener);

    oldViewRef.current = view;

    return () => {
      view.scrollDOM.removeEventListener("scroll", scrollListener);
      view.destroy();
      oldViewRef.current = null;
    };
  }, [oldYaml, createOldDecorations]);

  // Update decorations when line diffs change
  useEffect(() => {
    if (oldViewRef.current && oldLineDiffs.length > 0) {
      // Force decoration update by dispatching a no-op transaction
      oldViewRef.current.dispatch({});
    }
  }, [oldLineDiffs.length]);

  // Setup new editor
  useEffect(() => {
    if (!newEditorRef.current) return;

    const extensions: Extension[] = [
      lineNumbers(),
      yaml(),
      syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
      EditorState.readOnly.of(true),
      EditorView.theme({
        "&": {
          height: "100%",
          fontSize: "14px",
        },
        ".cm-content": {
          padding: "12px",
          fontFamily: "var(--font-mono), 'Fira Code', monospace",
        },
        ".cm-scroller": {
          overflow: "auto",
        },
        ".cm-gutters": {
          backgroundColor: "#f6f8fa",
          borderRight: "1px solid #e1e4e8",
        },
        ".cm-line": {
          position: "relative",
        },
        ".cm-line-added": {
          backgroundColor: "#e6ffed",
        },
        ".cm-line-modified": {
          backgroundColor: "#fff5b1",
        },
        ".cm-line-added:hover, .cm-line-modified:hover": {
          cursor: "pointer",
          opacity: 0.95,
        },
        ".cm-line-added::before": {
          content: '""',
          position: "absolute",
          left: 0,
          top: 0,
          bottom: 0,
          width: "4px",
          backgroundColor: "#28a745",
        },
      }),
      EditorView.decorations.of((view) => createNewDecorations(view.state)),
      EditorView.scrollMargins.of({ top: 0, bottom: 0 }),
    ];

    const state = EditorState.create({
      doc: newYaml,
      extensions,
    });

    const view = new EditorView({
      state,
      parent: newEditorRef.current,
    });

    // Sync scrolling
    const scrollListener = () => {
      if (!scrollSyncRef.current || !oldViewRef.current) return;
      scrollSyncRef.current = false;
      const scrollTop = view.scrollDOM.scrollTop;
      oldViewRef.current.scrollDOM.scrollTop = scrollTop;
      setTimeout(() => {
        scrollSyncRef.current = true;
      }, 50);
    };

    view.scrollDOM.addEventListener("scroll", scrollListener);

    newViewRef.current = view;

    return () => {
      view.scrollDOM.removeEventListener("scroll", scrollListener);
      view.destroy();
      newViewRef.current = null;
    };
  }, [newYaml, createNewDecorations]);

  // Update decorations when line diffs change
  useEffect(() => {
    if (newViewRef.current && newLineDiffs.length > 0) {
      // Force decoration update by dispatching a no-op transaction
      newViewRef.current.dispatch({});
    }
  }, [newLineDiffs.length]);

  // Handle line clicks to show comments
  useEffect(() => {
    const handleLineClick = (e: MouseEvent, side: "old" | "new") => {
      const target = e.target as HTMLElement;
      const lineElement = target.closest(".cm-line");
      if (!lineElement) return;

      // Get line number from CodeMirror's line number gutter or calculate from position
      const view = side === "old" ? oldViewRef.current : newViewRef.current;
      if (!view) return;

      const pos = view.posAtCoords({ x: e.clientX, y: e.clientY });
      if (pos === null) return;

      const line = view.state.doc.lineAt(pos);
      const lineNum = line.number;

      // Find the change associated with this line
      const change = diff.changes.find((c) => {
        const mapping = changeLineMap.get(c.id);
        if (side === "old") {
          return mapping?.oldLine === lineNum;
        } else {
          return mapping?.newLine === lineNum;
        }
      });

      // Also check if this line is part of a changed region
      if (!change) {
        // Check if line is in a changed region by looking at line diffs
        const lineDiffs = side === "old" ? oldLineDiffs : newLineDiffs;
        if (lineNum <= lineDiffs.length) {
          const lineDiff = lineDiffs[lineNum - 1];
          if (lineDiff.type !== "unchanged") {
            // Find any change that might be related to this line
            const relatedChange = diff.changes.find((c) => {
              const mapping = changeLineMap.get(c.id);
              if (side === "old") {
                return mapping?.oldLine && Math.abs(mapping.oldLine - lineNum) <= 5;
              } else {
                return mapping?.newLine && Math.abs(mapping.newLine - lineNum) <= 5;
              }
            });
            if (relatedChange) {
              const rect = lineElement.getBoundingClientRect();
              setPopoverPosition({ x: rect.left, y: rect.bottom + 8 });
              setSelectedChangeId(relatedChange.id);
              return;
            }
          }
        }
        return;
      }

      if (change) {
        const rect = lineElement.getBoundingClientRect();
        setPopoverPosition({ x: rect.left, y: rect.bottom + 8 });
        setSelectedChangeId(change.id);
      }
    };

    const oldEditor = oldEditorRef.current;
    const newEditor = newEditorRef.current;

    const oldHandler = (e: MouseEvent) => handleLineClick(e, "old");
    const newHandler = (e: MouseEvent) => handleLineClick(e, "new");

    if (oldEditor) {
      oldEditor.addEventListener("click", oldHandler);
    }
    if (newEditor) {
      newEditor.addEventListener("click", newHandler);
    }

    return () => {
      if (oldEditor) {
        oldEditor.removeEventListener("click", oldHandler);
      }
      if (newEditor) {
        newEditor.removeEventListener("click", newHandler);
      }
    };
  }, [diff.changes, changeLineMap, oldLineDiffs, newLineDiffs]);

  const selectedChange = diff.changes.find((c) => c.id === selectedChangeId);

  return (
    <div className="w-full">
      {/* Header */}
      <div className="border-b border-gray-200 bg-gray-50 flex">
        <div className="flex-1 border-r border-gray-200 px-4 py-2">
          <span className="text-sm font-medium text-gray-700">Old Version</span>
        </div>
        <div className="flex-1 px-4 py-2">
          <span className="text-sm font-medium text-gray-700">New Version</span>
        </div>
      </div>

      {/* Split view */}
      <div className="grid grid-cols-1 lg:grid-cols-2 border-b border-gray-200" style={{ minHeight: "400px", height: "600px" }}>
        <div className="border-r border-gray-200 overflow-hidden bg-white">
          <div ref={oldEditorRef} className="h-full" />
        </div>
        <div className="overflow-hidden bg-white">
          <div ref={newEditorRef} className="h-full" />
        </div>
      </div>

      {/* Comment popover */}
      {selectedChange && popoverPosition && (
        <ChangePopover
          change={selectedChange}
          position={popoverPosition}
          onClose={() => {
            setSelectedChangeId(null);
            setPopoverPosition(null);
          }}
        />
      )}
    </div>
  );
}
