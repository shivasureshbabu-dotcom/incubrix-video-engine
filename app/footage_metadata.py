
from urllib.parse import urlparse


def validate_footage_metadata(metadata: dict) -> dict:
    """Check that a clip includes source and licensing information."""

    required_fields = [
        "clip_id",
        "source_name",
        "source_url",
        "license_name",
        "license_url",
        "creator",
    ]

    for field in required_fields:
        value = metadata.get(field)

        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Missing or empty field: {field}")

    for field in ["source_url", "license_url"]:
        parsed = urlparse(metadata[field])

        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError(f"{field} must be a valid web URL")

    return {
        **metadata,
        "metadata_valid": True,
    }
