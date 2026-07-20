# Java I/O Streams — FileIO, BufferedReader & Serialization

## What You'll Master
- The difference between **byte streams** and **character streams**
- Reading/writing files efficiently with `BufferedReader`/`BufferedWriter`
- **Serialization** — converting objects to bytes and back
- Java NIO (`Files`, `Path`) — the modern approach

---

## Stream Hierarchy

```
InputStream  ──▶  FileInputStream, ByteArrayInputStream
OutputStream ──▶  FileOutputStream, PrintStream

Reader  ──▶  InputStreamReader  ──▶  BufferedReader, FileReader
Writer  ──▶  OutputStreamWriter ──▶  BufferedWriter, FileWriter, PrintWriter
```

**Byte streams** → images, audio, binary files  
**Character streams** → text files (handles encoding automatically)

---

## Reading Files — Three Approaches

### 1. BufferedReader (Classic — most interviews expect this)
```java
try (BufferedReader br = new BufferedReader(new FileReader("data.txt"))) {
    String line;
    while ((line = br.readLine()) != null) {
        System.out.println(line);
    }
} // auto-closed by try-with-resources
```

### 2. Java NIO Files.lines() — Java 8+ (Production preferred)
```java
Path path = Path.of("data.txt");
try (Stream<String> lines = Files.lines(path)) {
    lines.filter(l -> l.contains("Java"))
         .forEach(System.out::println);
}
```

### 3. Files.readAllLines() — small files only
```java
List<String> lines = Files.readAllLines(Path.of("data.txt"));
```

---

## Writing Files

```java
// BufferedWriter
try (BufferedWriter bw = new BufferedWriter(new FileWriter("out.txt"))) {
    bw.write("Line 1");
    bw.newLine();
    bw.write("Line 2");
}

// NIO — one liner
Files.writeString(Path.of("out.txt"), "Hello NIO!", StandardOpenOption.CREATE);

// Append mode
Files.writeString(Path.of("out.txt"), "\nAppended", StandardOpenOption.APPEND);
```

---

## Serialization — Saving Objects to Disk

```java
import java.io.*;

public class Employee implements Serializable {
    private static final long serialVersionUID = 1L; // version control
    private String name;
    private transient String password; // transient = NOT serialized
    private int age;
}

// Serialize (write to file)
try (ObjectOutputStream oos = new ObjectOutputStream(
        new FileOutputStream("emp.ser"))) {
    oos.writeObject(new Employee("Arun", "secret", 22));
}

// Deserialize (read from file)
try (ObjectInputStream ois = new ObjectInputStream(
        new FileInputStream("emp.ser"))) {
    Employee emp = (Employee) ois.readObject();
    System.out.println(emp.getName()); // "Arun"
    System.out.println(emp.getPassword()); // null (was transient)
}
```

**Key rules:**
- Class must implement `Serializable`
- `transient` fields are skipped
- Always define `serialVersionUID` to prevent `InvalidClassException` after code changes

---

## Java NIO Path & Files API

```java
Path p = Path.of("data", "report.txt"); // OS-independent path

Files.exists(p)              // boolean
Files.isReadable(p)          // boolean
Files.createDirectories(p)   // mkdir -p
Files.copy(src, dest, StandardCopyOption.REPLACE_EXISTING)
Files.delete(p)
Files.size(p)                // bytes

// Walk directory tree
Files.walk(Path.of("src"))
     .filter(f -> f.toString().endsWith(".java"))
     .forEach(System.out::println);
```

---

## Zoho Interview Questions

**Q1**: What is the difference between `FileReader` and `BufferedReader`?
> `FileReader` reads one character at a time from disk (expensive syscall per char). `BufferedReader` wraps it and reads a chunk (default 8KB) at once, dramatically reducing I/O syscalls.

**Q2**: What does `transient` do in serialization?
> It tells the JVM to skip that field during serialization. Use it for sensitive data (passwords), computed fields, or non-serializable objects.

**Q3**: What happens if `serialVersionUID` doesn't match during deserialization?
> `InvalidClassException` is thrown — the saved file is incompatible with the current class definition.

---

## Revision Checkpoint

> Write code to read a CSV file line by line, split each line by comma, and print the second column. Use try-with-resources.
