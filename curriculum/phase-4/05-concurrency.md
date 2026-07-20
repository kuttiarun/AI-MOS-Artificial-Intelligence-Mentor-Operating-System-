# Java Concurrency — Threads, Synchronization, and Safe Shared State

## Why This Concept Exists
A single-threaded program executes one instruction at a time. Modern CPUs have 8–32 cores sitting idle. Java Threads let you harness all cores simultaneously — but concurrent access to shared data causes race conditions, deadlocks, and memory visibility bugs that are notoriously hard to debug.

## Problem Before Proper Concurrency Primitives
```java
// Two threads both incrementing a shared counter
int count = 0;
// Thread A reads count (0), Thread B reads count (0)
// Thread A writes count+1 = 1, Thread B writes count+1 = 1
// count is 1, but you made 2 increments — lost update!
```

## Real-World Analogy
Think of shared memory as a whiteboard in a meeting room. Without a "talking token" (lock), everyone writes simultaneously and the whiteboard becomes unreadable.

## Thread Lifecycle
```
NEW → RUNNABLE → [BLOCKED/WAITING/TIMED_WAITING] → TERMINATED
```

## Three Ways to Create Threads
```java
// 1. Extend Thread
class MyThread extends Thread {
    public void run() { System.out.println("Running"); }
}

// 2. Implement Runnable (preferred — allows extending another class)
Thread t = new Thread(() -> System.out.println("Lambda thread"));
t.start();

// 3. ExecutorService (production preferred)
ExecutorService exec = Executors.newFixedThreadPool(4);
exec.submit(() -> processTask());
exec.shutdown();
```

## synchronized — The Basic Lock
```java
public class Counter {
    private int count = 0;
    
    public synchronized void increment() { count++; }     // method lock
    
    public void decrement() {
        synchronized (this) { count--; }                   // block lock
    }
}
```

## volatile — Memory Visibility
```java
// Without volatile: threads cache the variable locally
// With volatile: every read/write goes straight to main memory
private volatile boolean running = true;

public void stop() { running = false; }
public void run() {
    while (running) { /* work */ }
}
```

## java.util.concurrent — Production Toolkit
| Class | Purpose |
|---|---|
| `AtomicInteger` | Lock-free thread-safe integer |
| `ReentrantLock` | Explicit lock with tryLock(), fairness |
| `CountDownLatch` | Wait for N events to complete |
| `CyclicBarrier` | N threads wait for each other |
| `Semaphore` | Control access to limited resources |
| `ConcurrentHashMap` | Thread-safe HashMap |
| `CompletableFuture<T>` | Async computation with chaining |

## Deadlock — How It Happens
```
Thread A holds Lock 1, waits for Lock 2
Thread B holds Lock 2, waits for Lock 1
→ Both wait forever
```
Prevention: always acquire locks in the same global order.

## Production Reality
At Zoho production scale, raw `synchronized` is avoided in favor of `java.util.concurrent` utilities. `CompletableFuture` chains replace nested callback hell. Thread pools are tuned to `2 * CPU_cores` for CPU-bound tasks.

## Zoho Interview Questions
1. What is a race condition? Give a concrete example.
2. What is the difference between `synchronized` and `volatile`?
3. How does `ConcurrentHashMap` achieve thread safety without global locking?
4. What causes a deadlock and how do you detect/prevent it?
5. What is the difference between `Callable` and `Runnable`?

## Revision Quiz
1. Why is `count++` not thread-safe even though it looks like one operation?
2. What does `thread.join()` do?
3. When would you use `ReentrantLock` over `synchronized`?
