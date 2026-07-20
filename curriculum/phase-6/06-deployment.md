# Deployment — Docker, CI/CD, and Production Readiness

## Why Deployment Knowledge Matters
Writing code is half the job. A senior Java developer must be able to containerize their service, define a build pipeline, and deploy confidently. Zoho engineers are expected to own their services from commit to production.

## Docker — Containerizing Your Spring Boot App

### Why Docker?
"Works on my machine" is not acceptable. Docker packages your app + its environment into a portable container that runs identically everywhere.

### Dockerfile for Spring Boot
```dockerfile
# Stage 1: Build
FROM eclipse-temurin:21-jdk-alpine AS builder
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN ./mvnw -q package -DskipTests

# Stage 2: Runtime (smaller image)
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - SPRING_DATASOURCE_URL=jdbc:postgresql://db:5432/mydb
      - SPRING_DATASOURCE_USERNAME=postgres
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=mydb
      - POSTGRES_PASSWORD=secret
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

## CI/CD Pipeline (GitHub Actions)
```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on: [push, pull_request]

jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up JDK 21
        uses: actions/setup-java@v4
        with:
          java-version: '21'
      
      - name: Run Tests
        run: mvn test
      
      - name: Check Coverage
        run: mvn verify  # JaCoCo gate runs here
      
      - name: Build Docker Image
        run: docker build -t my-app:${{ github.sha }} .
      
      - name: Push to Registry
        run: docker push registry.company.com/my-app:${{ github.sha }}
```

## Health Checks — Spring Actuator
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

```properties
management.endpoints.web.exposure.include=health,info,metrics
management.endpoint.health.show-details=when-authorized
```

```bash
curl http://localhost:8080/actuator/health
# {"status":"UP","components":{"db":{"status":"UP"},"diskSpace":{"status":"UP"}}}
```

## Production Environment Variables
```bash
# Never hardcode secrets — use environment variables
export SPRING_DATASOURCE_PASSWORD=<from-secret-manager>
export JWT_SECRET=<from-secret-manager>
export SPRING_PROFILES_ACTIVE=prod
```

## Production Checklist
- [ ] No secrets in code or git history
- [ ] Health endpoint configured
- [ ] JVM flags: `-XX:+UseG1GC -XX:+HeapDumpOnOutOfMemoryError`
- [ ] Structured JSON logging (not plain text)
- [ ] Graceful shutdown: `server.shutdown=graceful`
- [ ] Docker image uses slim JRE (not full JDK)
- [ ] Resource limits set in container orchestrator

## Production Reality
At Zoho, every service has a Dockerfile, a CI pipeline, and is deployed via Kubernetes. New engineers are expected to understand the build → test → containerize → deploy flow from day one.

## Zoho Interview Questions
1. What is the difference between a Docker image and a container?
2. Why use a multi-stage Dockerfile?
3. What is a CI/CD pipeline and what steps does it typically contain?
4. What does `docker-compose` solve that plain `docker run` doesn't?
5. What is the Spring Boot Actuator `/health` endpoint used for?

## Revision Quiz
1. What command builds a Docker image from a Dockerfile?
2. What is the risk of using `SPRING_PROFILES_ACTIVE=prod` in development?
3. What environment variable pattern avoids hardcoding DB passwords?
