"""Ingress to Gateway API converter."""

__version__ = "0.2.0"

from .annotations import get_annotation_warnings, parse_annotations
from .converter import convert_ingress_to_gateway, parse_ingress, resources_to_yaml
from .grpc import create_grpc_route, is_grpc_backend
from .providers import apply_provider_defaults, get_provider, list_providers
from .report import generate_diff_summary, generate_migration_report
from .reverse import convert_gateway_to_ingress, gateway_resources_to_ingress_yaml
from .validation import validate_gateway, validate_httproute, validate_ingress

__all__ = [
    "__version__",
    "parse_annotations",
    "get_annotation_warnings",
    "convert_ingress_to_gateway",
    "parse_ingress",
    "resources_to_yaml",
    "create_grpc_route",
    "is_grpc_backend",
    "get_provider",
    "list_providers",
    "apply_provider_defaults",
    "generate_migration_report",
    "generate_diff_summary",
    "convert_gateway_to_ingress",
    "gateway_resources_to_ingress_yaml",
    "validate_ingress",
    "validate_gateway",
    "validate_httproute",
]
