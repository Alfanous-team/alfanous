#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facet Search Examples for Alfanous API

This script demonstrates how to use the faceted search feature in Alfanous
to get aggregated counts of search results grouped by various fields.
"""

from alfanous import api

def print_separator():
    print("\n" + "=" * 70 + "\n")

def example_1_basic_facet():
    """Example 1: Basic facet search by sura_id"""
    print("Example 1: Search for 'الله' (Allah) with sura facets")
    print_separator()
    
    results = api.search(query="الله", facets="sura_id", flags={"perpage": 5})
    
    print(f"Total results: {results['search']['interval']['total']}")
    print(f"\nFirst 5 results:")
    for i, aya in list(results['search']['ayas'].items())[:5]:
        print(f"  [{i}] Sura {aya['identifier']['sura_id']}:{aya['identifier']['aya_id']} - {aya['identifier']['sura_name']}")
    
    print(f"\nTop 10 Suras by frequency:")
    for facet in results['search']['facets']['sura_id'][:10]:
        print(f"  Sura {facet['value']}: {facet['count']} occurrences")

def example_2_multiple_facets():
    """Example 2: Multiple facets at once"""
    print("Example 2: Search for 'الصلاة' (prayer) with multiple facets")
    print_separator()
    
    results = api.search(query="الصلاة", facets="sura_id,juz", flags={"perpage": 3})
    
    print(f"Total results: {results['search']['interval']['total']}")
    
    print(f"\nTop 5 Suras:")
    for facet in results['search']['facets']['sura_id'][:5]:
        print(f"  Sura {facet['value']}: {facet['count']} occurrences")
    
    print(f"\nTop 5 Juz (parts):")
    for facet in results['search']['facets']['juz'][:5]:
        print(f"  Juz {facet['value']}: {facet['count']} occurrences")

def example_3_filter_and_facet():
    """Example 3: Filter by field and get facets"""
    print("Example 3: Search in Sura 2 (Al-Baqara) with chapter facets")
    print_separator()
    
    results = api.search(query="sura_id:2", facets="chapter", flags={"perpage": 5})
    
    print(f"Total verses in Sura 2: {results['search']['interval']['total']}")
    
    print(f"\nTop 10 chapters/themes in Sura 2:")
    for facet in results['search']['facets']['chapter'][:10]:
        print(f"  {facet['value']}: {facet['count']} verses")

def example_4_juz_distribution():
    """Example 4: View distribution across Juz"""
    print("Example 4: Distribution of 'الجنة' (paradise) across Juz")
    print_separator()
    
    results = api.search(query="الجنة", facets="juz")
    
    print(f"Total results: {results['search']['interval']['total']}")
    
    print(f"\nDistribution by Juz (showing all):")
    for facet in results['search']['facets']['juz']:
        print(f"  Juz {facet['value']:2d}: {facet['count']:3d} occurrences")

def example_5_using_do_method():
    """Example 5: Using the do() method"""
    print("Example 5: Using api.do() method with facets")
    print_separator()
    
    results = api.do({
        "action": "search",
        "query": "محمد",
        "facets": "sura_id,sura_type",
        "page": 1,
        "perpage": 3
    })
    
    print(f"Total results: {results['search']['interval']['total']}")
    
    print(f"\nSuras containing 'محمد':")
    for facet in results['search']['facets']['sura_id']:
        print(f"  Sura {facet['value']}: {facet['count']} occurrences")
    
    print(f"\nDistribution by Sura type:")
    for facet in results['search']['facets']['sura_type']:
        print(f"  {facet['value']}: {facet['count']} occurrences")

def main():
    print("\n")
    print("*" * 70)
    print("  Alfanous Facet Search Examples")
    print("*" * 70)
    
    example_1_basic_facet()
    example_2_multiple_facets()
    example_3_filter_and_facet()
    example_4_juz_distribution()
    example_5_using_do_method()
    
    print_separator()
    print("All examples completed successfully!")
    print("\nAvailable facet fields:")
    print("  - sura_id: Group by Sura (chapter) number")
    print("  - juz: Group by Juz (part) number")
    print("  - chapter: Group by main topic/chapter")
    print("  - topic: Group by subtopic")
    print("  - sura_type: Group by Meccan/Medinan classification")
    print()

if __name__ == "__main__":
    main()
