"""AWS ALB and GCE Ingress annotation support."""

from typing import Any

# AWS ALB Ingress Controller annotations
ALB_ANNOTATION_MAP = {
    "alb.ingress.kubernetes.io/scheme": {
        "description": "Load balancer scheme (internal/internet-facing)",
        "gateway_equivalent": "Gateway infrastructure annotation",
    },
    "alb.ingress.kubernetes.io/target-type": {
        "description": "Target type (ip/instance)",
        "gateway_equivalent": "Provider-specific configuration",
    },
    "alb.ingress.kubernetes.io/listen-ports": {
        "description": "Listener ports configuration",
        "gateway_equivalent": "Gateway.spec.listeners",
    },
    "alb.ingress.kubernetes.io/certificate-arn": {
        "description": "ACM certificate ARN",
        "gateway_equivalent": "Gateway.spec.listeners[].tls.certificateRefs",
    },
    "alb.ingress.kubernetes.io/ssl-redirect": {
        "description": "SSL redirect port",
        "gateway_equivalent": "HTTPRoute.filters[].requestRedirect",
    },
    "alb.ingress.kubernetes.io/healthcheck-path": {
        "description": "Health check path",
        "gateway_equivalent": "HealthCheckPolicy (provider-specific)",
    },
    "alb.ingress.kubernetes.io/healthcheck-interval-seconds": {
        "description": "Health check interval",
        "gateway_equivalent": "HealthCheckPolicy (provider-specific)",
    },
    "alb.ingress.kubernetes.io/backend-protocol": {
        "description": "Backend protocol (HTTP/HTTPS/GRPC)",
        "gateway_equivalent": "BackendTLSPolicy or GRPCRoute",
    },
    "alb.ingress.kubernetes.io/actions.*": {
        "description": "Custom actions (redirect, fixed-response)",
        "gateway_equivalent": "HTTPRoute.filters",
    },
    "alb.ingress.kubernetes.io/conditions.*": {
        "description": "Custom routing conditions",
        "gateway_equivalent": "HTTPRoute.matches",
    },
    "alb.ingress.kubernetes.io/group.name": {
        "description": "Ingress group name",
        "gateway_equivalent": "Multiple HTTPRoutes with same parentRef",
    },
    "alb.ingress.kubernetes.io/group.order": {
        "description": "Ingress group order",
        "gateway_equivalent": "HTTPRoute ordering (not directly supported)",
    },
    "alb.ingress.kubernetes.io/load-balancer-attributes": {
        "description": "ALB attributes",
        "gateway_equivalent": "Provider-specific Gateway annotations",
    },
    "alb.ingress.kubernetes.io/target-group-attributes": {
        "description": "Target group attributes",
        "gateway_equivalent": "Provider-specific BackendPolicy",
    },
    "alb.ingress.kubernetes.io/subnets": {
        "description": "Subnet IDs or names",
        "gateway_equivalent": "GatewayClass parameters or Gateway annotation",
    },
    "alb.ingress.kubernetes.io/security-groups": {
        "description": "Security group IDs",
        "gateway_equivalent": "GatewayClass parameters or Gateway annotation",
    },
    "alb.ingress.kubernetes.io/wafv2-acl-arn": {
        "description": "WAF ACL ARN",
        "gateway_equivalent": "Provider-specific policy",
    },
}

# GCE Ingress annotations
GCE_ANNOTATION_MAP = {
    "kubernetes.io/ingress.class": {
        "description": "Ingress class (gce, gce-internal)",
        "gateway_equivalent": "Gateway.spec.gatewayClassName",
    },
    "kubernetes.io/ingress.global-static-ip-name": {
        "description": "Global static IP name",
        "gateway_equivalent": "Gateway.spec.addresses",
    },
    "kubernetes.io/ingress.regional-static-ip-name": {
        "description": "Regional static IP name",
        "gateway_equivalent": "Gateway.spec.addresses",
    },
    "ingress.gcp.kubernetes.io/pre-shared-cert": {
        "description": "Pre-shared SSL certificate",
        "gateway_equivalent": "Gateway.spec.listeners[].tls",
    },
    "networking.gke.io/managed-certificates": {
        "description": "GKE managed certificates",
        "gateway_equivalent": "Gateway.spec.listeners[].tls.certificateRefs",
    },
    "networking.gke.io/v1beta1.FrontendConfig": {
        "description": "Frontend configuration",
        "gateway_equivalent": "Gateway configuration + policies",
    },
    "cloud.google.com/backend-config": {
        "description": "Backend configuration",
        "gateway_equivalent": "BackendPolicy (provider-specific)",
    },
    "cloud.google.com/neg": {
        "description": "Network Endpoint Groups",
        "gateway_equivalent": "Provider-specific backend configuration",
    },
    "cloud.google.com/app-protocols": {
        "description": "Application protocols per port",
        "gateway_equivalent": "BackendTLSPolicy or route type",
    },
}


