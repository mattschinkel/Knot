# Golem

> **Don't generate code. Generate computation.**

**Golem is an AI-native programming language designed for LLMs to generate, edit, verify, and reason about programs — not for humans as the primary authors.** Source files use the `.gol` extension; site/package brand is **golemlang**.

Golem does not treat source code as a pile of text that an AI must repeatedly rewrite.

**The program is a semantic graph.  
Text is only a representation of that graph.**

That distinction is the foundation of Golem.

---

## Why Golem Exists

Traditional programming languages were designed around humans typing and editing text.

LLMs have different strengths.

An LLM is exceptionally good at:

- generating structured representations
- identifying relationships between concepts
- transforming existing structures
- reasoning about types and dependencies
- working incrementally
- operating from explicit constraints
- repairing a known-invalid structure
- producing highly regular patterns

It is less reliable when forced to repeatedly regenerate large amounts of fragile text while preserving every unrelated character.

Golem is designed around the first set of strengths.

> **Golem is not a language that makes an LLM imitate a human programmer.**
>
> **It is a programming representation designed around what an intelligent system is good at.**

---

# The Core Idea

In Golem, the canonical program is a **typed semantic graph with stable node IDs**.

Text is a serialization.

This means the compiler does not fundamentally think:

```text
"Here is a file containing characters."
```

It thinks:

```text
Program
 ├── node
 │    ├── type
 │    ├── inputs
 │    ├── outputs
 │    └── relationships
 ├── node
 └── node
```

Multiple representations can therefore describe the same underlying program.

```text
              ┌──────────────┐
              │ Semantic     │
              │ Graph        │
              │ SOURCE TRUTH │
              └──────┬───────┘
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
      Canonical   Pretty      Binary
        AIR        Text        Form
```

The graph is the program.

The text is merely how humans and machines choose to view it.

---

# Designed for LLMs

Golem treats the LLM as a computational participant rather than simply a code generator.

The design asks:

> **What would a programming language look like if the primary author were an intelligent system instead of a human typing characters?**

That leads to a different set of priorities.

### Semantic density

Every token should contribute meaningful information.

### Deterministic structure

The same program should have a predictable representation.

### Minimal ambiguity

The grammar should leave as little room as possible for multiple interpretations.

### Surgical modification

Changing one thing should not require regenerating everything around it.

### Machine-readable feedback

Compiler errors should be structured information, not prose that an LLM has to parse with regex.

### Explicit uncertainty

An incomplete thought should be representable without pretending it is complete.

### Constrained generation

When possible, invalid output should be impossible to generate rather than merely detected afterward.

---

# Stop Rewriting Files

Traditional AI coding often looks like this:

```text
LLM
 ↓
generate source text
 ↓
compiler
 ↓
error
 ↓
LLM
 ↓
rewrite source text
 ↓
compiler
 ↓
...
```

A tiny change can cause an LLM to regenerate hundreds of lines.

Golem instead provides **graph operations**.

```text
MODIFY
REPLACE
INSERT
DELETE
```

An LLM can target a specific node instead of rewriting an entire file.

Conceptually:

```text
REPLACE node=0xA71F
WITH ...
```

This makes program modification a structural operation.

> **Don't regenerate the program. Modify the program.**

Golem can also report the **blast radius** of an edit so an agent can understand what its change affects before committing to it.

---

# Stable Node IDs

Every meaningful node can have a stable identity.

That gives an AI something extremely valuable:

**a persistent handle to a piece of computation.**

Instead of saying:

> "Change the third `if` inside the function near line 147."

An agent can say:

```text
MODIFY node=0xA71F
```

The physical location of the text does not have to be the identity of the program element.

This makes long-lived AI interaction with code substantially more natural.

---

# Incomplete Reasoning Is Allowed

LLMs frequently know that something is missing.

Traditional programming languages generally force the programmer to provide a value immediately.

Golem makes uncertainty explicit.

```text
?
```

or:

```text
?:T
```

can represent a **hole**.

A hole is not simply a syntax error.

It is a first-class statement:

> **The structure is known, but this part has not been resolved yet.**

This allows Golem to distinguish:

```text
VALID
PARTIAL
INVALID
```

A partially constructed program can still be analyzed and type-checked.

This enables iterative reasoning instead of forcing an agent to invent an answer merely to make the program parse.

> **You don't have to pretend you know the answer.**

---

# Errors That an AI Can Actually Use

Human-oriented compiler errors often look like:

```text
error: mismatched types
```

That is useful to a human.

For an AI, Golem aims for structured diagnostics such as:

```text
ERROR
type: TYPE_MISMATCH
node: 0xA71F
expected: List[I32]
received: List[String]

repairs:
  - CONVERT_ELEMENTS[String -> I32]
  - REPLACE_EXPRESSION
  - CHANGE_EXPECTED_TYPE
```

The goal is simple:

> **Don't merely tell the AI that it is wrong. Give it structured information with which it can become correct.**

Repair candidates can become part of the machine-to-machine interface between the compiler and the reasoning system.

---

# Prevent Invalid Generation

Golem is designed to work with constrained decoding.

With a grammar such as GBNF, an LLM can be restricted to producing syntactically valid Golem representations.

Instead of:

```text
generate → parse → reject → repair
```

the system can move toward:

```text
generate only valid structures
```

This is particularly useful with local and hosted inference systems that support grammar-constrained generation.

> **Don't detect syntax errors after generation. Prevent them during generation.**

---

# Deterministic by Design

Golem separates intelligence from certainty.

The deterministic kernel handles things that should never depend on an LLM's opinion.

For example:

```text
ADD[2, 3]
```

must always produce:

```text
5
```

