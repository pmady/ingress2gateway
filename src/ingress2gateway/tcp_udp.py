"""TCPRoute and UDPRoute support for Gateway API."""

from typing import Any


def is_tcp_backend(ingress: dict[str, Any], service_name: str) -> bool:
    """Check if a backend is a TCP service based on annotations or port."""
    annotations = ingress.get("metadata", {}).get("annotations", {})

    # Check for TCP protocol annotation
    backend_protocol = annotations.get("nginx.ingress.kubernetes.io/backend-protocol", "").upper()
    if backend_protocol == "TCP":
        return True

    # Check for TCP stream annotation
    if annotations.get("nginx.ingress.kubernetes.io/ssl-passthrough") == "true":
        return True

    # Check for known TCP ports in service name
    tcp_indicators = ["tcp", "mysql", "postgres", "redis", "mongo", "kafka", "amqp"]
    service_lower = service_name.lower()
    return any(indicator in service_lower for indicator in tcp_indicators)


def is_udp_backend(ingress: dict[str, Any], service_name: str) -> bool:
    """Check if a backend is a UDP service based on annotations or port."""
    annotations = ingress.get("metadata", {}).get("annotations", {})

    # Check for UDP protocol annotation
    backend_protocol = annotations.get("nginx.ingress.kubernetes.io/backend-protocol", "").upper()
    if backend_protocol == "UDP":
        return True

    # Check for known UDP services in service name
    udp_indicators = ["udp", "dns", "ntp", "syslog", "tftp", "snmp"]
    service_lower = service_name.lower()
    return any(indicator in service_lower for indicator in udp_indicators)


def create_tcp_route(
    name: str,
    namespace: str,
    gateway_name: str,
    service_name: str,
    port: int,
    hostname: str | None = None,
) -> dict[str, Any]:
    """Create a TCPRoute resource."""
    tcp_route: dict[str, Any] = {
        "apiVersion": "gateway.networking.k8s.io/v1alpha2",
        "kind": "TCPRoute",
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
                    ]
                }
            ],
        },
    }

    return tcp_route


def create_udp_route(
    name: str,
    namespace: str,
    gateway_name: str,
    service_name: str,
    port: int,
) -> dict[str, Any]:
    """Create a UDPRoute resource."""
    udp_route: dict[str, Any] = {
        "apiVersion": "gateway.networking.k8s.io/v1alpha2",
        "kind": "UDPRoute",
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
                    ]
                }
            ],
        },
    }

    return udp_route


def create_tcp_listener(
    hostname: str | None,
    port: int,
) -> dict[str, Any]:
    """Create a TCP listener for Gateway."""
    listener_name = f"tcp-{port}"
    if hostname:
        safe_hostname = hostname.replace(".", "-").replace("*", "wildcard")
        listener_name = f"tcp-{safe_hostname}-{port}"

    listener: dict[str, Any] = {
        "name": listener_name,
        "port": port,
        "protocol": "TCP",
        "allowedRoutes": {
            "namespaces": {"from": "Same"},
            "kinds": [{"kind": "TCPRoute"}],
        },
    }

    if hostname:
        listener["hostname"] = hostname

    return listener


def create_udp_listener(
    port: int,
) -> dict[str, Any]:
    """Create a UDP listener for Gateway."""
    return {
        "name": f"udp-{port}",
        "port": port,
        "protocol": "UDP",
        "allowedRoutes": {
            "namespaces": {"from": "Same"},
            "kinds": [{"kind": "UDPRoute"}],
        },
    }


def detect_tcp_udp_services(ingress: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Detect TCP and UDP services from Ingress annotations."""
    tcp_services: list[dict[str, Any]] = []
    udp_services: list[dict[str, Any]] = []

    annotations = ingress.get("metadata", {}).get("annotations", {})

    # Parse nginx tcp-services annotation
    # Format: "port: namespace/service:servicePort"
    tcp_services_annotation = annotations.get("nginx.ingress.kubernetes.io/tcp-services", "")
    if tcp_services_annotation:
        for mapping in tcp_services_annotation.split(","):
            mapping = mapping.strip()
            if ":" in mapping:
                parts = mapping.split(":")
                if len(parts) >= 2:
                    port = int(parts[0].strip())
                    service_info = parts[1].strip()
                    if "/" in service_info:
                        ns, svc_port = service_info.split("/", 1)
                        if ":" in svc_port:
                            svc, svc_port_num = svc_port.split(":", 1)
                            tcp_services.append(
                                {
                                    "port": port,
                                    "namespace": ns,
                                    "service": svc,
                                    "servicePort": int(svc_port_num),
                                }
                            )

    # Parse nginx udp-services annotation
    udp_services_annotation = annotations.get("nginx.ingress.kubernetes.io/udp-services", "")
    if udp_services_annotation:
        for mapping in udp_services_annotation.split(","):
            mapping = mapping.strip()
            if ":" in mapping:
                parts = mapping.split(":")
                if len(parts) >= 2:
                    port = int(parts[0].strip())
                    service_info = parts[1].strip()
                    if "/" in service_info:
                        ns, svc_port = service_info.split("/", 1)
                        if ":" in svc_port:
                            svc, svc_port_num = svc_port.split(":", 1)
                            udp_services.append(
                                {
                                    "port": port,
                                    "namespace": ns,
                                    "service": svc,
                                    "servicePort": int(svc_port_num),
                                }
                            )

    return {"tcp": tcp_services, "udp": udp_services}
