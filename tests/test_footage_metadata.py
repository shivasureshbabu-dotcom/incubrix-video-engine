
import pytest

from app.footage_metadata import validate_footage_metadata


def valid_metadata():
    return {
        "clip_id": "clip_001",
        "source_name": "Example Footage Provider",
        "source_url": "https://example.com/video/clip_001",
        "license_name": "Example License",
        "license_url": "https://example.com/license",
        "creator": "Example Creator",
    }


def test_valid_metadata_is_accepted():
    result = validate_footage_metadata(valid_metadata())

    assert result["metadata_valid"] is True
    assert result["clip_id"] == "clip_001"


def test_missing_creator_is_rejected():
    metadata = valid_metadata()
    del metadata["creator"]

    with pytest.raises(ValueError):
        validate_footage_metadata(metadata)


def test_invalid_source_url_is_rejected():
    metadata = valid_metadata()
    metadata["source_url"] = "not-a-url"

    with pytest.raises(ValueError):
        validate_footage_metadata(metadata)


def test_empty_license_name_is_rejected():
    metadata = valid_metadata()
    metadata["license_name"] = ""

    with pytest.raises(ValueError):
        validate_footage_metadata(metadata)
