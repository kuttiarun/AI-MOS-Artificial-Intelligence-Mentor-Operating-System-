# Interfaces: Contracts and Polymorphism

## 1. Core Why
Large-scale software requires teams to work on separate components in parallel. If components are tightly coupled, one developer's modifications can break another's code. Interfaces solve this by establishing strict, language-enforced contracts. They define what operations a class must expose, allowing different components to interact seamlessly while their concrete implementations remain entirely decoupled.

---

## 2. The Problem
Suppose you are building a document exporter. Initially, you write a concrete PDF writer class. If other modules import this concrete class directly:
```java
public class Editor {
    private PDFWriter writer = new PDFWriter(); // Tight coupling!
    
    public void save() {
        writer.writePDF();
    }
}
```
If you need to support Word Document exporting (`DocxWriter`), you must completely rewrite the `Editor` class, causing compilation failures across all dependent modules.

---

## 3. The Analogy
Think of a **USB standard port**. The USB foundation defines a standard hardware contract (pins, voltage levels, size). Laptop manufacturers build USB ports, and peripheral developers build USB mice, flash drives, and keyboards. 
The mouse developer does not need to know the motherboard layout of the laptop, nor does the laptop manufacturer need to know how optical sensors track motion. As long as both adhere to the USB contract, they interface perfectly.

---

## 4. The Theory
Interfaces define abstract contracts. Before Java 8, interfaces could only contain abstract methods (no bodies) and public static final constants.

### Java 8 default and static methods
To support backward compatibility without breaking existing implementer classes (such as adding stream support to the Collections interface), Java 8 introduced **default methods**:
- **Default Methods**: Use the `default` keyword. They have a concrete body and are inherited by all implementation classes. Implementer classes can optionally override them.
- **Static Methods**: Interfaces can also declare static helper methods that belong strictly to the interface type, not the instance.

---

## 5. The Syntax
Here is how interfaces and default methods are implemented:

```java
// Abstract Interface Contract
public interface DocumentExporter {
    // 1. Abstract method contract
    void export(String content);

    // 2. Java 8 Default method (inherited by default)
    default void logExport(String content) {
        System.out.println("LOG: Initiating export process of " + content.length() + " chars.");
    }

    // 3. Static helper method
    static boolean isValidExporter(String format) {
        return format.equalsIgnoreCase("pdf") || format.equalsIgnoreCase("docx");
    }
}
```

Implementations declare adherence using the `implements` keyword:
```java
public class PdfExporter implements DocumentExporter {
    @Override
    public void export(String content) {
        logExport(content); // Calling the inherited default method
        System.out.println("Converting text into PDF byte structures...");
    }
}
```
Now, dependent client systems operate on the abstract type:
```java
public class DocumentManager {
    private final DocumentExporter exporter;

    // Injected dependency decouples document logic from exporting mechanics
    public DocumentManager(DocumentExporter exporter) {
        this.exporter = exporter;
    }

    public void process(String text) {
        exporter.export(text); // resolved dynamically at runtime!
    }
}
```
