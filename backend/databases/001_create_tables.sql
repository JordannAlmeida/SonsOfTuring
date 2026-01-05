CREATE TABLE IF NOT EXISTS agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    llm int NOT NULL,
    reasoning BOOLEAN NOT NULL,
    type_model VARCHAR(255) NOT NULL,
    output_parser VARCHAR(255),
    instructions TEXT,
    has_storage BOOLEAN DEFAULT FALSE,
    knowledge_collection_name VARCHAR(255),
    knowledge_description TEXT,
    knowledge_top_k INT DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tools (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    function_caller VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agents_tools (
    agent_id int NOT NULL,
    tool_id int NOT NULL,
    PRIMARY KEY (agent_id, tool_id)
);
