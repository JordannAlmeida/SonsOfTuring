# SonsOfTuring

This is a project to manage agents AI. It permits create agents by configurations setted previouslly.

## Running Locally with Docker

To run the application locally using Docker, follow these steps:

1.  **Navigate to the `runLocal` directory:**
    ```bash
    cd runLocal
    ```

2.  **Build and start the services:**
    ```bash
    docker compose up -d --build
    ```

This will start the following services:

*   **Backend**: The FastAPI application running on `http://localhost:8000`.
*   **PostgreSQL**: The database running on port `5432`.
*   **Jaeger**: The monitoring tool running on `http://localhost:16686`.

### Accessing Services

*   **Backend API**: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
*   **Jaeger UI**: [http://localhost:16686](http://localhost:16686)
*   **Database**: `localhost:5432` (User: `user`, Password: `password`, DB: `sonsofturing`)

### Stopping Services

To stop the services, run:

```bash
docker compose down
```