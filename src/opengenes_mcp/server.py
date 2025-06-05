#!/usr/bin/env python3
"""OpenGenes MCP Server - Database query interface for OpenGenes aging research data."""

import asyncio
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from pydantic import BaseModel, Field
from eliot import start_action

# Get the database path using proper pathlib resolution
DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "open_genes.sqlite"

class QueryResult(BaseModel):
    """Result from a database query."""
    rows: List[Dict[str, Any]] = Field(description="Query result rows")
    count: int = Field(description="Number of rows returned")
    query: str = Field(description="The SQL query that was executed")

class DatabaseManager:
    """Manages SQLite database connections and queries."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}")
    
    def execute_query(self, sql: str, params: Optional[tuple] = None) -> QueryResult:
        """Execute a read-only SQL query and return results."""
        with start_action(action_type="execute_query", sql=sql, params=params) as action:
            # Basic safety check for read-only operations
            sql_upper = sql.upper().strip()
            if any(keyword in sql_upper for keyword in ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE']):
                action.log(message_type="query_rejected", error="Only SELECT queries are allowed")
                raise ValueError("Only SELECT queries are allowed")
            
            # Execute query - let any DB errors bubble up naturally
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # This allows dict-like access to rows
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                
                rows = cursor.fetchall()
                # Convert sqlite3.Row objects to dictionaries
                rows_dicts = [dict(row) for row in rows]
                
                result = QueryResult(
                    rows=rows_dicts,
                    count=len(rows_dicts),
                    query=sql
                )
                
                action.add_success_fields(rows_count=len(rows_dicts))
                return result

class OpenGenesTools(FastMCP):
    """OpenGenes MCP Server with database tools that can be inherited and extended."""
    
    def __init__(
        self, 
        name: str = "OpenGenes MCP Server",
        db_path: Path = DB_PATH,
        prefix: str = "opengenes_",
        huge_query_tool: bool = False,
        **kwargs
    ):
        """Initialize the OpenGenes tools with a database manager and FastMCP functionality."""
        # Initialize FastMCP with the provided name and any additional kwargs
        super().__init__(name=name, **kwargs)
        
        # Initialize our database manager
        self.db_manager = DatabaseManager(db_path)
        
        self.prefix = prefix
        self.huge_query_tool = huge_query_tool
        # Register our tools and resources
        self._register_opengenes_tools()
        self._register_opengenes_resources()
    
    def _register_opengenes_tools(self):
        """Register OpenGenes-specific tools."""
        self.tool(name=f"{self.prefix}get_schema_info", description="Get information about the database schema")(self.get_schema_info)
        self.tool(name=f"{self.prefix}example_queries", description="Get a list of example SQL queries")(self.get_example_queries)
        description = "Query the Opengenes database that contains data about genes involved in longevity, lifespan extension experiments on model organisms, and changes in human and other organisms with aging."
        if self.huge_query_tool:
            # Load and concatenate the prompt from data folder using proper pathlib resolution
            project_root = Path(__file__).resolve().parent.parent.parent
            prompt_path = project_root / "data" / "prompt.txt"
            try:
                with prompt_path.open("r", encoding="utf-8") as f:
                    prompt_content = f.read().strip()
                description = description + "\n\n" + prompt_content
            except FileNotFoundError:
                # Fallback if prompt file is not found
                pass
            self.tool(name=f"{self.prefix}db_query", description=description)(self.db_query)
        else:
            description = description + " Before caling this tool the first time, always check tools that provide schema information and example queries."
            self.tool(name=f"{self.prefix}db_query", description=description)(self.db_query)

    
    def _register_opengenes_resources(self):
        """Register OpenGenes-specific resources."""
        from opengenes_mcp.resources import register_resources
        register_resources(self)
    
    def db_query(self, sql: str) -> QueryResult:
        """
        Execute a read-only SQL query against the OpenGenes database.
        
        This tool queries the following tables:
        
        1. lifespan_change - Contains experimental data about genetic interventions and their effects on lifespan
        2. gene_criteria - Contains criteria classifications for aging-related genes  
        3. gene_hallmarks - Contains hallmarks of aging associated with specific genes
        4. longevity_associations - Contains genetic variants associated with longevity
        
        The database schema includes:
        - lifespan_change: HGNC, model_organism, sex, effect_on_lifespan, intervention details, lifespan measurements, etc.
        - gene_criteria: HGNC, criteria (12 different aging-related criteria)
        - gene_hallmarks: HGNC, hallmarks of aging 
        - longevity_associations: HGNC, polymorphism details, ethnicity, study type, etc.
        
        IMPORTANT: Only SELECT queries are allowed. No INSERT, UPDATE, DELETE, or DDL operations.
        
        Args:
            sql: The SQL SELECT query to execute
            
        Returns:
            QueryResult: Contains the query results, row count, and executed query
            
        Example queries:
        - SELECT HGNC, effect_on_lifespan FROM lifespan_change WHERE model_organism = 'mouse' LIMIT 10
        - SELECT DISTINCT criteria FROM gene_criteria
        - SELECT HGNC, COUNT(*) as experiments FROM lifespan_change GROUP BY HGNC ORDER BY experiments DESC LIMIT 20
        """
        with start_action(action_type="db_query_tool", sql=sql) as action:
            result = self.db_manager.execute_query(sql)
            return result

    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get information about the database schema including table names, column names, and enumerations.
        
        Returns:
            Dict containing table schemas, column information, and available enumerations
        """
        with start_action(action_type="get_schema_info") as action:
            # Get table information
            tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
            tables_result = self.db_manager.execute_query(tables_query)
            table_names = [row['name'] for row in tables_result.rows]
            
            action.add_success_fields(tables_found=len(table_names), table_names=table_names)
            
            schema_info = {
                "tables": {},
                "enumerations": {}
            }
            
            # Get column information for each table
            for table_name in table_names:
                pragma_query = f"PRAGMA table_info({table_name})"
                columns_result = self.db_manager.execute_query(pragma_query)
                
                schema_info["tables"][table_name] = {
                    "columns": [
                        {
                            "name": col["name"],
                            "type": col["type"],
                            "nullable": not col["notnull"],
                            "primary_key": bool(col["pk"])
                        }
                        for col in columns_result.rows
                    ]
                }
            
            # Add known enumerations from the prompt
            schema_info["enumerations"] = self._get_known_enumerations()
            
            action.add_success_fields(schema_retrieved=True, total_tables=len(table_names))
            return schema_info

    def get_example_queries(self) -> List[Dict[str, str]]:
        """
        Get a list of example SQL queries that can be used with the OpenGenes database.
        
        Returns:
            List of dictionaries containing example queries with descriptions
        """
        examples = [
            {
                "description": "Get top 10 genes with most lifespan experiments",
                "query": "SELECT HGNC, COUNT(*) as experiment_count FROM lifespan_change WHERE HGNC IS NOT NULL GROUP BY HGNC ORDER BY experiment_count DESC LIMIT 10"
            },
            {
                "description": "Find genes that increase lifespan in mice",
                "query": "SELECT DISTINCT HGNC, effect_on_lifespan FROM lifespan_change WHERE model_organism = 'mouse' AND effect_on_lifespan = 'increases lifespan' AND HGNC IS NOT NULL"
            },
            {
                "description": "Get all criteria for a specific gene (e.g., TP53)",
                "query": "SELECT criteria FROM gene_criteria WHERE HGNC = 'TP53'"
            },
            {
                "description": "Find genes associated with specific hallmarks of aging",
                "query": "SELECT HGNC, \"hallmarks of aging\" FROM gene_hallmarks WHERE \"hallmarks of aging\" LIKE '%mitochondrial%'"
            },
            {
                "description": "Get longevity associations for specific ethnicity",
                "query": "SELECT HGNC, \"polymorphism type\", \"nucleotide substitution\", ethnicity FROM longevity_associations WHERE ethnicity LIKE '%Italian%'"
            },
            {
                "description": "Count experiments by model organism",
                "query": "SELECT model_organism, COUNT(*) as count FROM lifespan_change GROUP BY model_organism ORDER BY count DESC"
            },
            {
                "description": "Find genes with both lifespan effects and longevity associations",
                "query": "SELECT DISTINCT lc.HGNC FROM lifespan_change lc INNER JOIN longevity_associations la ON lc.HGNC = la.HGNC WHERE lc.HGNC IS NOT NULL"
            },
            {
                "description": "Get genes with specific intervention methods",
                "query": "SELECT DISTINCT HGNC, intervention_method FROM lifespan_change WHERE intervention_method = 'gene knockout' AND HGNC IS NOT NULL"
            },
            {
                "description": "Find genes that affect both mammals and non-mammals",
                "query": """SELECT DISTINCT HGNC 
                           FROM lifespan_change 
                           WHERE HGNC IN (
                               SELECT HGNC FROM lifespan_change WHERE model_organism IN ('mouse', 'rat', 'rabbit', 'hamster')
                           ) AND HGNC IN (
                               SELECT HGNC FROM lifespan_change WHERE model_organism IN ('roundworm Caenorhabditis elegans', 'fly Drosophila melanogaster', 'yeasts')
                           )"""
            },
            {
                "description": "Get summary statistics for lifespan changes",
                "query": "SELECT effect_on_lifespan, COUNT(*) as count, AVG(lifespan_percent_change_mean) as avg_change FROM lifespan_change WHERE lifespan_percent_change_mean IS NOT NULL GROUP BY effect_on_lifespan"
            }
        ]
        
        return examples

    def _get_known_enumerations(self) -> Dict[str, Dict[str, List[str]]]:
        """Get the known enumerations for database fields."""
        return {
            "lifespan_change": {
                "model_organism": ["mouse", "roundworm Caenorhabditis elegans", "fly Drosophila melanogaster", "rabbit", "rat", "acyrthosiphon pisum", "yeasts", "fish Nothobranchius furzeri", "fungus Podospora anserina", "hamster", "zebrafish", "fish Nothobranchius guentheri"],
                "sex": ["male", "female", "all", "hermaphrodites", "not specified", "None"],
                "effect_on_lifespan": ["increases lifespan", "no change", "decreases lifespan", "increases lifespan in animals with decreased lifespans", "decreases survival under stress conditions", "improves survival under stress conditions", "decreases life span in animals with increased lifespans", "no change under stress conditions"],
                "main_effect_on_lifespan": ["loss of function", "switch of function", "gain of function"],
                "intervention_way": ["changes in genome level", "combined (inducible mutation)", "interventions by selective drug/RNAi"],
                "intervention_method": ["gene knockout", "gene modification to affect product activity/stability", "gene modification", "additional copies of a gene in the genome", "addition to the genome of a dominant-negative gene variant that reduces the activity of an endogenous protein", "treatment with vector with additional gene copies", "gene modification to reduce protein activity/stability", "interfering RNA transgene", "RNA interferention", "gene modification to increase protein activity/stability", "introduction into the genome of a construct under the control of a gene promoter, which causes death or a decrease in the viability of cells expressing the gene", "knockout of gene isoform", "tissue-specific gene knockout", "reduced expression of one of the isoforms in transgenic animals", "gene modification to reduce gene expression", "treatment with gene product inducer", "None", "tissue-specific gene overexpression", "additional copies of a gene in transgenic animals", "treatment with a gene product inhibitor", "treatment with protein", "gene modification to increase gene expression", "removal of cells expressing the gene", "splicing modification"]
            },
            "gene_criteria": {
                "criteria": ["Age-related changes in gene expression, methylation or protein activity", "Age-related changes in gene expression, methylation or protein activity in humans", "Association of genetic variants and gene expression levels with longevity", "Regulation of genes associated with aging", "Changes in gene activity extend non-mammalian lifespan", "Changes in gene activity protect against age-related impairment", "Age-related changes in gene expression, methylation or protein activity in non-mammals", "Changes in gene activity extend mammalian lifespan", "Changes in gene activity reduce mammalian lifespan", "Changes in gene activity enhance age-related deterioration", "Changes in gene activity reduce non-mammalian lifespan", "Association of the gene with accelerated aging in humans"]
            },
            "longevity_associations": {
                "polymorphism_type": ["SNP", "In/Del", "n/a", "haplotype", "VNTR", "PCR-RFLP"],
                "ethnicity": ["Caucasian, American", "European", "Greek", "Ashkenazi Jewish", "Polish", "Chinese", "Caucasian", "Italian", "Japanese", "Danish", "Spanish", "German", "European, East Asian, African American", "n/a", "Chinese, Han", "Italian, Southern", "German, American", "Caucasian, African-American", "East Asian, Europeans, Caucasian American", "Japanese American", "Italian, Calabrian", "Korean", "Belarusian", "mixed", "Caucasian, Ashkenazi Jewish", "Dutch", "Amish", "French", "Ashkenazi Jewish, Amish, Caucasian", "Japanese, Okinawan", "North-eastern Italian", "Tatars", "American, Caucasians; Italian, Southern; French; Ashkenazi Jewish", "Chinese, Bama Yao, Guangxi Province", "Swiss", "German, Danes, French", "American, Caucasian", "Italian, Central", "Finnish"],
                "study_type": ["GWAS", "iGWAS", "candidate genes study", "gene-based association approach", "family study", "single-variant association approach", "meta-analysis of GWAS, replication of previous findings", "meta-analysis of GWAS", "GWAS, discovery + replication", "GWAS, replication", "meta-analysis of GWAS, replication", "n/a", "meta-analysis of candidate gene studies", "immunochip, discovery + replication", "immunochip"],
                "sex": ["all", "male", "not specified", "female"]
            }
        }

# Initialize the OpenGenes MCP server (which inherits from FastMCP)
mcp = OpenGenesTools()

# CLI functions
def cli_app():
    """Run the MCP server."""
    mcp.run(transport="streamable-http")

def cli_app_stdio():
    """Run the MCP server with stdio transport."""
    mcp.run(transport="stdio")

def cli_app_sse():
    """Run the MCP server with SSE transport.""" 
    mcp.run(transport="sse")

if __name__ == "__main__":
    cli_app()