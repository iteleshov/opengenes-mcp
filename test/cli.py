#!/usr/bin/env python3
"""Command-line interface for OpenGenes MCP testing tools."""

import sys
import argparse
from typing import List, Optional, Dict, Any
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from test_prompt_validation import (
    run_validation_tests, 
    run_specific_test as run_validation_test,
    list_available_tests
)
from test_query_performance import (
    run_performance_benchmarks,
    run_quick_benchmark
)
from test_server import main as run_server_tests


def run_all_tests(verbose: bool = False) -> int:
    """Run all test suites."""
    print("🧪 Running OpenGenes MCP Test Suite")
    print("=" * 50)
    
    test_suites: List[tuple[str, callable]] = [
        ("Server Tests", run_server_tests),
        ("Prompt Validation Tests", run_validation_tests),
        ("Performance Benchmarks", run_performance_benchmarks)
    ]
    
    failed_suites: List[str] = []
    
    for suite_name, test_function in test_suites:
        print(f"\n🔍 Running {suite_name}...")
        print("-" * 30)
        
        try:
            exit_code = test_function()
            if exit_code == 0:
                print(f"✅ {suite_name} passed")
            else:
                print(f"❌ {suite_name} failed (exit code: {exit_code})")
                failed_suites.append(suite_name)
        except Exception as e:
            print(f"💥 {suite_name} crashed: {e}")
            failed_suites.append(suite_name)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUITE SUMMARY")
    print("=" * 50)
    
    total_suites = len(test_suites)
    passed_suites = total_suites - len(failed_suites)
    
    print(f"Total test suites: {total_suites}")
    print(f"Passed: {passed_suites}")
    print(f"Failed: {len(failed_suites)}")
    
    if failed_suites:
        print(f"\n❌ Failed suites: {', '.join(failed_suites)}")
        return 1
    else:
        print("\n🎉 All test suites passed!")
        return 0


def run_quick_tests() -> int:
    """Run quick validation tests only."""
    print("⚡ Running Quick Tests")
    print("=" * 30)
    
    # Run server connectivity test
    print("🔗 Testing database connectivity...")
    try:
        run_server_tests()  # This function prints its own results
        print("✅ Server tests completed")
    except SystemExit as e:
        if e.code != 0:
            print("❌ Server tests failed")
            return 1
    except Exception as e:
        print(f"❌ Server test error: {e}")
        return 1
    
    # Run quick performance benchmark
    print("\n⏱️  Running quick performance benchmark...")
    run_quick_benchmark()
    
    # Run a subset of validation tests
    print("\n✅ Running core validation tests...")
    import pytest
    validation_exit = pytest.main([
        "test/test_prompt_validation.py::TestPromptQueryValidation::test_genes_increase_lifespan",
        "test/test_prompt_validation.py::TestPromptQueryValidation::test_hallmarks_multi_value_search",
        "test/test_prompt_validation.py::TestPromptQueryValidation::test_database_structure",
        "-v", "--tb=short"
    ])
    
    if validation_exit == 0:
        print("\n🎉 Quick tests completed successfully!")
        return 0
    else:
        print("\n❌ Some quick tests failed")
        return 1


def validate_query(query: str) -> int:
    """Validate a specific SQL query."""
    print(f"🔍 Validating query: {query}")
    print("-" * 50)
    
    try:
        from opengenes_mcp.server import db_query
        result = db_query(query)
        
        print(f"✅ Query executed successfully")
        print(f"📊 Returned {result.count} rows")
        
        if result.rows and result.count > 0:
            print(f"📝 Sample result: {result.rows[0]}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return 1


def show_test_categories() -> None:
    """Show available test categories."""
    categories: Dict[str, str] = {
        "server": "Basic server functionality and database connectivity",
        "validation": "Prompt query validation and multi-value field tests", 
        "performance": "Query performance benchmarks and optimization tests",
        "integrity": "Data integrity and referential consistency tests",
        "all": "Run all test categories",
        "quick": "Run essential tests only (faster execution)"
    }
    
    print("📋 Available Test Categories")
    print("=" * 40)
    
    for category, description in categories.items():
        print(f"  {category:<12} - {description}")


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OpenGenes MCP Testing CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test/cli.py --all                    # Run all tests
  python test/cli.py --quick                  # Run quick tests only
  python test/cli.py --category validation    # Run validation tests
  python test/cli.py --performance            # Run performance benchmarks
  python test/cli.py --validate "SELECT COUNT(*) FROM lifespan_change"
  python test/cli.py --list-tests            # List available test methods
        """
    )
    
    parser.add_argument("--all", action="store_true", 
                       help="Run all test suites")
    parser.add_argument("--quick", action="store_true",
                       help="Run quick essential tests only")
    parser.add_argument("--category", choices=["server", "validation", "performance", "integrity"],
                       help="Run specific test category")
    parser.add_argument("--performance", action="store_true",
                       help="Run performance benchmarks")
    parser.add_argument("--validate", type=str,
                       help="Validate a specific SQL query")
    parser.add_argument("--list-tests", action="store_true",
                       help="List available test methods")
    parser.add_argument("--list-categories", action="store_true",
                       help="List available test categories")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Handle list options
    if args.list_categories:
        show_test_categories()
        return 0
    
    if args.list_tests:
        list_available_tests()
        return 0
    
    # Handle validation
    if args.validate:
        return validate_query(args.validate)
    
    # Handle test execution
    if args.all:
        return run_all_tests(args.verbose)
    elif args.quick:
        return run_quick_tests()
    elif args.performance:
        return run_performance_benchmarks()
    elif args.category == "server":
        return run_server_tests()
    elif args.category == "validation":
        return run_validation_tests()
    elif args.category == "performance":
        return run_performance_benchmarks()
    elif args.category == "integrity":
        import pytest
        return pytest.main(["test/test_prompt_validation.py::TestDataIntegrity", "-v"])
    else:
        # Default: show help and available categories
        parser.print_help()
        print("\n")
        show_test_categories()
        return 0


if __name__ == "__main__":
    sys.exit(main()) 