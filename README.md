# Ingress to Gateway API Converter

A web application to convert Kubernetes Ingress objects to Gateway API resources.

## Features

- **Web GUI**: Interactive interface with YAML editors
- **REST API**: Programmatic conversion via `/api/convert` endpoint
- **Real-time conversion**: Instant feedback with syntax highlighting
- **Copy to clipboard**: Easy export of converted resources

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

### API

```bash
curl -X POST http://localhost:8000/api/convert \
  -H "Content-Type: application/json" \
  -d '{
    "ingress_yaml": "apiVersion: networking.k8s.io/v1\nkind: Ingress\nmetadata:\n  name: example\nspec:\n  rules:\n    - host: example.com\n      http:\n        paths:\n          - path: /\n            pathType: Prefix\n            backend:\n              service:\n                name: my-service\n                port:\n                  number: 80"
  }'
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

## License

MIT
