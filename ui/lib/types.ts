/** TypeScript types matching the API schemas from the yaml-diffs backend. */

export enum ChangeType {
  SECTION_ADDED = "section_added",
  SECTION_REMOVED = "section_removed",
  CONTENT_CHANGED = "content_changed",
  SECTION_MOVED = "section_moved",
  TITLE_CHANGED = "title_changed",
  UNCHANGED = "unchanged",
}

export interface DiffResult {
  id: string;
  section_id: string;
  change_type: ChangeType;
  marker: string;
  old_marker_path: string[] | null;
  new_marker_path: string[] | null;
  old_id_path: string[] | null;
  new_id_path: string[] | null;
  old_content: string | null;
  new_content: string | null;
  old_title: string | null;
  new_title: string | null;
  old_section_yaml: string | null;
  new_section_yaml: string | null;
  old_line_number: number | null;
  new_line_number: number | null;
}

export interface DocumentDiff {
  changes: DiffResult[];
  added_count: number;
  deleted_count: number;
  modified_count: number;
  moved_count: number;
}

export interface DiffRequest {
  old_yaml: string;
  new_yaml: string;
}

export interface DiffResponse {
  diff: DocumentDiff;
}

export interface ErrorResponse {
  error: string;
  message: string;
  details?: Array<Record<string, unknown>> | null;
}
