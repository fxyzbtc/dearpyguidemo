#!/usr/bin/env python3
"""
Test script to validate the combined search and filter functionality.
This script checks if the JavaScript functions are properly integrated.
"""

import os
import re

def check_implementation():
    """Check if the combined filter implementation is correctly added."""
    
    html_file = "spslinksall_interactive.html"
    
    if not os.path.exists(html_file):
        print("❌ HTML file not found!")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("currentProtocolFilter variable", r"let currentProtocolFilter"),
        ("applyCombinedFilter function", r"function applyCombinedFilter\(\)"),
        ("applyCombinedSearchAndProtocolFilter function", r"function applyCombinedSearchAndProtocolFilter\(\)"),
        ("clearAllFilters function", r"function clearAllFilters\(\)"),
        ("updateFilterStatus function", r"function updateFilterStatus\(\)"),
        ("Clear All button", r"Clear All"),
        ("Tooltip attributes", r"title="),
    ]
    
    results = []
    for check_name, pattern in checks:
        if re.search(pattern, content):
            results.append(f"✅ {check_name} - Found")
        else:
            results.append(f"❌ {check_name} - Missing")
    
    for result in results:
        print(result)
    
    # Check for any syntax errors in key functions
    critical_functions = [
        "applyCombinedFilter",
        "filterProtocol", 
        "handleSearch",
        "clearAllFilters"
    ]
    
    print("\n🔍 Checking function integrity:")
    for func in critical_functions:
        pattern = rf"function {func}\([^)]*\)\s*\{{[^}}]*\}}"
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            print(f"✅ {func} function structure looks good")
        else:
            print(f"⚠️  {func} function might have syntax issues")
    
    return True

def generate_test_cases():
    """Generate test cases for manual testing."""
    
    test_cases = [
        {
            "name": "Basic Search",
            "steps": [
                "1. Type 'HLR' in search box",
                "2. Verify nodes containing HLR are highlighted",
                "3. Check status shows 'Search: HLR (X matches)'"
            ]
        },
        {
            "name": "Protocol Filter Only",
            "steps": [
                "1. Click 'M3UA' button",
                "2. Verify only M3UA nodes are visible",
                "3. Check status shows 'M3UA filter'"
            ]
        },
        {
            "name": "Combined Search + Protocol",
            "steps": [
                "1. Type 'HLR' in search box",
                "2. Click 'M3UA' button", 
                "3. Verify only M3UA nodes containing HLR are visible",
                "4. Check status shows 'Search: HLR (X matches) + M3UA filter'"
            ]
        },
        {
            "name": "Clear Search Only",
            "steps": [
                "1. Have both search and protocol filters active",
                "2. Click 'Clear Search' button",
                "3. Verify search is cleared but M3UA filter remains",
                "4. Check status shows only 'M3UA filter'"
            ]
        },
        {
            "name": "Clear All Filters",
            "steps": [
                "1. Have both search and protocol filters active",
                "2. Click 'Clear All' button",
                "3. Verify all filters are cleared",
                "4. Check status shows 'No filter'"
            ]
        }
    ]
    
    print("\n📋 Manual Test Cases:")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        for step in test_case['steps']:
            print(f"   {step}")
    
    print("\n" + "=" * 50)
    print("💡 Tips:")
    print("- Open spslinksall_interactive.html in browser")
    print("- Use browser developer tools (F12) to check for errors")
    print("- Test with different search terms: HLR, MSC, SPS_A")
    print("- Try RegExp patterns like '^SPS.*HLR' or 'M3LNK.*01$'")

if __name__ == "__main__":
    print("🔍 Combined Search + Filter Implementation Checker")
    print("=" * 55)
    
    check_implementation()
    generate_test_cases()
    
    print(f"\n📂 Files to test:")
    print(f"   • spslinksall_interactive.html (main implementation)")
    print(f"   • COMBINED_FILTER_README.md (documentation)")
