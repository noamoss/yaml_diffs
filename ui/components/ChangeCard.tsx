"use client";

import { useState, useEffect } from "react";
import { DiffResult, ChangeType } from "@/lib/types";
import { computeCharDiff, formatMarkerPath, DiffChunk } from "@/lib/diff-utils";
import { useDiscussionsStore } from "@/stores/discussions";
import DiscussionThread from "./DiscussionThread";

interface ChangeCardProps {
  change: DiffResult;
  index: number;
}

function getChangeTypeStyles(changeType: ChangeType) {
  switch (changeType) {
    case ChangeType.SECTION_ADDED:
      return {
        badge: "bg-green-100 text-green-800 border-green-300",
        bg: "bg-green-50",
      };
    case ChangeType.SECTION_REMOVED:
      return {
        badge: "bg-red-100 text-red-800 border-red-300",
        bg: "bg-red-50",
      };
    case ChangeType.CONTENT_CHANGED:
      return {
        badge: "bg-yellow-100 text-yellow-800 border-yellow-300",
        bg: "bg-yellow-50",
      };
    case ChangeType.TITLE_CHANGED:
      return {
        badge: "bg-blue-100 text-blue-800 border-blue-300",
        bg: "bg-blue-50",
      };
    case ChangeType.SECTION_MOVED:
      return {
        badge: "bg-purple-100 text-purple-800 border-purple-300",
        bg: "bg-purple-50",
      };
    default:
      return {
        badge: "bg-gray-100 text-gray-800 border-gray-300",
        bg: "bg-gray-50",
      };
  }
}

function formatChangeType(changeType: ChangeType): string {
  return changeType
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function renderDiffedText(chunks: DiffChunk[], type: "old" | "new") {
  return (
    <pre className="whitespace-pre-wrap text-sm font-mono break-words">
      {chunks.map((chunk, i) => {
        if (chunk.type === "unchanged") {
          return <span key={i}>{chunk.text}</span>;
        }
        if (chunk.type === "removed" && type === "old") {
          return (
            <span key={i} className="bg-red-200 line-through">
              {chunk.text}
            </span>
          );
        }
        if (chunk.type === "added" && type === "new") {
          return (
            <span key={i} className="bg-green-200 font-semibold">
              {chunk.text}
            </span>
          );
        }
        return <span key={i}>{chunk.text}</span>;
      })}
    </pre>
  );
}

interface DiffContentProps {
  oldContent: string | null;
  newContent: string | null;
}

function DiffContent({ oldContent, newContent }: DiffContentProps) {
  const [diffChunks, setDiffChunks] = useState<DiffChunk[] | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!oldContent && !newContent) {
      setDiffChunks(null);
      return;
    }

    if (!oldContent || !newContent) {
      setDiffChunks(null);
      return;
    }

    // Compute diff asynchronously
    setLoading(true);
    computeCharDiff(oldContent, newContent)
      .then((chunks) => {
        setDiffChunks(chunks);
        setLoading(false);
      })
      .catch(() => {
        // Fallback on error
        setDiffChunks([
          { text: oldContent, type: "removed" },
          { text: newContent, type: "added" },
        ]);
        setLoading(false);
      });
  }, [oldContent, newContent]);

  if (!oldContent && !newContent) return null;

  if (!oldContent) {
    // Added content
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="text-sm text-gray-500 italic">(empty)</div>
        <div className="bg-green-50 border border-green-200 rounded p-3 overflow-x-auto">
          <pre className="whitespace-pre-wrap text-sm font-mono">
            {newContent}
          </pre>
        </div>
      </div>
    );
  }

  if (!newContent) {
    // Removed content
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="bg-red-50 border border-red-200 rounded p-3 overflow-x-auto">
          <pre className="whitespace-pre-wrap text-sm font-mono">
            {oldContent}
          </pre>
        </div>
        <div className="text-sm text-gray-500 italic">(empty)</div>
      </div>
    );
  }

  if (loading || !diffChunks) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="bg-red-50 border border-red-200 rounded p-3">
          <pre className="whitespace-pre-wrap text-sm font-mono">
            {oldContent}
          </pre>
        </div>
        <div className="bg-green-50 border border-green-200 rounded p-3">
          <pre className="whitespace-pre-wrap text-sm font-mono">
            {newContent}
          </pre>
        </div>
      </div>
    );
  }

  // Modified content - show character-level diff
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div className="bg-red-50 border border-red-200 rounded p-3 overflow-x-auto">
        {renderDiffedText(diffChunks, "old")}
      </div>
      <div className="bg-green-50 border border-green-200 rounded p-3 overflow-x-auto">
        {renderDiffedText(diffChunks, "new")}
      </div>
    </div>
  );
}

