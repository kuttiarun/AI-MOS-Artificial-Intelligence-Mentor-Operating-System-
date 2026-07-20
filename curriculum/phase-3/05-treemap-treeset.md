# TreeMap & TreeSet — Sorted Collections & Red-Black Trees

## What You'll Master
- How `TreeMap` and `TreeSet` maintain **sorted order** automatically
- The **Red-Black Tree** data structure behind them
- `NavigableMap` and `NavigableSet` APIs for range queries
- When to choose TreeMap vs HashMap

---

## TreeMap — Sorted Key-Value Map

```java
TreeMap<String, Integer> scores = new TreeMap<>();
scores.put("Arun",  85);
scores.put("Priya", 92);
scores.put("Ram",   78);
scores.put("Divya", 95);

// Keys always in natural sorted order
System.out.println(scores); // {Arun=85, Divya=95, Priya=92, Ram=78}

// Navigation methods
scores.firstKey()                   // "Arun"
scores.lastKey()                    // "Ram"
scores.headMap("Priya")             // {Arun=85, Divya=95}  (exclusive)
scores.tailMap("Priya")             // {Priya=92, Ram=78}   (inclusive)
scores.subMap("Divya", "Ram")       // {Divya=95, Priya=92}
scores.floorKey("Krishna")          // "Divya" (greatest key ≤ "Krishna")
scores.ceilingKey("Krishna")        // "Priya" (smallest key ≥ "Krishna")
scores.higherKey("Priya")           // "Ram"
scores.lowerKey("Priya")            // "Divya"
scores.pollFirstEntry()             // removes and returns {Arun=85}
scores.descendingMap()              // reversed view
```

---

## Red-Black Tree — Why O(log n) Is Guaranteed

A Red-Black Tree is a **self-balancing BST** with 5 rules:
1. Every node is either **Red** or **Black**
2. The root is **Black**
3. No two adjacent Red nodes (Red parent → Red child)
4. All paths from any node to its null leaves have the **same number of Black nodes**
5. Null leaves are considered Black

These rules guarantee the tree height ≤ 2·log₂(n+1), giving **O(log n)** for all operations.

```
HashMap  → O(1) average, but O(n) worst (hash collision)
TreeMap  → O(log n) guaranteed, always sorted
```

---

## Custom Sort Order with Comparator

```java
// Reverse order
TreeMap<String, Integer> reversed = new TreeMap<>(Comparator.reverseOrder());

// Sort by string length, then alphabetically
TreeMap<String, Integer> byLength = new TreeMap<>(
    Comparator.comparingInt(String::length).thenComparing(Comparator.naturalOrder())
);
byLength.put("Arun", 1);
byLength.put("Ram", 2);
byLength.put("Priya", 3);
// {Ram=2, Arun=1, Priya=3}
```

---

## TreeSet — Sorted Unique Elements

```java
TreeSet<Integer> set = new TreeSet<>(List.of(5, 3, 8, 1, 3, 9));
System.out.println(set); // [1, 3, 5, 8, 9] — sorted, no duplicates

set.first()           // 1
set.last()            // 9
set.floor(6)          // 5 (greatest element ≤ 6)
set.ceiling(6)        // 8 (smallest element ≥ 6)
set.headSet(5)        // [1, 3] (exclusive)
set.tailSet(5)        // [5, 8, 9] (inclusive)
set.subSet(3, 9)      // [3, 5, 8] (from inclusive, to exclusive)
set.pollFirst()       // removes and returns 1
set.descendingSet()   // [9, 8, 5, 3]
```

---

## LinkedHashMap — Insertion-Order Map

```java
// Maintains insertion order (unlike HashMap) but O(1) access (unlike TreeMap)
Map<String, Integer> cache = new LinkedHashMap<>();
cache.put("first", 1);
cache.put("second", 2);
cache.put("third", 3);
System.out.println(cache); // {first=1, second=2, third=3}

// LRU Cache pattern using LinkedHashMap
int capacity = 3;
Map<Integer, Integer> lru = new LinkedHashMap<>(capacity, 0.75f, true) {
    protected boolean removeEldestEntry(Map.Entry<Integer, Integer> eldest) {
        return size() > capacity; // remove oldest when full
    }
};
```

---

## Comparison Table

| Feature | HashMap | LinkedHashMap | TreeMap |
|---|---|---|---|
| Order | None | Insertion | Sorted |
| Time (get/put) | O(1) avg | O(1) avg | O(log n) |
| Null key | ✅ (1) | ✅ (1) | ❌ |
| Thread-safe | ❌ | ❌ | ❌ |
| Use case | General | LRU cache | Range queries |

---

## Zoho Interview Questions

**Q1**: When would you choose TreeMap over HashMap?
> When you need **sorted iteration** or **range queries** (floor/ceiling/subMap). TreeMap's O(log n) cost is worth it for these operations. If you only need key-value lookup with no ordering, HashMap is faster.

**Q2**: Implement an LRU cache in Java.
> Use `LinkedHashMap` with `accessOrder=true` and override `removeEldestEntry()` — exactly as shown above.

---

## Revision Checkpoint

> Given a list of words, find the word with the highest frequency using a `TreeMap`. If there are ties, return the lexicographically smallest word.
