# SonsOfTuring - AI Coding Agent Instructions

## Project Overview

**SonsOfTuring** is an agent management platform that creates, configures, and executes AI agents with pluggable LLM backends and tools. The system provides a REST API to retrieve pre-configured agents from PostgreSQL and execute them against various LLM providers (OpenAI, Claude, Gemini, etc.) via the `agno` framework.

### Architecture Layers

```
Controllers (FastAPI routes)
    ↓
Services (business logic, caching)
    ↓
Repository (database queries)
    ↓
Entities (domain models)
```

### Core Components:

Factory (dynamic agent construction) - use agno library to build agents based on configuration recovery from database or cache.

ExecuteAgent (agent execution) - runs the constructed agent with input prompts and returns outputs.

## Practices

- Avoid use unecessary comments in code.
- Follow async programming patterns for I/O operations.
- Use dependency injection for services and repositories.
- Separate concerns: controllers handle HTTP, services handle logic, repositories handle DB access.

### Local Development
```bash
cd backend
uv sync              # Install dependencies
uv run               # Start FastAPI server (auto-reload on file changes)
```

### Docker Stack
```bash
cd runLocal
docker compose up -d --build  # Starts: PostgreSQL, Jaeger (tracing), ClickHouse, OpenLIT
```

**Key Credentials:**
- PostgreSQL: `user:password@localhost:5432/sonsofturing`
- API: `http://localhost:8000/docs` (Swagger UI)
- Jaeger: `http://localhost:16686` (distributed tracing)

**Environment Variables:** Set in Docker Compose:
- `DATABASE_URL`: PostgreSQL DSN
- `OTEL_EXPORTER_OTLP_ENDPOINT`: Jaeger gRPC endpoint (default: `http://jaeger:4317`)
- `APP_NAME`: Identifies service in logs/telemetry

## Core Patterns

### Data Flow: Getting & Executing Agents

1. **Controllers** (`src/controllers/manage_agents.py`):
   - HTTP endpoint handler receives request
   - Creates service via dependency injection (`get_manage_agents_service()`)
   - Calls service method, returns JSON response

2. **Services** (`src/services/manager_agents.py`):
   - Receives repository injected in `__init__`
   - Implements business logic (filtering, caching, transformation)
   - **Caching pattern**: Before DB query, check Redis via `self.cache.exists()` / `self.cache.get()`
   - Returns DTOs (data transfer objects) not entities

3. **Repository** (`src/repository/agents_repository.py`):
   - Direct database access via `postgres_manager.get_connection()`
   - Uses async context managers: `async with connection.transaction():`
   - Returns entity objects (domain models)

4. **Entities** (`src/models/entity/agent_entity.py`):
   - Plain Python classes holding agent/tool data
   - `AgentEntity`: full config (id, name, description, model, tools[], reasoning, type_model)
   - `AgentResumeEntity`: summary (id, name) for list queries

5. **Factory** (`src/core/agets/factory_agent.py`):
   - Builds `agno.Agent` instances from `AgentFactoryInput` DTO
   - Maps `ModelLLM` enum to specific LLM class (Claude, Gemini, etc.)
   - Applies tools and reasoning config
   - Called by service layer for agent execution

### Model Enum: ModelLLM

Located in `src/models/dto/agents/agentLLM.py`. Maps integer DB values to LLM providers:
- `1: GEMINI`, `2: CLAUDE`, `3: OPEANAI`, `4: XAI`, `5: OLLAMA`, `6: GROQ`, `7: DEEPSEEK`

When working with agent configs: use `ModelLLM.get_from_int(model_id)` for DB→enum conversion.

### Database Schema

- **agents**: Core agent metadata (name, description, llm, reasoning, type_model, output_parser)
- **tools**: Tool definitions (name, description, function_caller)
- **agents_tools**: Many-to-many join (agent_id, tool_id)

Queries use async PostgreSQL pool (asyncpg) with parameterized queries (`$1, $2` syntax).

## Common Development Tasks

### Adding a New Agent Endpoint

1. **Service method** in `src/services/manager_agents.py`:
   ```python
   async def get_custom_agents(self, ...):
       result = await self.agents_repository.get_custom_agents(...)
       return [GetCustomAgentResponse(...) for r in result]
   ```

2. **Repository method** in `src/repository/agents_repository.py`:
   ```python
   async def get_custom_agents(self, ...):
       query = "SELECT ... FROM agents WHERE ..."
       async with postgres_manager.get_connection() as conn:
           rows = await conn.fetch(query, ...)
       return [AgentEntity(...) for row in rows]
   ```

3. **Controller route** in `src/controllers/manage_agents.py`:
   ```python
   @router.get("/custom")
   async def get_custom_agents(..., service=Depends(get_manage_agents_service)):
       return await service.get_custom_agents(...)
   ```

4. **Response DTO** in `src/models/ui/agents/manage_agents.py` (Pydantic model)

### Adding a New LLM Provider

1. Import LLM class in `src/core/agets/factory_agent.py` (from `agno.models.*`)
2. Add enum value to `ModelLLM` in `src/models/dto/agents/agentLLM.py`
3. Add elif branch in `FactoryAgent.build_agent()` to instantiate the model
4. Increment max integer value in database enum reference

### Debugging Database Issues

- Check connection pool: `postgres_manager._pool` status
- Raw query execution: use `connection.fetch()` or `connection.cursor()` depending on result size
- Connection context manager ensures cleanup: always use `async with postgres_manager.get_connection()`

## Project Conventions

- **Async everywhere**: All I/O operations (DB, API calls) use async/await
- **Dependency injection**: Services injected in controller via `Depends()`, repository injected in service `__init__`
- **Entity→DTO transformation**: Repositories return entities, services transform to response DTOs
- **Cache-aside pattern**: Check cache before DB query; layer caching in service (not repository)
- **Type hints required**: All function signatures include type annotations (enforced by pyright/mypy)
- **Pydantic for I/O**: Request/response payloads are Pydantic `BaseModel` subclasses in `src/models/ui/`
- **Absolute imports**: Import paths from workspace root (e.g., `from src.config.database...` or relative)

## Testing & Validation

- **Health endpoint**: `GET /health` confirms service is running
- **Swagger docs**: `http://localhost:8000/docs` auto-generated from FastAPI route signatures
- **Observability**: All requests traced via OpenTelemetry to Jaeger; check UI for latency/spans

## Observability & Tracing

OpenTelemetry configured in `src/config/monitory/`:
- **otel_config.py**: Traces FastAPI requests, logs, HTTP calls
- **otel_ai_config.py**: Traces LLM API calls (via OpenLIT integration)

Jaeger UI shows full request traces including agent execution spans. Useful for latency analysis and debugging.
