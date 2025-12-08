# CLI Reference

The `ingress2gateway` CLI provides a full-featured command-line interface for converting Ingress resources to Gateway API.

## Installation

```bash
pip install ingress2gateway
```

## Commands

### convert

Convert Ingress YAML to Gateway API resources.

```bash
ingress2gateway convert [OPTIONS] INPUT_FILE
```

**Arguments:**

- `INPUT_FILE`: Path to input Ingress YAML file (required)

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output FILE` | Output file path | stdout |
| `-p, --provider PROVIDER` | Gateway provider preset | `istio` |
| `--grpc / --no-grpc` | Enable gRPC route detection | `--no-grpc` |
| `--validate / --no-validate` | Validate output | `--validate` |
| `--report FILE` | Generate migration report | - |
| `-q, --quiet` | Suppress informational output | - |

**Examples:**

```bash
# Basic conversion
ingress2gateway convert ingress.yaml -o gateway.yaml

# With Envoy Gateway provider
ingress2gateway convert ingress.yaml -o gateway.yaml -p envoy

# Enable gRPC detection
ingress2gateway convert ingress.yaml -o gateway.yaml --grpc

# Generate migration report
ingress2gateway convert ingress.yaml -o gateway.yaml --report migration.md

# Quiet mode (only output YAML)
ingress2gateway convert ingress.yaml -q > gateway.yaml
```

### reverse

Convert Gateway API resources back to Ingress (reverse conversion).

```bash
ingress2gateway reverse [OPTIONS] INPUT_FILE
```

**Arguments:**

- `INPUT_FILE`: Path to input Gateway API YAML file (required)

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output FILE` | Output file path | stdout |
| `-q, --quiet` | Suppress informational output | - |

**Examples:**

```bash
# Reverse conversion
ingress2gateway reverse gateway.yaml -o ingress.yaml

# Output to stdout
ingress2gateway reverse gateway.yaml -q
```

### validate

Validate an Ingress YAML file.

```bash
ingress2gateway validate INPUT_FILE
```

**Arguments:**

- `INPUT_FILE`: Path to Ingress YAML file to validate (required)

**Examples:**

```bash
# Validate Ingress file
ingress2gateway validate ingress.yaml

# Use in CI/CD (exits with code 1 on failure)
ingress2gateway validate ingress.yaml || echo "Validation failed"
```

**Output:**

```
✓ Ingress is valid

Warnings:
  • spec.rules[0].http: No paths defined
```

### providers

List available provider presets.

```bash
ingress2gateway providers
```

**Output:**

```
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━┓
┃ ID       ┃ Name                    ┃ Gateway Class                    ┃ gRPC ┃ TCP  ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━┩
│ istio    │ Istio                   │ istio                            │ ✓    │ ✓    │
│ envoy    │ Envoy Gateway           │ eg                               │ ✓    │ ✓    │
│ contour  │ Contour                 │ contour                          │ ✓    │ ✓    │
│ kong     │ Kong                    │ kong                             │ ✓    │ ✓    │
│ nginx    │ NGINX Gateway Fabric    │ nginx                            │ ✗    │ ✗    │
│ traefik  │ Traefik                 │ traefik                          │ ✓    │ ✓    │
│ gke      │ GKE Gateway Controller  │ gke-l7-global-external-managed   │ ✓    │ ✗    │
└──────────┴─────────────────────────┴──────────────────────────────────┴──────┴──────┘
```

### serve

Start the web UI server.

```bash
ingress2gateway serve [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--host HOST` | Host to bind to | `0.0.0.0` |
| `--port PORT` | Port to bind to | `8000` |
| `--reload` | Enable auto-reload | - |

**Examples:**

```bash
# Start server on default port
ingress2gateway serve

# Custom port
ingress2gateway serve --port 3000

# Development mode with auto-reload
ingress2gateway serve --reload
```

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | Error (invalid input, validation failure, etc.) |

## Environment Variables

The CLI respects the following environment variables:

| Variable | Description |
|----------|-------------|
| `NO_COLOR` | Disable colored output |

## Piping and Scripting

The CLI is designed to work well in scripts and pipelines:

```bash
# Pipe from kubectl
kubectl get ingress my-ingress -o yaml | ingress2gateway convert - -q > gateway.yaml

# Process multiple files
for f in ingresses/*.yaml; do
  ingress2gateway convert "$f" -o "gateways/$(basename $f)" -q
done

# Validate all ingresses
find . -name "ingress*.yaml" -exec ingress2gateway validate {} \;
```
