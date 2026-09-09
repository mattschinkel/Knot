from knot.values import Program, Value, Bracketed, BracketedValue
from knot.ast import Program as ASTProgram

import re

def parse_program(text: str) -> Program:
    """Parse a program from text using canonical bracket syntax."""

    # Split on newlines and strip whitespace
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # Join lines with spaces for processing
    content = ' '.join(lines)

    # Use regex to find bracketed expressions
    # Pattern: [content] or [content, ...] or [content; ...]
    pattern = r'\[([^\]]*?)\]'

    # Replace bracketed expressions with a placeholder
    result = []

    # Use a stack-based approach to handle nested brackets
    i = 0
    while i < len(content):
        if content[i] == '[':
            # Find matching closing bracket
            depth = 1
            j = i + 1
            while j < len(content) and depth > 0:
                if content[j] == '[':
                    depth += 1
                elif content[j] == ']':
                    depth -= 1
                j += 1

            # Extract content between brackets
            bracket_content = content[i+1:j-1]

            # Parse the bracketed content
            bracketed_value = parse_bracketed(bracket_content)

            result.append(Bracketed(i, bracketed_value))
            i = j
        else:
            result.append(Value(content[i]))
            i += 1

    return Program(result)

def parse_bracketed(content: str) -> BracketedValue:
    """Parse a single bracketed expression."""
    # Split on commas and semicolons
    parts = re.split(r',|;', content)

    # Remove empty strings
    parts = [p.strip() for p in parts if p.strip()]

    # Return a list of values
    return BracketedValue(parts)

def parse_bracketed(content: str) -> BracketedValue:
    """Parse a single bracketed expression."""
    # Split on commas and semicolons
    parts = re.split(r',|;', content)

    # Remove empty strings
    parts = [p.strip() for p in parts if p.strip()]

    # Return a list of values
    return BracketedValue(parts)
