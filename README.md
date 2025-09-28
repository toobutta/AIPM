# AIPM GitHub Harvester

Extract AI tool/function invocation metadata from GitHub repositories for the AIPM registry.

## Overview

The AIPM GitHub Harvester is a Python tool that automatically discovers and extracts metadata about AI tools, functions, and their invocation patterns from GitHub repositories. It parses various file types including documentation, READMEs, OpenAPI specifications, MCP configurations, and tool definitions to build a comprehensive registry of AI capabilities.

## Features

- **Repository Discovery**: Process multiple repositories from a simple text file
- **Multi-format Parsing**: Support for docs, READMs, OpenAPI specs (JSON/YAML), MCP configs, and tool definitions
- **AIPM Mapping**: Automatically map discovered metadata to AIPM standard fields
- **Multiple Output Formats**: Generate both JSONL and CSV outputs for flexibility
- **GitHub Integration**: Built-in GitHub Action for automated nightly runs and PR-triggered updates
- **Data Registry**: Organized output structure in `data/registry/` for easy consumption

## Installation

### From Source

```bash
git clone https://github.com/toobutta/AIPM.git
cd AIPM
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/toobutta/AIPM.git
cd AIPM
pip install -e ".[dev]"
pre-commit install
```

## Usage

### CLI Interface

```bash
# Process repositories from a file
aipm-harvester harvest --repos-file repos.txt --output-dir data/registry/

# Process a single repository
aipm-harvester harvest --repo https://github.com/example/repo --output-dir data/registry/

# With custom configuration
aipm-harvester harvest --repos-file repos.txt --config config.yaml --output-dir data/registry/
```

### Input Format

Create a `repos.txt` file with one repository URL per line:

```
https://github.com/openai/openai-python
https://github.com/anthropic-ai/anthropic-sdk-python
https://github.com/microsoft/semantic-kernel
```

### Configuration

The harvester supports configuration via YAML files:

```yaml
# config.yaml
output:
  formats: ["jsonl", "csv"]
  base_dir: "data/registry"

parsing:
  include_patterns:
    - "docs/**"
    - "README*"
    - "examples/**"
    - "openapi/*.{json,yaml,yml}"
    - "mcp/**"
    - "tools/**"
  
  exclude_patterns:
    - "node_modules/**"
    - ".git/**"
    - "**/__pycache__/**"

github:
  token: ${GITHUB_TOKEN}  # Optional for private repos
```

## AIPM Field Mapping

The harvester extracts and maps the following AIPM fields:

- **functions**: Discovered function/tool definitions
- **invocation_paradigm**: How tools are invoked (API, CLI, SDK, etc.)
- **args/result schema**: Input/output schemas and types
- **protocol**: Communication protocol (HTTP, gRPC, WebSocket, etc.)
- **provider**: Tool provider/organization
- **model**: AI model requirements or compatibility

## Output Structure

```
data/registry/
├── harvested_metadata.jsonl    # Line-delimited JSON output
├── harvested_metadata.csv      # CSV format for analysis
├── functions/                  # Function-specific extracts
│   ├── openai_functions.jsonl
│   └── anthropic_functions.jsonl
└── repositories/               # Per-repo metadata
    ├── openai_openai-python.jsonl
    └── anthropic_anthropic-sdk-python.jsonl
```

## GitHub Action

The harvester includes a GitHub Action for automated processing:

```yaml
# .github/workflows/harvest.yml
name: AIPM Harvester
on:
  schedule:
    - cron: "0 2 * * *"  # Nightly at 2 AM UTC
  pull_request:
    paths: ["repos.txt", "config.yaml"]

jobs:
  harvest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run AIPM Harvester
        uses: ./
        with:
          repos-file: repos.txt
          output-dir: data/registry/
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black .
ruff check --fix .

# Type checking
mypy aipm_github_harvester/
```

### Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all checks pass
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- Issues: [GitHub Issues](https://github.com/toobutta/AIPM/issues)
- Documentation: [Project Wiki](https://github.com/toobutta/AIPM/wiki)