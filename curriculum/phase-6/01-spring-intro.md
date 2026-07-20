# Spring Boot Introduction — Dependency Injection and IoC

## Why Spring Exists
Before Spring (2003), Java EE (J2EE) required XML configuration files hundreds of lines long just to wire a simple service. Spring's Inversion of Control and Dependency Injection made enterprise Java manageable. Spring Boot (2014) eliminated even Spring's configuration overhead.

## Core Concepts

### Inversion of Control (IoC)
Traditional code: *you* create objects. `UserService service = new UserService();`
IoC: the **framework** creates and manages objects for you. You ask the container, it delivers.

### Dependency Injection (DI)
Instead of creating your dependencies, you *declare* them and Spring *injects* them:
```java
// Without DI — tightly coupled
class OrderService {
    private UserRepository repo = new UserRepository(); // hardcoded
}

// With DI — loosely coupled
@Service
class OrderService {
    private final UserRepository repo;
    
    // Spring injects UserRepository automatically
    public OrderService(UserRepository repo) {
        this.repo = repo;
    }
}
```

## The Spring Bean Container (ApplicationContext)
```
ApplicationContext
├── Beans (managed objects — created, configured, wired by Spring)
│   ├── @Component (generic)
│   ├── @Service    (business logic)
│   ├── @Repository (data access)
│   └── @Controller (web layer)
└── Configuration (@Configuration + @Bean factories)
```

## Spring Boot — Auto-Configuration
`@SpringBootApplication` = `@Configuration` + `@EnableAutoConfiguration` + `@ComponentScan`

Spring Boot scans your classpath and automatically configures:
- DataSource (if `spring-data-jpa` on classpath + `application.properties` has DB URL)
- Embedded Tomcat server (if `spring-web` present)
- Jackson JSON mapper (if `jackson-databind` present)

## application.properties / application.yml
```properties
# application.properties
server.port=8080
spring.datasource.url=jdbc:postgresql://localhost:5432/aimos
spring.datasource.username=postgres
spring.jpa.hibernate.ddl-auto=update
logging.level.root=INFO
```

## Bean Scopes
| Scope | Instances | Use Case |
|---|---|---|
| `singleton` | One per context (default) | Stateless services |
| `prototype` | New per injection | Stateful objects |
| `request` | One per HTTP request | Web: request-scoped state |
| `session` | One per HTTP session | Web: user session data |

## Profiles
```java
@Profile("dev")
@Bean
public DataSource h2DataSource() { ... } // used in development

@Profile("prod")  
@Bean
public DataSource postgresDataSource() { ... } // used in production
```

## Production Reality
Every Zoho Java service is built on Spring Boot. Understanding the container lifecycle (bean creation, initialization, destruction) is required knowledge for any Java developer role.

## Zoho Interview Questions
1. What is Inversion of Control? How is it different from Dependency Injection?
2. What is the difference between `@Component`, `@Service`, and `@Repository`?
3. What does `@SpringBootApplication` actually do?
4. How does Spring Boot auto-configuration work?
5. What is the difference between singleton and prototype scope?

## Revision Quiz
1. What annotation marks a class as a Spring-managed bean?
2. What is constructor injection and why is it preferred over field injection?
3. What does `spring.jpa.hibernate.ddl-auto=update` do?
