"""GRPCRoute generation support."""

from typing import Any


def is_grpc_backend(annotations: dict[str, str], backend_protocol: str | None = None) -> bool:
    """
    Detect if a backend is a gRPC service.

    Checks annotations and backend protocol hints.
    """
    if backend_protocol and backend_protocol.upper() in ("GRPC", "GRPCS"):
        return True

    grpc_indicators = [
        "nginx.ingress.kubernetes.io/backend-protocol",
        "nginx.ingress.kubernetes.io/grpc-backend",
    ]

    for key in grpc_indicators:
        value = annotations.get(key, "").upper()
        if value in ("GRPC", "GRPCS", "TRUE", "YES"):
            return True

    return False


def create_grpc_route(
    name: str,
    namespace: str,
    gateway_name: str,
    host: str | None,
    service_name: str,
    port: int,
    method_match: str | None = None,
) -> dict[str, Any]:
    """
    Create a GRPCRoute resource.

    Args:
        name: Name for the GRPCRoute
        namespace: Kubernetes namespace
        gateway_name: Name of the parent Gateway
        host: Optional hostname
        service_name: Backend service name
        port: Backend service port
        method_match: Optional gRPC method pattern (e.g., "mypackage.MyService/MyMethod")
    """
    grpc_route: dict[str, Any] = {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "GRPCRoute",
        "metadata": {
            "name": name,
            "namespace": namespace,
        },
        "spec": {
            "parentRefs": [
                {
                    "name": gateway_name,
                    "namespace": namespace,
                }
            ],
            "rules": [
                {
                    "backendRefs": [
                        {
                            "name": service_name,
                            "port": port,
                        }
                    ],
                }
            ],
        },
    }

    if host:
        grpc_route["spec"]["hostnames"] = [host]

    if method_match:
        # Parse method match pattern
        if "/" in method_match:
            service, method = method_match.rsplit("/", 1)
            grpc_route["spec"]["rules"][0]["matches"] = [
                {
                    "method": {
                        "service": service,
                        "method": method,
                    }
                }
            ]

    return grpc_route


def convert_to_grpc_routes(
    httproutes: list[dict[str, Any]],
    annotations: dict[str, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Convert HTTPRoutes to GRPCRoutes where appropriate.

    Returns tuple of (remaining_httproutes, grpc_routes).
    """
    if not is_grpc_backend(annotations):
        return httproutes, []

    grpc_routes = []
    remaining_http = []

    for route in httproutes:
        metadata = route.get("metadata", {})
        spec = route.get("spec", {})

        # Create GRPCRoute from HTTPRoute
        grpc_route = create_grpc_route(
            name=metadata.get("name", "grpc-route"),
            namespace=metadata.get("namespace", "default"),
            gateway_name=spec.get("parentRefs", [{}])[0].get("name", "gateway"),
            host=spec.get("hostnames", [None])[0] if spec.get("hostnames") else None,
            service_name=spec.get("rules", [{}])[0]
            .get("backendRefs", [{}])[0]
            .get("name", "service"),
            port=spec.get("rules", [{}])[0].get("backendRefs", [{}])[0].get("port", 80),
        )
        grpc_routes.append(grpc_route)

    return remaining_http, grpc_routes
