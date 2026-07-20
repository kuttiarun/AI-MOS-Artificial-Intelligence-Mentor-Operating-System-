# JVM Memory Model — Stack, Heap, and Garbage Collection

## Why This Concept Exists
Understanding JVM memory is the difference between writing code that works and code that scales. Memory leaks, `OutOfMemoryError`, GC pauses, and `StackOverflowError` are production incidents that trace directly to misunderstanding how the JVM manages memory.

## JVM Memory Layout
```
┌──────────────────────────────────────────────────────┐
│                     JVM Process                      │
│  ┌─────────────────┐   ┌────────────────────────┐   │
│  │   Thread Stack   │   │          Heap          │   │
│  │ ┌─────────────┐ │   │  ┌──────┐  ┌────────┐  │   │
│  │ │ Stack Frame │ │   │  │Young │  │  Old   │  │   │
│  │ │ local vars  │ │   │  │ Gen  │  │  Gen   │  │   │
│  │ │ return addr │ │   │  └──────┘  └────────┘  │   │
│  │ └─────────────┘ │   └────────────────────────┘   │
│  └─────────────────┘                                 │
│  ┌─────────────────────────────────────────────────┐ │
│  │               Metaspace (class metadata)         │ │
│  └─────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

## Stack vs Heap
| Property | Stack | Heap |
|---|---|---|
| Stores | Primitives, references, frames | Objects, arrays |
| Scope | Per thread | Shared across threads |
| Size | Small (default 512KB-1MB) | Large (configurable GBs) |
| Speed | Fast (LIFO pointer) | Slower (GC managed) |
| Error | `StackOverflowError` | `OutOfMemoryError` |

## Object Lifecycle
```
1. new Object() → allocated in Eden (Young Gen)
2. Survives minor GC → moves to Survivor space
3. Survives several GCs → promoted to Old Gen (Tenured)
4. No more references → eligible for GC
5. GC runs → memory reclaimed
```

## Garbage Collection Algorithms
| GC | Description | When to Use |
|---|---|---|
| Serial GC | Single thread, stop-the-world | Small apps |
| Parallel GC | Multiple threads, stop-the-world | Throughput-sensitive |
| G1 GC (default Java 9+) | Region-based, low pause time | Most production apps |
| ZGC / Shenandoah | Ultra-low latency (<1ms pauses) | Low-latency services |

## Common Memory Leaks
```java
// 1. Static collections holding references
static Map<String, Object> cache = new HashMap<>(); // never cleared!

// 2. Unclosed streams / connections
BufferedReader reader = new BufferedReader(...); // not in try-with-resources

// 3. Listeners not deregistered
eventBus.register(this); // forgot to deregister on component destroy
```

## JVM Flags for Production Tuning
```bash
-Xms512m -Xmx2g          # heap min/max
-XX:+UseG1GC              # use G1 garbage collector
-XX:+PrintGCDetails       # log GC events
-Xss1m                    # thread stack size
```

## Production Reality
At Zoho, G1GC is the default. Memory leaks are caught with heap dump analysis tools (`jmap`, VisualVM, Eclipse MAT). Always enable `-XX:+HeapDumpOnOutOfMemoryError` in production.

## Zoho Interview Questions
1. What is the difference between the stack and the heap?
2. Explain the Young Generation and why it exists.
3. What is a memory leak in Java? How do you detect one?
4. How does G1GC differ from CMS garbage collector?
5. What causes `StackOverflowError` versus `OutOfMemoryError`?

## Revision Quiz
1. Where are local variables stored — stack or heap?
2. What happens to an object when its last reference goes out of scope?
3. What JVM flag increases the maximum heap size?
