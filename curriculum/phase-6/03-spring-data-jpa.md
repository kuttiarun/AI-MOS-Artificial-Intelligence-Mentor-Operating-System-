# Spring Data JPA — Database Access with Repository Pattern

## Why Spring Data JPA Exists
Before Spring Data, writing database access code meant dozens of lines of boilerplate: open connection, prepare statement, execute, map ResultSet to objects, close connection, handle exceptions. JPA (Java Persistence API) maps Java objects to database tables. Spring Data JPA eliminates even JPA boilerplate.

## The Abstraction Stack
```
Your Code
  └── Spring Data Repository (interface only)
        └── Hibernate (JPA implementation)
              └── JDBC Driver
                    └── PostgreSQL / MySQL
```

## JPA Entity — Mapping Java to Table
```java
@Entity
@Table(name = "users")
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true)
    private String email;
    
    @Column(name = "full_name")
    private String name;
    
    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Order> orders = new ArrayList<>();
}
```

## Spring Data Repository
```java
// Spring generates all implementation — you write only the interface
public interface UserRepository extends JpaRepository<User, Long> {
    
    // Derived query — Spring generates SQL from method name
    Optional<User> findByEmail(String email);
    
    List<User> findByNameContainingIgnoreCase(String name);
    
    // Custom JPQL
    @Query("SELECT u FROM User u WHERE u.email = :email AND u.active = true")
    Optional<User> findActiveUserByEmail(@Param("email") String email);
    
    // Native SQL
    @Query(value = "SELECT * FROM users WHERE created_at > ?1", nativeQuery = true)
    List<User> findRecentUsers(LocalDateTime since);
}
```

## Relationships
| Type | Annotation | Example |
|---|---|---|
| One-to-One | `@OneToOne` | User ↔ Profile |
| One-to-Many | `@OneToMany` | User → Orders |
| Many-to-One | `@ManyToOne` | Order → User |
| Many-to-Many | `@ManyToMany` | Student ↔ Course |

## Fetch Types — Critical Performance Concern
```java
// LAZY (preferred) — loads orders only when you access them
@OneToMany(fetch = FetchType.LAZY)
private List<Order> orders;

// EAGER (avoid for collections) — loads orders with every User query
@OneToMany(fetch = FetchType.EAGER)
private List<Order> orders;
```

## N+1 Problem — Most Common JPA Bug
```java
// This makes 1 query for all users, then N queries for each user's orders
List<User> users = userRepo.findAll();
users.forEach(u -> System.out.println(u.getOrders().size())); // N+1!

// Fix: JOIN FETCH
@Query("SELECT u FROM User u JOIN FETCH u.orders")
List<User> findAllWithOrders();
```

## Transactions
```java
@Service
@Transactional
public class OrderService {
    public void placeOrder(Order order) {
        // All DB operations in this method run in one transaction
        // If any fails, ALL are rolled back automatically
        userRepo.updateBalance(order.getUserId(), -order.getAmount());
        orderRepo.save(order);
        inventoryRepo.decrementStock(order.getItemId());
    }
}
```

## Production Reality
At Zoho, Hibernate is used with PostgreSQL. The N+1 problem is the #1 JPA performance killer — caught via `spring.jpa.show-sql=true` in development. Entities always use `FetchType.LAZY` on collections.

## Zoho Interview Questions
1. What is the N+1 problem and how do you fix it?
2. What is the difference between `LAZY` and `EAGER` fetching?
3. What does `@Transactional` guarantee?
4. How does Spring Data derive a query from a method name like `findByEmailAndActive`?
5. What is the difference between JPQL and native SQL queries?

## Revision Quiz
1. What base interface do you extend to get full CRUD for an entity?
2. Write a repository method that finds users by last name containing a substring.
3. What `application.properties` property shows all SQL queries being executed?
