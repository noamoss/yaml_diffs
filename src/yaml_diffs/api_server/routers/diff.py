"""Document diff endpoint.

Provides POST /api/v1/diff endpoint for comparing two YAML documents.
"""

from io import StringIO

from fastapi import APIRouter, status

from yaml_diffs.api_server.schemas import DiffRequest, DiffResponse
from yaml_diffs.diff import diff_documents, enrich_diff_with_yaml_extraction
from yaml_diffs.loader import load_document

router = APIRouter()


@router.post(
    "/api/v1/diff",
    response_model=DiffResponse,
    status_code=status.HTTP_200_OK,
    tags=["diff"],
    summary="Diff two YAML documents",
    description="Compares two YAML documents and returns detected changes.",
)
def diff_documents_endpoint(request: DiffRequest) -> DiffResponse:
    """Diff two YAML documents.

    Accepts two YAML documents (old and new versions) and compares them
    to detect changes. Returns a DocumentDiff object containing all
    detected changes including additions, deletions, modifications, and movements.

    Args:
        request: DiffRequest containing old and new YAML content as strings.

    Returns:
        DiffResponse with DocumentDiff containing all detected changes.

    Raises:
        HTTPException: If document loading or diffing fails (handled by exception handlers in main.py).

    Examples:
        >>> POST /api/v1/diff
        {
            "old_yaml": "document:\\n  id: 'test'\\n  ...",
            "new_yaml": "document:\\n  id: 'test'\\n  ..."
        }
        {
            "diff": {
                "changes": [...],
                "added_count": 1,
                "deleted_count": 0,
                "modified_count": 1,
                "moved_count": 0
            }
        }
    """
    # Convert YAML strings to file-like objects for load_document
    old_yaml_io = StringIO(request.old_yaml)
    new_yaml_io = StringIO(request.new_yaml)

    # Load both documents
    old_doc = load_document(old_yaml_io)
    new_doc = load_document(new_yaml_io)

    # Diff the documents
    diff = diff_documents(old_doc, new_doc)

    # Enrich with YAML extraction and line numbers
    enrich_diff_with_yaml_extraction(diff, request.old_yaml, request.new_yaml)

    return DiffResponse(diff=diff)
