# Usage Guide

## Web Interface

The web interface provides an interactive way to convert Ingress resources with a modern UI.

### Getting Started

1. **Start the server**

   ```bash
   ingress2gateway serve --port 8000
   ```

2. **Open the browser** at <http://localhost:8000>

3. **Paste your Ingress YAML** in the left editor panel

4. **Select your provider** from the dropdown (Istio, Envoy, Contour, etc.)

5. **Click "Convert"** to generate Gateway API resources

6. **Download or copy** the output using the toolbar buttons

### Web UI Features

- **Dark/Light Theme**: Toggle between themes using the button in the header
- **Provider Selection**: Choose your Gateway API implementation
- **Conversion Mode**: Switch between Ingress→Gateway and Gateway→Ingress
- **gRPC Detection**: Enable automatic detection of gRPC backends
- **Validation**: Toggle input/output validation
- **Diff Summary**: View field mappings between Ingress and Gateway API
- **Warnings Tab**: See conversion warnings and unsupported features
- **Download Options**:
  - Single YAML file
  - Separate files (ZIP)
  - Kustomize structure (ZIP)
  - Migration report (Markdown)

### Example Workflow

1. Load an example or paste your Ingress YAML
2. Select "Istio" as the provider
3. Enable "Detect gRPC" if you have gRPC services
4. Click "Convert"
5. Review the Diff Summary tab to understand the mapping
6. Check the Warnings tab for any manual steps needed
7. Download as Kustomize for production use

## CLI Usage

### Basic Conversion

```bash
# Convert single file
ingress2gateway convert ingress.yaml -o gateway.yaml

# Convert with provider preset
ingress2gateway convert ingress.yaml -o gateway.yaml -p envoy

# Convert with gRPC detection
ingress2gateway convert ingress.yaml -o gateway.yaml --grpc
```

### Multi-Document YAML

The tool supports YAML files with multiple Ingress resources:

```yaml
# multi-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app1-ingress
spec:
  rules:
    - host: app1.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: app1
                port:
                  number: 80
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app2-ingress
spec:
  rules:
    - host: app2.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: app2
                port:
                  number: 80
```

```bash
ingress2gateway convert multi-ingress.yaml -o gateway.yaml
```

### Migration Reports

Generate detailed migration reports:

```bash
ingress2gateway convert ingress.yaml -o gateway.yaml --report migration.md
```

The report includes:

- Summary of converted resources
- Field mapping details
- Warnings and unsupported features
- Manual steps required
- Useful kubectl commands

### Reverse Conversion

Convert Gateway API resources back to Ingress:

```bash
ingress2gateway reverse gateway.yaml -o ingress.yaml
```

This is useful for:

- Migration rollback
- Understanding the reverse mapping
- Testing bidirectional conversion

### Validation

Validate Ingress files before conversion:

```bash
ingress2gateway validate ingress.yaml
```

Output shows errors and warnings:

```text
✓ Ingress is valid

Warnings:
  • spec.rules[0].http: Consider adding explicit pathType
```

## REST API

### Convert Endpoint

**POST** `/api/convert`

```bash
curl -X POST http://localhost:8000/api/convert \
  -H "Content-Type: application/json" \
  -d '{
    "ingress_yaml": "apiVersion: networking.k8s.io/v1\nkind: Ingress...",
    "provider": "istio",
    "detect_grpc": false
  }'
```

Response:

```json
{
  "gateway_yaml": "apiVersion: gateway.networking.k8s.io/v1\nkind: Gateway...",
  "gateway": { ... },
  "httproutes": [ ... ],
  "grpcroutes": [ ... ],
  "warnings": [ ... ],
  "diff_summary": { ... }
}
```

### Reverse Endpoint

**POST** `/api/reverse`

```bash
curl -X POST http://localhost:8000/api/reverse \
  -H "Content-Type: application/json" \
  -d '{"gateway_yaml": "..."}'
```

### Validate Endpoint

**POST** `/api/validate`

```bash
curl -X POST http://localhost:8000/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "yaml_content": "...",
    "resource_type": "ingress"
  }'
```

Response:

```json
{
  "valid": true,
  "errors": [],
  "warnings": ["spec.rules[0].http: No paths defined"]
}
```

### Download Endpoints

**POST** `/api/download/single` - Single YAML file

**POST** `/api/download/separate` - Separate files in ZIP

**POST** `/api/download/kustomize` - Kustomize structure in ZIP

### Report Endpoint

**POST** `/api/report`

```bash
curl -X POST http://localhost:8000/api/report \
  -H "Content-Type: application/json" \
  -d '{"ingress_yaml": "..."}' \
  -o migration-report.md
```

### Providers Endpoint

**GET** `/api/providers`

```bash
curl http://localhost:8000/api/providers
```

Response:

```json
[
  {
    "id": "istio",
    "name": "Istio",
    "gateway_class": "istio",
    "supports_grpc": true,
    "supports_tcp": true
  },
  ...
]
```

### Health Check

**GET** `/health`

```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

### OpenAPI Documentation

Interactive API documentation is available at:

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

## Python API

### Basic Usage

```python
from ingress2gateway import (
    convert_ingress_to_gateway,
    parse_ingress,
    resources_to_yaml,
)

# Load Ingress YAML
with open("ingress.yaml") as f:
    yaml_content = f.read()

# Parse and convert
ingress = parse_ingress(yaml_content)
resources = convert_ingress_to_gateway(ingress)

# Output as YAML
output = resources_to_yaml(resources)
print(output)
```

### With Provider Defaults

```python
from ingress2gateway import (
    convert_ingress_to_gateway,
    parse_ingress,
    apply_provider_defaults,
)

ingress = parse_ingress(yaml_content)
resources = convert_ingress_to_gateway(ingress)

# Apply Istio defaults
resources["gateway"] = apply_provider_defaults(resources["gateway"], "istio")
```

### With Validation

```python
from ingress2gateway import (
    parse_ingress,
    validate_ingress,
    validate_gateway,
)

ingress = parse_ingress(yaml_content)

# Validate input
result = validate_ingress(ingress)
if not result.is_valid:
    for error in result.errors:
        print(f"Error at {error.path}: {error.message}")
```

### With Annotations

```python
from ingress2gateway import parse_annotations, get_annotation_warnings

annotations = ingress.get("metadata", {}).get("annotations", {})
parsed = parse_annotations(annotations)

# Get filters to apply to HTTPRoute
filters = parsed.get("filters", [])

# Get warnings about unsupported annotations
warnings = get_annotation_warnings(parsed)
```

### Generate Migration Report

```python
from ingress2gateway import generate_migration_report

report = generate_migration_report(
    ingress=ingress,
    gateway=resources["gateway"],
    httproutes=resources["httproutes"],
    warnings=warnings,
)

with open("migration.md", "w") as f:
    f.write(report)
```
