# GitHub Action

ingress2gateway provides a GitHub Action for automated conversion of Ingress resources to Gateway API in your CI/CD pipelines.

## Basic Usage

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
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `input-file` | Path to input Ingress YAML file | Yes | - |
| `output-file` | Path to output Gateway API YAML file | No | `gateway-resources.yaml` |
| `provider` | Gateway provider preset | No | `istio` |
| `detect-grpc` | Enable gRPC route detection | No | `false` |
| `generate-report` | Generate migration report | No | `false` |
| `report-file` | Path to migration report file | No | `migration-report.md` |

## Outputs

| Output | Description |
|--------|-------------|
| `gateway-yaml` | Path to generated Gateway API YAML file |
| `report` | Path to migration report (if generated) |

## Examples

### With Provider Preset

```yaml
- name: Convert Ingress to Gateway API
  uses: pmady/ingress2gateway@v1
  with:
    input-file: ingress.yaml
    output-file: gateway.yaml
    provider: envoy
```

### With Migration Report

```yaml
- name: Convert Ingress to Gateway API
  uses: pmady/ingress2gateway@v1
  with:
    input-file: ingress.yaml
    output-file: gateway.yaml
    generate-report: true
    report-file: docs/migration-report.md
```

### With gRPC Detection

```yaml
- name: Convert Ingress to Gateway API
  uses: pmady/ingress2gateway@v1
  with:
    input-file: ingress.yaml
    output-file: gateway.yaml
    detect-grpc: true
```

### Complete Workflow with Commit

```yaml
name: Convert and Commit Gateway API Resources

on:
  push:
    branches: [main]
    paths:
      - 'manifests/ingress/**'

jobs:
  convert:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - uses: actions/checkout@v4

      - name: Convert Ingress to Gateway API
        uses: pmady/ingress2gateway@v1
        with:
          input-file: manifests/ingress/app-ingress.yaml
          output-file: manifests/gateway/app-gateway.yaml
          provider: istio
          generate-report: true
          report-file: docs/migration-report.md

      - name: Commit converted files
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add manifests/gateway/ docs/migration-report.md
          git diff --staged --quiet || git commit -m "chore: update Gateway API resources"
          git push
```

### Pull Request Workflow

```yaml
name: Validate and Convert Ingress

on:
  pull_request:
    paths:
      - '**/*ingress*.yaml'

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
          generate-report: true

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: gateway-resources
          path: |
            k8s/gateway.yaml
            migration-report.md

      - name: Comment on PR
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('migration-report.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '## Migration Report\n\n' + report
            });
```

### Matrix Strategy for Multiple Files

```yaml
name: Convert Multiple Ingress Files

on:
  workflow_dispatch:

jobs:
  convert:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        ingress:
          - { input: 'app1/ingress.yaml', output: 'app1/gateway.yaml' }
          - { input: 'app2/ingress.yaml', output: 'app2/gateway.yaml' }
          - { input: 'app3/ingress.yaml', output: 'app3/gateway.yaml' }

    steps:
      - uses: actions/checkout@v4

      - name: Convert ${{ matrix.ingress.input }}
        uses: pmady/ingress2gateway@v1
        with:
          input-file: ${{ matrix.ingress.input }}
          output-file: ${{ matrix.ingress.output }}
          provider: istio
```

## Artifacts

The action automatically uploads the generated Gateway YAML and migration report (if enabled) as workflow artifacts. You can download these from the Actions tab in your repository.

## Troubleshooting

### Action fails with "No Ingress resources found"

Ensure your input file contains a valid Kubernetes Ingress resource with `kind: Ingress`.

### Provider not recognized

Use one of the supported providers: `istio`, `envoy`, `contour`, `kong`, `nginx`, `traefik`, `gke`.

### Permission denied when committing

Add the `contents: write` permission to your job:

```yaml
jobs:
  convert:
    permissions:
      contents: write
```
