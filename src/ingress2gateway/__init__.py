"""Ingress to Gateway API converter."""

__version__ = "0.3.0"

from .alb_gce import parse_alb_annotations, parse_cloud_annotations, parse_gce_annotations
from .annotations import get_annotation_warnings, parse_annotations
from .converter import convert_ingress_to_gateway, parse_ingress, resources_to_yaml
from .grpc import create_grpc_route, is_grpc_backend
from .providers import apply_provider_defaults, get_provider, list_providers
from .reference_grant import create_reference_grant, generate_reference_grants
from .report import generate_diff_summary, generate_migration_report
from .reverse import convert_gateway_to_ingress, gateway_resources_to_ingress_yaml
from .tcp_udp import create_tcp_route, create_udp_route, is_tcp_backend, is_udp_backend
from .validation import validate_gateway, validate_httproute, validate_ingress

__all__ = [
    "__version__",
    # Annotations
    "parse_annotations",
    "get_annotation_warnings",
    "parse_alb_annotations",
    "parse_gce_annotations",
    "parse_cloud_annotations",
    # Converter
    "convert_ingress_to_gateway",
    "parse_ingress",
    "resources_to_yaml",
    # gRPC
    "create_grpc_route",
    "is_grpc_backend",
    # TCP/UDP
    "create_tcp_route",
    "create_udp_route",
    "is_tcp_backend",
    "is_udp_backend",
    # Providers
    "get_provider",
    "list_providers",
    "apply_provider_defaults",
    # Reference Grants
    "create_reference_grant",
    "generate_reference_grants",
    # Reports
    "generate_migration_report",
    "generate_diff_summary",
    # Reverse conversion
    "convert_gateway_to_ingress",
    "gateway_resources_to_ingress_yaml",
    # Validation
    "validate_ingress",
    "validate_gateway",
    "validate_httproute",
]
