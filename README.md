# Ingress to Gateway API Converter

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI](https://github.com/pmady/ingress2gateway/actions/workflows/ci.yml/badge.svg)](https://github.com/pmady/ingress2gateway/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/ingress2gateway/badge/?version=latest)](https://ingress2gateway.readthedocs.io/en/latest/?badge=latest)

A comprehensive tool to convert Kubernetes Ingress objects to Gateway API resources with CLI, Web UI, and GitHub Action support.

## Features

### Core Conversion

- **Ingress → Gateway API**: Convert Ingress to Gateway + HTTPRoute resources
- **Gateway API → Ingress**: Reverse conversion for migration rollback
- **Multi-document YAML**: Process multiple Ingress resources at once
- **GRPCRoute Support**: Automatic detection and conversion of gRPC backends
- **TCPRoute/UDPRoute**: Support for TCP and UDP backend services
- **ReferenceGrant**: Auto-generate ReferenceGrants for cross-namespace references

### Annotation Support

- **Nginx Ingress**: Rewrite rules, SSL redirect, CORS, rate limiting
- **Traefik**: Middlewares, entrypoints, priorities
- **Istio**: Ingress class, revision labels
- **AWS ALB**: Certificate ARN, target type, scheme, actions
- **GCE/GKE**: Static IP, managed certificates, backend config

### Provider Presets

| Provider | Gateway Class | gRPC | TCP |
|----------|---------------|------|-----|
| Istio | `istio` | ✓ | ✓ |
| Envoy Gateway | `eg` | ✓ | ✓ |
| Contour | `contour` | ✓ | ✓ |
| Kong | `kong` | ✓ | ✓ |
| NGINX Gateway Fabric | `nginx` | ✗ | ✗ |
| Traefik | `traefik` | ✓ | ✓ |
| GKE | `gke-l7-global-external-managed` | ✓ | ✗ |

### User Interfaces

- **Web GUI**: Interactive interface with dark/light theme, diff view, validation
- **CLI Tool**: Full-featured command-line interface
- **REST API**: Programmatic conversion endpoints
- **GitHub Action**: CI/CD integration for automated conversion
- **kubectl Plugin**: Native kubectl integration
- **Helm Chart**: Deploy web UI to Kubernetes

### Additional Features

- **Validation**: Input and output schema validation
- **Migration Reports**: Detailed markdown reports with manual steps
- **Download Options**: Single YAML, separate files, or Kustomize structure

## Installation

### Using pip

```bash
pip install ingress2gateway
```

### Using uv (recommended for development)

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/pmady/ingress2gateway.git
cd ingress2gateway
uv sync
```

### From source

```bash
git clone https://github.com/pmady/ingress2gateway.git
cd ingress2gateway
pip install -e .
```

## Quick Start

### CLI Usage

```bash
# Basic conversion
ingress2gateway convert ingress.yaml -o gateway.yaml

# With provider preset
ingress2gateway convert ingress.yaml -o gateway.yaml -p istio

# Enable gRPC detection
ingress2gateway convert ingress.yaml -o gateway.yaml --grpc

# Generate migration report
ingress2gateway convert ingress.yaml -o gateway.yaml --report migration.md

# Reverse conversion (Gateway API to Ingress)
ingress2gateway reverse gateway.yaml -o ingress.yaml

# Validate Ingress file
ingress2gateway validate ingress.yaml

# List available providers
ingress2gateway providers

# Start web server
ingress2gateway serve --port 8000
```

### Web Interface

1. Start the server:

   ```bash
   ingress2gateway serve --port 8000
   ```

2. Open <http://localhost:8000> in your browser

3. Paste your Ingress YAML in the left panel

4. Select your provider preset

5. Click "Convert" to generate Gateway API resources

**Web UI Features:**

- Dark/light theme toggle
- Provider selection dropdown
- Bidirectional conversion (Ingress ↔ Gateway)
- gRPC detection option
- Diff summary showing field mappings
- Validation results with errors/warnings
- Multiple download formats (YAML, ZIP, Kustomize)
- Migration report generation

### REST API

```bash
# Convert Ingress to Gateway API
curl -X POST http://localhost:8000/api/convert \
  -H "Content-Type: application/json" \
  -d '{
    "ingress_yaml": "apiVersion: networking.k8s.io/v1\nkind: Ingress...",
    "provider": "istio",
    "detect_grpc": false
  }'

# Reverse conversion
curl -X POST http://localhost:8000/api/reverse \
  -H "Content-Type: application/json" \
  -d '{"gateway_yaml": "..."}'

# Validate YAML
curl -X POST http://localhost:8000/api/validate \
  -H "Content-Type: application/json" \
  -d '{"yaml_content": "...", "resource_type": "ingress"}'

# List providers
curl http://localhost:8000/api/providers

# Download as single YAML
curl -X POST http://localhost:8000/api/download/single \
  -H "Content-Type: application/json" \
  -d '{"ingress_yaml": "..."}' -o gateway.yaml

# Download as Kustomize
curl -X POST http://localhost:8000/api/download/kustomize \
  -H "Content-Type: application/json" \
  -d '{"ingress_yaml": "..."}' -o gateway-kustomize.zip

