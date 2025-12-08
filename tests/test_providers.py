"""Tests for provider presets."""

from src.ingress2gateway.providers import (
    apply_provider_defaults,
    get_gateway_class,
    get_provider,
    list_providers,
)


def test_list_providers():
    """Test listing all providers."""
    providers = list_providers()

    assert len(providers) > 0
    assert all("id" in p and "name" in p for p in providers)


def test_get_provider_istio():
    """Test getting Istio provider config."""
    provider = get_provider("istio")

    assert provider["name"] == "Istio"
    assert provider["gateway_class"] == "istio"
    assert provider["supports_grpc"] is True


def test_get_provider_unknown():
    """Test getting unknown provider falls back to Istio."""
    provider = get_provider("unknown")

    assert provider["gateway_class"] == "istio"


def test_get_gateway_class():
    """Test getting gateway class for provider."""
    assert get_gateway_class("istio") == "istio"
    assert get_gateway_class("envoy") == "eg"
    assert get_gateway_class("kong") == "kong"


def test_apply_provider_defaults():
    """Test applying provider defaults to gateway."""
    gateway = {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "Gateway",
        "metadata": {"name": "test"},
        "spec": {
            "gatewayClassName": "default",
            "listeners": [{"name": "http", "port": 80, "protocol": "HTTP"}],
        },
    }

    result = apply_provider_defaults(gateway, "contour")

    assert result["spec"]["gatewayClassName"] == "contour"
    assert result["spec"]["listeners"][0]["allowedRoutes"]["namespaces"]["from"] == "All"
