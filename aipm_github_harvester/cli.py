"""Command-line interface for AIPM GitHub Harvester."""

import os
import sys
import logging
import time
from pathlib import Path
from typing import List, Optional

import click
import yaml
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table
from rich.progress import Progress

from .core.harvester import GitHubHarvester
from .core.models import HarvestConfig, HarvestResult
from .exporters.formats import ExporterFactory
from .utils.file_utils import read_repos_file, ensure_directory

# Setup rich console
console = Console()


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('git').setLevel(logging.WARNING)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """AIPM GitHub Harvester - Extract AI tool metadata from GitHub repositories."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    setup_logging(verbose)


@cli.command()
@click.option('--repos-file', type=click.Path(exists=True), help='File containing repository URLs (one per line)')
@click.option('--repo', multiple=True, help='Single repository URL (can be used multiple times)')
@click.option('--output-dir', '-o', default='data/registry', help='Output directory for results')
@click.option('--config', type=click.Path(exists=True), help='Configuration file (YAML)')
@click.option('--format', 'formats', multiple=True, default=['jsonl', 'csv'], help='Output formats')
@click.option('--parallel/--sequential', default=True, help='Process repositories in parallel')
@click.option('--max-workers', type=int, default=4, help='Maximum number of parallel workers')
@click.pass_context
def harvest(
    ctx: click.Context,
    repos_file: Optional[str],
    repo: tuple[str, ...],
    output_dir: str,
    config: Optional[str],
    formats: tuple[str, ...],
    parallel: bool,
    max_workers: int
) -> None:
    """Harvest AI tool metadata from GitHub repositories."""
    
    # Load configuration
    harvest_config = load_config(config) if config else HarvestConfig()
    
    # Override config with CLI options
    if output_dir != 'data/registry':
        harvest_config.base_output_dir = output_dir
    harvest_config.output_formats = list(formats)
    harvest_config.parallel_processing = parallel
    harvest_config.max_workers = max_workers
    
    # Get list of repositories
    repo_urls = []
    
    if repos_file:
        repo_urls.extend(read_repos_file(repos_file))
        console.print(f"Loaded {len(repo_urls)} repositories from {repos_file}")
    
    if repo:
        repo_urls.extend(repo)
        console.print(f"Added {len(repo)} repositories from command line")
    
    if not repo_urls:
        console.print("[red]Error: No repositories specified. Use --repos-file or --repo.[/red]")
        sys.exit(1)
    
    # Remove duplicates while preserving order
    unique_repos = []
    seen = set()
    for url in repo_urls:
        if url not in seen:
            unique_repos.append(url)
            seen.add(url)
    
    console.print(f"Processing {len(unique_repos)} unique repositories")
    
    # Create harvester
    harvester = GitHubHarvester(harvest_config)
    
    # Ensure output directory exists
    ensure_directory(harvest_config.base_output_dir)
    
    # Harvest repositories
    results = []
    start_time = time.time()
    
    try:
        for result in harvester.harvest_repositories(unique_repos):
            results.append(result)
            
            # Display progress
            display_harvest_result(result)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Harvest interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error during harvest: {e}[/red]")
        if ctx.obj['verbose']:
            console.print_exception()
        sys.exit(1)
    
    total_time = time.time() - start_time
    
    # Export results
    export_results(results, harvest_config)
    
    # Display summary
    display_summary(results, total_time)


@cli.command()
@click.option('--output-dir', '-o', default='data/registry', help='Output directory to analyze')
def analyze(output_dir: str) -> None:
    """Analyze harvested metadata and display statistics."""
    
    if not Path(output_dir).exists():
        console.print(f"[red]Output directory does not exist: {output_dir}[/red]")
        sys.exit(1)
    
    # Look for metadata files
    jsonl_file = Path(output_dir) / "harvested_metadata.jsonl"
    csv_file = Path(output_dir) / "harvested_metadata.csv"
    
    if jsonl_file.exists():
        analyze_jsonl_file(jsonl_file)
    elif csv_file.exists():
        analyze_csv_file(csv_file)
    else:
        console.print("[red]No metadata files found in output directory[/red]")
        sys.exit(1)


def load_config(config_path: str) -> HarvestConfig:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        # Handle environment variable substitution
        config_data = substitute_env_vars(config_data)
        
        return HarvestConfig(**config_data)
    
    except Exception as e:
        console.print(f"[red]Error loading config file {config_path}: {e}[/red]")
        sys.exit(1)


def substitute_env_vars(data):
    """Recursively substitute environment variables in config data."""
    if isinstance(data, dict):
        return {key: substitute_env_vars(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [substitute_env_vars(item) for item in data]
    elif isinstance(data, str) and data.startswith('${') and data.endswith('}'):
        env_var = data[2:-1]
        return os.environ.get(env_var, data)
    else:
        return data


def display_harvest_result(result: HarvestResult) -> None:
    """Display harvest result for a single repository."""
    repo_name = result.repository.full_name or result.repository.name
    
    if result.errors:
        console.print(f"[red]✗ {repo_name}[/red] - {len(result.errors)} errors")
        if result.errors:
            for error in result.errors[:3]:  # Show first 3 errors
                console.print(f"  [red]Error: {error}[/red]")
    else:
        tools_count = len(result.tools_found)
        files_count = result.total_files_scanned
        console.print(f"[green]✓ {repo_name}[/green] - {tools_count} tools from {files_count} files")


def export_results(results: List[HarvestResult], config: HarvestConfig) -> None:
    """Export results in specified formats."""
    console.print(f"\n[cyan]Exporting results to {config.base_output_dir}[/cyan]")
    
    for format_name in config.output_formats:
        try:
            exporter = ExporterFactory.get_exporter(format_name)
            exporter.export_results(results, config.base_output_dir)
            console.print(f"[green]✓ Exported to {format_name.upper()} format[/green]")
        except Exception as e:
            console.print(f"[red]✗ Error exporting to {format_name}: {e}[/red]")


def display_summary(results: List[HarvestResult], total_time: float) -> None:
    """Display harvest summary statistics."""
    console.print("\n[bold cyan]Harvest Summary[/bold cyan]")
    
    total_repos = len(results)
    successful_repos = len([r for r in results if not r.errors])
    failed_repos = total_repos - successful_repos
    
    total_tools = sum(len(r.tools_found) for r in results)
    total_files = sum(r.total_files_scanned for r in results)
    
    # Create summary table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Repositories Processed", str(total_repos))
    table.add_row("Successful", str(successful_repos))
    table.add_row("Failed", str(failed_repos))
    table.add_row("Total Tools Extracted", str(total_tools))
    table.add_row("Total Files Scanned", str(total_files))
    table.add_row("Processing Time", f"{total_time:.1f} seconds")
    
    if total_tools > 0:
        table.add_row("Tools per Repository", f"{total_tools / total_repos:.1f}")
        table.add_row("Files per Tool", f"{total_files / total_tools:.1f}")
    
    console.print(table)
    
    # Show top providers if any tools found
    if total_tools > 0:
        provider_counts = {}
        for result in results:
            for tool in result.tools_found:
                provider = tool.provider or "Unknown"
                provider_counts[provider] = provider_counts.get(provider, 0) + 1
        
        if provider_counts:
            console.print("\n[bold cyan]Top Providers[/bold cyan]")
            sorted_providers = sorted(provider_counts.items(), key=lambda x: x[1], reverse=True)
            
            for provider, count in sorted_providers[:10]:
                console.print(f"  {provider}: {count} tools")


def analyze_jsonl_file(file_path: Path) -> None:
    """Analyze JSONL metadata file."""
    import json
    
    tools = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    tools.append(json.loads(line))
    except Exception as e:
        console.print(f"[red]Error reading JSONL file: {e}[/red]")
        return
    
    console.print(f"\n[cyan]Analysis of {file_path}[/cyan]")
    console.print(f"Total tools: {len(tools)}")
    
    # Analyze by provider
    providers = {}
    for tool in tools:
        provider = tool.get('provider', 'Unknown')
        providers[provider] = providers.get(provider, 0) + 1
    
    console.print(f"\nProviders: {len(providers)}")
    for provider, count in sorted(providers.items(), key=lambda x: x[1], reverse=True)[:10]:
        console.print(f"  {provider}: {count}")


def analyze_csv_file(file_path: Path) -> None:
    """Analyze CSV metadata file."""
    import pandas as pd
    
    try:
        df = pd.read_csv(file_path)
        console.print(f"\n[cyan]Analysis of {file_path}[/cyan]")
        console.print(f"Total tools: {len(df)}")
        
        if 'provider' in df.columns:
            provider_counts = df['provider'].value_counts().head(10)
            console.print(f"\nTop providers:")
            for provider, count in provider_counts.items():
                console.print(f"  {provider}: {count}")
                
    except Exception as e:
        console.print(f"[red]Error reading CSV file: {e}[/red]")


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()