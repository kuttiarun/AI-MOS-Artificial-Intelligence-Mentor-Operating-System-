# Arrays: Fixed-Size Contiguous Memory

## Why Does This Lesson Exist?

Arrays are the foundational data structure. Every other Java collection (`ArrayList`, `LinkedList`, `HashMap`) is built upon arrays at some level. Understanding arrays at the memory level is essential for understanding why other collections behave the way they do.

This is also a prime Zoho interview topic: "Why is ArrayList get(index) O(1)?" — because it's backed by an array.

---

## The Core Analogy: A Row of Numbered Parking Spaces

Imagine a parking lot with 10 **numbered** spaces in a **straight line**:

```text
Space:  [ 0 ] [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ] [ 8 ] [ 9 ]
Car:    [ A ] [ B ] [   ] [ D ] [   ] [ F ] [   ] [   ] [   ] [   ]
```

Properties of this parking lot:
1. **Fixed size**: You declared 10 spaces when you built the lot — you can't add an 11th without building a new lot
2. **Contiguous**: All spaces are side by side — no gaps between space 3 and space 4
3. **Indexed**: Finding space 7 is instant — you don't search from space 0

**This is exactly how an array works in memory.**

---

## Arrays in Memory: Contiguous Allocation

When you declare `int[] arr = new int[5]`, the JVM:
1. Allocates **5 × 4 = 20 bytes** of contiguous RAM
2. Returns the **base address** (memory address of the first element)

```text
Base Address: 0x1000

[0x1000] [0x1004] [0x1008] [0x100C] [0x1010]
   arr[0]   arr[1]   arr[2]   arr[3]   arr[4]
   
Each int = 4 bytes, addresses are sequential
```

**Accessing `arr[i]` is constant time O(1) because:**
```text
Address of arr[i] = Base Address + (i × element_size)
Address of arr[3] = 0x1000 + (3 × 4) = 0x100C
```

The CPU computes this address directly — no searching required.

---

## Array Characteristics

| Property | Value | Why |
|---|---|---|
| **Access by index** | O(1) | Direct address calculation |
| **Search (unsorted)** | O(n) | Must check each element |
| **Insert at end** | O(1) (if space) | Write to next index |
| **Insert at middle** | O(n) | Must shift elements right |
| **Delete at middle** | O(n) | Must shift elements left |
| **Fixed size** | ✅ | Allocated at creation, cannot grow |

---

## Why Arrays Cannot Grow

Once the JVM allocates `new int[5]`, those 20 bytes are reserved. If the next program data starts at address `0x1014`, there's no guarantee the 6th element can be placed at `0x1014` — another object might already be there.

To "grow" an array, you must:
1. Allocate a new, larger array
2. Copy all elements from the old array to the new one
3. Update references to point to the new array

**This is exactly what `ArrayList` does internally when it runs out of capacity** — this is why ArrayList.add() is O(1) amortized, but occasionally triggers an O(n) resize.

---

## Java Array Syntax

```java
// Declaration and allocation
int[] numbers = new int[5];        // 5 elements, all initialized to 0
String[] names = new String[3];    // 3 elements, all null

// Initialization with values
int[] primes = {2, 3, 5, 7, 11};  // Length determined automatically

// Access
int first = primes[0];             // O(1)
primes[2] = 99;                    // O(1) write

// Iteration
for (int i = 0; i < primes.length; i++) {
    System.out.println(primes[i]);
}

// Enhanced for loop (for-each)
for (int prime : primes) {
    System.out.println(prime);
}
```

---

## Multi-Dimensional Arrays

Java arrays can be arrays of arrays (not true 2D matrices):

```java
int[][] matrix = new int[3][4];  // 3 rows, 4 columns
matrix[1][2] = 42;               // Row 1, Column 2
```

Each row is a separate array object — rows don't need to be the same length (jagged arrays are allowed).

---

## Key Concepts to Remember

| Concept | Key Insight |
|---|---|
| **Contiguous Memory** | Elements stored in adjacent bytes — enables O(1) index access |
| **O(1) Access** | CPU computes address = base + (index × element_size) |
| **Fixed Size** | Cannot grow/shrink — must copy to a new array |
| **O(n) Insert/Delete** | Must shift elements to maintain contiguity |
| **Cache Friendly** | Contiguous layout means excellent CPU cache performance |

---

## Verification Checkpoint Gate

> **Your task:** Explain why accessing any element in an array is O(1) time. Use the memory address calculation formula and contrast it with why searching for a value (not by index) is O(n). Explain what "contiguous memory" means and why it matters for performance.
