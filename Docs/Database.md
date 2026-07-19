## AI-MOS Database DDL Specification v1.0

### 1. Database Extensions & Global Triggers

Before creating tables, we need to ensure support for automated UUID generation and timestamp updating.

```sql
-- Enable UUID extension for secure, unguessable user identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create a reusable function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

```

---

### 2. Table Creation Scripts

#### Table: `users`

Stores user authentication details and onboarding diagnostic configurations.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    target_role VARCHAR(100) DEFAULT 'Generalist', -- e.g., 'Java Developer (Zoho)'[cite: 1]
    operating_system VARCHAR(50) NOT NULL,        -- e.g., 'Ubuntu', 'Windows', 'macOS'[cite: 1]
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Trigger to auto-update updated_at for users
CREATE TRIGGER update_users_modtime
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

```

#### Table: `curriculum_nodes`

Represents the static learning tree structure. If a parent prerequisite node is deleted, dependent nodes will prevent accidental deletion via `RESTRICT`.

```sql
CREATE TABLE curriculum_nodes (
    id VARCHAR(100) PRIMARY KEY, -- Unique slug like 'java-oop-polymorphism'[cite: 1]
    title VARCHAR(255) NOT NULL,
    phase INT NOT NULL,           -- Phase index number[cite: 1]
    prerequisite_id VARCHAR(100),
    content_path VARCHAR(512) NOT NULL, -- Path to physical Markdown file[cite: 1]
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_prerequisite 
        FOREIGN KEY (prerequisite_id) 
        REFERENCES curriculum_nodes(id) 
        ON DELETE RESTRICT
);

```

#### Table: `user_progress`

Tracks active user progress states through the curriculum. If a user account is deleted, their progress data cascades and deletes automatically.

```sql
CREATE TABLE user_progress (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    node_id VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'locked',
    confidence_score INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_progress_user 
        FOREIGN KEY (user_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE,
        
    CONSTRAINT fk_progress_node 
        FOREIGN KEY (node_id) 
        REFERENCES curriculum_nodes(id) 
        ON DELETE CASCADE,

    CONSTRAINT check_status 
        CHECK (status IN ('locked', 'unlocked', 'in_progress', 'completed')),

    CONSTRAINT check_confidence 
        CHECK (confidence_score BETWEEN 0 AND 10),

    -- Prevents duplicate entries for the exact same user/node pair
    CONSTRAINT unique_user_node 
        UNIQUE (user_id, node_id)
);

-- Trigger to auto-update updated_at for user_progress
CREATE TRIGGER update_user_progress_modtime
    BEFORE UPDATE ON user_progress
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

```

#### Table: `weak_areas`

Tracks recurring weak items flagged by the AI logic evaluator.

```sql
CREATE TABLE weak_areas (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    node_id VARCHAR(100) NOT NULL,
    failure_count INT NOT NULL DEFAULT 1,
    review_status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_weak_user 
        FOREIGN KEY (user_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE,
        
    CONSTRAINT fk_weak_node 
        FOREIGN KEY (node_id) 
        REFERENCES curriculum_nodes(id) 
        ON DELETE CASCADE,

    CONSTRAINT check_review_status 
        CHECK (review_status IN ('active', 'resolved')),

    CONSTRAINT unique_user_weak_node 
        UNIQUE (user_id, node_id)
);

-- Trigger to auto-update updated_at for weak_areas
CREATE TRIGGER update_weak_areas_modtime
    BEFORE UPDATE ON weak_areas
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

```

---

### 3. Database Performance Optimization (Indexes)

Because the AI Gateway will query progress records and current learning weaknesses with every user message, we must implement indexes to ensure sub-millisecond query responses.

```sql
-- Optimize user login and session verification queries
CREATE INDEX idx_users_email ON users(email);

-- Optimize core engine lookups tracking what a user is working on right now
CREATE INDEX idx_user_progress_lookup ON user_progress(user_id, status);

-- Optimize the Research Coach logic when scanning for unresolved user weaknesses
CREATE INDEX idx_weak_areas_active ON weak_areas(user_id, review_status);

```

---