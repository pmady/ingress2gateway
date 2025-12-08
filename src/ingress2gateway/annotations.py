"""Annotation parsing for various ingress controllers."""

from typing import Any

# Nginx Ingress annotations mapping
NGINX_ANNOTATIONS = {
    "nginx.ingress.kubernetes.io/rewrite-target": "url_rewrite",
    "nginx.ingress.kubernetes.io/ssl-redirect": "ssl_redirect",
    "nginx.ingress.kubernetes.io/force-ssl-redirect": "ssl_redirect",
    "nginx.ingress.kubernetes.io/proxy-body-size": "request_body_size",
    "nginx.ingress.kubernetes.io/proxy-connect-timeout": "connect_timeout",
    "nginx.ingress.kubernetes.io/proxy-read-timeout": "read_timeout",
    "nginx.ingress.kubernetes.io/proxy-send-timeout": "send_timeout",
    "nginx.ingress.kubernetes.io/limit-rps": "rate_limit_rps",
    "nginx.ingress.kubernetes.io/limit-connections": "rate_limit_connections",
    "nginx.ingress.kubernetes.io/whitelist-source-range": "ip_whitelist",
    "nginx.ingress.kubernetes.io/cors-allow-origin": "cors_origins",
    "nginx.ingress.kubernetes.io/cors-allow-methods": "cors_methods",
    "nginx.ingress.kubernetes.io/cors-allow-headers": "cors_headers",
    "nginx.ingress.kubernetes.io/enable-cors": "cors_enabled",
    "nginx.ingress.kubernetes.io/app-root": "app_root",
    "nginx.ingress.kubernetes.io/backend-protocol": "backend_protocol",
    "nginx.ingress.kubernetes.io/canary": "canary",
    "nginx.ingress.kubernetes.io/canary-weight": "canary_weight",
}

# Traefik annotations mapping
TRAEFIK_ANNOTATIONS = {
    "traefik.ingress.kubernetes.io/router.middlewares": "middlewares",
    "traefik.ingress.kubernetes.io/router.entrypoints": "entrypoints",
    "traefik.ingress.kubernetes.io/router.tls": "tls_enabled",
    "traefik.ingress.kubernetes.io/router.priority": "priority",
}

# Istio annotations mapping
ISTIO_ANNOTATIONS = {
    "kubernetes.io/ingress.class": "ingress_class",
    "istio.io/rev": "istio_revision",
}


def parse_annotations(annotations: dict[str, str]) -> dict[str, Any]:
    """
    Parse ingress annotations and return structured configuration.

    Returns a dictionary with parsed annotation values.
    """
    if not annotations:
        return {}

    result = {
        "filters": [],
        "warnings": [],
        "unsupported": [],
    }

    for key, value in annotations.items():
        # Nginx annotations
        if key in NGINX_ANNOTATIONS:
            _parse_nginx_annotation(key, value, result)
        # Traefik annotations
        elif key in TRAEFIK_ANNOTATIONS:
            _parse_traefik_annotation(key, value, result)
        # Istio annotations
        elif key in ISTIO_ANNOTATIONS:
            _parse_istio_annotation(key, value, result)
        # Unknown annotations
        elif any(
            prefix in key for prefix in ["nginx.", "traefik.", "istio.", "kubernetes.io/ingress"]
        ):
            result["unsupported"].append({"annotation": key, "value": value})

    return result


def _parse_nginx_annotation(key: str, value: str, result: dict[str, Any]) -> None:
    """Parse nginx-specific annotations."""
    annotation_type = NGINX_ANNOTATIONS[key]

    if annotation_type == "url_rewrite":
        result["filters"].append(
            {
                "type": "URLRewrite",
                "urlRewrite": {"path": {"type": "ReplacePrefixMatch", "replacePrefixMatch": value}},
            }
        )
    elif annotation_type == "ssl_redirect":
        if value.lower() in ("true", "yes", "1"):
            result["filters"].append(
                {
                    "type": "RequestRedirect",
                    "requestRedirect": {"scheme": "https", "statusCode": 301},
                }
            )
    elif annotation_type == "backend_protocol":
        result["backend_protocol"] = value.upper()
    elif annotation_type == "cors_enabled":
        if value.lower() in ("true", "yes", "1"):
            result["cors_enabled"] = True
    elif annotation_type == "cors_origins":
        result["cors_origins"] = value.split(",")
    elif annotation_type == "cors_methods":
        result["cors_methods"] = value.split(",")
    elif annotation_type == "cors_headers":
        result["cors_headers"] = value.split(",")
    elif annotation_type == "rate_limit_rps":
        result["warnings"].append(
            f"Rate limiting ({value} rps) requires provider-specific configuration"
        )
    elif annotation_type == "ip_whitelist":
        result["warnings"].append(
            f"IP whitelist ({value}) requires AuthorizationPolicy or provider config"
        )
    elif annotation_type == "canary":
        result["canary"] = value.lower() in ("true", "yes", "1")
    elif annotation_type == "canary_weight":
        result["canary_weight"] = int(value)
    else:
        result["warnings"].append(f"Annotation {key}={value} noted but not directly converted")


def _parse_traefik_annotation(key: str, value: str, result: dict[str, Any]) -> None:
    """Parse traefik-specific annotations."""
    annotation_type = TRAEFIK_ANNOTATIONS[key]

    if annotation_type == "middlewares":
        result["warnings"].append(
            f"Traefik middlewares ({value}) require manual conversion to Gateway API filters"
        )
    elif annotation_type == "priority":
        result["warnings"].append(f"Route priority ({value}) not directly supported in Gateway API")
    else:
        result["unsupported"].append({"annotation": key, "value": value})


def _parse_istio_annotation(key: str, value: str, result: dict[str, Any]) -> None:
    """Parse istio-specific annotations."""
    annotation_type = ISTIO_ANNOTATIONS[key]

    if annotation_type == "ingress_class":
        result["ingress_class"] = value
    elif annotation_type == "istio_revision":
        result["istio_revision"] = value


def annotations_to_filters(parsed: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert parsed annotations to Gateway API HTTPRoute filters."""
    return parsed.get("filters", [])


def get_annotation_warnings(parsed: dict[str, Any]) -> list[str]:
    """Get warnings from annotation parsing."""
    warnings = parsed.get("warnings", [])
    for item in parsed.get("unsupported", []):
        warnings.append(f"Unsupported annotation: {item['annotation']}={item['value']}")
    return warnings
