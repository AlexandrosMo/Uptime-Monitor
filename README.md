# Uptime Monitor

Uptime Monitor is a lightweight, container-ready service for monitoring the availability and response times of HTTP endpoints. It provides a RESTful API for managing monitored targets, a web dashboard for status visualization, and Prometheus-compatible metrics for integration with observability stacks.

## Features

- **Monitor any HTTP endpoint** with customizable intervals
- **Web dashboard** for real-time status and historical checks
- **REST API** for managing targets and retrieving status
- **Prometheus metrics** endpoint for easy integration
- **Docker & Docker Compose** support for easy deployment
- **SQLite** for persistent storage

## Getting Started

### Clone the Repository

```sh
git clone https://github.com/AlexandrosMo/uptime-monitor.git
cd uptime-monitor
```

### Quick Start with Docker

```sh
docker build -t uptime-monitor .
docker run -p 8000:8000 -v $(pwd)/data:/data uptime-monitor
```

Visit [http://localhost:8000/status](http://localhost:8000/status) for the dashboard, or [http://localhost:8000/docs](http://localhost:8000/docs) for the API documentation.

### Using Docker Compose

A sample `docker-compose.yml` is provided:

```sh
docker-compose up --build
```

### Local Development (without Docker)

1. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```
2. Run the application:
    ```sh
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

## API Endpoints

- `GET /status` — Web dashboard
- `GET /docs` — Swagger/OpenAPI documentation
- `GET /metrics` — Prometheus metrics
- `GET /healthz` — Health check
- `POST /targets` — Add a new target
- `GET /targets` — List all targets
- `DELETE /targets/{target_id}` — Remove a target

## Configuration

Configuration is managed via environment variables:

| Variable                | Default              | Description                        |
|-------------------------|----------------------|------------------------------------|
| `PORT`                  | 8000                 | Application port                   |
| `DB_PATH`               | /data/uptime.db      | SQLite database path               |
| `CHECKER_SCAN_INTERVAL` | 5                    | Seconds between checks             |
| `HTTP_TIMEOUT`          | 10                   | HTTP request timeout (seconds)     |
| `LOG_LEVEL`             | INFO                 | Logging level                      |

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Please open issues or pull requests via