# Generate migration report
curl -X POST http://localhost:8000/api/report \
  -H "Content-Type: application/json" \
  -d '{"ingress_yaml": "..."}' -o migration-report.md
```

### GitHub Action

Add to your workflow:

```yaml
name: Convert Ingress to Gateway API

on:
  push:
    paths:
      - 'k8s/ingress.yaml'

jobs:
  convert:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Convert Ingress to Gateway API
        uses: pmady/ingress2gateway@v1
        with:
          input-file: k8s/ingress.yaml
          output-file: k8s/gateway.yaml
          provider: istio
          generate-report: true
          report-file: migration-report.md

      - name: Commit converted files
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add k8s/gateway.yaml migration-report.md
          git commit -m "Convert Ingress to Gateway API" || exit 0
          git push
```

**Action Inputs:**

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `input-file` | Path to input Ingress YAML | Yes | - |
| `output-file` | Path to output Gateway YAML | No | `gateway-resources.yaml` |
| `provider` | Gateway provider preset | No | `istio` |
| `detect-grpc` | Enable gRPC detection | No | `false` |
| `generate-report` | Generate migration report | No | `false` |
| `report-file` | Path to report file | No | `migration-report.md` |

### kubectl Plugin

Install the kubectl plugin for native kubectl integration:

```bash
# Download and install
curl -LO https://github.com/pmady/ingress2gateway/releases/latest/download/kubectl-ingress2gateway
chmod +x kubectl-ingress2gateway
sudo mv kubectl-ingress2gateway /usr/local/bin/

# Usage
kubectl ingress2gateway convert my-ingress -n default
kubectl ingress2gateway list -A
kubectl ingress2gateway apply my-ingress -n default --dry-run
kubectl ingress2gateway diff my-ingress -n default
```

### Helm Chart

Deploy the web UI to your Kubernetes cluster:

```bash
# Add the Helm repository
helm repo add ingress2gateway https://pmady.github.io/ingress2gateway
helm repo update

# Install
helm install ingress2gateway ingress2gateway/ingress2gateway

# With custom values
helm install ingress2gateway ingress2gateway/ingress2gateway \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=ingress2gateway.example.com
```

## Conversion Mapping

### Resource Mapping

| Ingress | Gateway API |
|---------|-------------|
| `Ingress` | `Gateway` + `HTTPRoute` |
| `spec.ingressClassName` | `spec.gatewayClassName` |
| `spec.tls` | `Gateway.spec.listeners` (HTTPS) |
| `spec.rules[].host` | `HTTPRoute.spec.hostnames` |
| `spec.rules[].http.paths` | `HTTPRoute.spec.rules` |
| `backend.service` | `HTTPRoute.spec.rules[].backendRefs` |
| `pathType: Prefix` | `path.type: PathPrefix` |
| `pathType: Exact` | `path.type: Exact` |

### Annotation Mapping

| Nginx Annotation | Gateway API Equivalent |
|------------------|------------------------|
| `nginx.ingress.kubernetes.io/rewrite-target` | `HTTPRoute.filters[].urlRewrite` |
| `nginx.ingress.kubernetes.io/ssl-redirect` | `HTTPRoute.filters[].requestRedirect` |
| `nginx.ingress.kubernetes.io/backend-protocol: GRPC` | Creates `GRPCRoute` instead |

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Web UI |
| `GET` | `/health` | Health check |
| `GET` | `/api/providers` | List available providers |
| `POST` | `/api/convert` | Convert Ingress to Gateway API |
| `POST` | `/api/reverse` | Convert Gateway API to Ingress |
| `POST` | `/api/validate` | Validate YAML content |
| `POST` | `/api/download/single` | Download as single YAML |
| `POST` | `/api/download/separate` | Download as separate files (ZIP) |
| `POST` | `/api/download/kustomize` | Download as Kustomize structure |
| `POST` | `/api/report` | Generate migration report |

### Python API

```python
from ingress2gateway import (
    convert_ingress_to_gateway,
    parse_ingress,
    resources_to_yaml,
    apply_provider_defaults,
    validate_ingress,
    convert_gateway_to_ingress,
    generate_migration_report,
)

# Parse and convert
ingress = parse_ingress(yaml_content)
resources = convert_ingress_to_gateway(ingress)

# Apply provider defaults
resources["gateway"] = apply_provider_defaults(resources["gateway"], "istio")

# Validate
result = validate_ingress(ingress)
if result.is_valid:
    print("Valid!")

# Generate YAML output
output = resources_to_yaml(resources)
print(output)
```

## Development

```bash
# Clone repository
git clone https://github.com/pmady/ingress2gateway.git
cd ingress2gateway

# Install dev dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/ingress2gateway

# Format code
uv run ruff format .

# Lint
uv run ruff check .

# Start dev server with auto-reload
uv run uvicorn src.ingress2gateway.main:app --reload
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

All contributors must sign off their commits (DCO). See the contributing guide for instructions.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [Gateway API](https://gateway-api.sigs.k8s.io/) - Official Kubernetes Gateway API
- [Kubernetes SIG Network](https://github.com/kubernetes-sigs/ingress2gateway) - Official ingress2gateway tool
