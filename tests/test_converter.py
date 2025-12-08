"""Tests for the converter module."""

import pytest

from src.ingress2gateway.converter import (
    convert_ingress_to_gateway,
    parse_ingress,
    resources_to_yaml,
)


def test_parse_valid_ingress():
    """Test parsing valid Ingress YAML."""
    yaml_str = """
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: test-ingress
  namespace: default
spec:
  rules:
    - host: example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-service
                port:
                  number: 80
"""
    result = parse_ingress(yaml_str)
    assert result["kind"] == "Ingress"
    assert result["metadata"]["name"] == "test-ingress"


def test_parse_invalid_yaml():
    """Test parsing invalid YAML raises ValueError."""
    with pytest.raises(ValueError, match="Invalid YAML"):
        parse_ingress("invalid: yaml: content: [")


def test_convert_basic_ingress():
    """Test converting a basic Ingress to Gateway API."""
    ingress = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {"name": "test", "namespace": "default"},
        "spec": {
            "ingressClassName": "nginx",
            "rules": [
                {
                    "host": "example.com",
                    "http": {
                        "paths": [
                            {
                                "path": "/api",
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {"name": "api-svc", "port": {"number": 8080}}
                                },
                            }
                        ]
                    },
                }
            ],
        },
    }

    result = convert_ingress_to_gateway(ingress)

    assert "gateway" in result
    assert "httproutes" in result
    assert result["gateway"]["kind"] == "Gateway"
    assert result["gateway"]["spec"]["gatewayClassName"] == "nginx"
    assert len(result["httproutes"]) == 1
    assert result["httproutes"][0]["kind"] == "HTTPRoute"


def test_convert_ingress_with_tls():
    """Test converting Ingress with TLS configuration."""
    ingress = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {"name": "tls-test", "namespace": "default"},
        "spec": {
            "tls": [{"hosts": ["secure.example.com"], "secretName": "tls-secret"}],
            "rules": [
                {
                    "host": "secure.example.com",
                    "http": {
                        "paths": [
                            {
                                "path": "/",
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {"name": "secure-svc", "port": {"number": 443}}
                                },
                            }
                        ]
                    },
                }
            ],
        },
    }

    result = convert_ingress_to_gateway(ingress)

    # Check for HTTPS listener
    listeners = result["gateway"]["spec"]["listeners"]
    https_listeners = [l for l in listeners if l["protocol"] == "HTTPS"]
    assert len(https_listeners) == 1
    assert https_listeners[0]["tls"]["certificateRefs"][0]["name"] == "tls-secret"


def test_convert_empty_ingress_raises():
    """Test that empty ingress raises ValueError."""
    with pytest.raises(ValueError, match="Empty ingress"):
        convert_ingress_to_gateway({})


def test_convert_wrong_kind_raises():
    """Test that wrong kind raises ValueError."""
    with pytest.raises(ValueError, match="Expected kind 'Ingress'"):
        convert_ingress_to_gateway({"kind": "Service"})


def test_resources_to_yaml():
    """Test converting resources to YAML string."""
    resources = {
        "gateway": {
            "apiVersion": "gateway.networking.k8s.io/v1",
            "kind": "Gateway",
            "metadata": {"name": "test"},
            "spec": {},
        },
        "httproutes": [
            {
                "apiVersion": "gateway.networking.k8s.io/v1",
                "kind": "HTTPRoute",
                "metadata": {"name": "test-route"},
                "spec": {},
            }
        ],
    }

    yaml_output = resources_to_yaml(resources)

    assert "kind: Gateway" in yaml_output
    assert "kind: HTTPRoute" in yaml_output
    assert "---" in yaml_output  # Document separator
