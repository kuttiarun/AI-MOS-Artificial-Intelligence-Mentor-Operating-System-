# Java Environment Setup: JDK, JVM & JRE

## Why Does This Lesson Exist?

Java developers often struggle with cryptic errors like `JAVA_HOME is not set`, `cannot find symbol`, or `unsupported class file major version`. These errors are not bugs in your code — they're symptoms of not understanding how Java's execution environment actually works.

This lesson explains the three-layer Java execution stack: JDK, JRE, and JVM. Understanding this prevents environment-related frustration and is a common Zoho interview topic.

---

## The Core Analogy: A Factory Production Line

Think of writing and running a Java program like a manufacturing process:

| Java Component | Factory Equivalent |
|---|---|
| **JDK** (Java Development Kit) | The full factory — includes all machines AND tools to design products |
| **JRE** (Java Runtime Environment) | The assembly floor — only what's needed to run already-built products |
| **JVM** (Java Virtual Machine) | The master machine that runs all other machines — interprets the product blueprint |

- A **developer** needs the full **JDK** to write and compile Java code
- An **end user** only needs the **JRE** to run a Java application
- The **JVM** is always present inside both — it's what actually runs bytecode

---

## The Three-Layer Stack

```text
┌─────────────────────────────────────────┐
│               JDK                       │
│  ┌───────────────────────────────────┐  │
│  │             JRE                   │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │          JVM                │  │  │
│  │  │  (Bytecode Execution Engine)│  │  │
│  │  └─────────────────────────────┘  │  │
│  │  + Java Standard Libraries        │  │
│  └───────────────────────────────────┘  │
│  + javac compiler + javadoc + jdb + ... │
└─────────────────────────────────────────┘
```

### JVM: Java Virtual Machine
- The core engine that **executes bytecode**
- Creates an abstraction layer over the OS — bytecode is OS-agnostic
- Manages **memory** (heap, stack, GC), **threads**, and **security**
- Different implementations exist: HotSpot (Oracle), OpenJ9 (IBM), GraalVM

### JRE: Java Runtime Environment
- = JVM + Java Standard Library (java.lang, java.util, java.io, etc.)
- What end users install to run Java applications
- Does **not** include the compiler (`javac`)

### JDK: Java Development Kit
- = JRE + Developer Tools
- **Developer tools**: `javac` (compiler), `javadoc` (documentation generator), `jdb` (debugger), `jar` (archiver), `jps`, `jstack`, `jmap` (profiling tools)
- Developers install this on their machines

---

## The Java Compilation & Execution Pipeline

```text
YourCode.java
      │
      │  javac (compiler)
      ▼
YourCode.class (bytecode)
      │
      │  java (JVM launcher)
      ▼
JVM loads .class into RAM
      │
      │  JIT Compiler (Just-In-Time)
      ▼
Native Machine Code (CPU executes)
```

**Key insight**: Java is both **compiled** and **interpreted**:
1. `javac` compiles `.java` → `.class` (bytecode) at **compile time**
2. The JVM interprets bytecode at **runtime**, but frequently executed "hot" code paths are **JIT-compiled** to native machine code for speed

---

## JAVA_HOME and the PATH

When you install the JDK, two environment variables must be configured:

- **`JAVA_HOME`**: Points to the root JDK directory
  ```text
  JAVA_HOME = C:\Program Files\Java\jdk-17
  ```
- **`PATH`**: Includes `%JAVA_HOME%\bin` so your terminal can find `java`, `javac`, etc.

**Common error symptoms:**
| Error | Cause |
|---|---|
| `'java' is not recognized as an internal command` | JDK `bin` not in PATH |
| `JAVA_HOME is not defined correctly` | JAVA_HOME points to wrong directory |
| `Unsupported class file major version 65` | Code compiled with JDK 21, running on JDK 11 |

---

## Java Versions: LTS vs. Non-LTS

Java releases follow a 6-month cycle. Long-Term Support (LTS) versions receive security updates for years:

| Version | LTS? | Key Features |
|---|---|---|
| Java 8 | ✅ | Lambdas, Stream API (widely deployed legacy) |
| Java 11 | ✅ | HTTP Client, var keyword |
| Java 17 | ✅ | Sealed classes, pattern matching |
| Java 21 | ✅ | Virtual threads (Project Loom) |

**Zoho standard**: Most internal Java systems target Java 11 or Java 17 LTS.

---

## Key Concepts to Remember

| Concept | Key Insight |
|---|---|
| **JVM** | Executes bytecode, manages memory, platform-agnostic |
| **JRE** | JVM + standard libraries — for running Java apps |
| **JDK** | JRE + compiler + dev tools — for developing Java |
| **Bytecode** | Platform-neutral intermediate representation |
| **JIT Compilation** | Hot code paths compiled to native code at runtime |
| **JAVA_HOME** | Environment variable pointing to JDK root |

---

## Verification Checkpoint Gate

> **Your task:** Explain the difference between the JDK, JRE, and JVM. Why does Java need both a compiler (`javac`) and a virtual machine (`java`)? Use the factory analogy or your own analogy to describe why bytecode allows "write once, run anywhere."
