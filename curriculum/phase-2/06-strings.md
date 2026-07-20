# Java String Class — Immutability, StringBuilder & String Pool

## What You'll Master
- Why `String` is immutable in Java and what that means in memory
- The **String Pool** (interning) and how `==` vs `.equals()` differs
- When to use `String` vs `StringBuilder` vs `StringBuffer`
- Essential String API methods every Java developer must know

---

## The String Pool — How Java Saves Memory

```java
String a = "hello";        // stored in String Pool
String b = "hello";        // reuses same pool object
String c = new String("hello"); // NEW heap object — NOT pooled

System.out.println(a == b);      // true  (same pool reference)
System.out.println(a == c);      // false (different objects)
System.out.println(a.equals(c)); // true  (same value)
```

> **Rule**: Always use `.equals()` for String comparison, NEVER `==`.

---

## Why Strings Are Immutable

```java
String s = "Java";
s.concat(" Developer"); // returns NEW String — s unchanged
System.out.println(s);  // still "Java"

// Correct:
s = s.concat(" Developer");
System.out.println(s);  // "Java Developer"
```

**Immutability benefits:**
- Thread-safe (no synchronization needed)
- Safe as HashMap keys (hashcode never changes)
- Security (passwords, file paths can't be mutated)

---

## StringBuilder — The Mutable Alternative

```java
// BAD — creates N intermediate String objects in loop
String result = "";
for (int i = 0; i < 1000; i++) {
    result += i;  // O(N²) time and memory
}

// GOOD — StringBuilder reuses internal char array
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 1000; i++) {
    sb.append(i);  // O(N) amortized
}
String result = sb.toString();
```

| | String | StringBuilder | StringBuffer |
|---|---|---|---|
| Mutable? | No | Yes | Yes |
| Thread-safe? | Yes (immutable) | No | Yes (synchronized) |
| Performance | Slow in loops | Fast | Slower (lock overhead) |

---

## Must-Know String Methods

```java
String s = "  Hello, Java World!  ";

s.trim()                    // "Hello, Java World!"
s.strip()                   // Java 11+ (handles Unicode whitespace)
s.toLowerCase()             // "  hello, java world!  "
s.toUpperCase()             // "  HELLO, JAVA WORLD!  "
s.substring(8, 12)          // "Java"
s.indexOf("Java")           // 8
s.replace("Java", "Python") // "  Hello, Python World!  "
s.contains("World")         // true
s.startsWith("  Hello")     // true
s.split(", ")               // ["  Hello", "Java World!  "]
s.chars()                   // IntStream of char values (Java 8+)

// String.format / formatted (Java 15+)
String.format("Hello, %s! You are %d years old.", "Arun", 22);
"Hello, %s!".formatted("Arun"); // Java 15+

// joining
String.join(", ", "A", "B", "C"); // "A, B, C"
```

---

## Zoho Interview Questions

**Q1**: What is the output?
```java
String s1 = new String("abc");
String s2 = new String("abc");
System.out.println(s1 == s2);
System.out.println(s1.equals(s2));
```
**Answer**: `false`, `true` — `new String()` always creates a heap object outside the pool.

**Q2**: How would you reverse a String in Java?
```java
// Using StringBuilder
String reversed = new StringBuilder("hello").reverse().toString();

// Manual (O(N))
char[] chars = "hello".toCharArray();
int l = 0, r = chars.length - 1;
while (l < r) {
    char tmp = chars[l]; chars[l] = chars[r]; chars[r] = tmp;
    l++; r--;
}
```

**Q3**: What is `intern()`?
```java
String s = new String("hello").intern(); // forces into String Pool
String t = "hello";
System.out.println(s == t); // true
```

---

## Revision Checkpoint

> Can you explain why `String` is immutable and what advantage that gives when using it as a `HashMap` key?
