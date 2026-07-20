"""
AI-MOS — Migration 005: GFG Curriculum Expansion (Phases 7-10 + Gap Fills)
================================================-------------------------
Revision ID : 005
Revises     : 004
Created     : 2026-07-20

Changes:
  - Seeds 7 phase 2-4 gap fill nodes
  - Seeds 8 Phase 7 nodes (Build Tools & Database)
  - Seeds 6 Phase 8 nodes (Design Patterns)
  - Seeds 7 Phase 9 nodes (System Design & Microservices)
  - Seeds 9 Phase 10 nodes (DSA for Interviews)
  - Links prerequisites in a continuous curriculum graph
"""

from alembic import op
import sqlalchemy as sa

revision: str = "005"
down_revision: str | None = "004"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # 1. Phase 2-4 Gap Fills
    op.execute("""
        INSERT INTO curriculum_nodes (id, title, phase, prerequisite_id, content_path)
        VALUES
          ('java-core-strings', 'Java String Class & Pool', 2, 'java-core-interface', 'curriculum/phase-2/06-strings.md'),
          ('java-core-io-streams', 'Java I/O Streams & NIO', 2, 'java-core-strings', 'curriculum/phase-2/07-io-streams.md'),
          ('java-core-operators', 'Operators & Bitwise Logic', 2, 'java-core-io-streams', 'curriculum/phase-2/08-operators.md'),
          ('java-collections-treeset', 'TreeMap & TreeSet Internals', 3, 'java-collections-hashmap', 'curriculum/phase-3/05-treemap-treeset.md'),
          ('java-collections-deque', 'ArrayDeque & PriorityQueue', 3, 'java-collections-treeset', 'curriculum/phase-3/06-deque-priority-queue.md'),
          ('java-core-multithreading', 'Multithreading & Concurrency Deep Dive', 4, 'java-advanced-concurrency', 'curriculum/phase-4/07-multithreading-deep.md'),
          ('java-advanced-servlet', 'Servlets, JSP & Filter Chain', 4, 'java-core-multithreading', 'curriculum/phase-4/08-servlet-jsp.md')
        ON CONFLICT (id) DO NOTHING;
    """)

    # Link phase 6 end to phase 7
    # Phase 7 — Build Tools & Database (8 nodes)
    op.execute("""
        INSERT INTO curriculum_nodes (id, title, phase, prerequisite_id, content_path)
        VALUES
          ('build-maven', 'Maven — POM, Scopes & Lifecycle', 7, 'spring-deployment', 'curriculum/phase-7/01-maven.md'),
          ('build-gradle', 'Gradle — Build Scripts & Plugins', 7, 'build-maven', 'curriculum/phase-7/02-gradle.md'),
          ('db-sql-fundamentals', 'SQL Fundamentals — Joins & Indexes', 7, 'build-gradle', 'curriculum/phase-7/03-sql-fundamentals.md'),
          ('db-sql-advanced', 'Advanced SQL — Transactions & Procedures', 7, 'db-sql-fundamentals', 'curriculum/phase-7/04-sql-advanced.md'),
          ('db-nosql-mongodb', 'MongoDB — Aggregation & Document DBs', 7, 'db-sql-advanced', 'curriculum/phase-7/05-nosql-mongodb.md'),
          ('db-hibernate-orm', 'Hibernate ORM — Mapping & Caching', 7, 'db-nosql-mongodb', 'curriculum/phase-7/06-hibernate-orm.md'),
          ('db-jpa-deep', 'JPA Deep Dive & N+1 Problem', 7, 'db-hibernate-orm', 'curriculum/phase-7/07-jpa-deep.md'),
          ('logging-slf4j', 'Logging — SLF4J, Logback & Log4j2', 7, 'db-jpa-deep', 'curriculum/phase-7/08-logging.md')
        ON CONFLICT (id) DO NOTHING;
    """)

    # Phase 8 — Design Patterns (6 nodes)
    op.execute("""
        INSERT INTO curriculum_nodes (id, title, phase, prerequisite_id, content_path)
        VALUES
          ('patterns-creational', 'Creational Patterns — Factory & Builder', 8, 'logging-slf4j', 'curriculum/phase-8/01-patterns-creational.md'),
          ('patterns-structural', 'Structural Patterns — Adapter & Decorator', 8, 'patterns-creational', 'curriculum/phase-8/02-patterns-structural.md'),
          ('patterns-behavioral', 'Behavioral Patterns — Strategy & Observer', 8, 'patterns-structural', 'curriculum/phase-8/03-patterns-behavioral.md'),
          ('patterns-solid', 'SOLID Principles in Practice', 8, 'patterns-behavioral', 'curriculum/phase-8/04-solid.md'),
          ('patterns-ddd', 'Domain-Driven Design (DDD) Basics', 8, 'patterns-solid', 'curriculum/phase-8/05-ddd.md'),
          ('patterns-clean-arch', 'Clean Architecture & Hexagonal Arch', 8, 'patterns-ddd', 'curriculum/phase-8/06-clean-arch.md')
        ON CONFLICT (id) DO NOTHING;
    """)

    # Phase 9 — System Design & Microservices (7 nodes)
    op.execute("""
        INSERT INTO curriculum_nodes (id, title, phase, prerequisite_id, content_path)
        VALUES
          ('sysdesign-fundamentals', 'System Design — Scalability & CAP', 9, 'patterns-clean-arch', 'curriculum/phase-9/01-sysdesign-fundamentals.md'),
          ('sysdesign-caching', 'Caching — Redis & Invalidation', 9, 'sysdesign-fundamentals', 'curriculum/phase-9/02-caching.md'),
          ('sysdesign-messaging', 'Message Queues — Kafka & Event-Driven', 9, 'sysdesign-caching', 'curriculum/phase-9/03-messaging.md'),
          ('microservices-intro', 'Microservices Patterns & API Gateway', 9, 'sysdesign-messaging', 'curriculum/phase-9/04-microservices-intro.md'),
          ('microservices-spring-cloud', 'Spring Cloud — Eureka & Config Server', 9, 'microservices-intro', 'curriculum/phase-9/05-spring-cloud.md'),
          ('microservices-resilience', 'Resilience4j — Circuit Breaker & Retry', 9, 'microservices-spring-cloud', 'curriculum/phase-9/06-resilience.md'),
          ('microservices-docker-k8s', 'Kubernetes Deployment for Microservices', 9, 'microservices-resilience', 'curriculum/phase-9/07-docker-k8s.md')
        ON CONFLICT (id) DO NOTHING;
    """)

    # Phase 10 — DSA for Interviews (9 nodes)
    op.execute("""
        INSERT INTO curriculum_nodes (id, title, phase, prerequisite_id, content_path)
        VALUES
          ('dsa-arrays-strings', 'DSA — Arrays, Strings & Two Pointer', 10, 'microservices-docker-k8s', 'curriculum/phase-10/01-dsa-arrays-strings.md'),
          ('dsa-linkedlist', 'DSA — LinkedList Patterns', 10, 'dsa-arrays-strings', 'curriculum/phase-10/02-dsa-linkedlist.md'),
          ('dsa-stack-queue', 'DSA — Stack, Queue & Monotonic Stack', 10, 'dsa-linkedlist', 'curriculum/phase-10/03-dsa-stack-queue.md'),
          ('dsa-trees', 'DSA — Trees & Binary Search Tree', 10, 'dsa-stack-queue', 'curriculum/phase-10/04-dsa-trees.md'),
          ('dsa-graphs', 'DSA — Graphs BFS, DFS & Dijkstra', 10, 'dsa-trees', 'curriculum/phase-10/05-dsa-graphs.md'),
          ('dsa-dp-intro', 'DSA — Dynamic Programming Basics', 10, 'dsa-graphs', 'curriculum/phase-10/06-dsa-dp-intro.md'),
          ('dsa-dp-advanced', 'DSA — Advanced DP Patterns', 10, 'dsa-dp-intro', 'curriculum/phase-10/07-dsa-dp-advanced.md'),
          ('dsa-sorting-searching', 'DSA — Sorting Algorithms & Binary Search', 10, 'dsa-dp-advanced', 'curriculum/phase-10/08-dsa-sorting.md'),
          ('dsa-interview-patterns', 'DSA — Top 10 Master Interview Patterns', 10, 'dsa-sorting-searching', 'curriculum/phase-10/09-dsa-patterns.md')
        ON CONFLICT (id) DO NOTHING;
    """)


def downgrade() -> None:
    op.execute("DELETE FROM curriculum_nodes WHERE phase IN (7, 8, 9, 10);")
    op.execute("DELETE FROM curriculum_nodes WHERE id IN ('java-core-strings', 'java-core-io-streams', 'java-core-operators', 'java-collections-treeset', 'java-collections-deque', 'java-core-multithreading', 'java-advanced-servlet');")
