"""Resources for OpenGenes MCP Server."""

from pathlib import Path
from fastmcp import FastMCP
from eliot import start_action, Message

# Get the prompt file path
PROMPT_PATH = Path(__file__).parent.parent.parent / "data" / "prompt.txt"

def register_resources(mcp: FastMCP):
    """Register resources with the MCP server."""
    
    @mcp.resource("resource://db-prompt")
    def get_db_prompt() -> str:
        """
        Get the database prompt that describes the OpenGenes database schema and usage guidelines.
        
        This resource contains detailed information about:
        - Database tables and their schemas
        - Column enumerations and valid values
        - Usage guidelines for querying the database
        - Examples of common queries
        
        Returns:
            The complete database prompt text
        """
        with start_action(action_type="get_db_prompt", prompt_path=str(PROMPT_PATH)) as action:
            try:
                if PROMPT_PATH.exists():
                    content = PROMPT_PATH.read_text(encoding='utf-8')
                    action.add_success_fields(file_exists=True, content_length=len(content))
                    return content
                else:
                    action.add_error_fields(file_exists=False, error="Prompt file not found")
                    Message.new(message_type="prompt_file_not_found", path=str(PROMPT_PATH)).write()
                    return "Database prompt file not found."
            except Exception as e:
                action.add_error_fields(error=str(e), error_type="file_read_error")
                return f"Error reading prompt file: {e}"
    
    @mcp.resource("resource://schema-summary")
    def get_schema_summary() -> str:
        """
        Get a summary of the OpenGenes database schema.
        
        Returns:
            A formatted summary of tables and their purposes
        """
        summary = """OpenGenes Database Schema Summary

1. lifespan_change
   - Contains experimental data about genetic interventions and their effects on lifespan
   - Key columns: HGNC (gene symbol), model_organism, sex, effect_on_lifespan
   - Includes intervention details, lifespan measurements, significance data
   - Contains data from various model organisms (mouse, C. elegans, fly, etc.)

2. gene_criteria  
   - Contains criteria classifications for aging-related genes
   - Key columns: HGNC (gene symbol), criteria
   - 12 different aging-related criteria categories
   - Links genes to specific aging research criteria

3. gene_hallmarks
   - Contains hallmarks of aging associated with specific genes  
   - Key columns: HGNC (gene symbol), hallmarks of aging
   - Maps genes to biological hallmarks of aging process
   - Includes various aging-related cellular and molecular processes

4. longevity_associations
   - Contains genetic variants associated with longevity
   - Key columns: HGNC (gene symbol), polymorphism details, ethnicity, study type
   - Population genetics data from longevity studies
   - Includes SNPs, indels, and other genetic variations

All tables are linked by HGNC gene symbols, allowing for comprehensive cross-table queries about aging-related genes."""
        
        return summary 