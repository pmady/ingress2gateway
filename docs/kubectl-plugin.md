# kubectl Plugin

The `kubectl-ingress2gateway` plugin provides native kubectl integration for converting Ingress resources to Gateway API.

## Installation

### Download from Release

```bash
# Download the plugin
curl -LO https://github.com/pmady/ingress2gateway/releases/latest/download/kubectl-ingress2gateway

# Make it executable
chmod +x kubectl-ingress2gateway

# Move to PATH
sudo mv kubectl-ingress2gateway /usr/local/bin/
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/pmady/ingress2gateway.git
cd ingress2gateway

# Install the package
pip install -e .

# Copy the plugin to PATH
sudo cp kubectl-ingress2gateway /usr/local/bin/
```

## Commands

### convert

Convert an Ingress resource to Gateway API resources.

```bash
# Convert from cluster
kubectl ingress2gateway convert my-ingress -n default

# Convert from file
kubectl ingress2gateway convert -f ingress.yaml

# With provider preset
kubectl ingress2gateway convert my-ingress -n default -p istio

# Output to file
kubectl ingress2gateway convert my-ingress -n default -o gateway.yaml

# Generate ReferenceGrants
kubectl ingress2gateway convert my-ingress -n default --reference-grants
```

### list

List Ingress resources in the cluster.

```bash
# List in current namespace
kubectl ingress2gateway list

# List in specific namespace
kubectl ingress2gateway list -n production

# List in all namespaces
kubectl ingress2gateway list -A
```

**Output:**

```
NAMESPACE            NAME                           HOSTS                                    CLASS
default              my-app-ingress                 app.example.com                          nginx
production           api-ingress                    api.example.com,api2.example.com         nginx
```

### apply

Convert and apply Gateway API resources to the cluster.

```bash
# Convert and apply
kubectl ingress2gateway apply my-ingress -n default

# With provider preset
kubectl ingress2gateway apply my-ingress -n default -p istio

# Dry run (show what would be applied)
kubectl ingress2gateway apply my-ingress -n default --dry-run

# From file
kubectl ingress2gateway apply -f ingress.yaml
```

### diff

Show the diff between converted resources and what exists in the cluster.

```bash
# Show diff
kubectl ingress2gateway diff my-ingress -n default

# With provider
kubectl ingress2gateway diff my-ingress -n default -p envoy
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--namespace` | `-n` | Kubernetes namespace |
| `--filename` | `-f` | Input YAML file |
| `--output` | `-o` | Output file path |
| `--provider` | `-p` | Provider preset (istio, envoy, contour, etc.) |
| `--reference-grants` | | Generate ReferenceGrants for cross-namespace refs |
| `--dry-run` | | Show what would be applied without applying |
| `--all-namespaces` | `-A` | List resources in all namespaces |

## Examples

### Basic Workflow

```bash
# 1. List existing Ingress resources
kubectl ingress2gateway list -A

# 2. Preview the conversion
kubectl ingress2gateway convert my-ingress -n default

# 3. Check what would change
kubectl ingress2gateway diff my-ingress -n default

# 4. Apply the converted resources
kubectl ingress2gateway apply my-ingress -n default
```

### Migration Script

```bash
#!/bin/bash
# migrate-ingresses.sh

NAMESPACE=${1:-default}
PROVIDER=${2:-istio}

# Get all Ingress names
INGRESSES=$(kubectl get ingress -n $NAMESPACE -o jsonpath='{.items[*].metadata.name}')

for ing in $INGRESSES; do
    echo "Converting $ing..."
    kubectl ingress2gateway convert $ing -n $NAMESPACE -p $PROVIDER -o "${ing}-gateway.yaml"
done

echo "Conversion complete. Review the generated files before applying."
```

### CI/CD Integration

```yaml
# .gitlab-ci.yml
convert-ingress:
  stage: prepare
  script:
    - kubectl ingress2gateway convert -f k8s/ingress.yaml -o k8s/gateway.yaml -p istio
  artifacts:
    paths:
      - k8s/gateway.yaml
```

## Troubleshooting

### Plugin Not Found

If kubectl doesn't recognize the plugin:

```bash
# Verify it's in PATH
which kubectl-ingress2gateway

# Check kubectl plugin list
kubectl plugin list
```

### Permission Denied

```bash
# Ensure the plugin is executable
chmod +x /usr/local/bin/kubectl-ingress2gateway
```

### Missing Dependencies

The plugin requires the `ingress2gateway` Python package:

```bash
pip install ingress2gateway
```
