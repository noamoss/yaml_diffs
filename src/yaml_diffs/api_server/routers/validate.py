"""Document validation endpoint.

Provides POST /api/v1/validate endpoint for validating YAML documents.
"""

from io import StringIO

from fastapi import APIRouter, status

from yaml_diffs.api_server.schemas import ValidateRequest, ValidateResponse
from yaml_diffs.validator import validate_document

router = APIRouter()


@router.post(
    "/api/v1/validate",
    response_model=ValidateResponse,
    status_code=status.HTTP_200_OK,
    tags=["validation"],
    summary="Validate a YAML document",
    description="Validates a YAML document against the OpenSpec schema and Pydantic models.",
)
def validate_document_endpoint(request: ValidateRequest) -> ValidateResponse:
    """Validate a YAML document.

    Accepts YAML content as a string and validates it against both the
    OpenSpec schema and Pydantic models. Returns validation result with
    either the validated document or detailed error information.

    Args:
        request: ValidateRequest containing YAML content as string.

    Returns:
        ValidateResponse with validation result.

    Raises:
        HTTPException: If validation fails (handled by exception handlers in main.py).

    Examples:
        >>> POST /api/v1/validate
        {
            "yaml": "document:\\n  id: 'test'\\n  ..."
        }
        {
            "valid": true,
            "document": {...}
        }
    """
    # Convert YAML string to file-like object for validate_document
    yaml_io = StringIO(request.yaml)
    document = validate_document(yaml_io)

    return ValidateResponse(
        valid=True,
        document=document,
    )
