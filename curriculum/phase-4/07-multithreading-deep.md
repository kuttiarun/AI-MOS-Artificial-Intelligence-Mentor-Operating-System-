# Multithreading Deep Dive — Executors, CompletableFuture & Fork/Join

## What You'll Master
- The `ExecutorService` framework — why raw `Thread` is outdated
- `Future` and `CompletableFuture` for async computation
- `CountDownLatch`, `CyclicBarrier`, `Semaphore` — synchronization tools
- The **Fork/Join Framework** for parallel divide-and-conquer

---

## ExecutorService — Thread Pool Management

```java
// NEVER do this in production
new Thread(() -> doWork()).start(); // no control, no reuse

// DO this instead — fixed thread pool
ExecutorService pool = Executors.newFixedThreadPool(4);

// Submit tasks
Future<Integer> future = pool.submit(() -> {
    Thread.sleep(1000);
    return 42;
});

// Do other work while task runs...
int result = future.get(); // blocks until done
pool.shutdown();           // graceful shutdown (waits for tasks)
pool.shutdownNow();        // forceful shutdown (interrupts tasks)
```

### Pool Types

| Factory | Behavior | Use Case |
|---|---|---|
| `newFixedThreadPool(n)` | n threads, queue overflow waits | CPU-bound tasks |
| `newCachedThreadPool()` | Grows/shrinks, reuses idle threads | Short-lived async tasks |
| `newSingleThreadExecutor()` | 1 thread, sequential | Background serial tasks |
| `newScheduledThreadPool(n)` | Supports delay/periodic scheduling | Cron-like tasks |
| `newVirtualThreadPerTaskExecutor()` | Java 21 — lightweight virtual threads | High-concurrency I/O |

---

## CompletableFuture — Async Pipelines

```java
CompletableFuture<String> cf = CompletableFuture
    .supplyAsync(() -> fetchUserFromDB(userId))   // runs in ForkJoinPool
    .thenApply(user -> enrichWithRoles(user))      // transform result
    .thenApply(user -> user.toJson())              // transform again
    .exceptionally(ex -> "{\"error\": \"" + ex.getMessage() + "\"}");

// Combine two futures
CompletableFuture<String> userFuture = CompletableFuture.supplyAsync(() -> "Arun");
CompletableFuture<Integer> ageFuture = CompletableFuture.supplyAsync(() -> 22);

CompletableFuture<String> combined = userFuture.thenCombine(
    ageFuture,
    (name, age) -> name + " is " + age + " years old"
);
System.out.println(combined.join()); // "Arun is 22 years old"

// Wait for all
CompletableFuture.allOf(cf1, cf2, cf3).join();
// Wait for first to complete
CompletableFuture.anyOf(cf1, cf2, cf3).thenAccept(result -> ...);
```

---

## Synchronization Utilities

### CountDownLatch — Wait for N tasks to finish
```java
int N = 5;
CountDownLatch latch = new CountDownLatch(N);

for (int i = 0; i < N; i++) {
    pool.submit(() -> {
        doWork();
        latch.countDown(); // decrements counter
    });
}
latch.await(); // blocks until counter reaches 0
System.out.println("All tasks done!");
```

### Semaphore — Limit concurrent access
```java
Semaphore sem = new Semaphore(3); // max 3 concurrent threads

pool.submit(() -> {
    sem.acquire();   // blocks if all 3 permits taken
    try { accessDB(); }
    finally { sem.release(); } // always release
});
```

### CyclicBarrier — Synchronize at a meeting point
```java
CyclicBarrier barrier = new CyclicBarrier(3, () -> System.out.println("All arrived!"));
// Each thread calls barrier.await() — only when ALL 3 call it do they proceed
```

---

## Fork/Join Framework — Parallel Divide & Conquer

```java
public class SumTask extends RecursiveTask<Long> {
    private static final int THRESHOLD = 1000;
    private final long[] arr;
    private final int start, end;

    @Override
    protected Long compute() {
        if (end - start <= THRESHOLD) {
            // Base case: compute directly
            long sum = 0;
            for (int i = start; i < end; i++) sum += arr[i];
            return sum;
        }
        // Divide
        int mid = (start + end) / 2;
        SumTask left  = new SumTask(arr, start, mid);
        SumTask right = new SumTask(arr, mid, end);
        left.fork();         // run left in separate thread
        long rightResult = right.compute(); // run right in this thread
        long leftResult  = left.join();     // wait for left
        return leftResult + rightResult;    // conquer
    }
}

ForkJoinPool pool = ForkJoinPool.commonPool();
long total = pool.invoke(new SumTask(arr, 0, arr.length));
```

---

## Zoho Interview Questions

**Q1**: Difference between `submit()` and `execute()` on ExecutorService?
> `execute()` takes a `Runnable`, returns nothing. `submit()` takes `Callable` or `Runnable`, returns a `Future` for tracking result/exception.

**Q2**: What is a deadlock and how do you prevent it?
> Deadlock = two threads each hold a lock the other needs.  
> Prevention: always acquire locks in the **same order**; use `tryLock()` with timeout; prefer higher-level constructs (`CompletableFuture`, `BlockingQueue`) over raw `synchronized`.

---

## Revision Checkpoint

> Using `CompletableFuture`, write code that calls 3 APIs concurrently and returns a combined result only after all three complete.
