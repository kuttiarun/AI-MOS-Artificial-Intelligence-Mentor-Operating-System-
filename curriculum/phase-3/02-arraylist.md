# ArrayList: Dynamic Array Internals

## Why Does This Lesson Exist?

`ArrayList` is the most commonly used collection in Java. It's also one of the most misunderstood. Interviewers at companies like Zoho regularly ask: "How does ArrayList grow? What is the amortized complexity of add()? Why is remove(0) expensive?"

This lesson gives you the internal implementation knowledge to answer these questions from first principles.

---

## The Core Analogy: A Hotel Expansion Strategy

Imagine a hotel that starts with 10 rooms. When guests fill all rooms:
1. They don't add rooms one at a time — that's expensive (construction overhead each time)
2. Instead, they build a **new wing** that's **1.5× the original size** (15 rooms)
3. Guests move to the new wing, old wing is demolished

This is **exactly** how `ArrayList` handles capacity growth.

---

## ArrayList Internal Structure

`ArrayList` wraps a plain Java array internally:

```java
// Simplified ArrayList internals (OpenJDK source):
public class ArrayList<E> {
    private Object[] elementData;   // The backing array
    private int size;               // Current number of elements (not array length!)
    
    private static final int DEFAULT_CAPACITY = 10;
    private static final float GROWTH_FACTOR = 1.5f;  // Approx
}
```

Key distinction:
- **`size`**: Number of actual elements stored (what you see with `.size()`)
- **`elementData.length`** (capacity): Physical size of the backing array

```text
size = 4, capacity = 10:
┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│ A │ B │ C │ D │   │   │   │   │   │   │
└───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
  0   1   2   3   (empty slots — reserved)
```

---

## The Add Operation: O(1) Amortized

**Case 1: Space is available (most common)**
```java
list.add("X");
// → elementData[size] = "X"
// → size++
// O(1) — single array write
```

**Case 2: Array is full (occasional)**
```java
// ArrayList detects: size == elementData.length
// 1. Creates new array of size: (oldCapacity * 3) / 2 + 1
// 2. System.arraycopy(old → new) — O(n) copy
// 3. elementData = newArray
// 4. Add the element — O(1)
```

**Why amortized O(1)?**

If you add n elements starting from an empty list:
- Copies triggered at sizes: 10, 15, 22, 33, 49...
- Total copies ≈ 10 + 15 + 22 + ... ≈ 3n
- Per-element average = 3n / n = **O(1) amortized**

The occasional O(n) resize is "paid for" by the O(1) operations that preceded it.

---

## Access and Search

```text
get(index):   O(1)  — direct array access: elementData[index]
set(index):   O(1)  — direct array write: elementData[index] = value
contains(x):  O(n)  — must iterate to find x
indexOf(x):   O(n)  — must iterate
```

---

## Insert and Remove

**Insert at end**: `add(element)` — O(1) amortized (see above)

**Insert at index**: `add(index, element)` — O(n)
```text
Before: [A][B][C][D][_]
Insert X at index 1:
        [A][B][C][D][_]
              ←shift→
        [A][_][B][C][D]
        [A][X][B][C][D]
```
Must shift all elements from `index` to `size` one position to the right.

**Remove at end**: `remove(size-1)` — O(1) — just decrement size

**Remove at index**: `remove(index)` — O(n)
```text
Remove index 1:
[A][B][C][D]
   ←shift←
[A][C][D][_]
```
Must shift all elements from `index+1` to `size` one position to the left.

---

## ArrayList vs. Array Comparison

| Operation | Array | ArrayList |
|---|---|---|
| Access by index | O(1) | O(1) |
| Append | ❌ Fixed size | O(1) amortized |
| Insert middle | O(n) | O(n) |
| Remove middle | O(n) | O(n) |
| Dynamic growth | ❌ | ✅ |
| Primitives | ✅ `int[]` | ❌ Must box (`Integer`) |

---

## Pre-sizing an ArrayList

If you know the approximate number of elements, initialize with capacity to avoid resizes:

```java
// Avoids multiple array allocations for large datasets
ArrayList<String> list = new ArrayList<>(1000);
```

This is a common performance optimization in Zoho's backend code.

---

## Key Concepts to Remember

| Concept | Key Insight |
|---|---|
| **Backing Array** | ArrayList wraps `Object[] elementData` internally |
| **size vs capacity** | size = elements stored; capacity = physical array length |
| **Growth Factor** | ~1.5× on resize — balances memory waste vs. resize frequency |
| **O(1) amortized** | Most adds are O(1); rare O(n) resize costs spread over many ops |
| **O(n) insert/remove** | Middle insertions require shifting all subsequent elements |

---

## Verification Checkpoint Gate

> **Your task:** Explain why `ArrayList.add()` is described as O(1) amortized rather than simply O(1). Walk through what happens when the backing array runs out of space. Why does ArrayList grow by 1.5× instead of by 1 element at a time or by 10× at once?