The kernel does not ask an LLM what `2 + 3` means.

Likewise, types, effects, capabilities, contracts, lowering, and other deterministic properties belong on the deterministic side of the system.

This creates a fundamental boundary:

> **The AI may propose. The kernel decides.**

---

# LLMs Are Optional

Golem does **not** require an LLM to execute a program.

A pure Golem program can compile and run without an LLM.

LLMs can participate where intelligence is useful:

- program synthesis
- repair
- code generation
- graph transformation
- documentation queries
- optional AI effects
- higher-level reasoning

The deterministic kernel remains deterministic.

This means Golem does not turn every program into an AI program.

Instead:

> **AI is a capability of the language, not a dependency of the language.**

---

# Capabilities Are the Security Boundary

AI-powered programs introduce an important question:

> What is the AI actually allowed to do?

Golem treats capabilities as explicit boundaries.

An agent can **request** a capability.

It cannot simply acquire one because it decided to use it.

This makes effects explicit and gives the surrounding system a place to enforce policy.

Conceptually:

```text
AI
 │
 │ request
 ▼
CAPABILITY
 │
 ├── allowed → execute
 │
 └── denied  → reject
```

The goal is to make authority explicit rather than implicit.

---

# Types, Effects, and Contracts

Golem moves important correctness information into the program representation itself.

The system is designed to reason about:

- types
- effects
- capabilities
- contracts
- dependencies
- units and dimensions

For example, dimensional information can become part of the type system:

```text
f64@meters
```

and operations can preserve dimensional correctness:

```text
meters * meters = meters²
```

This allows correctness properties to be represented structurally instead of relying entirely on runtime behavior.

---

# Two Halves of the Compiler

Golem intentionally separates two different jobs.

## The AI Front-End

The AI side handles things that require judgment:

- synthesis
- repair
- interpretation
- transformation
- resolving holes
- proposing changes

## The Deterministic Back-End

The deterministic side handles things that require certainty:

- validation
- lowering
- type enforcement
- effect enforcement
- capability enforcement
- execution

The core invariant is:

> **If the deterministic back-end ever needs to guess, the AI front-end has failed to provide enough information.**

The back-end should never invent intent.

---

# Compiler as an AI Interface

Golem is designed to expose the compiler as a machine-oriented interface.

An agent should be able to ask the compiler to:

```text
eval
typecheck
run
constrain
doc_query
query
```

This makes the compiler something an agent can interact with directly rather than merely something that gets invoked after a file is generated.

Golem's compiler can therefore become a **computational tool for an AI agent**.

---

# A Different Programming Workflow

Traditional:

```text
Human
  ↓
write text
  ↓
compiler
  ↓
binary
```

AI-assisted:

```text
Human
  ↓
LLM
  ↓
generate text
  ↓
compiler
  ↓
errors
  ↓
LLM
  ↓
rewrite text
```

Golem:

```text
Human / Agent
       ↓
   semantic intent
       ↓
   Golem graph
       ↓
 ┌─────┴─────┐
 │           │
AI          Kernel
reasoning   verification
 │           │
 └─────┬─────┘
       ↓
    execution
```

The goal is to make the programming environment itself a better interface for machine reasoning.

---

# Why Not Just Use Python, Rust, C++, or JavaScript?

Because those languages were not designed around this problem.

They optimize for various combinations of:

- human readability
- human typing
- human maintenance
- conventional tooling
- historical compatibility
- ecosystem compatibility

Golem starts from a different optimization target:

> **LLM generation, reasoning, modification, verification, and execution.**

Golem does not need to win by being a better Python.

It needs to win by being a better **AI programming interface**.

---

# The Design Principle

Every feature in Golem should answer one question:

> **Does this make an intelligent system better at generating, understanding, modifying, verifying, or executing computation?**

If the answer is no, the feature deserves scrutiny.

Human convenience is valuable.

But it is not the primary optimization target.

---

# What Golem Is Trying to Become

Golem is ultimately aiming toward a programming environment where an AI can:

1. Understand an existing program as a semantic structure.
2. Query that structure.
3. Identify the exact computation it wants to change.
4. Make a surgical graph modification.
5. Leave unresolved portions as typed holes when necessary.
6. Ask the compiler for structured diagnostics.
7. Apply machine-readable repairs.
8. Generate only valid syntax through constrained decoding.
9. Prove or verify deterministic properties through the kernel.
10. Execute the resulting program without requiring an LLM.

And eventually:

> **Golem's compiler will be written in Golem itself.**

The deterministic core should bootstrap independently, with AI-assisted capabilities layered on afterward.

---

# Current Status

**Design / v0.1**

Golem is currently in the language-design and implementation-planning stage.

The repository contains the language design, compiler architecture, agent-building workflow, progress tracking, and supporting documentation.

The project is intentionally being designed before the full compiler is implemented.

---

# Repository

```text
ai_docs/
  golem_design.md     # Core language and compiler design
  golem_agents.md       # LLM agent crew
  ai.txt               # Project working rules

grammar/               # Grammar and constrained-generation work
src/golem/              # Compiler implementation
cli/                   # Command-line interface
fmt/                   # Formatter
lsp/                   # Language server
vm/                    # Runtime / VM
tests/                 # Tests
tools/                 # Development tools
web/                   # Build / progress dashboard

progress.md            # Development progress
instructions.txt       # Project instructions
name_changes.md        # Naming history
```

---

# The Philosophy in One Sentence

> **Golem is a programming language where the computer program is a semantic structure first and text second, designed around the strengths of intelligent systems rather than the habits of human typists.**

Or, even shorter:

# **Don't generate code. Generate computation.**

---

## Author

**Matthew Schinkel**

## License

To be decided.
