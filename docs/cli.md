# CLI Reference

The CLI provides a full-featured command-line interface for converting Ingress resources to Gateway API.

## Command Names

The CLI is available under two names:

- **`i2g`** - Short, convenient name (recommended)
- **`ingress2gateway`** - Full name (for backward compatibility)

Both commands are identical and can be used interchangeably.

## Installation

```bash
pip install ingress2gateway
```

## Commands

### convert

Convert Ingress YAML to Gateway API resources.

```bash
i2g convert [OPTIONS] INPUT_FILE
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
i2g convert ingress.yaml -o gateway.yaml

# With Envoy Gateway provider
i2g convert ingress.yaml -o gateway.yaml -p envoy

# Enable gRPC detection
i2g convert ingress.yaml -o gateway.yaml --grpc

# Generate migration report
i2g convert ingress.yaml -o gateway.yaml --report migration.md

# Quiet mode (only output YAML)
i2g convert ingress.yaml -q > gateway.yaml
```

### reverse

Convert Gateway API resources back to Ingress (reverse conversion).

```bash
i2g reverse [OPTIONS] INPUT_FILE
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
i2g reverse gateway.yaml -o ingress.yaml

# Output to stdout
i2g reverse gateway.yaml -q
```

### validate

Validate an Ingress YAML file.

```bash
i2g validate INPUT_FILE
```

**Arguments:**

- `INPUT_FILE`: Path to Ingress YAML file to validate (required)

**Examples:**

```bash
# Validate Ingress file
i2g validate ingress.yaml

# Use in CI/CD (exits with code 1 on failure)
i2g validate ingress.yaml || echo "Validation failed"
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
i2g providers
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
i2g serve [OPTIONS]
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
i2g serve

# Custom port
i2g serve --port 3000

# Development mode with auto-reload
i2g serve --reload
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
kubectl get ingress my-ingress -o yaml | i2g convert - -q > gateway.yaml

# Process multiple files
for f in ingresses/*.yaml; do
  i2g convert "$f" -o "gateways/$(basename $f)" -q
done

# Validate all ingresses
find . -name "ingress*.yaml" -exec i2g validate {} \;
```
