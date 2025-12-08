"""Validation for Ingress and Gateway API resources."""

from typing import Any

# Simplified schemas for validation
INGRESS_REQUIRED_FIELDS = ["apiVersion", "kind", "metadata", "spec"]
GATEWAY_REQUIRED_FIELDS = ["apiVersion", "kind", "metadata", "spec"]
HTTPROUTE_REQUIRED_FIELDS = ["apiVersion", "kind", "metadata", "spec"]


class ValidationError:
    """Represents a validation error."""

    def __init__(self, path: str, message: str, severity: str = "error"):
        self.path = path
        self.message = message
        self.severity = severity  # "error", "warning", "info"

    def __repr__(self) -> str:
        return f"[{self.severity.upper()}] {self.path}: {self.message}"

    def to_dict(self) -> dict[str, str]:
        return {"path": self.path, "message": self.message, "severity": self.severity}


class ValidationResult:
    """Result of validation."""

    def __init__(self):
        self.errors: list[ValidationError] = []
        self.warnings: list[ValidationError] = []

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, path: str, message: str) -> None:
        self.errors.append(ValidationError(path, message, "error"))

    def add_warning(self, path: str, message: str) -> None:
        self.warnings.append(ValidationError(path, message, "warning"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.is_valid,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
        }


def validate_ingress(ingress: dict[str, Any]) -> ValidationResult:
    """Validate an Ingress resource."""
    result = ValidationResult()

    if not ingress:
        result.add_error("", "Empty ingress object")
        return result

    # Check required fields
    for field in INGRESS_REQUIRED_FIELDS:
        if field not in ingress:
            result.add_error(field, f"Missing required field: {field}")

    # Validate apiVersion
    api_version = ingress.get("apiVersion", "")
    if api_version not in [
        "networking.k8s.io/v1",
        "networking.k8s.io/v1beta1",
        "extensions/v1beta1",
    ]:
        result.add_warning("apiVersion", f"Unexpected apiVersion: {api_version}")

    # Validate kind
    kind = ingress.get("kind", "")
    if kind != "Ingress":
        result.add_error("kind", f"Expected 'Ingress', got '{kind}'")

    # Validate metadata
    metadata = ingress.get("metadata", {})
    if not metadata.get("name"):
        result.add_error("metadata.name", "Missing required field: name")

    # Validate spec
    spec = ingress.get("spec", {})
    if not spec:
        result.add_warning("spec", "Empty spec")
    else:
        # Check for rules or defaultBackend
        if not spec.get("rules") and not spec.get("defaultBackend"):
            result.add_warning("spec", "No rules or defaultBackend defined")

        # Validate rules
        for i, rule in enumerate(spec.get("rules", [])):
            _validate_ingress_rule(rule, f"spec.rules[{i}]", result)

        # Validate TLS
        for i, tls in enumerate(spec.get("tls", [])):
            _validate_ingress_tls(tls, f"spec.tls[{i}]", result)

    return result


def _validate_ingress_rule(rule: dict[str, Any], path: str, result: ValidationResult) -> None:
    """Validate an Ingress rule."""
    http = rule.get("http", {})
    if not http:
        result.add_warning(path, "Rule has no http configuration")
        return

    paths = http.get("paths", [])
    if not paths:
        result.add_warning(f"{path}.http", "No paths defined")

    for i, path_config in enumerate(paths):
        backend = path_config.get("backend", {})
        if not backend:
            result.add_error(f"{path}.http.paths[{i}]", "Missing backend")
        else:
            service = backend.get("service", backend)
            if not service.get("name"):
                result.add_error(f"{path}.http.paths[{i}].backend", "Missing service name")


def _validate_ingress_tls(tls: dict[str, Any], path: str, result: ValidationResult) -> None:
    """Validate TLS configuration."""
    if not tls.get("hosts"):
        result.add_warning(path, "TLS configuration has no hosts")
    if not tls.get("secretName"):
        result.add_warning(path, "TLS configuration has no secretName")


def validate_gateway(gateway: dict[str, Any]) -> ValidationResult:
    """Validate a Gateway resource."""
    result = ValidationResult()

    if not gateway:
        result.add_error("", "Empty gateway object")
        return result

    # Check required fields
    for field in GATEWAY_REQUIRED_FIELDS:
        if field not in gateway:
            result.add_error(field, f"Missing required field: {field}")

    # Validate apiVersion
    api_version = gateway.get("apiVersion", "")
    if not api_version.startswith("gateway.networking.k8s.io/"):
        result.add_warning("apiVersion", f"Unexpected apiVersion: {api_version}")

    # Validate kind
    kind = gateway.get("kind", "")
    if kind != "Gateway":
        result.add_error("kind", f"Expected 'Gateway', got '{kind}'")

    # Validate spec
    spec = gateway.get("spec", {})
    if not spec.get("gatewayClassName"):
        result.add_error("spec.gatewayClassName", "Missing gatewayClassName")

    listeners = spec.get("listeners", [])
    if not listeners:
        result.add_warning("spec.listeners", "No listeners defined")

    for i, listener in enumerate(listeners):
        if not listener.get("name"):
            result.add_error(f"spec.listeners[{i}].name", "Missing listener name")
        if not listener.get("port"):
            result.add_error(f"spec.listeners[{i}].port", "Missing listener port")
        if not listener.get("protocol"):
            result.add_error(f"spec.listeners[{i}].protocol", "Missing listener protocol")

    return result


def validate_httproute(route: dict[str, Any]) -> ValidationResult:
    """Validate an HTTPRoute resource."""
    result = ValidationResult()

    if not route:
        result.add_error("", "Empty HTTPRoute object")
        return result

    # Check required fields
    for field in HTTPROUTE_REQUIRED_FIELDS:
        if field not in route:
            result.add_error(field, f"Missing required field: {field}")

    # Validate kind
    kind = route.get("kind", "")
    if kind != "HTTPRoute":
        result.add_error("kind", f"Expected 'HTTPRoute', got '{kind}'")

    # Validate spec
    spec = route.get("spec", {})
    if not spec.get("parentRefs"):
        result.add_error("spec.parentRefs", "Missing parentRefs")

    rules = spec.get("rules", [])
    if not rules:
        result.add_warning("spec.rules", "No rules defined")

    for i, rule in enumerate(rules):
        backend_refs = rule.get("backendRefs", [])
        if not backend_refs:
            result.add_warning(f"spec.rules[{i}]", "No backendRefs defined")

    return result


def validate_conversion_output(resources: dict[str, Any]) -> ValidationResult:
    """Validate the complete conversion output."""
    result = ValidationResult()

    # Validate gateway
    gateway = resources.get("gateway")
    if gateway:
        gateway_result = validate_gateway(gateway)
        result.errors.extend(gateway_result.errors)
        result.warnings.extend(gateway_result.warnings)

    # Validate HTTPRoutes
    for i, route in enumerate(resources.get("httproutes", [])):
        route_result = validate_httproute(route)
        for error in route_result.errors:
            error.path = f"httproutes[{i}].{error.path}"
            result.errors.append(error)
        for warning in route_result.warnings:
            warning.path = f"httproutes[{i}].{warning.path}"
            result.warnings.append(warning)

    # Validate GRPCRoutes
    for i, route in enumerate(resources.get("grpcroutes", [])):
        if route.get("kind") != "GRPCRoute":
            result.add_error(f"grpcroutes[{i}].kind", "Expected 'GRPCRoute'")

    return result
