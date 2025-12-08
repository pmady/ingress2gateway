"""Migration report generation."""

from datetime import datetime
from typing import Any


def generate_migration_report(
    ingress: dict[str, Any],
    resources: dict[str, Any],
    warnings: list[str],
    unsupported: list[dict[str, str]],
) -> str:
    """
    Generate a markdown migration report.

    Args:
        ingress: Original Ingress resource
        resources: Converted Gateway API resources
        warnings: List of warning messages
        unsupported: List of unsupported features

    Returns:
        Markdown formatted report
    """
    ingress_meta = ingress.get("metadata", {})
    ingress_name = ingress_meta.get("name", "unknown")
    namespace = ingress_meta.get("namespace", "default")

    gateway = resources.get("gateway", {})
    httproutes = resources.get("httproutes", [])
    grpcroutes = resources.get("grpcroutes", [])

    report = f"""# Migration Report: {ingress_name}

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary

| Item | Value |
|------|-------|
| Source Ingress | `{ingress_name}` |
| Namespace | `{namespace}` |
| Gateway Created | `{gateway.get("metadata", {}).get("name", "N/A")}` |
| HTTPRoutes Created | {len(httproutes)} |
| GRPCRoutes Created | {len(grpcroutes)} |
| Warnings | {len(warnings)} |
| Unsupported Features | {len(unsupported)} |

## Conversion Details

### Gateway

- **Name**: `{gateway.get("metadata", {}).get("name", "N/A")}`
- **Gateway Class**: `{gateway.get("spec", {}).get("gatewayClassName", "N/A")}`
- **Listeners**: {len(gateway.get("spec", {}).get("listeners", []))}

"""

    # List listeners
    listeners = gateway.get("spec", {}).get("listeners", [])
    if listeners:
        report += "#### Listeners\n\n"
        report += "| Name | Port | Protocol | Hostname |\n"
        report += "|------|------|----------|----------|\n"
        for listener in listeners:
            report += f"| {listener.get('name', 'N/A')} | {listener.get('port', 'N/A')} | {listener.get('protocol', 'N/A')} | {listener.get('hostname', '*')} |\n"
        report += "\n"

    # HTTPRoutes
    if httproutes:
        report += "### HTTPRoutes\n\n"
        for i, route in enumerate(httproutes, 1):
            route_meta = route.get("metadata", {})
            route_spec = route.get("spec", {})
            hostnames = route_spec.get("hostnames", ["*"])
            rules_count = len(route_spec.get("rules", []))

            report += f"#### {i}. `{route_meta.get('name', 'N/A')}`\n\n"
            report += f"- **Hostnames**: {', '.join(hostnames)}\n"
            report += f"- **Rules**: {rules_count}\n"

            for j, rule in enumerate(route_spec.get("rules", []), 1):
                matches = rule.get("matches", [{}])
                backends = rule.get("backendRefs", [])
                path = matches[0].get("path", {}).get("value", "/") if matches else "/"

                report += f"  - Rule {j}: `{path}` → "
                if backends:
                    backend = backends[0]
                    report += f"`{backend.get('name', 'N/A')}:{backend.get('port', 80)}`\n"
                else:
                    report += "No backend\n"

            report += "\n"

    # GRPCRoutes
    if grpcroutes:
        report += "### GRPCRoutes\n\n"
        for i, route in enumerate(grpcroutes, 1):
            route_meta = route.get("metadata", {})
            report += f"#### {i}. `{route_meta.get('name', 'N/A')}`\n\n"

    # Warnings
    if warnings:
        report += "## ⚠️ Warnings\n\n"
        report += "The following items require attention:\n\n"
        for warning in warnings:
            report += f"- {warning}\n"
        report += "\n"

    # Unsupported features
    if unsupported:
        report += "## ❌ Unsupported Features\n\n"
        report += "The following features could not be automatically converted:\n\n"
        report += "| Annotation | Value | Notes |\n"
        report += "|------------|-------|-------|\n"
        for item in unsupported:
            report += f"| `{item.get('annotation', 'N/A')}` | `{item.get('value', 'N/A')}` | Requires manual configuration |\n"
        report += "\n"

    # Manual steps
    report += """## 📋 Manual Steps Required

1. **Review Gateway Class**: Ensure the gateway class `{gateway_class}` is installed in your cluster
2. **TLS Certificates**: Verify that referenced TLS secrets exist
3. **Test Routes**: Test each route after applying the new resources
4. **Remove Old Ingress**: Once verified, remove the original Ingress resource

## 🔗 Useful Commands

```bash
# Apply the converted resources
kubectl apply -f gateway.yaml
kubectl apply -f httproutes.yaml

# Verify Gateway status
kubectl get gateway {gateway_name} -n {namespace}

# Check HTTPRoute status
kubectl get httproute -n {namespace}

# Test connectivity
curl -H "Host: <hostname>" http://<gateway-ip>/
```

## 📚 References

- [Gateway API Documentation](https://gateway-api.sigs.k8s.io/)
- [Migration Guide](https://gateway-api.sigs.k8s.io/guides/migrating-from-ingress/)
""".format(
        gateway_class=gateway.get("spec", {}).get("gatewayClassName", "N/A"),
        gateway_name=gateway.get("metadata", {}).get("name", "gateway"),
        namespace=namespace,
    )

    return report


def generate_diff_summary(
    ingress: dict[str, Any], resources: dict[str, Any]
) -> list[dict[str, Any]]:
    """
    Generate a summary of differences between Ingress and Gateway API.

    Returns a list of mapping items showing field correspondences.
    """
    mappings = []

    ingress_meta = ingress.get("metadata", {})
    ingress_spec = ingress.get("spec", {})
    gateway = resources.get("gateway", {})
    gateway_spec = gateway.get("spec", {})

    # Name mapping
    mappings.append(
        {
            "ingress_field": "metadata.name",
            "ingress_value": ingress_meta.get("name", ""),
            "gateway_field": "metadata.name",
            "gateway_value": gateway.get("metadata", {}).get("name", ""),
        }
    )

    # Ingress class mapping
    mappings.append(
        {
            "ingress_field": "spec.ingressClassName",
            "ingress_value": ingress_spec.get("ingressClassName", ""),
            "gateway_field": "spec.gatewayClassName",
            "gateway_value": gateway_spec.get("gatewayClassName", ""),
        }
    )

    # TLS mapping
    tls_count = len(ingress_spec.get("tls", []))
    https_listeners = [
        listener
        for listener in gateway_spec.get("listeners", [])
        if listener.get("protocol") == "HTTPS"
    ]
    mappings.append(
        {
            "ingress_field": "spec.tls",
            "ingress_value": f"{tls_count} TLS entries",
            "gateway_field": "spec.listeners (HTTPS)",
            "gateway_value": f"{len(https_listeners)} HTTPS listeners",
        }
    )

    # Rules mapping
    rules_count = len(ingress_spec.get("rules", []))
    httproutes_count = len(resources.get("httproutes", []))
    mappings.append(
        {
            "ingress_field": "spec.rules",
            "ingress_value": f"{rules_count} rules",
            "gateway_field": "HTTPRoutes",
            "gateway_value": f"{httproutes_count} HTTPRoutes",
        }
    )

    return mappings
