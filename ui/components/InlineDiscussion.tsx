"use client";

import { useState } from "react";
import { DiffResult, ChangeType } from "@/lib/types";
import { formatMarkerPath } from "@/lib/diff-utils";
import { useDiscussionsStore } from "@/stores/discussions";
import DiscussionThread from "./DiscussionThread";

interface InlineDiscussionProps {
  change: DiffResult;
  lineNumber: number;
  side: "old" | "new";
}

function formatChangeType(changeType: ChangeType): string {
  return changeType
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function getChangeTypeStyles(changeType: ChangeType) {
  switch (changeType) {
    case ChangeType.SECTION_ADDED:
      return "bg-green-100 text-green-800 border-green-300";
    case ChangeType.SECTION_REMOVED:
      return "bg-red-100 text-red-800 border-red-300";
    case ChangeType.CONTENT_CHANGED:
      return "bg-yellow-100 text-yellow-800 border-yellow-300";
    case ChangeType.TITLE_CHANGED:
      return "bg-blue-100 text-blue-800 border-blue-300";
    case ChangeType.SECTION_MOVED:
      return "bg-purple-100 text-purple-800 border-purple-300";
    default:
      return "bg-gray-100 text-gray-800 border-gray-300";
  }
}

export default function InlineDiscussion({ change, lineNumber, side }: InlineDiscussionProps) {
  const [commentText, setCommentText] = useState("");

  const changeId = change.id;
  const discussion = useDiscussionsStore((state) => state.getDiscussion(changeId));
  const addDiscussion = useDiscussionsStore((state) => state.addDiscussion);
  const addComment = useDiscussionsStore((state) => state.addComment);
  const editComment = useDiscussionsStore((state) => state.editComment);
  const deleteComment = useDiscussionsStore((state) => state.deleteComment);

  const handleAddComment = () => {
    if (!commentText.trim()) return;
    if (!changeId) return;

    const discussionId = discussion ? discussion.id : addDiscussion(changeId);
    addComment(discussionId, commentText);
    setCommentText("");
  };

  const handleDiscussionActions = {
    onAddComment: (text: string, parentCommentId?: string) => {
      if (!changeId) return;
      const discussionId = discussion ? discussion.id : addDiscussion(changeId);
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
    JSON.stringify(change.old_marker_path) !== JSON.stringify(change.new_marker_path);
  const hasTitleChange = change.old_title !== change.new_title;
  const hasContentChange =
    change.old_content !== change.new_content ||
    (change.old_content === null && change.new_content !== null) ||
    (change.old_content !== null && change.new_content === null);

  return (
    <div className="bg-white border border-gray-300 rounded-lg shadow-sm p-3 w-80 max-w-full">
      {/* Header */}
      <div className="mb-3 pb-2 border-b border-gray-200">
        <div className="flex items-center gap-2 mb-2">
          <span
            className={`px-2 py-1 text-xs font-semibold rounded border ${getChangeTypeStyles(
              change.change_type
            )}`}
          >
            {formatChangeType(change.change_type)}
          </span>
        </div>
        <div className="text-xs space-y-1">
          <div>
            <span className="font-medium text-gray-700">Marker:</span>{" "}
            <span className="font-mono text-gray-900">{change.marker}</span>
          </div>
          {hasPathChange && (
            <div>
              <span className="font-medium text-gray-700">Path:</span>{" "}
              <span className="text-gray-600">
                {formatMarkerPath(change.old_marker_path)} →{" "}
                {formatMarkerPath(change.new_marker_path)}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Change details */}
      {(hasTitleChange || hasContentChange) && (
        <div className="mb-3 pb-2 border-b border-gray-200 space-y-2">
          {hasTitleChange && (
            <div>
              <h5 className="text-xs font-semibold text-gray-700 mb-1">Title Change:</h5>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-red-50 border border-red-200 rounded p-2">
                  <div className="font-mono text-gray-800">{change.old_title || "(empty)"}</div>
                </div>
                <div className="bg-green-50 border border-green-200 rounded p-2">
                  <div className="font-mono text-gray-800">{change.new_title || "(empty)"}</div>
                </div>
              </div>
            </div>
          )}
          {hasContentChange && (
            <div>
              <h5 className="text-xs font-semibold text-gray-700 mb-1">Content Change:</h5>
              <div className="grid grid-cols-2 gap-2 text-xs max-h-32 overflow-y-auto">
                <div className="bg-red-50 border border-red-200 rounded p-2">
                  <pre className="whitespace-pre-wrap font-mono text-gray-800 text-xs">
                    {change.old_content || "(empty)"}
                  </pre>
                </div>
                <div className="bg-green-50 border border-green-200 rounded p-2">
                  <pre className="whitespace-pre-wrap font-mono text-gray-800 text-xs">
                    {change.new_content || "(empty)"}
                  </pre>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Discussion */}
      <div className="space-y-2">
        <h5 className="text-xs font-semibold text-gray-700">Discussion</h5>
        <textarea
          value={commentText}
          onChange={(e) => setCommentText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
              handleAddComment();
            }
          }}
          className="w-full p-2 border border-gray-300 rounded resize-none text-xs"
          rows={3}
          placeholder="Add a comment... (Cmd/Ctrl+Enter to submit)"
        />
        <button
          onClick={handleAddComment}
          disabled={!commentText.trim()}
          className="px-3 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          Comment
        </button>

        {discussion && discussion.comments.length > 0 && (
          <div className="mt-3">
            <DiscussionThread comments={discussion.comments} {...handleDiscussionActions} />
          </div>
        )}
      </div>
    </div>
  );
}
