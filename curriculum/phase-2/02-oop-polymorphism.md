# OOP: Polymorphism and Dynamic Method Dispatch

## 1. Core Why
In large-scale systems, software requirements change constantly. If your code relies on concrete types, every time you add a new entity, you must modify existing code. Polymorphism decoupling allows client code to interact with abstract contracts, meaning you can introduce new subclasses without modifying or recompiling the existing business logic.

---

## 2. The Problem
Imagine writing a billing system for an e-commerce platform. Initially, you only accept credit cards:
```java
public class BillingSystem {
    public void processPayment(CreditCardPayment payment) {
        payment.authorize();
    }
}
```
What happens when you add PayPal? You have to write an overloaded method:
```java
public void processPayment(PayPalPayment payment) {
    payment.authorize();
}
```
As you add Apple Pay, Google Pay, and Bitcoin, your `BillingSystem` class swells with duplicate boilerplate and breaks the Open-Closed Principle (OCP).

---

## 3. The Analogy
Think of a **universal wall outlet** (socket). The outlet defines a standard interface/contract for electricity delivery. It does not care what type of appliance you plug into it—a vacuum cleaner, a smartphone charger, or a microwave. All it requires is that the plug fits the socket standard. 

The socket is polymorphic: it behaves differently depending on the concrete device plugged into it, yet the room's wiring system remains completely unchanged.

---

## 4. The Theory
Polymorphism in Java is achieved via **dynamic method dispatch** (runtime polymorphism). 

When you call an overridden method through a superclass reference, Java determines which version of the method to execute at runtime, not compile time. This is managed under the hood using **virtual method tables (vtables)**. Every class containing virtual methods has a vtable mapping method signatures to their actual memory locations.

---

## 5. The Syntax
Here is how we define the contract and its implementations in Java:

```java
// The abstract contract
public interface PaymentMethod {
    void authorize();
}

// Concrete implementation 1
public class CreditCardPayment implements PaymentMethod {
    @Override
    public void authorize() {
        System.out.println("Validating card limits with Bank API...");
    }
}

// Concrete implementation 2
public class PayPalPayment implements PaymentMethod {
    @Override
    public void authorize() {
        System.out.println("Redirecting user to PayPal secure gateway login...");
    }
}
```

Now, the `BillingSystem` code remains clean, stable, and open to extension:
```java
public class BillingSystem {
    // Client code interacts only with the abstract contract
    public void processPayment(PaymentMethod payment) {
        payment.authorize(); // Dynamic dispatch resolves this at runtime!
    }
}
```
