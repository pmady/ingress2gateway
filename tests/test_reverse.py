"""Tests for reverse conversion (Gateway API to Ingress)."""

from src.ingress2gateway.reverse import (
    convert_gateway_to_ingress,
    gateway_resources_to_ingress_yaml,
    parse_gateway_resources,
)


def test_parse_gateway_resources():
    """Test parsing Gateway API YAML."""
    yaml_content = """
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: test-gateway
  namespace: default
spec:
  gatewayClassName: istio
  listeners:
    - name: http
      port: 80
      protocol: HTTP
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: test-route
  namespace: default
spec:
  parentRefs:
    - name: test-gateway
  rules:
    - backendRefs:
        - name: my-service
          port: 8080
"""
    gateway, httproutes = parse_gateway_resources(yaml_content)

    assert gateway is not None
    assert gateway["kind"] == "Gateway"
    assert len(httproutes) == 1
    assert httproutes[0]["kind"] == "HTTPRoute"


def test_convert_gateway_to_ingress():
    """Test converting Gateway to Ingress."""
    gateway = {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "Gateway",
        "metadata": {"name": "test", "namespace": "default"},
        "spec": {
            "gatewayClassName": "istio",
            "listeners": [{"name": "http", "port": 80, "protocol": "HTTP"}],
        },
    }

    httproutes = [
        {
            "apiVersion": "gateway.networking.k8s.io/v1",
            "kind": "HTTPRoute",
            "metadata": {"name": "test-route", "namespace": "default"},
            "spec": {
                "hostnames": ["example.com"],
                "rules": [
                    {
                        "matches": [{"path": {"type": "PathPrefix", "value": "/api"}}],
                        "backendRefs": [{"name": "api-service", "port": 8080}],
                    }
                ],
            },
        }
    ]

    ingress = convert_gateway_to_ingress(gateway, httproutes)

    assert ingress["kind"] == "Ingress"
    assert ingress["metadata"]["name"] == "test"
    assert len(ingress["spec"]["rules"]) == 1
    assert ingress["spec"]["rules"][0]["host"] == "example.com"


def test_gateway_resources_to_ingress_yaml():
    """Test converting Gateway resources to Ingress YAML."""
    gateway = {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "Gateway",
        "metadata": {"name": "test", "namespace": "default"},
        "spec": {"gatewayClassName": "istio", "listeners": []},
    }

    yaml_output = gateway_resources_to_ingress_yaml(gateway, [])

    assert "kind: Ingress" in yaml_output
    assert "name: test" in yaml_output
