# What is Programming? Variables, Types & Logic

## Why Does This Lesson Exist?

Before you learn Java's syntax, you need to understand what a program **actually is** at a fundamental level. Too many beginners treat programming as a collection of memorized syntax rules — they type code without understanding why it's structured that way.

This lesson gives you the foundational mental model: programs are precise instructions for transforming data.

---

## The Core Analogy: A Recipe

A computer program is like a **cooking recipe**:

- **Ingredients** = Input data (user name, a number, a list of items)
- **Recipe steps** = Instructions the program executes
- **The dish** = Output (a result, a report, a web page)

The key difference: a recipe can be interpreted loosely by a human chef. A computer program must be **absolutely precise**. The CPU follows your instructions *exactly as written*, no guessing, no common sense.

**This is why debugging is hard**: when a program misbehaves, the CPU did exactly what you told it to — you just told it the wrong thing.

---

## What is a Variable?

A **variable** is a named container for a value stored in RAM.

```text
Think of RAM as a giant row of labeled boxes:
┌─────────┬─────────┬─────────┬─────────┐
│  name   │   age   │ salary  │ isAdmin │
│ "Aruna" │   24    │  45000  │  false  │
└─────────┴─────────┴─────────┴─────────┘
```

Each box:
1. Has a **name** (the variable name) — how you refer to it in code
2. Holds a **value** — the data stored in that memory location
3. Has a **type** — what kind of data it can hold

In Java:
```java
String name = "Aruna";
int age = 24;
double salary = 45000.50;
boolean isAdmin = false;
```

---

## Data Types: The Blueprint for Memory

A **data type** tells the CPU:
1. **How many bytes of RAM** to allocate for this variable
2. **How to interpret those bytes** (number? text? true/false?)

### Primitive Types in Java

| Type | Size | Range / Purpose |
|---|---|---|
| `byte` | 1 byte | -128 to 127 |
| `short` | 2 bytes | -32,768 to 32,767 |
| `int` | 4 bytes | ~±2.1 billion (most common integer) |
| `long` | 8 bytes | ~±9.2 quintillion |
| `float` | 4 bytes | Decimal numbers (less precise) |
| `double` | 8 bytes | Decimal numbers (most common) |
| `char` | 2 bytes | Single character |
| `boolean` | 1 bit | `true` or `false` |

**Why do types matter?** Because the same 4 bytes of RAM can mean a completely different number depending on how you interpret them. The type is the contract that says "interpret these bytes as an `int`."

---

## Logic: The Three Control Structures

Every program ever written uses exactly three types of logic:

### 1. Sequence
Execute instructions one after another:
```text
Step 1 → Step 2 → Step 3 → Done
```

### 2. Selection (If / Else)
Make a decision based on a condition:
```text
if (age >= 18) {
    "You can vote"
} else {
    "Too young to vote"
}
```

### 3. Iteration (Loops)
Repeat instructions multiple times:
```text
for each student in class:
    calculate grade
    add to report
```

**All programs — from a simple calculator to a cloud database — are built from these three structures combined in different ways.**

---

## How a Program Runs: Compilation vs. Interpretation

Before a CPU can execute your Java code, it must be translated into machine language (binary instructions the CPU understands).

**Java uses a two-step process:**

```text
Your Java Code (.java)
        ↓  [Compiler: javac]
  Bytecode (.class)
        ↓  [JVM: java]
  Machine Instructions (CPU executes)
```

1. **Compile time**: `javac` translates your `.java` file into `.class` bytecode
2. **Runtime**: The JVM (Java Virtual Machine) interprets or JIT-compiles that bytecode into CPU instructions

This "write once, run anywhere" design is why Java bytecode can run on Windows, Linux, and macOS without recompiling.

---

## Key Concepts to Remember

| Concept | Key Insight |
|---|---|
| **Variable** | Named container for a value in RAM |
| **Data Type** | Defines size and interpretation of memory bytes |
| **Sequence** | Instructions execute top to bottom |
| **Selection** | Programs can make decisions with `if/else` |
| **Iteration** | Programs can repeat actions with loops |
| **Compilation** | Source code must be translated before the CPU can run it |

---

## Verification Checkpoint Gate

> **Your task:** Explain the purpose of data types in programming. Why can't we just store all values as plain numbers without specifying a type? Use the "labeled boxes in RAM" analogy or your own analogy to explain what a variable actually is at the memory level.
