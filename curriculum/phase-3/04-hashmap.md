# HashMap: Hashing, Buckets, and Collision Resolution

## 1. Core Why
When dealing with large volumes of data, searching sequentially through lists or arrays scales poorly—$O(N)$ time complexity. HashMaps solve this by offering near-instantaneous $O(1)$ search, insert, and delete operations, regardless of data size, by turning keys directly into array index coordinates.

---

## 2. The Problem
If you store key-value pairs in a standard list, finding a value by its key requires scanning elements one by one. If you have 1 million elements, you might make 1 million comparisons. Even with sorted arrays and binary search, it requires $O(\log N)$ comparisons. We need a way to look up a record in a single step.

---

## 3. The Analogy
Imagine a massive library sorting books. If books were cataloged sequentially, the librarian would have to look through every single shelf to find "Moby Dick". 

Instead, the library uses a **hash function**: it takes the book's title, extracts the first letter, and assigns it to a bucket matching that letter (e.g., "M" books go strictly to shelf 13). When you request "Moby Dick", the librarian does not search shelves A-L; they go directly to shelf 13.

---

## 4. The Theory
A HashMap is backed by an array of buckets. When you execute `map.put(key, value)`:
1. `hashCode()` is invoked on the key to produce an integer.
2. The hash is compressed to fit the array's capacity: `index = hash & (capacity - 1)`.
3. If two different keys map to the same index, a **collision** occurs. 

Java resolves collisions using **Chaining**: each index holds a linked list (or a balanced red-black tree if the chain length exceeds 8) of entries mapping to that bucket.

---

## 5. The Syntax
Here is how the bucket structure is declared and utilized:

```java
import java.util.HashMap;

public class MapDemo {
    public static void main(String[] args) {
        // Instantiate the map
        HashMap<String, Integer> studentGrades = new HashMap<>();

        // 1. Put keys into the map (calculates hash, compresses index, writes to bucket)
        studentGrades.put("Alice", 95);
        studentGrades.put("Bob", 88);

        // 2. Fetch value by key in O(1) time
        int grade = studentGrades.get("Alice");
        System.out.println("Alice's Grade: " + grade);
    }
}
```