def parse_alb_annotations(annotations: dict[str, str]) -> dict[str, Any]:
    """Parse AWS ALB Ingress annotations."""
    result: dict[str, Any] = {
        "filters": [],
        "gateway_config": {},
        "warnings": [],
        "unsupported": [],
    }

    for key, value in annotations.items():
        if not key.startswith("alb.ingress.kubernetes.io/"):
            continue

        annotation_name = key.replace("alb.ingress.kubernetes.io/", "")

        # Handle SSL redirect
        if annotation_name == "ssl-redirect":
            result["filters"].append(
                {
                    "type": "RequestRedirect",
                    "requestRedirect": {
                        "scheme": "https",
                        "statusCode": 301,
                    },
                }
            )
            continue

        # Handle certificate ARN
        if annotation_name == "certificate-arn":
            result["gateway_config"]["certificateArn"] = value
            result["warnings"].append(
                f"ACM certificate ARN '{value}' needs to be converted to "
                "Kubernetes Secret or provider-specific certificate reference"
            )
            continue

        # Handle listen-ports
        if annotation_name == "listen-ports":
            try:
                import json

                ports = json.loads(value)
                result["gateway_config"]["listenPorts"] = ports
            except json.JSONDecodeError:
                result["warnings"].append(f"Could not parse listen-ports: {value}")
            continue

        # Handle backend protocol
        if annotation_name == "backend-protocol":
            if value.upper() == "GRPC":
                result["gateway_config"]["useGrpcRoute"] = True
            elif value.upper() == "HTTPS":
                result["gateway_config"]["backendTls"] = True
            continue

        # Handle scheme
        if annotation_name == "scheme":
            result["gateway_config"]["scheme"] = value
            if value == "internal":
                result["warnings"].append(
                    "Internal load balancer requires provider-specific "
                    "GatewayClass or Gateway annotation"
                )
            continue

        # Handle target-type
        if annotation_name == "target-type":
            result["gateway_config"]["targetType"] = value
            result["warnings"].append(f"Target type '{value}' is provider-specific configuration")
            continue

        # Handle group.name (Ingress grouping)
        if annotation_name == "group.name":
            result["gateway_config"]["groupName"] = value
            result["warnings"].append(
                f"Ingress group '{value}' - all Ingresses in this group "
                "should reference the same Gateway"
            )
            continue

        # Handle actions (complex routing)
        if annotation_name.startswith("actions."):
            action_name = annotation_name.replace("actions.", "")
            result["warnings"].append(
                f"ALB action '{action_name}' requires manual conversion to HTTPRoute filters"
            )
            result["unsupported"].append(
                {"annotation": key, "value": value, "reason": "Complex ALB action"}
            )
            continue

        # Handle conditions (complex routing)
        if annotation_name.startswith("conditions."):
            condition_name = annotation_name.replace("conditions.", "")
            result["warnings"].append(
                f"ALB condition '{condition_name}' requires manual conversion to HTTPRoute matches"
            )
            result["unsupported"].append(
                {"annotation": key, "value": value, "reason": "Complex ALB condition"}
            )
            continue

        # Track other annotations as potentially unsupported
        if annotation_name in ALB_ANNOTATION_MAP:
            info = ALB_ANNOTATION_MAP[annotation_name]
            result["warnings"].append(f"{info['description']}: {info['gateway_equivalent']}")
        else:
            result["unsupported"].append(
                {"annotation": key, "value": value, "reason": "Unknown ALB annotation"}
            )

    return result


