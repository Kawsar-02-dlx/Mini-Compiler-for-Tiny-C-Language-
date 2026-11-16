# ?? Mini Compiler for Tiny C Language

A lightweight compiler/interpreter implementation in Python designed for the **Tiny C** language. This project demonstrates foundational concepts of compiler design and programming language theory, including lexical analysis, recursive descent parsing, symbol table tracking, semantic checks, and interactive statement execution.

---

## ?? Project Overview

- **Author**: Kawsar Hamid
- **Institution**: Brainware University
- **Repository**: [Mini-Compiler-for-Tiny-C-Language-](https://github.com/Kawsar-02-dlx/Mini-Compiler-for-Tiny-C-Language-)

Tiny C is an educational, streamlined subset of the C programming language. This project provides an end-to-end execution pipeline from raw C-like source code to runtime evaluation.

---

## ? Features

- **Lexical Analysis & Parsing**: Tokenizes identifiers, keywords, numbers, operators, and delimiters.
- **Arithmetic Expression Evaluation**: Respects standard operator precedence (*, / over +, -) and unary operations (+, -).
- **Relational Conditions**: Supports ==, !=, <, >, <=, and >=.
- **Variable Management & Symbol Table**:
  - Declaration with or without initial value (int a = 10;, int b;)
  - Fast identifier lookups and updates
  - Detection of undefined variables or table overflow
- **Control Flow Statements**:
  - if (...) { ... } else { ... } branching
  - while (...) { ... } looping
- **I/O Capabilities**: Built-in print statement (e.g., print x;, print(x + 5);).
- **Robust Error Handling**:
  - **Syntax Errors**: Unmatched braces, malformed expressions, missing semicolons.
  - **Semantic Errors**: Undeclared identifiers, duplicate declarations.
  - **Runtime Errors**: Division by zero, 32-bit signed integer overflow, and infinite loop safeguards.
- **Interactive REPL**: Interactive command-line environment with automatic multi-line block collection for braced statements.

---

## ??? Architecture & Workflow

`	ext
  +-------------------------+
  ¦  Source Code (Tiny C)   ¦
  +-------------------------+
               ?
  +-------------------------+
  ¦ Token / Lexical Analysis ¦
  +-------------------------+
               ?
  +-------------------------+
  ¦ Syntax & Logic Parsing  ¦ <---> +--------------------------+
  +-------------------------+       ¦       Symbol Table       ¦
               ?                    ¦ (Tracks Variables/Memory)¦
  +-------------------------+       +--------------------------+
  ¦ Execution & Evaluation  ¦
  +-------------------------+
               ?
  +-------------------------+
  ¦  Output / Diagnostics   ¦
  +-------------------------+
`

---

## ?? Getting Started

### Prerequisites
- Python 3.8+ (No external third-party dependencies required; uses standard libraries)

### Running the Interpreter

`ash
python compiler.py
`

You will see the welcome shell:
`	ext
================================================
       MINI C INTERPRETER - TINY C LANGUAGE
================================================
Supported statements:
  int x = 10;
  int y;
  x = x + 1;
  print x;
  print(x + 1);
  if (x > 5) { ... } else { ... }
  while (x > 0) { ... }
Type 'exit' to quit.
------------------------------------------------
mini-c> 
`

---

## ?? Example Usage

### 1. Variables and Arithmetic
`c
int a = 15;
int b = 4;
int c = (a * 2) + (b - 1);
print c;
`

### 2. If-Else Condition
`c
int score = 75;
if (score >= 50) {
    print 1;
} else {
    print 0;
}
`

### 3. While Loop
`c
int count = 5;
while (count > 0) {
    print count;
    count = count - 1;
}
`

---

## ?? Repository Structure

`	ext
+-- compiler.py           # Main Tiny C compiler and REPL implementation
+-- TinyCcompiler.pptx    # Project presentation slides & architecture explanation
+-- .gitignore            # Git ignore configuration
+-- README.md             # Project documentation
`

---

## ?? License
This project is open-source and intended for academic and educational purposes.
