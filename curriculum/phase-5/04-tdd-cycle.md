# Test-Driven Development — Red-Green-Refactor Cycle

## Why TDD Exists
Most developers write code, then tests. TDD flips this — you write the test first, watch it fail (Red), write the minimum code to make it pass (Green), then improve the design without breaking behavior (Refactor). The result: cleaner architecture, better coverage, and tests as living documentation.

## The TDD Cycle
```
    ┌─────────┐
    │  RED    │  Write a failing test
    └────┬────┘
         │
    ┌────▼────┐
    │  GREEN  │  Write minimum code to pass
    └────┬────┘
         │
    ┌────▼────┐
    │REFACTOR │  Improve design, keep tests green
    └────┬────┘
         │
         └─────────→ (repeat)
```

## Concrete Example
**Requirement**: A `StringCalculator.add()` method that sums numbers from a comma-separated string.

### Step 1 — RED (write failing test first)
```java
@Test
void testEmptyStringReturnsZero() {
    StringCalculator calc = new StringCalculator();
    assertEquals(0, calc.add(""));    // FAILS — class doesn't exist yet
}
```

### Step 2 — GREEN (minimum code to pass)
```java
public class StringCalculator {
    public int add(String numbers) {
        if (numbers.isEmpty()) return 0;
        return 0; // just enough to pass this test
    }
}
```

### Step 3 — RED again (next test)
```java
@Test
void testSingleNumber() {
    assertEquals(5, calc.add("5")); // FAILS
}
```

### Step 4 — GREEN + REFACTOR
```java
public int add(String numbers) {
    if (numbers.isEmpty()) return 0;
    return Arrays.stream(numbers.split(","))
        .mapToInt(Integer::parseInt)
        .sum();
}
```

## Test Pyramid (TDD Context)
| Test Level | TDD Impact |
|---|---|
| Unit | Primary TDD target — test each method |
| Integration | Added after unit tests exist |
| E2E | Written against acceptance criteria |

## Benefits of TDD
- **Design feedback**: Hard-to-test code is usually bad design.
- **Coverage by default**: Tests written before code means code without tests can't exist.
- **Regression safety**: Any future change that breaks behavior is immediately visible.
- **Documentation**: Tests describe intended behavior better than comments.

## Pitfalls
- Writing tests so tight they test implementation, not behavior (test brittle, breaks on refactor)
- Skipping the Refactor step — accumulates technical debt
- Using TDD for every line (overkill for trivial getters/setters)

## Production Reality
At Zoho, TDD is the standard for new feature development. Existing codebases use test-after for legacy code coverage recovery. The key metric is behavior coverage, not line coverage.

## Zoho Interview Questions
1. What is the Red-Green-Refactor cycle?
2. Why would you write a test before the implementation?
3. What is the difference between TDD and BDD (Behaviour-Driven Development)?
4. Can you use TDD with Mockito? How?
5. How does TDD influence the design of classes?

## Revision Quiz
1. What does a "Red" test mean in TDD?
2. In the Refactor step, are you allowed to change test logic?
3. What is the "simplest thing that could possibly work" principle in TDD?