def parse_gce_annotations(annotations: dict[str, str]) -> dict[str, Any]:
    """Parse GCE Ingress annotations."""
    result: dict[str, Any] = {
        "filters": [],
        "gateway_config": {},
        "warnings": [],
        "unsupported": [],
    }

    for key, value in annotations.items():
        # Handle kubernetes.io annotations
        if key == "kubernetes.io/ingress.class":
            if value in ("gce", "gce-internal"):
                result["gateway_config"]["gatewayClassName"] = "gke-l7-global-external-managed"
                if value == "gce-internal":
                    result["gateway_config"]["gatewayClassName"] = (
                        "gke-l7-rilb"  # Regional internal LB
                    )
            continue

        if key == "kubernetes.io/ingress.global-static-ip-name":
            result["gateway_config"]["addresses"] = [{"type": "NamedAddress", "value": value}]
            continue

        if key == "kubernetes.io/ingress.regional-static-ip-name":
            result["gateway_config"]["addresses"] = [{"type": "NamedAddress", "value": value}]
            result["warnings"].append("Regional static IP requires regional Gateway class")
            continue

        # Handle ingress.gcp.kubernetes.io annotations
        if key == "ingress.gcp.kubernetes.io/pre-shared-cert":
            certs = [c.strip() for c in value.split(",")]
            result["gateway_config"]["preSharedCerts"] = certs
            result["warnings"].append(
                f"Pre-shared certificates {certs} need to be referenced in Gateway TLS config"
            )
            continue

        # Handle networking.gke.io annotations
        if key == "networking.gke.io/managed-certificates":
            certs = [c.strip() for c in value.split(",")]
            result["gateway_config"]["managedCertificates"] = certs
            result["warnings"].append(
                f"Managed certificates {certs} should be referenced via "
                "ManagedCertificate resources in Gateway"
            )
            continue

        if key == "networking.gke.io/v1beta1.FrontendConfig":
            result["gateway_config"]["frontendConfig"] = value
            result["warnings"].append(
                f"FrontendConfig '{value}' features need manual migration to Gateway policies"
            )
            continue

        # Handle cloud.google.com annotations
        if key == "cloud.google.com/backend-config":
            result["gateway_config"]["backendConfig"] = value
            result["warnings"].append(
                f"BackendConfig '{value}' features need manual migration to "
                "GCPBackendPolicy or HealthCheckPolicy"
            )
            continue

        if key == "cloud.google.com/neg":
            result["gateway_config"]["neg"] = value
            result["warnings"].append("NEG configuration is typically automatic with GKE Gateway")
            continue

        if key == "cloud.google.com/app-protocols":
            try:
                import json

                protocols = json.loads(value)
                result["gateway_config"]["appProtocols"] = protocols
                for port, protocol in protocols.items():
                    if protocol.upper() == "HTTP2":
                        result["warnings"].append(
                            f"Port {port} uses HTTP2 - ensure backend supports it"
                        )
                    elif protocol.upper() == "GRPC":
                        result["gateway_config"]["useGrpcRoute"] = True
            except json.JSONDecodeError:
                result["warnings"].append(f"Could not parse app-protocols: {value}")
            continue

        # Track GCE-specific annotations
        if key.startswith(("ingress.gcp.", "networking.gke.", "cloud.google.com/")):
            result["unsupported"].append(
                {"annotation": key, "value": value, "reason": "GCE-specific annotation"}
            )

    return result


def parse_cloud_annotations(annotations: dict[str, str]) -> dict[str, Any]:
    """Parse both AWS ALB and GCE annotations."""
    alb_result = parse_alb_annotations(annotations)
    gce_result = parse_gce_annotations(annotations)

    # Merge results
    return {
        "filters": alb_result["filters"] + gce_result["filters"],
        "gateway_config": {**alb_result["gateway_config"], **gce_result["gateway_config"]},
        "warnings": alb_result["warnings"] + gce_result["warnings"],
        "unsupported": alb_result["unsupported"] + gce_result["unsupported"],
    }


def get_alb_annotation_docs() -> list[dict[str, str]]:
    """Get documentation for ALB annotations."""
    return [
        {"annotation": f"alb.ingress.kubernetes.io/{k}", **v} for k, v in ALB_ANNOTATION_MAP.items()
    ]


def get_gce_annotation_docs() -> list[dict[str, str]]:
    """Get documentation for GCE annotations."""
    return [{"annotation": k, **v} for k, v in GCE_ANNOTATION_MAP.items()]
