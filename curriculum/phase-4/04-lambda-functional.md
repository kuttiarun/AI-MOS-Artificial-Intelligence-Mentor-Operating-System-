# Lambda Expressions & Functional Interfaces — Java 8 Functional Programming

## Why This Concept Exists
Lambda expressions allow you to treat behavior as data. Before Java 8, passing behavior required anonymous inner classes — 5 lines of boilerplate for a single comparison. Lambdas collapse this into one expressive line.

## Problem Before Lambdas
```java
// Anonymous class — verbose
Collections.sort(names, new Comparator<String>() {
    @Override
    public int compare(String a, String b) {
        return a.compareTo(b);
    }
});

// Lambda — clean
Collections.sort(names, (a, b) -> a.compareTo(b));

// Even cleaner — method reference
Collections.sort(names, String::compareTo);
```

## Lambda Syntax
```
(parameters) -> expression
(parameters) -> { statements; }
```

```java
Runnable r = () -> System.out.println("Hello");
Comparator<Integer> c = (a, b) -> a - b;
Function<String, Integer> len = s -> s.length();
```

## Functional Interfaces (java.util.function)
| Interface | Method | Usage |
|---|---|---|
| `Supplier<T>` | `T get()` | Produces a value |
| `Consumer<T>` | `void accept(T)` | Consumes a value |
| `Function<T,R>` | `R apply(T)` | Maps T → R |
| `Predicate<T>` | `boolean test(T)` | Tests a condition |
| `BiFunction<T,U,R>` | `R apply(T,U)` | Two inputs, one output |
| `UnaryOperator<T>` | `T apply(T)` | Same type in/out |

## Method References
| Type | Syntax | Example |
|---|---|---|
| Static method | `ClassName::method` | `Math::abs` |
| Instance method (unbound) | `ClassName::method` | `String::toLowerCase` |
| Instance method (bound) | `instance::method` | `"hello"::equals` |
| Constructor | `ClassName::new` | `ArrayList::new` |

## Closures and Effectively Final
```java
int threshold = 100; // effectively final
Predicate<Integer> check = n -> n > threshold; // OK
// threshold = 200; // Would break the lambda — compile error
```

## Custom Functional Interfaces
```java
@FunctionalInterface
public interface Validator<T> {
    boolean validate(T value);
    
    // Can have default methods
    default Validator<T> and(Validator<T> other) {
        return value -> this.validate(value) && other.validate(value);
    }
}
```

## Production Reality
At Zoho, lambdas appear everywhere: Spring event listeners, CompletableFuture chains, JPA Specifications. Method references are preferred over lambdas when the mapping is direct to a method.

## Zoho Interview Questions
1. What is a functional interface? Can it have more than one abstract method?
2. What is the difference between `Function<T,R>` and `UnaryOperator<T>`?
3. What does "effectively final" mean in the context of lambda captures?
4. How does a method reference differ from a lambda?
5. What is the `@FunctionalInterface` annotation and is it required?

## Revision Quiz
1. Write a `Predicate<String>` that checks if a string is longer than 5 characters.
2. Convert this to a method reference: `s -> s.toUpperCase()`
3. What happens if you try to modify a captured variable inside a lambda?
