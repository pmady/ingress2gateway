"""Tests for validation module."""

from src.ingress2gateway.validation import (
    ValidationResult,
    validate_gateway,
    validate_httproute,
    validate_ingress,
)


def test_validate_valid_ingress():
    """Test validating a valid Ingress."""
    ingress = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {"name": "test", "namespace": "default"},
        "spec": {
            "rules": [
                {
                    "host": "example.com",
                    "http": {
                        "paths": [
                            {
                                "path": "/",
                                "pathType": "Prefix",
                                "backend": {"service": {"name": "svc", "port": {"number": 80}}},
                            }
                        ]
                    },
                }
            ]
        },
    }

    result = validate_ingress(ingress)

    assert result.is_valid
    assert len(result.errors) == 0


def test_validate_empty_ingress():
    """Test validating empty Ingress."""
    result = validate_ingress({})

    assert not result.is_valid
    assert len(result.errors) > 0


def test_validate_ingress_wrong_kind():
    """Test validating Ingress with wrong kind."""
    ingress = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Service",
        "metadata": {"name": "test"},
        "spec": {},
    }

    result = validate_ingress(ingress)

    assert not result.is_valid
    assert any("kind" in e.path for e in result.errors)


def test_validate_valid_gateway():
    """Test validating a valid Gateway."""
    gateway = {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "Gateway",
        "metadata": {"name": "test"},
        "spec": {
            "gatewayClassName": "istio",
            "listeners": [{"name": "http", "port": 80, "protocol": "HTTP"}],
        },
    }

    result = validate_gateway(gateway)

    assert result.is_valid


def test_validate_gateway_missing_class():
    """Test validating Gateway without gatewayClassName."""
    gateway = {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "Gateway",
        "metadata": {"name": "test"},
        "spec": {"listeners": []},
    }

    result = validate_gateway(gateway)

    assert not result.is_valid
    assert any("gatewayClassName" in e.path for e in result.errors)


def test_validate_valid_httproute():
    """Test validating a valid HTTPRoute."""
    route = {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "HTTPRoute",
        "metadata": {"name": "test"},
        "spec": {
            "parentRefs": [{"name": "gateway"}],
            "rules": [{"backendRefs": [{"name": "svc", "port": 80}]}],
        },
    }

    result = validate_httproute(route)

    assert result.is_valid


def test_validation_result_to_dict():
    """Test ValidationResult to_dict method."""
    result = ValidationResult()
    result.add_error("test.path", "Test error")
    result.add_warning("test.warning", "Test warning")

    d = result.to_dict()

    assert d["valid"] is False
    assert len(d["errors"]) == 1
    assert len(d["warnings"]) == 1
