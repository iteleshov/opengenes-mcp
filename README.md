# opengenes-mcp

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

### For STDIO mode (recommended):
Create a configuration file for your MCP client:

```json
{
  "mcpServers": {
    "opengenes-mcp": {
      "command": "uvx",
      "args": ["opengenes-mcp"]
    }
  }
}
```

### For HTTP mode:
If you prefer to run the server as a web service:

```json
{
  "mcpServers": {
    "opengenes-mcp": {
      "url": "http://localhost:3001/mcp"
    }
  }
}
```

### Inspecting OpenGenes MCP server

If you want to inspect the methods provided by the MCP server, use npx (you may need to install nodejs and npm):

For STDIO mode:
```bash
npx @modelcontextprotocol/inspector
```

Then manually configure:
- **Command**: `uvx`
- **Arguments**: `["opengenes-mcp"]`

For HTTP mode (if server is running):
```bash
npx @modelcontextprotocol/inspector
```

Then manually configure:
- **URL**: `http://localhost:3001/mcp`

After that you can explore the tools and resources with MCP Inspector at http://127.0.0.1:6274

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

Run tests for the MCP server:
```bash
uv run pytest -vvv -s
```

You can also run manual tests:
```bash
uv run python test/manual_test_questions.py
```

## Architecture

The server is built using:

- **FastMCP**: Modern MCP framework for Python
- **SQLite**: Local database storage for OpenGenes data
- **Pydantic**: Data validation and serialization
- **aiosqlite**: Async SQLite support
- **Eliot**: Structured logging

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
