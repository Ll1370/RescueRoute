# CPSC 323 - Assignment 1: Lexical Analyzer for Rat26F
# Usage: python3 lexer.py <input file>

import sys

KEYWORDS = {"function", "integer", "boolean", "real", "if", "else", "fi",
            "while", "return", "get", "put", "true", "false"}
SEPARATORS = {"(", ")", "{", "}", ",", ";", "@"}
OPERATORS = {"==", "!=", "<=", ">=", "+", "-", "*", "/", "=", "<", ">"}

# DFSM for identifiers L(L|D|_)*, integers D+ and reals D*.D+
# Columns: letter, digit, "_", ".", other.  State 5 is the dead state.
TABLE = [
    [1, 2, 5, 3, 5],   # 0 start
    [1, 1, 1, 5, 5],   # 1 identifier (accepting)
    [5, 2, 5, 3, 5],   # 2 integer    (accepting)
    [5, 4, 5, 5, 5],   # 3 saw ".", needs a digit
    [5, 4, 5, 5, 5],   # 4 real       (accepting)
]
ACCEPTING = {1: "identifier", 2: "integer", 4: "real"}


def column(ch):
    """Return the DFSM table column for a character."""
    if ch.isascii() and ch.isalpha():
        return 0
    if ch.isascii() and ch.isdigit():
        return 1
    return {"_": 2, ".": 3}.get(ch, 4)


def lexer(src, pos):
    """Return the next (token, lexeme, new position); token is None at end of file."""
    # Skip whitespace and ! comments ! ("!=" is an operator, not a comment).
    while pos < len(src):
        if src[pos].isspace():
            pos += 1
        elif src[pos] == "!" and src[pos:pos + 2] != "!=":
            end = src.find("!", pos + 1)
            pos = len(src) if end == -1 else end + 1
        else:
            break
    if pos >= len(src):
        return None, None, pos

    # Run the DFSM, remembering the last accepting state (longest match).
    state, token, end, i = 0, None, pos, pos
    while i < len(src):
        state = TABLE[state][column(src[i])]
        if state == 5:
            break
        i += 1
        if state in ACCEPTING:
            token, end = ACCEPTING[state], i
    if token:
        lexeme = src[pos:end]
        if token == "identifier" and lexeme.lower() in KEYWORDS:
            token = "keyword"
        return token, lexeme, end

    # Operators (two-character ones first), then separators.
    if src[pos:pos + 2] in OPERATORS:
        return "operator", src[pos:pos + 2], pos + 2
    if src[pos] in OPERATORS:
        return "operator", src[pos], pos + 1
    if src[pos] in SEPARATORS:
        return "separator", src[pos], pos + 1
    return "unknown", src[pos], pos + 1


def main():
    """Print every token and lexeme in the given source file."""
    with open(sys.argv[1]) as f:
        src = f.read()
    print(f"{'token':<15}lexeme")
    print("-" * 30)
    pos = 0
    while True:
        token, lexeme, pos = lexer(src, pos)
        if token is None:
            break
        print(f"{token:<15}{lexeme}")


if __name__ == "__main__":
    main()
