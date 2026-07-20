# Spring MVC — Building REST APIs

## Why Spring MVC Exists
Spring MVC provides a structured way to handle HTTP requests without writing raw Servlet code. `@RestController` maps URLs to Java methods. The framework handles request parsing, JSON serialization, validation, and error responses automatically.

## Request Lifecycle
```
HTTP Request
  → DispatcherServlet
    → HandlerMapping (finds @RequestMapping)
      → Controller method
        → Service layer
          → Response serialized to JSON
            → HTTP Response
```

## Core Annotations
| Annotation | Purpose |
|---|---|
| `@RestController` | `@Controller` + `@ResponseBody` — returns JSON |
| `@RequestMapping("/api/v1")` | Base URL mapping for class |
| `@GetMapping("/users")` | HTTP GET handler |
| `@PostMapping("/users")` | HTTP POST handler |
| `@PutMapping("/users/{id}")` | HTTP PUT handler |
| `@DeleteMapping("/users/{id}")` | HTTP DELETE handler |
| `@PathVariable` | Extract `{id}` from URL |
| `@RequestBody` | Deserialize JSON body to object |
| `@RequestParam` | Extract query param `?page=1` |
| `@ResponseStatus` | Override default HTTP status code |

## Example REST Controller
```java
@RestController
@RequestMapping("/api/v1/users")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/{id}")
    public ResponseEntity<UserDto> getUser(@PathVariable Long id) {
        return userService.findById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public UserDto createUser(@RequestBody @Valid CreateUserRequest request) {
        return userService.create(request);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deleteUser(@PathVariable Long id) {
        userService.delete(id);
    }
}
```

## Validation with `@Valid`
```java
public class CreateUserRequest {
    @NotBlank(message = "Email is required")
    @Email
    private String email;
    
    @NotBlank
    @Size(min = 2, max = 50)
    private String name;
    
    @Min(18) @Max(120)
    private int age;
}
```

## Global Exception Handling
```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(UserNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ErrorResponse handleNotFound(UserNotFoundException ex) {
        return new ErrorResponse(404, ex.getMessage());
    }
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleValidation(MethodArgumentNotValidException ex) {
        String msg = ex.getBindingResult().getFieldErrors().stream()
            .map(e -> e.getField() + ": " + e.getDefaultMessage())
            .collect(Collectors.joining(", "));
        return new ErrorResponse(400, msg);
    }
}
```

## Production Reality
At Zoho, every public API uses `ResponseEntity<T>` for explicit status codes, `@Valid` for input validation, and `@RestControllerAdvice` for centralized error handling. Never return raw objects without a DTO layer — it leaks internal model details.

## Zoho Interview Questions
1. What is the difference between `@Controller` and `@RestController`?
2. How does `@RequestBody` work? What serialization library does Spring use by default?
3. What is `@RestControllerAdvice` and why is it better than try-catch in every controller?
4. What happens when `@Valid` validation fails on a `@RequestBody`?
5. What is the difference between `@PathVariable` and `@RequestParam`?

## Revision Quiz
1. Which annotation creates a GET endpoint at `/users/{id}`?
2. How do you return a 201 CREATED response?
3. Write a `@RestControllerAdvice` that handles `IllegalArgumentException` with 400.
