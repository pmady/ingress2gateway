# Getting Started

## Prerequisites

- Python 3.11 or later
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Installation

### Using uv (recommended)

```bash
# Clone the repository
git clone https://github.com/pmady/ingress2gateway.git
cd ingress2gateway

# Install dependencies
uv sync

# Run the application
uv run uvicorn src.ingress2gateway.main:app --reload --host 0.0.0.0 --port 8000
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/pmady/ingress2gateway.git
cd ingress2gateway

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
pip install -e .

# Run the application
uvicorn src.ingress2gateway.main:app --reload --host 0.0.0.0 --port 8000
```

## Verify Installation

Once the server is running, open your browser and navigate to:

- **Web UI**: <http://localhost:8000>
- **API Docs**: <http://localhost:8000/docs>
- **Health Check**: <http://localhost:8000/health>
