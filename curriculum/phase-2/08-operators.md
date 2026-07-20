# Operators, Expressions & Type Casting in Java

## What You'll Master
- All Java operator categories with precedence rules
- Integer vs floating point arithmetic pitfalls
- Bitwise and shift operators (critical for interviews)
- Widening vs narrowing type casting and when each applies

---

## Operator Categories & Precedence

| Priority | Operators | Example |
|---|---|---|
| 1 (highest) | `()`, `[]`, `.` | method calls, array access |
| 2 | `++`, `--`, `!`, `~`, `+`, `-` (unary) | `!flag`, `-x` |
| 3 | `*`, `/`, `%` | multiplication, division, modulo |
| 4 | `+`, `-` | addition, subtraction |
| 5 | `<<`, `>>`, `>>>` | bit shifts |
| 6 | `<`, `>`, `<=`, `>=`, `instanceof` | comparisons |
| 7 | `==`, `!=` | equality |
| 8 | `&` | bitwise AND |
| 9 | `^` | bitwise XOR |
| 10 | `\|` | bitwise OR |
| 11 | `&&` | logical AND (short-circuit) |
| 12 | `\|\|` | logical OR (short-circuit) |
| 13 | `? :` | ternary |
| 14 (lowest) | `=`, `+=`, `-=`, etc. | assignment |

---

## Arithmetic Pitfalls

```java
// Integer division truncates
int result = 7 / 2;     // 3, NOT 3.5
double d   = 7 / 2;     // 3.0 (int division THEN widened)
double d2  = 7.0 / 2;   // 3.5 (floating point division)
double d3  = (double) 7 / 2; // 3.5 (explicit cast first)

// Integer overflow — wraps silently
int max = Integer.MAX_VALUE; // 2147483647
System.out.println(max + 1); // -2147483648 (overflow!)
// Fix: use long
long safe = (long) max + 1;  // 2147483648

// % with negatives
System.out.println(-7 % 3);  // -1 (sign follows dividend in Java)
System.out.println(7 % -3);  // 1

// Float precision
System.out.println(0.1 + 0.2); // 0.30000000000000004
// Fix: use BigDecimal
new BigDecimal("0.1").add(new BigDecimal("0.2")); // 0.3
```

---

## Bitwise Operators — Interview Goldmine

```java
// & (AND)  |  | (OR)  |  ^ (XOR)  |  ~ (NOT)
int a = 0b1010; // 10
int b = 0b1100; // 12

a & b  // 0b1000 = 8  (both bits must be 1)
a | b  // 0b1110 = 14 (at least one bit is 1)
a ^ b  // 0b0110 = 6  (bits differ)
~a     // 0b...10101 = -11 (flip all bits)

// Shift operators
int x = 8;  // 0b1000
x << 1      // 16  (multiply by 2)
x >> 1      // 4   (divide by 2, preserves sign)
x >>> 1     // 4   (unsigned right shift, fills with 0)

int neg = -8;
neg >> 1    // -4  (sign bit preserved)
neg >>> 1   // 2147483644 (fills with 0 — treats as unsigned)
```

**Practical uses:**
```java
// Check if number is even: (n & 1) == 0
// Check if number is power of 2: (n & (n-1)) == 0
// Swap without temp: a ^= b; b ^= a; a ^= b;
// Set bit k: n | (1 << k)
// Clear bit k: n & ~(1 << k)
// Toggle bit k: n ^ (1 << k)
```

---

## Type Casting

```java
// Widening (implicit — safe, no data loss)
int i = 42;
long l = i;      // auto-widened
double d = i;    // auto-widened

// Narrowing (explicit — possible data loss)
double pi = 3.14159;
int truncated = (int) pi;  // 3 — decimal part lost
byte b = (byte) 200;       // -56 — overflow wraps around

// Common gotcha
char c = 'A';
int ascii = c;    // 65 (widening — char to int)
char back = (char) 65; // 'A'

// instanceof before cast
Object obj = "Hello";
if (obj instanceof String s) { // Java 16+ pattern matching
    System.out.println(s.length()); // no explicit cast needed
}
```

---

## Short-Circuit Evaluation

```java
int count = 0;
boolean result = (count != 0) && (10 / count > 1); // safe — && short-circuits
// Without short-circuit: 10 / 0 would throw ArithmeticException

// || short-circuits too
String s = null;
boolean ok = (s != null) || s.isEmpty(); // safe — || stops after true
```

---

## Zoho Interview Question

**Q**: What is the output?
```java
int x = 5;
int y = x++ + ++x;
System.out.println(y);
System.out.println(x);
```
**Answer**: `y = 5 + 7 = 12`, `x = 7`  
- `x++` → uses 5, then x becomes 6  
- `++x` → x becomes 7, uses 7

---

## Revision Checkpoint

> Write a method that checks if a given integer is a power of 2 using only bitwise operators — no loops or division allowed.
