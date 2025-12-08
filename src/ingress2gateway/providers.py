"""Provider presets for different Gateway API implementations."""

from typing import Any

# Provider configurations
PROVIDERS = {
    "istio": {
        "name": "Istio",
        "gateway_class": "istio",
        "supports_grpc": True,
        "supports_tcp": True,
        "default_annotations": {},
        "listener_defaults": {
            "allowedRoutes": {"namespaces": {"from": "Same"}},
        },
    },
    "envoy": {
        "name": "Envoy Gateway",
        "gateway_class": "eg",
        "supports_grpc": True,
        "supports_tcp": True,
        "default_annotations": {},
        "listener_defaults": {
            "allowedRoutes": {"namespaces": {"from": "Same"}},
        },
    },
    "contour": {
        "name": "Contour",
        "gateway_class": "contour",
        "supports_grpc": True,
        "supports_tcp": True,
        "default_annotations": {},
        "listener_defaults": {
            "allowedRoutes": {"namespaces": {"from": "All"}},
        },
    },
    "kong": {
        "name": "Kong",
        "gateway_class": "kong",
        "supports_grpc": True,
        "supports_tcp": True,
        "default_annotations": {
            "konghq.com/strip-path": "true",
        },
        "listener_defaults": {
            "allowedRoutes": {"namespaces": {"from": "Same"}},
        },
    },
    "nginx": {
        "name": "NGINX Gateway Fabric",
        "gateway_class": "nginx",
        "supports_grpc": False,
        "supports_tcp": False,
        "default_annotations": {},
        "listener_defaults": {
            "allowedRoutes": {"namespaces": {"from": "Same"}},
        },
    },
    "traefik": {
        "name": "Traefik",
        "gateway_class": "traefik",
        "supports_grpc": True,
        "supports_tcp": True,
        "default_annotations": {},
        "listener_defaults": {
            "allowedRoutes": {"namespaces": {"from": "Same"}},
        },
    },
    "gke": {
        "name": "GKE Gateway Controller",
        "gateway_class": "gke-l7-global-external-managed",
        "supports_grpc": True,
        "supports_tcp": False,
        "default_annotations": {},
        "listener_defaults": {
            "allowedRoutes": {"namespaces": {"from": "Same"}},
        },
    },
}


def get_provider(name: str) -> dict[str, Any]:
    """Get provider configuration by name."""
    return PROVIDERS.get(name.lower(), PROVIDERS["istio"])


def list_providers() -> list[dict[str, str]]:
    """List all available providers."""
    return [{"id": k, "name": v["name"]} for k, v in PROVIDERS.items()]


def get_gateway_class(provider: str) -> str:
    """Get the gateway class name for a provider."""
    return get_provider(provider)["gateway_class"]


def apply_provider_defaults(gateway: dict[str, Any], provider: str) -> dict[str, Any]:
    """Apply provider-specific defaults to a Gateway resource."""
    config = get_provider(provider)

    # Update gateway class
    gateway["spec"]["gatewayClassName"] = config["gateway_class"]

    # Apply listener defaults
    for listener in gateway["spec"].get("listeners", []):
        for key, value in config["listener_defaults"].items():
            if key not in listener:
                listener[key] = value

    # Add provider annotations if any
    if config["default_annotations"]:
        if "annotations" not in gateway["metadata"]:
            gateway["metadata"]["annotations"] = {}
        gateway["metadata"]["annotations"].update(config["default_annotations"])

    return gateway
