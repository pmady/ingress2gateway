"""Core converter logic for Ingress to Gateway API."""

from typing import Any

import yaml


def _parse_port(port_value: Any) -> int:
    """Parse port value to integer, defaulting to 80."""
    if port_value and str(port_value).isdigit():
        return int(port_value)
    return 80


def parse_ingress(ingress_yaml: str) -> dict[str, Any]:
    """Parse Ingress YAML string into a dictionary."""
    try:
        return yaml.safe_load(ingress_yaml)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML: {e}")


def convert_ingress_to_gateway(ingress: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """
    Convert a Kubernetes Ingress object to Gateway API resources.

    Returns a dictionary with 'gateway' and 'httproutes' keys.
    """
    if not ingress:
        raise ValueError("Empty ingress object")

    kind = ingress.get("kind", "")
    if kind != "Ingress":
        raise ValueError(f"Expected kind 'Ingress', got '{kind}'")

    metadata = ingress.get("metadata", {})
    name = metadata.get("name", "converted-gateway")
    namespace = metadata.get("namespace", "default")

    spec = ingress.get("spec", {})
    ingress_class = spec.get("ingressClassName", "")

    # Extract TLS configuration
    tls_hosts = set()
    tls_secrets = {}
    for tls in spec.get("tls", []):
        secret_name = tls.get("secretName", "")
        for host in tls.get("hosts", []):
            tls_hosts.add(host)
            if secret_name:
                tls_secrets[host] = secret_name

    # Build Gateway listeners
    listeners = []
    all_hosts = set()

    for rule in spec.get("rules", []):
        host = rule.get("host", "*")
        all_hosts.add(host)

    # Add HTTPS listeners for TLS hosts
    for host in tls_hosts:
        listener = {
            "name": f"https-{host.replace('.', '-').replace('*', 'wildcard')}",
            "hostname": host if host != "*" else None,
            "port": 443,
            "protocol": "HTTPS",
            "tls": {
                "mode": "Terminate",
                "certificateRefs": [
                    {
                        "kind": "Secret",
                        "name": tls_secrets.get(host, f"{name}-tls"),
                    }
                ],
            },
            "allowedRoutes": {
                "namespaces": {"from": "Same"},
            },
        }
        if listener["hostname"] is None:
            del listener["hostname"]
        listeners.append(listener)

    # Add HTTP listeners for non-TLS hosts
    http_hosts = all_hosts - tls_hosts
    if http_hosts or not tls_hosts:
        for host in http_hosts or ["*"]:
            listener = {
                "name": f"http-{host.replace('.', '-').replace('*', 'wildcard')}",
                "hostname": host if host != "*" else None,
                "port": 80,
                "protocol": "HTTP",
                "allowedRoutes": {
                    "namespaces": {"from": "Same"},
                },
            }
            if listener["hostname"] is None:
                del listener["hostname"]
            listeners.append(listener)

    # If no listeners, add a default HTTP listener
    if not listeners:
        listeners.append(
            {
                "name": "http",
                "port": 80,
                "protocol": "HTTP",
                "allowedRoutes": {
                    "namespaces": {"from": "Same"},
                },
            }
        )

    # Build Gateway resource
    gateway = {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "Gateway",
        "metadata": {
            "name": name,
            "namespace": namespace,
        },
        "spec": {
            "gatewayClassName": ingress_class or "istio",
            "listeners": listeners,
        },
    }

    # Build HTTPRoute resources
    httproutes = []

    for rule in spec.get("rules", []):
        host = rule.get("host")
        http = rule.get("http", {})
        paths = http.get("paths", [])

        rules = []
        for path_config in paths:
            path = path_config.get("path", "/")
            path_type = path_config.get("pathType", "Prefix")
            backend = path_config.get("backend", {})

            # Handle both old and new Ingress backend formats
            service = backend.get("service", backend)
            service_name = service.get("name", "")

            # Handle port - can be number or name
            port = service.get("port", {})
            if isinstance(port, dict):
                port_value = port.get("number") or port.get("name")
            else:
                port_value = port or service.get("servicePort")

            # Convert pathType to Gateway API match type
            is_prefix = path_type in ["Prefix", "ImplementationSpecific"]
            match_type = "PathPrefix" if is_prefix else "Exact"

            rule_config = {
                "matches": [
                    {
                        "path": {
                            "type": match_type,
                            "value": path,
                        },
                    }
                ],
                "backendRefs": [
                    {
                        "name": service_name,
                        "port": _parse_port(port_value),
                    }
                ],
            }
            rules.append(rule_config)

        if rules:
            httproute = {
                "apiVersion": "gateway.networking.k8s.io/v1",
                "kind": "HTTPRoute",
                "metadata": {
                    "name": f"{name}-{host.replace('.', '-') if host else 'default'}",
                    "namespace": namespace,
                },
                "spec": {
                    "parentRefs": [
                        {
                            "name": name,
                            "namespace": namespace,
                        }
                    ],
                    "rules": rules,
                },
            }

            if host:
                httproute["spec"]["hostnames"] = [host]

            httproutes.append(httproute)

    # Handle default backend if present
    default_backend = spec.get("defaultBackend", {})
    if default_backend:
        service = default_backend.get("service", default_backend)
        service_name = service.get("name", "")
        port = service.get("port", {})
        if isinstance(port, dict):
            port_value = port.get("number") or port.get("name")
        else:
            port_value = port or service.get("servicePort")

        if service_name:
            default_route = {
                "apiVersion": "gateway.networking.k8s.io/v1",
                "kind": "HTTPRoute",
                "metadata": {
                    "name": f"{name}-default",
                    "namespace": namespace,
                },
                "spec": {
                    "parentRefs": [
                        {
                            "name": name,
                            "namespace": namespace,
                        }
                    ],
                    "rules": [
                        {
                            "matches": [
                                {
                                    "path": {
                                        "type": "PathPrefix",
                                        "value": "/",
                                    },
                                }
                            ],
                            "backendRefs": [
                                {
                                    "name": service_name,
                                    "port": _parse_port(port_value),
                                }
                            ],
                        }
                    ],
                },
            }
            httproutes.append(default_route)

    return {
        "gateway": gateway,
        "httproutes": httproutes,
    }


def resources_to_yaml(resources: dict[str, Any]) -> str:
    """Convert Gateway API resources to YAML string."""
    documents = [resources["gateway"]] + resources["httproutes"]
    return yaml.dump_all(documents, default_flow_style=False, sort_keys=False)
