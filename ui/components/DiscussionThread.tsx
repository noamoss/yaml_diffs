"use client";

import { useState } from "react";
import { Comment } from "@/stores/discussions";

interface DiscussionThreadProps {
  comments: Comment[];
  onAddComment: (text: string, parentCommentId?: string) => void;
  onEditComment: (commentId: string, text: string) => void;
  onDeleteComment: (commentId: string) => void;
}

export default function DiscussionThread({
  comments,
  onAddComment,
  onEditComment,
  onDeleteComment,
}: DiscussionThreadProps) {
  const [replyingTo, setReplyingTo] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [replyText, setReplyText] = useState("");
  const [editText, setEditText] = useState("");

  const handleSubmitReply = (parentId?: string) => {
    if (replyText.trim()) {
      onAddComment(replyText, parentId);
      setReplyText("");
      setReplyingTo(null);
    }
  };

  const handleSubmitEdit = (commentId: string) => {
    if (editText.trim()) {
      onEditComment(commentId, editText);
      setEditText("");
      setEditingId(null);
    }
  };

  const startEdit = (comment: Comment) => {
    setEditingId(comment.id);
    setEditText(comment.text);
  };

  const renderComment = (comment: Comment, depth: number = 0) => {
    const isEditing = editingId === comment.id;
    const isReplying = replyingTo === comment.id;

    return (
      <div
        key={comment.id}
        className={`${depth > 0 ? "ml-8 mt-3 border-l-2 border-gray-200 pl-4" : ""}`}
      >
        <div className="bg-white border border-gray-200 rounded-lg p-3">
          {isEditing ? (
            <div>
              <textarea
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded resize-none"
                rows={3}
                autoFocus
              />
              <div className="mt-2 flex gap-2">
                <button
                  onClick={() => handleSubmitEdit(comment.id)}
                  className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                >
                  Save
                </button>
                <button
                  onClick={() => {
                    setEditingId(null);
                    setEditText("");
                  }}
                  className="px-3 py-1 bg-gray-200 text-gray-700 rounded text-sm hover:bg-gray-300"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <>
              <div className="flex items-start justify-between">
                <p className="text-sm text-gray-800 whitespace-pre-wrap">
                  {comment.text}
                </p>
                <div className="flex gap-2 ml-2">
                  <button
                    onClick={() => startEdit(comment)}
                    className="text-xs text-gray-500 hover:text-gray-700"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => onDeleteComment(comment.id)}
                    className="text-xs text-red-500 hover:text-red-700"
                  >
                    Delete
                  </button>
                </div>
              </div>
              <div className="mt-2 flex items-center justify-between">
                <span className="text-xs text-gray-500">
                  {new Date(comment.timestamp).toLocaleString()}
                </span>
                {depth === 0 && (
                  <button
                    onClick={() => {
                      setReplyingTo(comment.id);
                      setReplyText("");
                    }}
                    className="text-xs text-blue-600 hover:text-blue-800"
                  >
                    Reply
                  </button>
                )}
              </div>
            </>
          )}
        </div>

        {isReplying && (
          <div className="mt-2 ml-4">
            <textarea
              value={replyText}
              onChange={(e) => setReplyText(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded resize-none"
              rows={2}
              placeholder="Write a reply..."
              autoFocus
            />
            <div className="mt-2 flex gap-2">
              <button
                onClick={() => handleSubmitReply(comment.id)}
                className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
              >
                Reply
              </button>
              <button
                onClick={() => {
                  setReplyingTo(null);
                  setReplyText("");
                }}
                className="px-3 py-1 bg-gray-200 text-gray-700 rounded text-sm hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {comment.replies.length > 0 && (
          <div className="mt-3">
            {comment.replies.map((reply) => renderComment(reply, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="mt-4 space-y-3">
      {comments.length === 0 ? (
        <p className="text-sm text-gray-500 italic">No comments yet.</p>
      ) : (
        comments.map((comment) => renderComment(comment))
      )}
    </div>
  );
}
