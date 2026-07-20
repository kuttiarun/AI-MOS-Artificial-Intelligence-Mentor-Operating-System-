# Java Streams API — Declarative Data Pipelines

## Why This Concept Exists
Before Streams (Java 8), processing collections required verbose for-loops, temporary variables, and nested conditionals. The Streams API brings functional pipeline thinking to Java — filter, transform, collect in one expressive chain.

## Problem Before Streams
```java
// Pre-Java 8 — find all senior engineers, get their names sorted
List<String> result = new ArrayList<>();
for (Employee e : employees) {
    if (e.getYearsExperience() > 5) {
        result.add(e.getName());
    }
}
Collections.sort(result);
```

## Real-World Analogy
A Stream is like an assembly line. Raw materials (source) go in, each station applies an operation (intermediate), and the finished product (terminal) comes out. No station stores the whole batch — items flow one at a time.

## Stream Pipeline Anatomy
```
Source → Intermediate Operations → Terminal Operation
```

```java
List<String> names = employees.stream()        // Source
    .filter(e -> e.getYearsExperience() > 5)   // Intermediate — lazy
    .map(Employee::getName)                     // Intermediate — lazy
    .sorted()                                  // Intermediate — lazy
    .collect(Collectors.toList());             // Terminal — triggers execution
```

## Intermediate vs Terminal Operations
| Type | Examples | Lazy? |
|---|---|---|
| Intermediate | `filter`, `map`, `flatMap`, `distinct`, `sorted`, `limit` | Yes |
| Terminal | `collect`, `forEach`, `reduce`, `count`, `findFirst`, `anyMatch` | No — triggers pipeline |

## Common Collectors
```java
// Group employees by department
Map<String, List<Employee>> byDept = employees.stream()
    .collect(Collectors.groupingBy(Employee::getDepartment));

// Average salary
OptionalDouble avgSalary = employees.stream()
    .mapToDouble(Employee::getSalary)
    .average();

// Join names with comma
String names = employees.stream()
    .map(Employee::getName)
    .collect(Collectors.joining(", "));
```

## Parallel Streams
```java
// Use parallel when: large dataset, CPU-bound, order doesn't matter
long count = employees.parallelStream()
    .filter(e -> e.getSalary() > 100_000)
    .count();
```

## Production Reality
- At Zoho scale, Streams replace most for-loop data transformations.
- Never mutate external state inside a stream (it breaks parallelism).
- Avoid infinitely-generating streams without `limit()`.
- `Optional` is the Stream-friendly null alternative.

## Zoho Interview Questions
1. What is the difference between `map()` and `flatMap()`?
2. Can you reuse a Stream? Why or why not?
3. When does the pipeline actually execute in a Stream?
4. What is the danger of using parallel streams with shared mutable state?
5. How do you convert a `Stream<String>` to a `Map<String, Integer>`?

## Common Mistakes
- Calling a terminal operation and then trying to reuse the stream
- Using parallel streams for I/O-bound tasks (worse than sequential)
- Forgetting that `sorted()` consumes all elements before passing downstream

## Revision Quiz
1. Name three terminal operations.
2. What is the difference between `reduce()` and `collect()`?
3. Write a stream that filters a list of integers, keeps only even numbers, squares them, and returns a sorted list.
