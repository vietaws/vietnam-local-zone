# Simple App Demo

A lightweight Express.js demo app that displays container info and exposes REST endpoints for users and products.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | HTML page showing container name, IP, and app version |
| GET | `/users` | List all users |
| GET | `/users/:id` | Get user by ID |
| GET | `/products` | List all products |
| GET | `/products/:id` | Get product by ID |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8080` | Port the server listens on |
| `BACKGROUND_COLOR` | `#283E5B` | Background color of the HTML page |

## Run Locally

```bash
npm install
npm start
```

## Run with Docker

```bash
docker build -t simple-app .
docker run -p 8080:8080 simple-app
```

Open [http://localhost:8080](http://localhost:8080)

## Built Docker container image demo:

Image: `vietaws/examples:v1`
