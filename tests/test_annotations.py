"""Tests for annotation parsing."""

from src.ingress2gateway.annotations import (
    annotations_to_filters,
    get_annotation_warnings,
    parse_annotations,
)


def test_parse_empty_annotations():
    """Test parsing empty annotations."""
    result = parse_annotations({})
    assert result == {}


def test_parse_nginx_rewrite_annotation():
    """Test parsing nginx rewrite annotation."""
    annotations = {"nginx.ingress.kubernetes.io/rewrite-target": "/api"}
    result = parse_annotations(annotations)

    assert "filters" in result
    assert len(result["filters"]) == 1
    assert result["filters"][0]["type"] == "URLRewrite"


def test_parse_nginx_ssl_redirect():
    """Test parsing nginx SSL redirect annotation."""
    annotations = {"nginx.ingress.kubernetes.io/ssl-redirect": "true"}
    result = parse_annotations(annotations)

    filters = result.get("filters", [])
    redirect_filters = [f for f in filters if f["type"] == "RequestRedirect"]
    assert len(redirect_filters) == 1
    assert redirect_filters[0]["requestRedirect"]["scheme"] == "https"


def test_parse_unsupported_annotation():
    """Test that unsupported annotations are tracked."""
    annotations = {"nginx.ingress.kubernetes.io/unknown-annotation": "value"}
    result = parse_annotations(annotations)

    assert "unsupported" in result
    assert len(result["unsupported"]) == 1


def test_get_annotation_warnings():
    """Test getting warnings from parsed annotations."""
    parsed = {
        "warnings": ["Warning 1"],
        "unsupported": [{"annotation": "test", "value": "value"}],
    }
    warnings = get_annotation_warnings(parsed)

    assert len(warnings) == 2
    assert "Warning 1" in warnings


def test_annotations_to_filters():
    """Test converting parsed annotations to filters."""
    parsed = {
        "filters": [{"type": "URLRewrite", "urlRewrite": {"path": "/new"}}],
    }
    filters = annotations_to_filters(parsed)

    assert len(filters) == 1
    assert filters[0]["type"] == "URLRewrite"
