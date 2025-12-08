"""Reverse conversion: Gateway API to Ingress."""

from typing import Any

import yaml


def convert_gateway_to_ingress(
    gateway: dict[str, Any],
    httproutes: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Convert Gateway API resources back to a Kubernetes Ingress.

    Args:
        gateway: Gateway resource
        httproutes: List of HTTPRoute resources

    Returns:
        Ingress resource dictionary
    """
    gateway_meta = gateway.get("metadata", {})
    gateway_spec = gateway.get("spec", {})

    # Build Ingress metadata
    ingress_name = gateway_meta.get("name", "converted-ingress")
    namespace = gateway_meta.get("namespace", "default")

    # Determine ingress class from gateway class
    gateway_class = gateway_spec.get("gatewayClassName", "")
    ingress_class = _map_gateway_class_to_ingress(gateway_class)

    # Extract TLS configuration from listeners
    tls_config = []
    for listener in gateway_spec.get("listeners", []):
        if listener.get("protocol") == "HTTPS":
            tls_entry: dict[str, Any] = {}
            hostname = listener.get("hostname")
            if hostname:
                tls_entry["hosts"] = [hostname]

            tls_refs = listener.get("tls", {}).get("certificateRefs", [])
            if tls_refs:
                tls_entry["secretName"] = tls_refs[0].get("name", "")

            if tls_entry:
                tls_config.append(tls_entry)

    # Build rules from HTTPRoutes
    rules = []
    for route in httproutes:
        route_spec = route.get("spec", {})
        hostnames = route_spec.get("hostnames", [])

        # Build paths from rules
        paths = []
        for rule in route_spec.get("rules", []):
            for match in rule.get("matches", [{}]):
                path_match = match.get("path", {})
                path_value = path_match.get("value", "/")
                path_type = _map_path_type(path_match.get("type", "PathPrefix"))

                backend_refs = rule.get("backendRefs", [])
                if backend_refs:
                    backend = backend_refs[0]
                    paths.append(
                        {
                            "path": path_value,
                            "pathType": path_type,
                            "backend": {
                                "service": {
                                    "name": backend.get("name", ""),
                                    "port": {"number": backend.get("port", 80)},
                                }
                            },
                        }
                    )

        # Create rule for each hostname (or one rule without host)
        if hostnames:
            for hostname in hostnames:
                rules.append({"host": hostname, "http": {"paths": paths}})
        elif paths:
            rules.append({"http": {"paths": paths}})

    # Build Ingress resource
    ingress: dict[str, Any] = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {
            "name": ingress_name,
            "namespace": namespace,
        },
        "spec": {},
    }

    if ingress_class:
        ingress["spec"]["ingressClassName"] = ingress_class

    if tls_config:
        ingress["spec"]["tls"] = tls_config

    if rules:
        ingress["spec"]["rules"] = rules

    return ingress


def _map_gateway_class_to_ingress(gateway_class: str) -> str:
    """Map Gateway class name to Ingress class name."""
    mapping = {
        "istio": "istio",
        "eg": "nginx",  # Envoy Gateway -> nginx as fallback
        "contour": "contour",
        "kong": "kong",
        "nginx": "nginx",
        "traefik": "traefik",
        "gke-l7-global-external-managed": "gce",
    }
    return mapping.get(gateway_class, gateway_class)


def _map_path_type(gateway_path_type: str) -> str:
    """Map Gateway API path type to Ingress pathType."""
    mapping = {
        "PathPrefix": "Prefix",
        "Exact": "Exact",
        "RegularExpression": "ImplementationSpecific",
    }
    return mapping.get(gateway_path_type, "Prefix")


def parse_gateway_resources(
    yaml_content: str,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    """
    Parse YAML content containing Gateway API resources.

    Returns tuple of (gateway, httproutes).
    """
    gateway = None
    httproutes = []

    try:
        documents = list(yaml.safe_load_all(yaml_content))
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML: {e}")

    for doc in documents:
        if not doc:
            continue
        kind = doc.get("kind", "")
        if kind == "Gateway":
            gateway = doc
        elif kind == "HTTPRoute":
            httproutes.append(doc)
        elif kind == "GRPCRoute":
            # Convert GRPCRoute to HTTPRoute-like structure for reverse conversion
            httproutes.append(_grpcroute_to_httproute_like(doc))

    return gateway, httproutes


def _grpcroute_to_httproute_like(grpcroute: dict[str, Any]) -> dict[str, Any]:
    """Convert GRPCRoute to HTTPRoute-like structure for processing."""
    # GRPCRoute has similar structure, just copy it
    return {
        "apiVersion": grpcroute.get("apiVersion"),
        "kind": "HTTPRoute",  # Treat as HTTPRoute for conversion
        "metadata": grpcroute.get("metadata", {}),
        "spec": grpcroute.get("spec", {}),
    }


def gateway_resources_to_ingress_yaml(
    gateway: dict[str, Any],
    httproutes: list[dict[str, Any]],
) -> str:
    """Convert Gateway API resources to Ingress YAML string."""
    ingress = convert_gateway_to_ingress(gateway, httproutes)
    return yaml.dump(ingress, default_flow_style=False, sort_keys=False)
