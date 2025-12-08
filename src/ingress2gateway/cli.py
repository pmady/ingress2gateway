"""Command-line interface for ingress2gateway."""

import sys
from pathlib import Path
from typing import Any

import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from .annotations import get_annotation_warnings, parse_annotations
from .converter import convert_ingress_to_gateway, parse_ingress, resources_to_yaml
from .grpc import convert_to_grpc_routes, is_grpc_backend
from .providers import apply_provider_defaults
from .report import generate_migration_report
from .reverse import (
    gateway_resources_to_ingress_yaml,
    parse_gateway_resources,
)
from .validation import validate_conversion_output, validate_ingress

console = Console()


@click.group()
@click.version_option(version="0.2.0", prog_name="ingress2gateway")
def main():
    """Convert Kubernetes Ingress objects to Gateway API resources."""
    pass


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), help="Output file (default: stdout)")
@click.option(
    "-p",
    "--provider",
    type=click.Choice(["istio", "envoy", "contour", "kong", "nginx", "traefik", "gke"]),
    default="istio",
    help="Gateway provider preset",
)
@click.option("--grpc/--no-grpc", default=False, help="Enable gRPC route detection")
@click.option("--validate/--no-validate", default=True, help="Validate output")
@click.option("--report", type=click.Path(), help="Generate migration report to file")
@click.option("-q", "--quiet", is_flag=True, help="Suppress informational output")
def convert(
    input_file: str,
    output: str | None,
    provider: str,
    grpc: bool,
    validate: bool,
    report: str | None,
    quiet: bool,
):
    """Convert Ingress YAML to Gateway API resources."""
    try:
        # Read input file
        input_path = Path(input_file)
        yaml_content = input_path.read_text()

        # Parse and convert
        result = _convert_yaml(yaml_content, provider, grpc, validate, quiet)

        if result is None:
            sys.exit(1)

        resources, ingress, warnings, unsupported = result

        # Generate output YAML
        output_yaml = resources_to_yaml(resources)

        # Add GRPCRoutes if any
        if resources.get("grpcroutes"):
            for grpc_route in resources["grpcroutes"]:
                output_yaml += "---\n" + yaml.dump(
                    grpc_route, default_flow_style=False, sort_keys=False
                )

        # Write output
        if output:
            Path(output).write_text(output_yaml)
            if not quiet:
                console.print(f"[green]✓[/green] Output written to {output}")
        else:
            if not quiet:
                console.print(Panel(Syntax(output_yaml, "yaml", theme="monokai"), title="Output"))
            else:
                click.echo(output_yaml)

        # Generate report if requested
        if report:
            report_content = generate_migration_report(ingress, resources, warnings, unsupported)
            Path(report).write_text(report_content)
            if not quiet:
                console.print(f"[green]✓[/green] Migration report written to {report}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), help="Output file (default: stdout)")
@click.option("-q", "--quiet", is_flag=True, help="Suppress informational output")
def reverse(input_file: str, output: str | None, quiet: bool):
    """Convert Gateway API resources back to Ingress (reverse conversion)."""
    try:
        # Read input file
        input_path = Path(input_file)
        yaml_content = input_path.read_text()

        # Parse Gateway resources
        gateway, httproutes = parse_gateway_resources(yaml_content)

        if not gateway:
            console.print("[red]Error:[/red] No Gateway resource found in input")
            sys.exit(1)

        # Convert to Ingress
        output_yaml = gateway_resources_to_ingress_yaml(gateway, httproutes)

        # Write output
        if output:
            Path(output).write_text(output_yaml)
            if not quiet:
                console.print(f"[green]✓[/green] Output written to {output}")
        else:
            if not quiet:
                console.print(Panel(Syntax(output_yaml, "yaml", theme="monokai"), title="Ingress"))
            else:
                click.echo(output_yaml)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
def validate_cmd(input_file: str):
    """Validate an Ingress YAML file."""
    try:
        input_path = Path(input_file)
        yaml_content = input_path.read_text()

        ingress = parse_ingress(yaml_content)
        result = validate_ingress(ingress)

        if result.is_valid:
            console.print("[green]✓[/green] Ingress is valid")
        else:
            console.print("[red]✗[/red] Validation failed")

        if result.errors:
            console.print("\n[red]Errors:[/red]")
            for error in result.errors:
                console.print(f"  • {error.path}: {error.message}")

        if result.warnings:
            console.print("\n[yellow]Warnings:[/yellow]")
            for warning in result.warnings:
                console.print(f"  • {warning.path}: {warning.message}")

        sys.exit(0 if result.is_valid else 1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@main.command()
def providers():
    """List available provider presets."""
    table = Table(title="Available Providers")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Gateway Class", style="yellow")
    table.add_column("gRPC", style="magenta")
    table.add_column("TCP", style="magenta")

    from .providers import PROVIDERS

    for provider_id, config in PROVIDERS.items():
        table.add_row(
            provider_id,
            config["name"],
            config["gateway_class"],
            "✓" if config["supports_grpc"] else "✗",
            "✓" if config["supports_tcp"] else "✗",
        )

    console.print(table)


@main.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
def serve(host: str, port: int, reload: bool):
    """Start the web UI server."""
    import uvicorn

    console.print(f"[green]Starting server at http://{host}:{port}[/green]")
    uvicorn.run(
        "ingress2gateway.main:app",
        host=host,
        port=port,
        reload=reload,
    )


def _convert_yaml(
    yaml_content: str,
    provider: str,
    detect_grpc: bool,
    do_validate: bool,
    quiet: bool,
) -> tuple[dict[str, Any], dict[str, Any], list[str], list[dict[str, str]]] | None:
    """
    Convert YAML content and return resources.

    Returns tuple of (resources, ingress, warnings, unsupported) or None on error.
    """
    # Handle multi-document YAML
    try:
        documents = list(yaml.safe_load_all(yaml_content))
    except yaml.YAMLError as e:
        console.print(f"[red]Error parsing YAML:[/red] {e}")
        return None

    all_resources: dict[str, Any] = {"gateway": None, "httproutes": [], "grpcroutes": []}
    all_warnings: list[str] = []
    all_unsupported: list[dict[str, str]] = []
    first_ingress = None

    for doc in documents:
        if not doc:
            continue

        kind = doc.get("kind", "")
        if kind != "Ingress":
            if not quiet:
                console.print(f"[yellow]Skipping non-Ingress resource: {kind}[/yellow]")
            continue

        if first_ingress is None:
            first_ingress = doc

        # Validate input
        if do_validate:
            validation = validate_ingress(doc)
            if not validation.is_valid:
                console.print("[red]Input validation failed:[/red]")
                for error in validation.errors:
                    console.print(f"  • {error.path}: {error.message}")
                return None

        # Parse annotations
        annotations = doc.get("metadata", {}).get("annotations", {})
        parsed_annotations = parse_annotations(annotations)
        all_warnings.extend(get_annotation_warnings(parsed_annotations))
        all_unsupported.extend(parsed_annotations.get("unsupported", []))

        # Convert
        resources = convert_ingress_to_gateway(doc)

        # Apply provider defaults
        resources["gateway"] = apply_provider_defaults(resources["gateway"], provider)

        # Handle gRPC detection
        if detect_grpc and is_grpc_backend(annotations):
            http_routes, grpc_routes = convert_to_grpc_routes(resources["httproutes"], annotations)
            resources["httproutes"] = http_routes
            resources["grpcroutes"] = grpc_routes

        # Merge resources
        if all_resources["gateway"] is None:
            all_resources["gateway"] = resources["gateway"]
        all_resources["httproutes"].extend(resources["httproutes"])
        all_resources["grpcroutes"].extend(resources.get("grpcroutes", []))

    if first_ingress is None:
        console.print("[red]Error:[/red] No Ingress resources found in input")
        return None

    # Validate output
    if do_validate:
        output_validation = validate_conversion_output(all_resources)
        if not output_validation.is_valid:
            console.print("[red]Output validation failed:[/red]")
            for error in output_validation.errors:
                console.print(f"  • {error.path}: {error.message}")
            return None

        if output_validation.warnings and not quiet:
            console.print("[yellow]Warnings:[/yellow]")
            for warning in output_validation.warnings:
                console.print(f"  • {warning.path}: {warning.message}")

    # Show annotation warnings
    if all_warnings and not quiet:
        console.print("\n[yellow]Annotation warnings:[/yellow]")
        for warning in all_warnings:
            console.print(f"  • {warning}")

    return all_resources, first_ingress, all_warnings, all_unsupported


if __name__ == "__main__":
    main()
