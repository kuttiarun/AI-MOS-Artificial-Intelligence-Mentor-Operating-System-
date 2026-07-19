# Abstract Classes: Partial Abstraction Patterns

## 1. Core Why
Sometimes, multiple subclasses share the same state and default behavior, but differ in key steps. If we use interfaces, we are forced to duplicate common state definitions and method implementations across every subclass. Abstract classes solve this by allowing you to define a **common base class** that implements shared properties and default operations, while leaving specific variation points abstract for subclasses to implement.

---

## 2. The Problem
Imagine implementing database connect modules for MySQL and Oracle:
```java
public interface Database {
    void connect();
    void executeQuery(String sql);
}
```
Both databases require identical logging handlers, query caching systems, and session counters. If you implement this interface, you will copy-paste the exact same logging and session handling code across `MySqlDatabase` and `OracleDatabase` classes, causing massive code duplication.

---

## 3. The Analogy
Think of a **home construction template**. The template provides a pre-built foundation, basic framing, and standard plumbing structures. However, it does not specify the paint color, flooring material, or interior trim. 

The building firm provides the abstract foundation (common to all houses in the neighborhood), while you (the subclass) customize the remaining abstract parameters to create your specific home.

---

## 4. The Theory
Abstract classes occupy a middle ground between concrete classes and interfaces:
- **Partial Abstraction**: They can declare instance fields (state), constructors, concrete methods, and abstract methods.
- **Constructor Inheritance Chain**: Abstract classes *cannot* be instantiated directly using `new`. However, they *must* have constructors. When you instantiate a subclass, the subclass constructor invokes the parent constructor via `super()` to initialize the abstract parent's fields in memory.

### Interface vs Abstract Class (Zoho Expectations)
Zoho interviewers frequently test this distinction. Remember these three parameters:
1. **Multiple Inheritance**: A class can implement multiple interfaces, but can extend only one abstract class.
2. **State Management**: Abstract classes can have instance variables (private, protected, package-private fields). Interface fields are strictly public static final constants.
3. **Design Intent**: Use interfaces to define a role or contract (what a class can do). Use abstract classes to define identity and structure (what a class is).

---

## 5. The Syntax
Here is how abstract classes are defined and extended:

```java
// Partial Abstraction Base Class
public abstract class DatabaseConnection {
    // 1. Shared state fields (impossible in interfaces)
    protected String connectionString;
    private int timeout;

    // 2. Base Constructor (called via super())
    protected DatabaseConnection(String connectionString, int timeout) {
        this.connectionString = connectionString;
        this.timeout = timeout;
    }

    // 3. Shared concrete behavior
    public void logConnection() {
        System.out.println("LOG: Connecting to " + connectionString + " (timeout=" + timeout + "s)");
    }

    // 4. Abstract variation points
    public abstract void authenticate();
}
```

Concrete subclasses inherit the structure and initialize it:
```java
public class MySqlDatabase extends DatabaseConnection {
    private String databaseName;

    public MySqlDatabase(String conn, int timeout, String dbName) {
        // Constructor chaining: invokes parent initialization first!
        super(conn, timeout);
        this.databaseName = dbName;
    }

    @Override
    public void authenticate() {
        logConnection(); // Calling inherited method
        System.out.println("Authenticating MySQL user access for " + databaseName);
    }
}
```
