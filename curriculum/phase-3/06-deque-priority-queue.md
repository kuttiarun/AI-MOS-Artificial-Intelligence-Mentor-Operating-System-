# ArrayDeque & LinkedHashMap — Deque, Stack & Queue Patterns

## What You'll Master
- Why `ArrayDeque` beats `Stack` and `LinkedList` for stack/queue use cases
- The `Deque` interface — double-ended queue operations
- `PriorityQueue` for heap-based ordering
- `LinkedHashMap` as an insertion-ordered, O(1) map

---

## ArrayDeque — The Go-To Stack & Queue

```java
// As a Stack (LIFO)
Deque<Integer> stack = new ArrayDeque<>();
stack.push(1);    // addFirst
stack.push(2);
stack.push(3);
stack.peek();     // 3 (top, no remove)
stack.pop();      // 3 (removeFirst)

// As a Queue (FIFO)
Deque<Integer> queue = new ArrayDeque<>();
queue.offer(1);   // addLast
queue.offer(2);
queue.offer(3);
queue.peek();     // 1 (front, no remove)
queue.poll();     // 1 (removeFirst)
```

**Why not `Stack` class?** It extends `Vector` (synchronized = slow) and is a legacy class.  
**Why not `LinkedList`?** ArrayDeque has better cache locality and no node allocation overhead.

---

## Full Deque API

```java
Deque<String> dq = new ArrayDeque<>();

// Front operations
dq.addFirst("A")    / dq.offerFirst("A")  // add to front
dq.peekFirst()       / dq.getFirst()       // view front
dq.pollFirst()       / dq.removeFirst()    // remove from front

// Rear operations
dq.addLast("Z")     / dq.offerLast("Z")   // add to rear
dq.peekLast()        / dq.getLast()        // view rear
dq.pollLast()        / dq.removeLast()     // remove from rear
```

`offer*` returns `false` on failure; `add*` throws exception.  
`poll*` returns `null` on empty; `remove*` throws exception.

---

## PriorityQueue — Min/Max Heap

```java
// Min-heap (default)
PriorityQueue<Integer> minHeap = new PriorityQueue<>();
minHeap.offer(5);
minHeap.offer(1);
minHeap.offer(3);
System.out.println(minHeap.peek()); // 1 (smallest always at top)

// Max-heap
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Comparator.reverseOrder());

// Custom comparator — sort tasks by priority
PriorityQueue<Task> taskQueue = new PriorityQueue<>(
    Comparator.comparingInt(Task::getPriority)
);

// Top-K pattern
int[] nums = {3, 1, 4, 1, 5, 9, 2, 6};
PriorityQueue<Integer> topK = new PriorityQueue<>(); // min-heap of size k
int k = 3;
for (int n : nums) {
    topK.offer(n);
    if (topK.size() > k) topK.poll(); // remove smallest
}
// topK now contains the 3 largest: [5, 6, 9]
```

---

## Performance Comparison

| Operation | ArrayDeque | LinkedList | PriorityQueue |
|---|---|---|---|
| Add front/rear | O(1) amortized | O(1) | — |
| Remove front/rear | O(1) | O(1) | — |
| Peek/Poll | O(1) | O(1) | O(log n) |
| Random access | O(n) | O(n) | — |
| Memory | Compact array | Node per element | Compact array |

---

## Monotonic Stack Pattern (Interview Staple)

```java
// Find next greater element for each element
int[] nums = {2, 1, 2, 4, 3};
int[] result = new int[nums.length];
Deque<Integer> stack = new ArrayDeque<>(); // stores indices

for (int i = 0; i < nums.length; i++) {
    while (!stack.isEmpty() && nums[stack.peek()] < nums[i]) {
        result[stack.pop()] = nums[i];
    }
    stack.push(i);
}
while (!stack.isEmpty()) result[stack.pop()] = -1;
// result: [2, 2, 4, -1, -1]
```

---

## Revision Checkpoint

> Implement a `MinStack` that supports `push()`, `pop()`, `top()`, and `getMin()` in O(1) time using `ArrayDeque`.
