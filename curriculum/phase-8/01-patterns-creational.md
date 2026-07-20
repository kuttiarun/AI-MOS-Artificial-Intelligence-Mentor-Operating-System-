# Creational Design Patterns — Singleton, Factory, Builder & Prototype

## What You'll Master
- The 4 most important creational patterns — used daily in Java
- Real Spring Boot examples for each pattern
- When to use each and common interview traps

---

## 1. Singleton — One Instance, Global Access

```java
// Thread-safe Singleton using enum (Joshua Bloch's recommendation)
public enum AppConfig {
    INSTANCE;
    private final String dbUrl = System.getenv("DB_URL");
    public String getDbUrl() { return dbUrl; }
}
AppConfig.INSTANCE.getDbUrl();

// Thread-safe Singleton using double-checked locking
public class ConnectionPool {
    private static volatile ConnectionPool instance; // volatile is CRITICAL

    private ConnectionPool() { /* initialize pool */ }

    public static ConnectionPool getInstance() {
        if (instance == null) {                    // first check (no lock)
            synchronized (ConnectionPool.class) {
                if (instance == null) {            // second check (with lock)
                    instance = new ConnectionPool();
                }
            }
        }
        return instance;
    }
}

// In Spring: @Bean is singleton by default — Spring manages it
@Configuration
class AppConfig {
    @Bean
    public ConnectionPool connectionPool() { return new ConnectionPool(); }
}
```

**Why enum Singleton?** — It's serialization-safe, reflection-safe, and thread-safe with zero boilerplate.

---

## 2. Factory Method — Delegate Object Creation

```java
// Create objects without specifying their exact class
interface Notification {
    void send(String message);
}

class EmailNotification  implements Notification { public void send(String m) { /* email */ } }
class SMSNotification    implements Notification { public void send(String m) { /* sms */ } }
class PushNotification   implements Notification { public void send(String m) { /* push */ } }

// Factory — centralizes creation logic
class NotificationFactory {
    public static Notification create(String type) {
        return switch (type.toUpperCase()) {
            case "EMAIL" -> new EmailNotification();
            case "SMS"   -> new SMSNotification();
            case "PUSH"  -> new PushNotification();
            default -> throw new IllegalArgumentException("Unknown type: " + type);
        };
    }
}

// Client doesn't know about concrete classes
Notification n = NotificationFactory.create("EMAIL");
n.send("Your order is shipped!");
```

**Spring example**: `BeanFactory`, `ApplicationContext` — Spring IS a factory.

---

## 3. Builder — Construct Complex Objects Step by Step

```java
// BAD — telescoping constructor (hard to read, error-prone)
new Pizza("large", "thin", true, false, true, "cheese", "pepperoni");

// GOOD — Builder pattern
public class Pizza {
    private final String size;    // required
    private final String crust;   // required
    private final boolean cheese;
    private final boolean pepperoni;
    private final boolean mushrooms;

    private Pizza(Builder b) {
        this.size = b.size; this.crust = b.crust;
        this.cheese = b.cheese; this.pepperoni = b.pepperoni;
        this.mushrooms = b.mushrooms;
    }

    public static class Builder {
        private final String size;   // required
        private final String crust;  // required
        private boolean cheese;
        private boolean pepperoni;
        private boolean mushrooms;

        public Builder(String size, String crust) {
            this.size = size; this.crust = crust;
        }
        public Builder cheese()     { cheese = true;     return this; }
        public Builder pepperoni()  { pepperoni = true;  return this; }
        public Builder mushrooms()  { mushrooms = true;  return this; }
        public Pizza build()        { return new Pizza(this); }
    }
}

// Clear, readable, and safe
Pizza pizza = new Pizza.Builder("large", "thin")
    .cheese()
    .pepperoni()
    .build();

// Lombok @Builder generates this for you:
@Builder
public class User { String name; int age; String email; }
User u = User.builder().name("Arun").age(22).email("a@b.com").build();
```

---

## 4. Prototype — Clone Existing Objects

```java
// When creating objects is expensive — clone instead
public class DatabaseQueryTemplate implements Cloneable {
    private String baseQuery;
    private Map<String, Object> params; // complex, expensive to init

    @Override
    public DatabaseQueryTemplate clone() {
        try {
            DatabaseQueryTemplate copy = (DatabaseQueryTemplate) super.clone();
            copy.params = new HashMap<>(this.params); // deep copy map
            return copy;
        } catch (CloneNotSupportedException e) {
            throw new AssertionError();
        }
    }
}

// Clone instead of re-initializing
DatabaseQueryTemplate template = registry.get("user-search");
DatabaseQueryTemplate query = template.clone();  // fast
query.addParam("name", "Arun");
```

---

## Pattern Decision Guide

| Situation | Pattern |
|---|---|
| Only ONE instance should exist (config, pool) | Singleton |
| Object creation logic is complex / needs centralization | Factory Method |
| Object has many optional fields, avoid telescoping constructor | Builder |
| Creating objects is expensive, need cheap copies | Prototype |

---

## Revision Checkpoint

> When would you choose `Factory Method` over `Builder`? Give a real-world example from a Java application where you'd use each.
