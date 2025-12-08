# Ingress to Gateway API Converter

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI](https://github.com/pmady/ingress2gateway/actions/workflows/ci.yml/badge.svg)](https://github.com/pmady/ingress2gateway/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/ingress2gateway/badge/?version=latest)](https://ingress2gateway.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/ingress2gateway.svg)](https://badge.fury.io/py/ingress2gateway)

A comprehensive tool to convert Kubernetes Ingress objects to Gateway API resources with CLI, Web UI, and GitHub Action support.

## Features

### Core Conversion
- **Ingress → Gateway API**: Convert Ingress to Gateway + HTTPRoute resources
- **Gateway API → Ingress**: Reverse conversion for migration rollback
- **Multi-document YAML**: Process multiple Ingress resources at once
- **GRPCRoute Support**: Automatic detection and conversion of gRPC backends

### Annotation Support
- **Nginx Ingress**: Rewrite rules, SSL redirect, CORS, rate limiting
- **Traefik**: Middlewares, entrypoints, priorities
- **Istio**: Ingress class, revision labels

### Provider Presets
- Istio, Envoy Gateway, Contour, Kong, NGINX Gateway Fabric, Traefik, GKE

### User Interfaces
- **Web GUI**: Interactive interface with dark/light theme, diff view, validation
- **CLI Tool**: Full-featured command-line interface
- **REST API**: Programmatic conversion endpoints
- **GitHub Action**: CI/CD integration for automated conversion

### Additional Features
- **Validation**: Input and output schema validation
- **Migration Reports**: Detailed markdown reports with manual steps
- **Download Options**: Single YAML, separate files, or Kustomize structure

## Installation

### Using uv (recommended)

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies and run
uv sync
uv run uvicorn src.ingress2gateway.main:app --reload
```

### Using pip

```bash
pip install -e .
uvicorn src.ingress2gateway.main:app --reload
```

## Usage

### Web Interface

1. Start the server:

```bash
uv run uvicorn src.ingress2gateway.main:app --reload --host 0.0.0.0 --port 8000
```

2. Open <http://localhost:8000> in your browser

3. Paste your Ingress YAML in the left panel

4. Click "Convert" to generate Gateway API resources

### CLI

```bash
# Convert Ingress to Gateway API
ingress2gateway convert ingress.yaml -o gateway.yaml

# With provider preset
ingress2gateway convert ingress.yaml -o gateway.yaml -p istio

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

### REST API

```bash
# Convert Ingress to Gateway API
curl -X POST http://localhost:8000/api/convert \
  -H "Content-Type: application/json" \
  -d '{"ingress_yaml": "...", "provider": "istio"}'

# Reverse conversion
curl -X POST http://localhost:8000/api/reverse \
  -H "Content-Type: application/json" \
  -d '{"gateway_yaml": "..."}'

# Validate
curl -X POST http://localhost:8000/api/validate \
  -H "Content-Type: application/json" \
  -d '{"yaml_content": "...", "resource_type": "ingress"}'
```

### GitHub Action

```yaml
- name: Convert Ingress to Gateway API
  uses: pmady/ingress2gateway@v1
  with:
    input-file: ingress.yaml
    output-file: gateway.yaml
    provider: istio
    generate-report: true
```

## Conversion Mapping

| Ingress | Gateway API |
|---------|-------------|
| `Ingress` | `Gateway` + `HTTPRoute` |
| `spec.ingressClassName` | `spec.gatewayClassName` |
| `spec.tls` | `Gateway.spec.listeners` (HTTPS) |
| `spec.rules[].host` | `HTTPRoute.spec.hostnames` |
| `spec.rules[].http.paths` | `HTTPRoute.spec.rules` |
| `backend.service` | `HTTPRoute.spec.rules[].backendRefs` |

## Development

```bash
# Install dev dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Format code
uv run ruff format .

# Lint
uv run ruff check .
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

All contributors must sign off their commits (DCO). See the contributing guide for instructions.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
