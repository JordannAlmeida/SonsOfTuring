import contextlib
from .config.monitory.otel_config import otel_config
from .config.monitory.otel_ai_config import otel_ai_config
from fastapi import FastAPI, HTTPException, status
from .config.database.postgres_manager import postgres_manager
from .controllers import manage_agents


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application is starting up...")
    otel_config.initialize(app)
    otel_ai_config.initialize()
    await postgres_manager.connect()
    print("FastAPI startup complete.")
    yield
    print("Application is shutting down...")
    otel_config.shutdown()
    await postgres_manager.disconnect()
    print("FastAPI shutdown complete.")

app = FastAPI(lifespan=lifespan)
@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc):
    return {
        "error": {
            "code": exc.status_code,
            "message": str("Unexpected error, call the system manager if it persists...")
        }
    }, status.HTTP_500_INTERNAL_SERVER_ERROR


app.include_router(manage_agents.router)



@app.get("/health")
async def health():
    return {"message": "health!"}
