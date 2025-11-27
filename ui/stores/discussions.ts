/** Zustand store for managing discussion threads on diff changes. */

import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

export interface Comment {
  id: string;
  text: string;
  timestamp: string;
  replies: Comment[];
}

export interface Discussion {
  id: string;
  changeId: string; // Links to DiffResult.id
  comments: Comment[];
}

// Legacy format for migration purposes
interface OldDiscussionFormat {
  sectionId?: string;
  changeId?: string;
  id?: string;
  comments?: Comment[];
}

interface DiscussionsState {
  discussions: Discussion[];
  addDiscussion: (changeId: string) => string; // Returns discussion ID
  addComment: (discussionId: string, text: string, parentCommentId?: string) => void;
  editComment: (discussionId: string, commentId: string, text: string) => void;
  deleteComment: (discussionId: string, commentId: string) => void;
  getDiscussion: (changeId: string) => Discussion | undefined;
  clearAll: () => void;
}

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
}

export const useDiscussionsStore = create<DiscussionsState>()(
  persist(
    (set, get) => ({
      discussions: [],

      addDiscussion: (changeId: string) => {
        // Validate changeId is provided
        if (!changeId) {
          console.error("addDiscussion called with empty changeId");
          return generateId();
        }

        const existing = get().discussions.find((d) => d.changeId === changeId);
        if (existing) {
          return existing.id;
        }

        const newDiscussion: Discussion = {
          id: generateId(),
          changeId,
          comments: [],
        };

        set((state) => ({
          discussions: [...state.discussions, newDiscussion],
        }));

        return newDiscussion.id;
      },

      addComment: (discussionId: string, text: string, parentCommentId?: string) => {
        if (!text.trim()) return;

        const newComment: Comment = {
          id: generateId(),
          text: text.trim(),
          timestamp: new Date().toISOString(),
          replies: [],
        };

        set((state) => ({
          discussions: state.discussions.map((discussion) => {
            if (discussion.id !== discussionId) return discussion;

            if (parentCommentId) {
              // Add as reply
              return {
                ...discussion,
                comments: discussion.comments.map((comment) => {
                  if (comment.id === parentCommentId) {
                    return {
                      ...comment,
                      replies: [...comment.replies, newComment],
                    };
                  }
                  // Recursively check replies
                  const updateReplies = (c: Comment): Comment => {
                    if (c.id === parentCommentId) {
                      return {
                        ...c,
                        replies: [...c.replies, newComment],
                      };
                    }
                    return {
                      ...c,
                      replies: c.replies.map(updateReplies),
                    };
                  };
                  return updateReplies(comment);
                }),
              };
            } else {
              // Add as top-level comment
              return {
                ...discussion,
                comments: [...discussion.comments, newComment],
              };
            }
          }),
        }));
      },

      editComment: (discussionId: string, commentId: string, text: string) => {
        if (!text.trim()) return;

        set((state) => ({
          discussions: state.discussions.map((discussion) => {
            if (discussion.id !== discussionId) return discussion;

            const updateComment = (comment: Comment): Comment => {
              if (comment.id === commentId) {
                return { ...comment, text: text.trim() };
              }
              return {
                ...comment,
                replies: comment.replies.map(updateComment),
              };
            };

            return {
              ...discussion,
              comments: discussion.comments.map(updateComment),
            };
          }),
        }));
      },

      deleteComment: (discussionId: string, commentId: string) => {
        set((state) => ({
          discussions: state.discussions.map((discussion) => {
            if (discussion.id !== discussionId) return discussion;

            const filterComment = (comment: Comment): Comment | null => {
              if (comment.id === commentId) return null;
              return {
                ...comment,
                replies: comment.replies.map(filterComment).filter((c): c is Comment => c !== null),
              };
            };

            return {
              ...discussion,
              comments: discussion.comments
                .map(filterComment)
                .filter((c): c is Comment => c !== null),
            };
          }),
        }));
      },

      getDiscussion: (changeId: string) => {
        // Validate changeId is provided
        if (!changeId) {
          console.error("getDiscussion called with empty changeId");
          return undefined;
        }

        // Filter out any discussions with invalid format (migration from old sectionId format)
        const discussions = get().discussions.filter((d): d is Discussion => {
          const oldFormat = d as unknown as OldDiscussionFormat;
          if (!d.changeId && oldFormat.sectionId) {
            // Old format - remove it
            return false;
          }
          return !!d.changeId;
        });

        // If we filtered out old discussions, update the store
        if (discussions.length !== get().discussions.length) {
          set({ discussions });
        }

        return discussions.find((d) => d.changeId === changeId);
      },

      clearAll: () => {
        set({ discussions: [] });
      },
    }),
    {
      name: "yaml-diff-discussions-v2", // Changed key to force fresh start and avoid old sectionId data
      storage: typeof window !== "undefined"
        ? createJSONStorage(() => localStorage)
        : undefined,
      // Migrate old data if it exists
      migrate: (persistedState: any, version: number) => {
        // Clear old data with sectionId format
        if (persistedState?.discussions) {
          const validDiscussions = persistedState.discussions.filter((d: unknown): d is Discussion => {
            const oldFormat = d as unknown as OldDiscussionFormat;
            // Only keep discussions with changeId (new format)
            return !!oldFormat.changeId && !oldFormat.sectionId;
          });
          return { ...persistedState, discussions: validDiscussions };
        }
        return persistedState;
      },
      version: 2, // Increment version to trigger migration
    }
  )
);
