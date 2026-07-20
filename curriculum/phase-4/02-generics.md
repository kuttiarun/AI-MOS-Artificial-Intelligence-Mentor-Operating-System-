# Java Generics — Type-Safe Flexible Code

## Why This Concept Exists
Before generics (Java 1.4), collections stored `Object`. You wrote `List list = new ArrayList()`, inserted a `String`, forgot, inserted an `Integer`, and got a `ClassCastException` at runtime — not compile time. Generics move these errors to compile time.

## Problem Before Generics
```java
// Pre-generics — compiles, crashes at runtime
List items = new ArrayList();
items.add("hello");
items.add(42);
String s = (String) items.get(1); // ClassCastException at RUNTIME
```

## Real-World Analogy
A generics type parameter is like a labeled container at a warehouse. You stamp "Fragile Glass Only" on a box — the label enforcement happens when items go IN, not when they come out.

## Core Syntax
```java
// Generic class
public class Box<T> {
    private T value;
    public void set(T value) { this.value = value; }
    public T get() { return value; }
}

Box<String> strBox = new Box<>();
strBox.set("hello");
String s = strBox.get(); // No cast needed

// Generic method
public static <T extends Comparable<T>> T max(T a, T b) {
    return a.compareTo(b) >= 0 ? a : b;
}
```

## Bounded Wildcards

| Syntax | Meaning | Use Case |
|---|---|---|
| `<T extends Number>` | T must be Number or subtype | Upper bound |
| `<? extends Animal>` | Unknown type that is Animal or subtype | Read-only producer |
| `<? super Dog>` | Unknown type that is Dog or supertype | Write-only consumer |

**PECS Rule: Producer Extends, Consumer Super**
```java
// Read from a list (producer) — use extends
public double sumOfList(List<? extends Number> list) { ... }

// Write to a list (consumer) — use super  
public void addNumbers(List<? super Integer> list) { ... }
```

## Type Erasure
At runtime, generics are erased. `List<String>` becomes `List` at bytecode level.
```java
List<String> strings = new ArrayList<>();
List<Integer> ints = new ArrayList<>();
System.out.println(strings.getClass() == ints.getClass()); // true!
```

## Production Reality
- Spring's `ResponseEntity<T>`, `Optional<T>`, `CompletableFuture<T>` are all generic.
- Hibernate's `TypedQuery<T>` prevents cast errors in database queries.
- Never use raw types in production code — enable compiler warnings.

## Zoho Interview Questions
1. What is type erasure and what limitations does it impose?
2. Explain the PECS principle with an example.
3. Can you create a generic array? Why or why not?
4. What is the difference between `<T extends Comparable<T>>` and `<T extends Comparable>`?
5. How do generic methods differ from generic classes?

## Common Mistakes
- Using raw types (`List` instead of `List<String>`)
- Forgetting type erasure leads to `instanceof` check failures
- Misapplying PECS (using `extends` when you need to write)

## Revision Quiz
1. What compiler error do raw types produce with modern Java settings?
2. When should you use `? super T` versus `? extends T`?
3. What does `<T extends Comparable<T> & Serializable>` mean?
