# Object-Oriented Programming: Classes, Objects, and Polymorphism

## 1. Core Why
In procedural programming, data and behavior are separated, leading to large, unmanageable states and code that is prone to regression. OOP solves this by encapsulating data and behavior into cohesive objects. When combined with polymorphism, it allows client code to interact with abstract interfaces, meaning systems can scale by adding new subclasses without modifying existing, tested code.

---

## 2. The Problem
Imagine coding a system to draw multiple shapes (circles, squares, triangles) to a UI canvas. In procedural code, you would write a series of conditional checks:
```java
public void drawShapes(List<Shape> shapes) {
    for (Shape shape : shapes) {
        if (shape.type == Circle) {
            drawCircle(shape);
        } else if (shape.type == Square) {
            drawSquare(shape);
        }
    }
}
```
Every time you add a new shape type, you must open, modify, and retest this function, violating the Open-Closed Principle (OCP).

---

## 3. The Analogy
Think of a **universal wall socket**. The socket represents an abstract type defining a standard contract. The appliances (vacuum, laptop charger, toaster) are concrete classes. 
The room's electrical infrastructure only interacts with the socket standard. It doesn't care what appliance is plugged in, as long as it adheres to the socket's physical contract. The socket behaves differently depending on the appliance attached to it, yet the room's wiring system remains completely unchanged.

---

## 4. The Theory
In the JVM, objects and class templates are handled in different memory spaces:
1. **Stack Memory**: Stores primitive values and references (pointers) to objects. Each method execution gets its own stack frame.
2. **Heap Memory**: Stores the actual objects (instance variables). Object allocation is handled dynamically at runtime.

### Dynamic Method Dispatch (vtables)
When you invoke an overridden method on an object using a superclass reference, the compiler does not decide which method runs. Instead, the JVM resolves this at runtime using the **Virtual Method Table (vtable)**.
- Every class loaded into memory has a vtable mapping method signatures to their actual binary memory locations.
- Invoking `parent.draw()` resolves to a specific subclass offset in the subclass's vtable, bypassing compilation static binding.

---

## 5. The Syntax
Here is how class blueprints and runtime polymorphism are declared in Java:

```java
// Abstract contract
public abstract class Shape {
    public abstract void draw();
}

// Concrete subclass 1
public class Circle extends Shape {
    @Override
    public void draw() {
        System.out.println("Drawing a Circle using radius formulas.");
    }
}

// Concrete subclass 2
public class Square extends Shape {
    @Override
    public void draw() {
        System.out.println("Drawing a Square using height and width vectors.");
    }
}
```

Now, your drawing engine only interacts with the base class contract:
```java
import java.util.List;

public class Canvas {
    // Dynamic Method Dispatch executes the correct subclass draw() at runtime
    public void render(List<Shape> shapes) {
        for (Shape shape : shapes) {
            shape.draw(); // resolved in **O(1)** time using the object's vtable!
        }
    }
}
```
