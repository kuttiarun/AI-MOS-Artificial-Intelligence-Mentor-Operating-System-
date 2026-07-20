# Maven — POM, Dependencies & Build Lifecycle

## What You'll Master
- What Maven solves and why every Java project uses it
- The `pom.xml` structure and dependency management
- Maven's **build lifecycle** — compile, test, package, deploy
- Dependency scopes, exclusions, and version conflict resolution

---

## What Is Maven?

Maven is a **build automation and dependency management tool**. It:
- Downloads JAR files automatically from Maven Central (no more manual JAR hell)
- Compiles, tests, and packages your code in one command
- Enforces a standard project structure every developer recognizes

```
my-project/
├── pom.xml                    ← Maven config
└── src/
    ├── main/
    │   ├── java/              ← Application code
    │   └── resources/         ← application.properties, etc.
    └── test/
        ├── java/              ← Test code
        └── resources/
```

---

## pom.xml — Project Object Model

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>

    <!-- Project identity (GAV coordinates) -->
    <groupId>com.aimos</groupId>
    <artifactId>learning-platform</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <packaging>jar</packaging>

    <!-- Inherited config (Spring Boot parent handles versions) -->
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
    </parent>

    <properties>
        <java.version>21</java.version>
    </properties>

    <dependencies>
        <!-- Compile scope (default) — included everywhere -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- Runtime scope — needed at runtime, not compile time -->
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <scope>runtime</scope>
        </dependency>

        <!-- Test scope — only for tests, not packaged -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>

        <!-- Provided scope — provided by server (e.g., Tomcat) -->
        <dependency>
            <groupId>javax.servlet</groupId>
            <artifactId>javax.servlet-api</artifactId>
            <scope>provided</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

---

## Build Lifecycle Phases

```bash
mvn compile           # compile src/main/java
mvn test              # run unit tests (JUnit)
mvn package           # create JAR/WAR in target/
mvn verify            # run integration tests
mvn install           # copy to local ~/.m2 repo
mvn deploy            # upload to remote repo (Nexus/Artifactory)

# Most common in practice
mvn clean package -DskipTests   # clean + package without running tests
mvn spring-boot:run             # run Spring Boot app
```

**Each phase runs all previous phases first**: `package` = compile + test + package.

---

## Dependency Scopes

| Scope | Compile | Test | Runtime | Packaged |
|---|---|---|---|---|
| `compile` (default) | ✅ | ✅ | ✅ | ✅ |
| `test` | ❌ | ✅ | ❌ | ❌ |
| `runtime` | ❌ | ✅ | ✅ | ✅ |
| `provided` | ✅ | ✅ | ❌ | ❌ |

---

## Resolving Dependency Conflicts

```xml
<!-- Problem: library-A needs logback 1.4, library-B needs logback 1.2 -->
<!-- Maven picks nearest in dependency tree (often wrong version) -->

<!-- Solution 1: Explicit version override -->
<dependency>
    <groupId>ch.qos.logback</groupId>
    <artifactId>logback-classic</artifactId>
    <version>1.4.14</version>
</dependency>

<!-- Solution 2: Exclude transitive dependency -->
<dependency>
    <groupId>some.library</groupId>
    <artifactId>library-A</artifactId>
    <exclusions>
        <exclusion>
            <groupId>ch.qos.logback</groupId>
            <artifactId>logback-classic</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

```bash
# Visualize dependency tree
mvn dependency:tree
mvn dependency:analyze  # find unused/undeclared deps
```

---

## Zoho Interview Questions

**Q1**: What is the difference between `install` and `deploy`?
> `install` puts the artifact in your local `~/.m2` repository (usable by other local projects). `deploy` uploads it to a shared remote repository (Nexus, Artifactory) so the whole team can use it.

**Q2**: What does `SNAPSHOT` mean in a version?
> A `SNAPSHOT` version (e.g., `1.0.0-SNAPSHOT`) is a development version that Maven re-downloads on every build if updated remotely. A release version (e.g., `1.0.0`) is immutable — once deployed, it never changes.

---

## Revision Checkpoint

> Explain the difference between `test` and `provided` scope. Why would you use `provided` for the Servlet API in a web application?
