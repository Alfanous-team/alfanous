#!/usr/bin/env python3
"""
Example script demonstrating the linguistic operations in Alfanous API

This script shows how to use the new linguistic operations:
- vocalize: Add diacritical marks (tashkeel) to Arabic text
- derive: Find roots and derivations of Arabic words
"""

import sys
sys.path.insert(0, 'src')

import alfanous.api as api


def example_vocalize():
    """Example of vocalization operation"""
    print("=" * 60)
    print("VOCALIZATION EXAMPLE")
    print("=" * 60)
    
    # Example 1: Vocalize a simple phrase
    text = "الحمد لله"
    result = api.linguistic(text, operation="vocalize")
    
    print(f"\nOriginal text:    {text}")
    print(f"Vocalized text:   {result['linguistic']['vocalized']}")
    
    # Example 2: Vocalize another phrase
    text = "بسم الله الرحمن الرحيم"
    result = api.linguistic(text, operation="vocalize")
    
    print(f"\nOriginal text:    {text}")
    print(f"Vocalized text:   {result['linguistic']['vocalized']}")


def example_derive():
    """Example of derivation operation"""
    print("\n" + "=" * 60)
    print("DERIVATION EXAMPLE")
    print("=" * 60)
    
    # Example 1: Find root and derivations of a single word
    text = "الحمد"
    result = api.linguistic(text, operation="derive")
    
    print(f"\nWord: {text}")
    word_info = result['linguistic']['words'][0]
    print(f"Lemma (جذر): {word_info['lemma']}")
    print(f"Root (أصل): {word_info['root']}")
    print(f"Lemma derivations (اشتقاقات من نفس الجذر): {', '.join(word_info['lemma_derivations'][:5])}")
    print(f"Root derivations (مشتقات أخرى): {', '.join(word_info['root_derivations'][:5])}")
    
    # Example 2: Analyze multiple words
    text = "الحمد لله"
    result = api.linguistic(text, operation="derive")
    
    print(f"\nPhrase: {text}")
    for word_info in result['linguistic']['words']:
        print(f"\n  Word: {word_info['word']}")
        print(f"    Lemma: {word_info['lemma']}")
        print(f"    Root: {word_info['root']}")
        if word_info['lemma_derivations']:
            print(f"    Sample derivations: {', '.join(word_info['lemma_derivations'][:3])}")


def example_using_do():
    """Example using the low-level do() API"""
    print("\n" + "=" * 60)
    print("USING do() API DIRECTLY")
    print("=" * 60)
    
    # Using do() for vocalize
    result = api.do({
        "action": "linguistic",
        "query": "قل هو الله احد",
        "operation": "vocalize"
    })
    
    print(f"\nVocalize via do():")
    print(f"  Input:  {result['linguistic']['text']}")
    print(f"  Output: {result['linguistic']['vocalized']}")
    
    # Using do() for derive
    result = api.do({
        "action": "linguistic",
        "query": "الله",
        "operation": "derive"
    })
    
    print(f"\nDerive via do():")
    word_info = result['linguistic']['words'][0]
    print(f"  Word: {word_info['word']}")
    print(f"  Lemma: {word_info['lemma']}")
    print(f"  Root: {word_info['root']}")


if __name__ == "__main__":
    example_vocalize()
    example_derive()
    example_using_do()
    
    print("\n" + "=" * 60)
    print("Examples completed successfully!")
    print("=" * 60)
