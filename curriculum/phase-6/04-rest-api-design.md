# REST API Design — Principles and Best Practices

## Why Good API Design Matters
An API is a contract with every client forever. Bad URL design, inconsistent status codes, and missing documentation cause bugs in every consumer. Zoho serves thousands of internal and external API clients — a bad design choice propagates across all of them.

## REST Constraints
1. **Stateless** — each request contains all info needed; no server-side session
2. **Resource-based** — URLs identify nouns, not verbs
3. **Uniform Interface** — consistent HTTP verbs + status codes
4. **Layered** — client doesn't know if it talks to proxy, LB, or real server

## URL Design — Nouns, Not Verbs
```
✅ Good                          ❌ Bad
GET    /api/v1/users             GET /api/v1/getUsers
POST   /api/v1/users             POST /api/v1/createUser
GET    /api/v1/users/42          GET /api/v1/getUserById?id=42
PUT    /api/v1/users/42          POST /api/v1/updateUser
DELETE /api/v1/users/42          POST /api/v1/deleteUser
GET    /api/v1/users/42/orders   GET /api/v1/getUserOrders?userId=42
```

## HTTP Status Codes — The Contract
| Range | Category | Common Codes |
|---|---|---|
| 2xx | Success | 200 OK, 201 Created, 204 No Content |
| 3xx | Redirect | 301 Moved, 304 Not Modified |
| 4xx | Client Error | 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 409 Conflict, 422 Unprocessable |
| 5xx | Server Error | 500 Internal Server Error, 503 Service Unavailable |

## Request/Response Design
```json
// Request — POST /api/v1/users
{
  "email": "arun@zoho.com",
  "name": "Arun Kumar",
  "role": "DEVELOPER"
}

// Success Response — 201 Created
{
  "id": "usr_abc123",
  "email": "arun@zoho.com",
  "name": "Arun Kumar",
  "createdAt": "2024-01-15T10:30:00Z"
}

// Error Response — 422 Unprocessable
{
  "error": "VALIDATION_FAILED",
  "message": "Email address is already in use",
  "field": "email",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Versioning
```
/api/v1/users    ← version in URL path (most common)
/api/users       + Header: Accept: application/vnd.api+json;version=1
```

## Pagination
```
GET /api/v1/users?page=0&size=20&sort=createdAt,desc

Response:
{
  "content": [...],
  "page": 0,
  "size": 20,
  "totalElements": 247,
  "totalPages": 13
}
```

## OpenAPI / Swagger Documentation
```java
@Operation(summary = "Get user by ID", description = "Returns user details")
@ApiResponses({
    @ApiResponse(responseCode = "200", description = "User found"),
    @ApiResponse(responseCode = "404", description = "User not found")
})
@GetMapping("/{id}")
public ResponseEntity<UserDto> getUser(@PathVariable Long id) { ... }
```

## Production Reality
At Zoho, every API requires: versioning, consistent error format, Swagger documentation, pagination for list endpoints, and rate limiting headers. Internal APIs follow the same standards as external ones.

## Zoho Interview Questions
1. What is the difference between PUT and PATCH?
2. When should you return 400 vs 422 vs 404?
3. Why are resources in URLs always plural nouns?
4. What is HATEOAS and is it required for a REST API?
5. How do you handle breaking changes in a public API?

## Revision Quiz
1. What HTTP status code should a successful POST/create return?
2. Design the URL structure for an API that manages blog posts and their comments.
3. What does the `204 No Content` status mean and when do you use it?
