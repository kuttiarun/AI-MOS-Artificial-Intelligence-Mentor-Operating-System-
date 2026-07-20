# Mockito — Mocking External Dependencies

## Why Mocking Exists
A unit test must be isolated. But your `OrderService` calls `PaymentGatewayClient`, which calls a real payment API. In a unit test, you don't want real network calls — they're slow, flaky, and cost money. Mockito lets you replace real dependencies with programmable fakes (mocks).

## Real-World Analogy
A flight simulator. Pilots train in a mock cockpit — realistic controls, but no real aircraft risk. Mockito is the simulator for your dependency layer.

## Core Mockito Concepts
| Concept | Meaning |
|---|---|
| Mock | A fake object that you control |
| Stub | Programming the mock to return specific values |
| Verify | Asserting that a method was called (or not called) |
| Spy | Wraps a real object — real behavior by default, selectively stubbed |
| Captor | Captures arguments passed to a mock method |

## Setup
```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {
    
    @Mock
    private PaymentGatewayClient paymentClient; // Mockito creates a fake
    
    @InjectMocks
    private OrderService orderService; // Mockito injects the mock into this
    
    @Test
    void testSuccessfulOrder() {
        // Stub: when paymentClient.charge() is called, return true
        when(paymentClient.charge(any(Order.class))).thenReturn(true);
        
        Order order = new Order("item-123", 99.99);
        boolean result = orderService.placeOrder(order);
        
        assertTrue(result);
        
        // Verify: paymentClient.charge() was called exactly once
        verify(paymentClient, times(1)).charge(order);
    }
}
```

## Stubbing Methods
```java
// Return a value
when(service.findById(1L)).thenReturn(Optional.of(user));

// Throw an exception
when(service.findById(999L)).thenThrow(new UserNotFoundException());

// Return different values on consecutive calls
when(service.getStatus()).thenReturn("PENDING", "PROCESSING", "DONE");

// Answer with logic
when(service.calculate(anyInt()))
    .thenAnswer(inv -> inv.getArgument(0) * 2);
```

## ArgumentCaptor
```java
@Captor
ArgumentCaptor<EmailRequest> emailCaptor;

@Test
void testEmailIsSentWithCorrectContent() {
    orderService.confirmOrder(order);
    
    verify(emailService).send(emailCaptor.capture());
    EmailRequest sent = emailCaptor.getValue();
    assertEquals("order-confirm@zoho.com", sent.getFrom());
    assertTrue(sent.getBody().contains(order.getId()));
}
```

## Spy — Partial Mocking
```java
List<String> realList = new ArrayList<>();
List<String> spyList = spy(realList);

spyList.add("hello");        // real method called
when(spyList.size()).thenReturn(100); // stubbed
System.out.println(spyList.size()); // 100
```

## Production Reality
At Zoho, every service layer test uses Mockito to isolate the repository/DAO layer. `@MockBean` (Spring Boot) is used in integration slices to replace specific beans with mocks.

## Zoho Interview Questions
1. What is the difference between a mock and a stub?
2. What is the difference between `mock()` and `spy()`?
3. When would you use `ArgumentCaptor`?
4. How does `@InjectMocks` work? What injection strategies does Mockito try?
5. What does `verify(mock, never()).method()` assert?

## Revision Quiz
1. How do you stub a method to throw an exception in Mockito?
2. What annotation creates a mock in JUnit 5 with `MockitoExtension`?
3. What is the risk of using `spy()` on a real object?
