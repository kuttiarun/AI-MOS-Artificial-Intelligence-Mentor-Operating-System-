# Spring Security — Authentication and Authorization

## Why Security Exists
Without security, any person on the internet can call your API, access any user's data, or execute admin operations. Spring Security provides the authentication layer (who are you?) and authorization layer (what are you allowed to do?).

## Security Filter Chain
```
HTTP Request
  → SecurityFilterChain
    → JwtAuthenticationFilter   (read + validate token)
    → UsernamePasswordAuthFilter (handle login)
    → FilterSecurityInterceptor  (check permissions)
      → Your Controller
```

## Key Concepts
| Concept | Meaning |
|---|---|
| Authentication | Proving identity ("I am Arun") |
| Authorization | Checking permissions ("Arun can read reports") |
| Principal | The currently authenticated user |
| GrantedAuthority | A permission/role ("ROLE_ADMIN") |
| SecurityContext | Thread-local storage of the current user |

## JWT (JSON Web Token) — Stateless Auth
```
Header.Payload.Signature

Header: { "alg": "HS256", "typ": "JWT" }
Payload: { "sub": "user123", "roles": ["ROLE_USER"], "exp": 1700000000 }
Signature: HMAC_SHA256(base64(header) + "." + base64(payload), secretKey)
```

The server signs the token. Any service can verify it with the secret key — no database lookup needed on each request.

## Spring Security Configuration (Spring Boot 3.x)
```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(AbstractHttpConfigurer::disable)
            .sessionManagement(s -> s.sessionCreationPolicy(STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/v1/auth/**").permitAll()
                .requestMatchers("/api/v1/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class);
        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(); // never store plaintext passwords!
    }
}
```

## JWT Filter Implementation
```java
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain) throws IOException, ServletException {
        String header = request.getHeader("Authorization");
        if (header != null && header.startsWith("Bearer ")) {
            String token = header.substring(7);
            if (jwtService.isValid(token)) {
                UsernamePasswordAuthenticationToken auth =
                    new UsernamePasswordAuthenticationToken(
                        jwtService.extractUsername(token), null,
                        jwtService.extractAuthorities(token)
                    );
                SecurityContextHolder.getContext().setAuthentication(auth);
            }
        }
        chain.doFilter(request, response);
    }
}
```

## Method-Level Security
```java
@PreAuthorize("hasRole('ADMIN')")
public void deleteUser(Long id) { ... }

@PreAuthorize("hasRole('USER') and #id == authentication.principal.id")
public UserDto getUser(Long id) { ... } // users can only read their own data
```

## BCrypt Password Hashing
```java
// Store — never store plaintext!
String hashed = passwordEncoder.encode("myPassword123");

// Verify
boolean matches = passwordEncoder.matches("myPassword123", hashed);
```

## Production Reality
At Zoho, JWT tokens have 15-minute expiry with refresh tokens. BCrypt with strength 12 is standard. All admin endpoints require `ROLE_ADMIN`. Security configs are reviewed in every PR.

## Zoho Interview Questions
1. What is the difference between authentication and authorization?
2. How does JWT enable stateless authentication?
3. Why should you never store passwords in plaintext?
4. What does `@PreAuthorize` do and how do you enable it?
5. What is the difference between `403 Forbidden` and `401 Unauthorized`?

## Revision Quiz
1. What Spring Security class stores the currently authenticated user?
2. What hash algorithm should you use for passwords in Spring Security?
3. Where in an HTTP request is the JWT token typically sent?
