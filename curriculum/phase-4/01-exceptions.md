# Java Exceptions — Understanding Failure Handling

## Why This Concept Exists
Before structured exception handling, programs crashed silently or printed cryptic error codes. Java introduced a formal Exception hierarchy so that errors are first-class objects — catchable, inspectable, and recoverable.

## Problem Before This Was Invented
In C, a function returns -1 to signal an error. But what if -1 is a valid value? Who checks the return? Developers ignored error codes. Programs crashed. Java made errors impossible to silently ignore.

## Real-World Analogy
Think of exceptions like fire alarms. A fire (exception) is detected, the alarm fires (throw), and response teams handle it (catch). If no one handles it, the building evacuates (JVM terminates).

## Exception Hierarchy
```
Throwable
├── Error (JVM-level, do NOT catch)
│   ├── OutOfMemoryError
│   └── StackOverflowError
└── Exception
    ├── RuntimeException (Unchecked — compiler won't force you to catch)
    │   ├── NullPointerException
    │   ├── ArrayIndexOutOfBoundsException
    │   └── IllegalArgumentException
    └── Checked Exceptions (compiler FORCES you to handle)
        ├── IOException
        ├── SQLException
        └── FileNotFoundException
```

## Checked vs Unchecked
| Type | Must Catch/Declare? | Examples |
|---|---|---|
| Checked | Yes | `IOException`, `SQLException` |
| Unchecked | No | `NullPointerException`, `ClassCastException` |
| Error | Never catch | `OutOfMemoryError` |

## Key Syntax
```java
try {
    FileReader f = new FileReader("data.txt"); // throws IOException
} catch (FileNotFoundException e) {
    System.err.println("File missing: " + e.getMessage());
} catch (IOException e) {
    System.err.println("Read error: " + e.getMessage());
} finally {
    // Always runs — close resources here
}
```

## Custom Exceptions
```java
public class InsufficientFundsException extends RuntimeException {
    private final double amount;
    
    public InsufficientFundsException(double amount) {
        super("Insufficient funds: need " + amount + " more");
        this.amount = amount;
    }
    
    public double getAmount() { return amount; }
}
```

## Production Reality
In production Java (Zoho scale), use **try-with-resources** for any AutoCloseable:
```java
try (Connection conn = dataSource.getConnection();
     PreparedStatement ps = conn.prepareStatement(sql)) {
    // resources auto-closed even on exception
}
```

## Zoho Interview Questions
1. What is the difference between `throw` and `throws`?
2. When would you create a custom checked vs unchecked exception?
3. What happens to the `finally` block if `System.exit(0)` is called inside `try`?
4. Explain exception chaining and why it matters for stack traces.
5. What is the problem with catching `Exception` or `Throwable` broadly?

## Common Mistakes
- Swallowing exceptions with empty catch blocks
- Catching `Exception` too broadly and hiding bugs
- Using exceptions for flow control (very slow — exceptions unwind the call stack)
- Not logging the original cause when re-throwing

## Revision Quiz
1. Is `NullPointerException` checked or unchecked?
2. What keyword declares that a method may throw a checked exception?
3. What is try-with-resources and why should you use it?
