# Integration Testing in Spring Boot

## Why Integration Testing Exists
Unit tests verify individual classes. Integration tests verify that all the pieces work together — the controller, service, repository, and database all wired correctly. They catch bugs that only appear at the boundaries: wrong SQL, misconfigured beans, missing transaction boundaries.

## Test Pyramid
```
         /\
        /  \  ← E2E Tests (few, slow, expensive)
       /────\
      / Integ \  ← Integration Tests (some)
     /──────────\
    /  Unit Tests \  ← (many, fast, cheap)
   /______________\
```

## Spring Boot Test Slices
Instead of loading the full application context (slow), use targeted test slices:

| Annotation | Loads | Use For |
|---|---|---|
| `@WebMvcTest` | Only web layer (controllers) | Testing HTTP mapping, validation |
| `@DataJpaTest` | Only JPA layer + H2 | Testing repositories and queries |
| `@SpringBootTest` | Full context | End-to-end integration |
| `@RestClientTest` | REST client beans | Testing external HTTP clients |

## @WebMvcTest — Testing Controllers
```java
@WebMvcTest(UserController.class)
class UserControllerTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @MockBean
    private UserService userService; // Replace real service with mock
    
    @Test
    void testGetUser_Returns200() throws Exception {
        when(userService.findById(1L))
            .thenReturn(new User(1L, "Arun"));
        
        mockMvc.perform(get("/api/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.name").value("Arun"));
    }
    
    @Test
    void testGetUser_NotFound_Returns404() throws Exception {
        when(userService.findById(999L))
            .thenThrow(new UserNotFoundException());
        
        mockMvc.perform(get("/api/users/999"))
            .andExpect(status().isNotFound());
    }
}
```

## @DataJpaTest — Testing Repositories
```java
@DataJpaTest
class UserRepositoryTest {
    
    @Autowired
    private UserRepository userRepo;
    
    @Test
    void testFindByEmail() {
        userRepo.save(new User("arun@zoho.com", "Arun"));
        
        Optional<User> found = userRepo.findByEmail("arun@zoho.com");
        assertTrue(found.isPresent());
        assertEquals("Arun", found.get().getName());
    }
}
// Uses H2 in-memory DB by default — no real Postgres needed
```

## TestContainers — Real Database in Tests
```java
@Testcontainers
@SpringBootTest
class RealDatabaseTest {
    
    @Container
    static PostgreSQLContainer<?> postgres = 
        new PostgreSQLContainer<>("postgres:15");
    
    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
    }
    
    // Tests now run against REAL Postgres in a Docker container
}
```

## Production Reality
At Zoho, CI pipelines run: unit tests → integration tests (with H2 or Testcontainers) → full system tests. `@WebMvcTest` catches 80% of API bugs without spinning up a database.

## Zoho Interview Questions
1. What is the difference between `@SpringBootTest` and `@WebMvcTest`?
2. Why use Testcontainers instead of H2 for integration tests?
3. How does `MockMvc` simulate HTTP requests without a running server?
4. What does `@MockBean` do differently from Mockito's `@Mock`?
5. What is `@DynamicPropertySource` and when do you need it?

## Revision Quiz
1. Which test slice annotation loads only the web layer?
2. What database does `@DataJpaTest` use by default?
3. How do you assert a JSON response field value in `MockMvc`?
