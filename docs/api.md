# API Reference

## Python API

### Converter Module

The core conversion logic is in `ingress2gateway.converter`.

#### `parse_ingress(ingress_yaml: str) -> dict`

Parse an Ingress YAML string into a Python dictionary.

```python
from ingress2gateway import parse_ingress

ingress = parse_ingress("""
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example
spec:
  rules:
    - host: example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-service
                port:
                  number: 80
""")
```

**Raises:** `ValueError` if the YAML is invalid.

#### `convert_ingress_to_gateway(ingress: dict) -> dict`

Convert an Ingress dictionary to Gateway API resources.

```python
from ingress2gateway import convert_ingress_to_gateway

resources = convert_ingress_to_gateway(ingress)
# resources["gateway"] - Gateway resource
# resources["httproutes"] - List of HTTPRoute resources
```

**Raises:** `ValueError` if the ingress is empty or has wrong kind.

#### `resources_to_yaml(resources: dict) -> str`

Convert Gateway API resources to a multi-document YAML string.

```python
from ingress2gateway import resources_to_yaml

yaml_output = resources_to_yaml(resources)
```

### Annotations Module

Parse and handle Ingress annotations.

#### `parse_annotations(annotations: dict) -> dict`

Parse Ingress annotations into structured configuration.

```python
from ingress2gateway import parse_annotations

annotations = {"nginx.ingress.kubernetes.io/rewrite-target": "/api"}
parsed = parse_annotations(annotations)
# parsed["filters"] - Gateway API filters
# parsed["warnings"] - Conversion warnings
# parsed["unsupported"] - Unsupported annotations
```

#### `get_annotation_warnings(parsed: dict) -> list[str]`

Get warning messages from parsed annotations.

```python
from ingress2gateway import get_annotation_warnings

warnings = get_annotation_warnings(parsed)
```

### Providers Module

Provider presets for different Gateway implementations.

#### `list_providers() -> list[dict]`

List all available provider presets.

```python
from ingress2gateway import list_providers

providers = list_providers()
for p in providers:
    print(f"{p['id']}: {p['name']} ({p['gateway_class']})")
```

#### `get_provider(provider_id: str) -> dict`

Get configuration for a specific provider.

```python
from ingress2gateway import get_provider

config = get_provider("istio")
# config["name"] - Provider name
# config["gateway_class"] - Gateway class name
# config["supports_grpc"] - gRPC support
# config["supports_tcp"] - TCP support
```

#### `apply_provider_defaults(gateway: dict, provider_id: str) -> dict`

Apply provider-specific defaults to a Gateway resource.

```python
from ingress2gateway import apply_provider_defaults

gateway = apply_provider_defaults(resources["gateway"], "contour")
```

### Validation Module

Validate Ingress and Gateway API resources.

#### `validate_ingress(ingress: dict) -> ValidationResult`

Validate an Ingress resource.

```python
from ingress2gateway import validate_ingress

result = validate_ingress(ingress)
if result.is_valid:
    print("Valid!")
else:
    for error in result.errors:
        print(f"{error.path}: {error.message}")
```

#### `validate_gateway(gateway: dict) -> ValidationResult`

Validate a Gateway resource.

#### `validate_httproute(route: dict) -> ValidationResult`

Validate an HTTPRoute resource.

#### `ValidationResult`

```python
class ValidationResult:
    is_valid: bool
    errors: list[ValidationError]
    warnings: list[ValidationWarning]

    def to_dict(self) -> dict
    def add_error(self, path: str, message: str)
    def add_warning(self, path: str, message: str)
```

### Reverse Module

Convert Gateway API resources back to Ingress.

#### `convert_gateway_to_ingress(gateway: dict, httproutes: list) -> dict`

Convert Gateway and HTTPRoutes to an Ingress resource.

```python
from ingress2gateway import convert_gateway_to_ingress

ingress = convert_gateway_to_ingress(gateway, httproutes)
```

#### `gateway_resources_to_ingress_yaml(gateway: dict, httproutes: list) -> str`

Convert Gateway resources to Ingress YAML string.

#### `parse_gateway_resources(yaml_content: str) -> tuple[dict, list]`

Parse Gateway API YAML into Gateway and HTTPRoute objects.

```python
from ingress2gateway.reverse import parse_gateway_resources

gateway, httproutes = parse_gateway_resources(yaml_content)
```

### gRPC Module

Handle gRPC route detection and generation.

#### `is_grpc_backend(ingress: dict, service_name: str) -> bool`

Check if a backend is a gRPC service based on annotations.

```python
from ingress2gateway import is_grpc_backend

if is_grpc_backend(ingress, "grpc-service"):
    print("This is a gRPC backend")
```

#### `create_grpc_route(httproute: dict) -> dict`

Create a GRPCRoute from an HTTPRoute.

```python
from ingress2gateway import create_grpc_route

grpcroute = create_grpc_route(httproute)
```

### Report Module

Generate migration reports.

#### `generate_migration_report(...) -> str`

Generate a comprehensive markdown migration report.

```python
from ingress2gateway import generate_migration_report

report = generate_migration_report(
    ingress=ingress,
    gateway=resources["gateway"],
    httproutes=resources["httproutes"],
    warnings=warnings,
    unsupported=unsupported,
)
```

#### `generate_diff_summary(ingress: dict, gateway: dict) -> dict`

Generate a diff summary showing field mappings.

```python
from ingress2gateway import generate_diff_summary

diff = generate_diff_summary(ingress, resources["gateway"])
```

## REST API

### POST /api/convert

Convert Ingress YAML to Gateway API resources.

**Request:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ingress_yaml` | string | Yes | Ingress YAML content |
| `provider` | string | No | Provider preset (default: `istio`) |
| `detect_grpc` | boolean | No | Enable gRPC detection (default: `false`) |

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| `gateway_yaml` | string | Combined YAML output |
| `gateway` | object | Gateway resource |
| `httproutes` | array | HTTPRoute resources |
| `grpcroutes` | array | GRPCRoute resources (if gRPC detected) |
| `warnings` | array | Conversion warnings |
| `diff_summary` | object | Field mapping summary |

### POST /api/reverse

Convert Gateway API YAML to Ingress.

**Request:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `gateway_yaml` | string | Yes | Gateway API YAML content |

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| `ingress_yaml` | string | Ingress YAML output |
| `ingress` | object | Ingress resource |

### POST /api/validate

Validate YAML content.

**Request:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `yaml_content` | string | Yes | YAML content to validate |
| `resource_type` | string | Yes | `ingress`, `gateway`, or `httproute` |

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| `valid` | boolean | Validation result |
| `errors` | array | Validation errors |
| `warnings` | array | Validation warnings |

### GET /api/providers

List available provider presets.

**Response:**

```json
[
  {
    "id": "istio",
    "name": "Istio",
    "gateway_class": "istio",
    "supports_grpc": true,
    "supports_tcp": true
  }
]
```

### POST /api/download/single

Download converted resources as single YAML file.

### POST /api/download/separate

Download converted resources as separate files in ZIP.

### POST /api/download/kustomize

Download converted resources as Kustomize structure in ZIP.

### POST /api/report

Generate migration report.

**Request:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ingress_yaml` | string | Yes | Ingress YAML content |
| `provider` | string | No | Provider preset |

**Response:** Markdown file download

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy"
}
```

## Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

| Status | Description |
|--------|-------------|
| 400 | Invalid input (bad YAML, wrong kind, validation error) |
| 500 | Internal server error |