export default function ChangeCard({ change, index }: ChangeCardProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [showDiscussion, setShowDiscussion] = useState(false);
  const [commentText, setCommentText] = useState("");

  const styles = getChangeTypeStyles(change.change_type);

  // Generate a stable ID for this change if missing (fallback for older API versions)
  // Use a combination of section_id, change_type, marker, and index to ensure uniqueness
  const changeId = change.id || `fallback-${change.section_id || 'unknown'}-${change.change_type || 'unknown'}-${change.marker || 'unknown'}-${index}`;

  // Only log warning in development mode if id is missing (not using fallback)
  if (!change.id && process.env.NODE_ENV === 'development') {
    console.warn("ChangeCard: change.id is missing, using fallback ID", { changeId, change });
  }

  const discussion = useDiscussionsStore((state) =>
    state.getDiscussion(changeId)
  );
  const addDiscussion = useDiscussionsStore((state) => state.addDiscussion);
  const addComment = useDiscussionsStore((state) => state.addComment);
  const editComment = useDiscussionsStore((state) => state.editComment);
  const deleteComment = useDiscussionsStore((state) => state.deleteComment);

  const handleAddComment = () => {
    if (!commentText.trim()) return;
    if (!changeId) {
      console.error("Cannot add comment: changeId is missing");
      return;
    }

    const discussionId = discussion
      ? discussion.id
      : addDiscussion(changeId);
    addComment(discussionId, commentText);
    setCommentText("");
    setShowDiscussion(true);
  };

  const handleDiscussionActions = {
    onAddComment: (text: string, parentCommentId?: string) => {
      if (!changeId) {
        console.error("Cannot add comment: changeId is missing");
        return;
      }
      const discussionId = discussion
        ? discussion.id
        : addDiscussion(changeId);
      addComment(discussionId, text, parentCommentId);
    },
    onEditComment: (commentId: string, text: string) => {
      if (!discussion) return;
      editComment(discussion.id, commentId, text);
    },
    onDeleteComment: (commentId: string) => {
      if (!discussion) return;
      deleteComment(discussion.id, commentId);
    },
  };

  const hasPathChange =
    JSON.stringify(change.old_marker_path) !==
    JSON.stringify(change.new_marker_path);
  const hasTitleChange = change.old_title !== change.new_title;
  const hasContentChange =
    change.old_content !== change.new_content ||
    (change.old_content === null && change.new_content !== null) ||
    (change.old_content !== null && change.new_content === null);

  return (
    <div className={`border rounded-lg ${styles.bg} ${isExpanded ? "" : "overflow-hidden"}`}>
      <div
        className="px-3 sm:px-4 py-3 cursor-pointer hover:bg-opacity-80 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <div className="flex flex-wrap items-center gap-2 sm:gap-3">
            <span className="text-sm font-medium text-gray-500">#{index + 1}</span>
            <span
              className={`px-2 py-1 text-xs font-semibold rounded border ${styles.badge}`}
            >
              {formatChangeType(change.change_type)}
            </span>
            <span className="text-sm font-mono text-gray-700">
              Marker: {change.marker}
            </span>
            {hasPathChange && (
              <span className="text-xs text-gray-600 hidden sm:inline">
                {formatMarkerPath(change.old_marker_path)} →{" "}
                {formatMarkerPath(change.new_marker_path)}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            {discussion && discussion.comments.length > 0 && (
              <span className="text-xs text-gray-500">
                {discussion.comments.length} comment
                {discussion.comments.length !== 1 ? "s" : ""}
              </span>
            )}
            <svg
              className={`w-5 h-5 text-gray-400 transition-transform ${
                isExpanded ? "rotate-180" : ""
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="px-4 pb-4 space-y-4">
          {hasTitleChange && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Title Change:</h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-red-50 border border-red-200 rounded p-3">
                  <div className="text-sm font-mono">
                    {change.old_title || "(empty)"}
                  </div>
                </div>
                <div className="bg-green-50 border border-green-200 rounded p-3">
                  <div className="text-sm font-mono">
                    {change.new_title || "(empty)"}
                  </div>
                </div>
              </div>
            </div>
          )}

          {hasContentChange && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Content Change:</h4>
              <div className="overflow-x-auto">
                <DiffContent
                  oldContent={change.old_content}
                  newContent={change.new_content}
                />
              </div>
            </div>
          )}

          <div className="border-t border-gray-200 pt-4">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowDiscussion(!showDiscussion);
                if (!discussion && changeId) {
                  addDiscussion(changeId);
                }
              }}
              className="text-sm text-blue-600 hover:text-blue-800 font-medium"
            >
              {showDiscussion ? "Hide" : "Add"} Comment
            </button>

            {showDiscussion && (
              <div className="mt-3">
                <textarea
                  value={commentText}
                  onChange={(e) => setCommentText(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                      handleAddComment();
                    }
                  }}
                  className="w-full p-2 border border-gray-300 rounded resize-none"
                  rows={3}
                  placeholder="Add a comment about this change... (Cmd/Ctrl+Enter to submit)"
                />
                <div className="mt-2 flex gap-2">
                  <button
                    onClick={handleAddComment}
                    disabled={!commentText.trim()}
                    className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                  >
                    Comment
                  </button>
                </div>
              </div>
            )}

            {discussion && discussion.comments.length > 0 && (
              <DiscussionThread
                comments={discussion.comments}
                {...handleDiscussionActions}
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
