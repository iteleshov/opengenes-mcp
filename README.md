# opengenes-mcp

[![Tests](https://github.com/longevity-genie/opengenes-mcp/actions/workflows/test.yml/badge.svg)](https://github.com/longevity-genie/opengenes-mcp/actions/workflows/test.yml)
[![PyPI version](https://badge.fury.io/py/opengenes-mcp.svg)](https://badge.fury.io/py/opengenes-mcp)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

MCP (Model Context Protocol) server for OpenGenes database

This server implements the Model Context Protocol (MCP) for OpenGenes, providing a standardized interface for accessing aging and longevity research data. MCP enables AI assistants and agents to query comprehensive biomedical datasets through structured interfaces. The OpenGenes database contains:

- **lifespan_change**: Experimental data about genetic interventions and their effects on lifespan across model organisms
- **gene_criteria**: Criteria classifications for aging-related genes (12 different categories)  
- **gene_hallmarks**: Hallmarks of aging associated with specific genes
- **longevity_associations**: Genetic variants associated with longevity from population studies

If you want to understand more about what the Model Context Protocol is and how to use it more efficiently, you can take the [DeepLearning AI Course](https://www.deeplearning.ai/short-courses/mcp-build-rich-context-ai-apps-with-anthropic/) or search for MCP videos on YouTube.

## About MCP (Model Context Protocol)

MCP is a protocol that bridges the gap between AI systems and specialized domain knowledge. It enables:

- **Structured Access**: Direct connection to authoritative aging and longevity research data
- **Natural Language Queries**: Simplified interaction with specialized databases through SQL
- **Type Safety**: Strong typing and validation through FastMCP
- **AI Integration**: Seamless integration with AI assistants and agents

## Available Tools

This server provides three main tools for interacting with the OpenGenes database:

1. **`opengenes_db_query(sql: str)`** - Execute read-only SQL queries against the OpenGenes database
2. **`opengenes_get_schema_info()`** - Get detailed schema information including tables, columns, and enumerations
3. **`opengenes_example_queries()`** - Get a list of example SQL queries with descriptions

## Available Resources

1. **`resource://db-prompt`** - Complete database schema documentation and usage guidelines
2. **`resource://schema-summary`** - Formatted summary of tables and their purposes

## Quick Start

### Installing uv

```bash
# Download and install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
uvx --version
```

uvx is a very nice tool that can run a python package installing it if needed.

### Running with uvx

You can run the opengenes-mcp server directly using uvx without cloning the repository:

#### STDIO Mode (for MCP clients that require stdio, can be useful when you want to save files)
```bash
# Run the server in stdio mode (default)
uvx opengenes-mcp

# Or explicitly specify stdio mode
uvx opengenes-mcp stdio
```

#### HTTP Mode (Web Server)
```bash
# Run the server in streamable HTTP mode on default (3001) port
uvx opengenes-mcp server

# Run on a specific port
uvx opengenes-mcp server --port 8000
```

#### SSE Mode (Server-Sent Events)
```bash
# Run the server in SSE mode
uvx opengenes-mcp sse
```

The HTTP mode will start a web server that you can access at `http://localhost:3001/mcp` (with documentation at `http://localhost:3001/docs`). The STDIO mode is designed for MCP clients that communicate via standard input/output, while SSE mode uses Server-Sent Events for real-time communication.

## Configuring your AI Client (Anthropic Claude Desktop, Cursor, Windsurf, etc.)

We provide preconfigured JSON files for different use cases:

### For STDIO mode (recommended):
Use `mcp-config-stdio.json` for connecting to the server via uvx:

```json
{
  "mcpServers": {
    "opengenes-mcp": {
      "command": "uvx",
      "args": ["opengenes-mcp"],
      "env": {
        "MCP_PORT": "3001",
        "MCP_HOST": "0.0.0.0",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

### For HTTP mode:
Use `mcp-config.json` for connecting to a locally running HTTP server:

```json
{
  "mcpServers": {
    "opengenes-mcp": {
      "url": "http://localhost:3001/mcp",
      "type": "streamable-http",
      "env": {
        "API_ACCESS_TOKEN": "access-token"
      }
    }
  }
}
```

### For local development:
Use `mcp-config-stdio-debug.json` when working with the cloned repository:

```json
{
  "mcpServers": {
    "opengenes-mcp": {
      "command": "uv",
      "args": ["run", "stdio"],
      "env": {
        "MCP_PORT": "3001",
        "MCP_HOST": "0.0.0.0",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

### Inspecting OpenGenes MCP server

If you want to inspect the methods provided by the MCP server, use npx (you may need to install nodejs and npm):

For STDIO mode with uvx:
```bash
npx @modelcontextprotocol/inspector --config mcp-config-stdio.json --server opengenes-mcp
```

For HTTP mode (ensure server is running first):
```bash
npx @modelcontextprotocol/inspector --config mcp-config.json --server opengenes-mcp
```

For local development:
```bash
npx @modelcontextprotocol/inspector --config mcp-config-stdio-debug.json --server opengenes-mcp
```

You can also run the inspector manually and configure it through the interface:
```bash
npx @modelcontextprotocol/inspector
```

After that you can explore the tools and resources with MCP Inspector at http://127.0.0.1:6274 (note, if you run inspector several times it can change port)

### Integration with AI Systems

To integrate this server with your MCP-compatible AI client, you can use one of the preconfigured JSON files provided in this repository:

*   **For connecting via STDIO mode (recommended):** Use `mcp-config-stdio.json`. This uses uvx to run the published package and doesn't require you to run anything locally first.
*   **For connecting to a locally running HTTP server:** Use `mcp-config.json`. Ensure the server is running first via `uv run server` (see [Running the MCP Server](#running-the-mcp-server)).
*   **For local development:** Use `mcp-config-stdio-debug.json`. This is useful when working with the cloned repository during development.

Simply point your AI client (like Cursor, Windsurf, ClaudeDesktop, VS Code with Copilot, or [others](https://github.com/punkpeye/awesome-mcp-clients)) to use the appropriate configuration file.

## Repository setup

```bash
# Clone the repository
git clone https://github.com/longevity-genie/opengenes-mcp.git
cd opengenes-mcp
uv sync
```

### Running the MCP Server

If you already cloned the repo you can run the server with uv:

```bash
# Start the MCP server locally (HTTP mode)
uv run server

# Or start in STDIO mode  
uv run stdio

# Or start in SSE mode
uv run sse
```

## Database Schema

### Main Tables

- **lifespan_change** (47 columns): Experimental lifespan data with intervention details across model organisms
- **gene_criteria** (2 columns): Gene classifications by aging criteria (12 different categories)
- **gene_hallmarks** (2 columns): Hallmarks of aging mappings for genes
- **longevity_associations** (11 columns): Population genetics longevity data from human studies

### Key Fields

- **HGNC**: Gene symbol (primary identifier across all tables)
- **model_organism**: Research organism (mouse, C. elegans, fly, etc.)
- **effect_on_lifespan**: Direction of lifespan change (increases/decreases/no change)
- **intervention_method**: Method of genetic intervention (knockout, overexpression, etc.)
- **criteria**: Aging-related gene classification (12 categories)
- **hallmarks of aging**: Biological aging processes associated with genes

## Example Queries

```sql
-- Get top genes with most lifespan experiments
SELECT HGNC, COUNT(*) as experiment_count 
FROM lifespan_change 
WHERE HGNC IS NOT NULL 
GROUP BY HGNC 
ORDER BY experiment_count DESC 
LIMIT 10;

-- Find genes that increase lifespan in mice
SELECT DISTINCT HGNC, effect_on_lifespan 
FROM lifespan_change 
WHERE model_organism = 'mouse' 
AND effect_on_lifespan = 'increases lifespan' 
AND HGNC IS NOT NULL;

-- Get hallmarks of aging for genes
SELECT HGNC, "hallmarks of aging" 
FROM gene_hallmarks 
WHERE "hallmarks of aging" LIKE '%mitochondrial%';

-- Find longevity associations by ethnicity
SELECT HGNC, "polymorphism type", "nucleotide substitution", ethnicity 
FROM longevity_associations 
WHERE ethnicity LIKE '%Italian%';

-- Find genes with both lifespan effects and longevity associations
SELECT DISTINCT lc.HGNC 
FROM lifespan_change lc 
INNER JOIN longevity_associations la ON lc.HGNC = la.HGNC 
WHERE lc.HGNC IS NOT NULL;
```

## Safety Features

- **Read-only access**: Only SELECT queries are allowed
- **Input validation**: Blocks INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, TRUNCATE operations
- **Error handling**: Comprehensive error handling with informative messages

## Testing & Verification

### Environment Setup for LLM Agent Tests

If you want to run LLM agent tests that use MCP functions with Gemini models, you need to set up a `.env` file with your Gemini API key:

```bash
# Create a .env file in the project root
echo "GEMINI_API_KEY=your-gemini-api-key-here" > .env
```

**Note:** The `.env` file and Gemini API key are only required for running LLM agent tests. All other tests and basic MCP server functionality work without any API keys.

### Running Tests

Run tests for the MCP server:
```bash
uv run pytest -vvv -s
```

You can also run manual tests:
```bash
uv run python test/manual_test_questions.py
```

You can use MCP inspector with locally built MCP server same way as with uvx.

*Note: Using the MCP Inspector is optional. Most MCP clients (like Cursor, Windsurf, etc.) will automatically display the available tools from this server once configured. However, the Inspector can be useful for detailed testing and exploration.*

*If you choose to use the Inspector via `npx`, ensure you have Node.js and npm installed. Using [nvm](https://github.com/nvm-sh/nvm) (Node Version Manager) is recommended for managing Node.js versions.*

## Example questions that MCP helps to answer

* What genes need to be downregulated in worms to extend their lifespan?
* What processes are improved in GHR knockout mice?
* Which genetic intervention led to the greatest increase in lifespan in flies?
* To what extent did the lifespan increase in mice overexpressing VEGFA?
* Are there any liver-specific interventions that increase lifespan in mice?
* Which gene-longevity association is confirmed by the greatest number of studies?
* What polymorphisms in FOXO3 are associated with human longevity?
* In which ethnic groups was the association of the APOE gene with longevity shown?
* Is the INS gene polymorphism associated with longevity?
* What genes are associated with transcriptional alterations?
* Which hallmarks are associated with the KL gene?
* What genes change their expression with aging in humans?
* How many genes are associated with longevity in humans?
* What types of studies have been conducted on the IGF1R gene?
* What evidence of the link between PTEN and aging do you know? 
* What genes are associated with both longevity and altered expression in aged humans?
* Is the expression of the ACE2 gene altered with aging in humans?
* Interventions on which genes extended mice lifespan most of all?
* Which knockdowns were most lifespan extending on model animals?

## License

This project is licensed under the MIT License.

## Acknowledgments

- [OpenGenes Database](https://open-genes.com/) for the comprehensive aging research data
- [Model Context Protocol](https://modelcontextprotocol.io/) for the protocol specification
- [FastMCP](https://github.com/jlowin/fastmcp) for the MCP server framework

This project is part of the [Longevity Genie](https://github.com/longevity-genie) organization, which develops open-source AI assistants and libraries for health, genetics, and longevity research.

We are supported by:

[![HEALES](https://heales.org/images/heales.jpg)](https://heales.org/)

*HEALES - Healthy Life Extension Society*

and

[![IBIMA](https://ibima.med.uni-rostock.de/images/IBIMA.jpg)](https://ibima.med.uni-rostock.de/)

[IBIMA - Institute for Biostatistics and Informatics in Medicine and Ageing Research](https://ibima.med.uni-rostock.de/)
