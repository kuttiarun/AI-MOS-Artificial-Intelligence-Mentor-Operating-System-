# HashMap: Hashing, Buckets, and Collision Resolution

## 1. Core Why
When dealing with large volumes of data, searching sequentially through lists or arrays scales poorly—**O(N)** time complexity. HashMaps solve this by offering near-instantaneous **O(1)** search, insert, and delete operations, regardless of data size, by turning keys directly into array index coordinates.

---

## 2. The Problem
If you store key-value pairs in a standard list, finding a value by its key requires scanning elements one by one. If you have 1 million elements, you might make 1 million comparisons. Even with sorted arrays and binary search, it requires **O(log N)** comparisons. We need a way to look up a record in a single step.

---

## 3. The Analogy
Imagine a massive library sorting books. If books were cataloged sequentially, the librarian would have to look through every single shelf to find "Moby Dick". 

Instead, the library uses a **hash function**: it takes the book's title, extracts the first letter, and assigns it to a bucket matching that letter (e.g., "M" books go strictly to shelf 13). When you request "Moby Dick", the librarian does not search shelves A-L; they go directly to shelf 13.

---

## 4. The Theory
A HashMap is backed by an array of buckets (`Node<K,V>[] table`). When you execute `map.put(key, value)`:
1. `hashCode()` is invoked on the key to produce an integer.
2. The hash is mixed to distribute bits: `hash = h ^ (h >>> 16)`.
3. The hash is compressed to fit the array's capacity: `index = hash & (capacity - 1)`.

### Collision Resolution: Chaining vs Treeification
If two different keys map to the same index (e.g., `key1.hashCode() != key2.hashCode()`, but `index1 == index2`), a **collision** occurs. 

Java resolves collisions using **Chaining**:
- **Linked List**: By default, colliding entries are appended as nodes in a linked list at that index bucket.
- **Treeification**: If the chain length at a single bucket exceeds a threshold of **8** (`TREEIFY_THRESHOLD`) and the total map capacity is at least **64**, Java converts the linked list into a balanced **Red-Black Tree** to improve search performance from **O(N)** to **O(log N)**.

### Load Factor and Dynamic Resizing (`resize()`)
To prevent buckets from filling up and degrading lookup performance, the HashMap must expand dynamically:
- **Load Factor**: The ratio of elements to total bucket capacity. The default is **0.75**.
- **Threshold**: The limit at which resizing is triggered (`capacity * load_factor`). For a map with 16 buckets, the threshold is **12**.
- **Resizing**: Once the element count exceeds the threshold, the `resize()` method is triggered:
  1. The array capacity is **doubled** (e.g. from 16 to 32).
  2. All existing entries are rehashed and redistributed across the new array buckets in **O(N)** time.

---

## 5. The Syntax
Here is how the bucket structure is declared and utilized:

```java
import java.util.HashMap;

public class MapDemo {
    public static void main(String[] args) {
        // 1. Instantiate the map (initial capacity = 16, load factor = 0.75)
        HashMap<String, Integer> studentGrades = new HashMap<>();

        // 2. Put keys into the map (calculates hash, compresses index, writes to bucket)
        studentGrades.put("Alice", 95);
        studentGrades.put("Bob", 88);

        // 3. Fetch value by key in O(1) time
        int grade = studentGrades.get("Alice");
        System.out.println("Alice's Grade: " + grade);
    }
}
```
