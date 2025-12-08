"""ReferenceGrant generation for cross-namespace references."""

from typing import Any


def detect_cross_namespace_refs(
    gateway: dict[str, Any],
    httproutes: list[dict[str, Any]],
    grpcroutes: list[dict[str, Any]] | None = None,
    tcproutes: list[dict[str, Any]] | None = None,
) -> list[dict[str, str]]:
    """Detect cross-namespace references that need ReferenceGrants."""
    refs: list[dict[str, str]] = []
    gateway_namespace = gateway.get("metadata", {}).get("namespace", "default")

    all_routes = httproutes + (grpcroutes or []) + (tcproutes or [])

    for route in all_routes:
        route_namespace = route.get("metadata", {}).get("namespace", "default")
        route_kind = route.get("kind", "HTTPRoute")

        # Check if route references gateway in different namespace
        for parent_ref in route.get("spec", {}).get("parentRefs", []):
            parent_ns = parent_ref.get("namespace", route_namespace)
            if parent_ns != route_namespace:
                refs.append(
                    {
                        "from_namespace": route_namespace,
                        "from_kind": route_kind,
                        "to_namespace": parent_ns,
                        "to_kind": "Gateway",
                        "to_name": parent_ref.get("name", ""),
                    }
                )

        # Check backend refs for cross-namespace services
        for rule in route.get("spec", {}).get("rules", []):
            for backend_ref in rule.get("backendRefs", []):
                backend_ns = backend_ref.get("namespace")
                if backend_ns and backend_ns != route_namespace:
                    refs.append(
                        {
                            "from_namespace": route_namespace,
                            "from_kind": route_kind,
                            "to_namespace": backend_ns,
                            "to_kind": "Service",
                            "to_name": backend_ref.get("name", ""),
                        }
                    )

    # Check TLS certificate refs
    for listener in gateway.get("spec", {}).get("listeners", []):
        tls = listener.get("tls", {})
        for cert_ref in tls.get("certificateRefs", []):
            cert_ns = cert_ref.get("namespace")
            if cert_ns and cert_ns != gateway_namespace:
                refs.append(
                    {
                        "from_namespace": gateway_namespace,
                        "from_kind": "Gateway",
                        "to_namespace": cert_ns,
                        "to_kind": cert_ref.get("kind", "Secret"),
                        "to_name": cert_ref.get("name", ""),
                    }
                )

    return refs


def create_reference_grant(
    from_namespace: str,
    from_kinds: list[str],
    to_namespace: str,
    to_kind: str,
    to_names: list[str] | None = None,
) -> dict[str, Any]:
    """Create a ReferenceGrant resource."""
    grant: dict[str, Any] = {
        "apiVersion": "gateway.networking.k8s.io/v1beta1",
        "kind": "ReferenceGrant",
        "metadata": {
            "name": f"allow-{from_namespace}-to-{to_kind.lower()}",
            "namespace": to_namespace,
        },
        "spec": {
            "from": [
                {
                    "group": "gateway.networking.k8s.io",
                    "kind": kind,
                    "namespace": from_namespace,
                }
                for kind in from_kinds
            ],
            "to": [
                {
                    "group": "" if to_kind == "Service" else "gateway.networking.k8s.io",
                    "kind": to_kind,
                }
            ],
        },
    }

    # Add specific resource names if provided
    if to_names:
        grant["spec"]["to"][0]["name"] = to_names[0] if len(to_names) == 1 else None

    return grant


def generate_reference_grants(
    gateway: dict[str, Any],
    httproutes: list[dict[str, Any]],
    grpcroutes: list[dict[str, Any]] | None = None,
    tcproutes: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Generate all required ReferenceGrant resources."""
    refs = detect_cross_namespace_refs(gateway, httproutes, grpcroutes, tcproutes)

    if not refs:
        return []

    # Group refs by (from_namespace, to_namespace, to_kind)
    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}

    for ref in refs:
        key = (ref["from_namespace"], ref["to_namespace"], ref["to_kind"])
        if key not in grouped:
            grouped[key] = {
                "from_namespace": ref["from_namespace"],
                "from_kinds": set(),
                "to_namespace": ref["to_namespace"],
                "to_kind": ref["to_kind"],
                "to_names": set(),
            }
        grouped[key]["from_kinds"].add(ref["from_kind"])
        if ref.get("to_name"):
            grouped[key]["to_names"].add(ref["to_name"])

    # Create ReferenceGrant for each group
    grants = []
    for group in grouped.values():
        grant = create_reference_grant(
            from_namespace=group["from_namespace"],
            from_kinds=list(group["from_kinds"]),
            to_namespace=group["to_namespace"],
            to_kind=group["to_kind"],
            to_names=list(group["to_names"]) if group["to_names"] else None,
        )
        grants.append(grant)

    return grants


def check_reference_grant_needed(
    route_namespace: str,
    backend_namespace: str | None,
) -> bool:
    """Check if a ReferenceGrant is needed for a backend reference."""
    if not backend_namespace:
        return False
    return route_namespace != backend_namespace
