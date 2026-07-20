# SOLID Principles — The Foundation of Good OOP Design

## What You'll Master
- All 5 SOLID principles with Java code examples
- How violating each principle causes real production problems
- How SOLID connects to Design Patterns and Spring's design

---

## S — Single Responsibility Principle (SRP)

> **One class, one reason to change.**

```java
// BAD — does too many things
class UserService {
    public void createUser(User u) { /* DB logic */ }
    public void sendWelcomeEmail(User u) { /* Email logic */ }
    public String generateReport() { /* Report logic */ }
}

// GOOD — each class has ONE job
class UserRepository { public void save(User u) { /* DB */ } }
class EmailService    { public void sendWelcome(User u) { /* Email */ } }
class UserReportGen   { public String generate() { /* Report */ } }

class UserService {
    private final UserRepository repo;
    private final EmailService   email;
    // Orchestrates — doesn't do the work itself
    public void register(User u) {
        repo.save(u);
        email.sendWelcome(u);
    }
}
```

---

## O — Open/Closed Principle (OCP)

> **Open for extension, closed for modification.**

```java
// BAD — adding new discount type requires modifying this class
class DiscountService {
    public double calculate(String type, double price) {
        if (type.equals("STUDENT"))  return price * 0.8;
        if (type.equals("EMPLOYEE")) return price * 0.7;
        // Adding "SENIOR" means editing this class — risk of breaking existing logic
        return price;
    }
}

// GOOD — extend via interface, don't modify existing code
interface DiscountStrategy {
    double apply(double price);
}

class StudentDiscount  implements DiscountStrategy { public double apply(double p) { return p * 0.8; } }
class EmployeeDiscount implements DiscountStrategy { public double apply(double p) { return p * 0.7; } }
class SeniorDiscount   implements DiscountStrategy { public double apply(double p) { return p * 0.6; } }

class DiscountService {
    public double calculate(DiscountStrategy strategy, double price) {
        return strategy.apply(price); // never needs to change
    }
}
```

---

## L — Liskov Substitution Principle (LSP)

> **A subclass must be usable anywhere its parent is used.**

```java
// BAD violation — Square breaks Rectangle behavior
class Rectangle {
    protected int width, height;
    public void setWidth(int w)  { width = w; }
    public void setHeight(int h) { height = h; }
    public int area() { return width * height; }
}

class Square extends Rectangle {
    @Override public void setWidth(int w)  { width = height = w; } // BREAKS LSP
    @Override public void setHeight(int h) { width = height = h; }
}

// Code that worked for Rectangle breaks with Square:
Rectangle r = new Square();
r.setWidth(5);
r.setHeight(10);
System.out.println(r.area()); // Expected 50, got 100

// FIX: don't force inheritance; use a common interface
interface Shape { int area(); }
class Rectangle implements Shape { /* ... */ }
class Square    implements Shape { /* ... */ }
```

---

## I — Interface Segregation Principle (ISP)

> **Don't force clients to implement methods they don't need.**

```java
// BAD — one fat interface
interface Worker {
    void work();
    void eat();    // robots don't eat
    void sleep();  // robots don't sleep
}

class HumanWorker implements Worker { /* all 3 make sense */ }
class RobotWorker implements Worker {
    public void eat()   { throw new UnsupportedOperationException(); } // WRONG
    public void sleep() { throw new UnsupportedOperationException(); }
}

// GOOD — split into specific interfaces
interface Workable  { void work(); }
interface Eatable   { void eat(); }
interface Sleepable { void sleep(); }

class HumanWorker implements Workable, Eatable, Sleepable { /* all 3 */ }
class RobotWorker implements Workable { /* only what it needs */ }
```

---

## D — Dependency Inversion Principle (DIP)

> **Depend on abstractions, not concretions.**

```java
// BAD — high-level module depends on low-level details
class OrderService {
    private MySQLOrderRepo repo = new MySQLOrderRepo(); // hardcoded!
    // Can't switch to MongoDB without editing OrderService
}

// GOOD — depend on interface (this is why Spring uses @Autowired)
interface OrderRepository {
    void save(Order order);
    Optional<Order> findById(Long id);
}

@Service
class OrderService {
    private final OrderRepository repo; // depends on ABSTRACTION

    public OrderService(OrderRepository repo) { // Spring injects the impl
        this.repo = repo;
    }
}

@Repository
class MySQLOrderRepo implements OrderRepository { /* MySQL impl */ }

@Repository
class MongoOrderRepo implements OrderRepository { /* MongoDB impl — swap anytime */ }
```

---

## SOLID in Spring Boot

| Principle | Spring Example |
|---|---|
| SRP | `@Service`, `@Repository`, `@Controller` separate concerns |
| OCP | `@ConditionalOnProperty` — extend config without changing code |
| LSP | Any `Repository` bean substitutable in `Service` |
| ISP | `CrudRepository`, `JpaRepository` (choose what you need) |
| DIP | `@Autowired` injects interfaces, not concrete classes |

---

## Revision Checkpoint

> Identify which SOLID principle is violated in this code and refactor it:
```java
class ReportExporter {
    public void export(Report r, String format) {
        if (format.equals("PDF"))  { /* PDF logic */ }
        if (format.equals("CSV"))  { /* CSV logic */ }
        if (format.equals("JSON")) { /* JSON logic */ }
    }
}
```
