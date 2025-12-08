# Getting Started

## Prerequisites

- Python 3.11 or later

## Installation

### Using pip (recommended)

```bash
pip install ingress2gateway
```

### Using uv (for development)

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/pmady/ingress2gateway.git
cd ingress2gateway

# Install dependencies
uv sync
```

### From source

```bash
# Clone the repository
git clone https://github.com/pmady/ingress2gateway.git
cd ingress2gateway

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
pip install -e .
```

## Quick Start

### CLI

```bash
# Convert Ingress to Gateway API
ingress2gateway convert ingress.yaml -o gateway.yaml

# With provider preset
ingress2gateway convert ingress.yaml -o gateway.yaml -p istio

# Reverse conversion
ingress2gateway reverse gateway.yaml -o ingress.yaml

# Validate
ingress2gateway validate ingress.yaml

# List providers
ingress2gateway providers

# Start web server
ingress2gateway serve --port 8000
```

### Web UI

Start the server and open your browser:

```bash
ingress2gateway serve --port 8000
```

Then navigate to <http://localhost:8000>

### Python API

```python
from ingress2gateway import (
    convert_ingress_to_gateway,
    parse_ingress,
    resources_to_yaml,
)

# Load and parse Ingress YAML
with open("ingress.yaml") as f:
    ingress = parse_ingress(f.read())

# Convert to Gateway API
resources = convert_ingress_to_gateway(ingress)

# Output as YAML
print(resources_to_yaml(resources))
```

## Verify Installation

### CLI

```bash
ingress2gateway --help
```

### Web Server

Once the server is running, open your browser and navigate to:

- **Web UI**: <http://localhost:8000>
- **API Docs**: <http://localhost:8000/docs>
- **Health Check**: <http://localhost:8000/health>

## Next Steps

- [CLI Reference](cli.md) - Full CLI documentation
- [Usage Guide](usage.md) - Detailed usage examples
- [Provider Presets](providers.md) - Configure for your Gateway implementation
- [GitHub Action](github-action.md) - CI/CD integration
