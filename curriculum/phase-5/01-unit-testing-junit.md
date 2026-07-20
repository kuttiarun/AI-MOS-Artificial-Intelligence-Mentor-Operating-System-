# JUnit 5 — Unit Testing Fundamentals

## Why Testing Exists
A codebase without tests is a codebase that only works by coincidence. Unit tests lock in correct behavior as a contract — when code changes, tests immediately tell you what broke. Zoho's engineering culture mandates tests before code reaches production review.

## What is a Unit Test?
A unit test verifies one isolated unit of behavior (usually a method) with no external dependencies (no database, no network). Fast, deterministic, repeatable.

## JUnit 5 Architecture
```
JUnit 5
├── JUnit Platform (runner, test engine)
├── JUnit Jupiter (new API: @Test, @BeforeEach, assertions)
└── JUnit Vintage (runs JUnit 3/4 tests)
```

## Core Annotations
| Annotation | Purpose |
|---|---|
| `@Test` | Mark a method as a test |
| `@BeforeEach` | Run before every test method |
| `@AfterEach` | Run after every test method |
| `@BeforeAll` | Run once before all tests (must be `static`) |
| `@AfterAll` | Run once after all tests (must be `static`) |
| `@Disabled` | Skip this test with a reason |
| `@DisplayName` | Human-readable test name |
| `@Nested` | Group related tests in inner class |
| `@ParameterizedTest` | Run same test with multiple inputs |

## Assertions (org.junit.jupiter.api.Assertions)
```java
assertEquals(expected, actual, "message");
assertNotNull(value);
assertTrue(condition);
assertThrows(IllegalArgumentException.class, () -> service.process(null));
assertAll("group",
    () -> assertEquals(200, response.getStatus()),
    () -> assertNotNull(response.getBody())
);
```

## Example Test Class
```java
@DisplayName("BankAccount Tests")
class BankAccountTest {
    
    private BankAccount account;
    
    @BeforeEach
    void setUp() {
        account = new BankAccount(1000.0);
    }
    
    @Test
    @DisplayName("Deposit increases balance")
    void testDeposit() {
        account.deposit(500.0);
        assertEquals(1500.0, account.getBalance(), 0.001);
    }
    
    @Test
    @DisplayName("Withdraw below zero throws exception")
    void testOverdraft() {
        assertThrows(InsufficientFundsException.class,
            () -> account.withdraw(2000.0));
    }
    
    @ParameterizedTest
    @ValueSource(doubles = {-1, 0, -100})
    @DisplayName("Invalid deposit amounts throw exception")
    void testInvalidDeposit(double amount) {
        assertThrows(IllegalArgumentException.class,
            () -> account.deposit(amount));
    }
}
```

## Production Reality
At Zoho, unit tests are mandatory in CI. A pull request with < 80% test coverage is rejected automatically. Tests run on every git push via Jenkins/GitHub Actions.

## Zoho Interview Questions
1. What is the difference between `@BeforeEach` and `@BeforeAll`?
2. How does `assertThrows()` work? What does it return?
3. What is a parameterized test and when is it useful?
4. What is the AAA pattern (Arrange-Act-Assert)?
5. How do you test a method that has no return value (void)?

## Revision Quiz
1. What annotation marks a JUnit 5 test method?
2. Write a test that verifies `Math.max(3, 7)` returns 7.
3. How do you verify that a specific exception is thrown?
