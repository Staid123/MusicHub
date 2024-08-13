# Music Hub

Music Hub is an application for managing music-related data. This project is built using FastAPI, PostgreSQL, Redis, Celery, and other tools, all orchestrated with Docker.

## Project Structure

- **music_fastapi**: The main FastAPI application service.
- **music_database**: PostgreSQL database for storing application data.
- **pgadmin**: pgAdmin service for managing the PostgreSQL database.
- **redis**: Redis service for caching and as a message broker for Celery.
- **worker**: Celery worker for handling asynchronous tasks.
- **flower**: Celery Flower for monitoring the Celery tasks.

## Prerequisites

Ensure you have the following installed:

- Docker
- Docker Compose

## Setup

### Environment Variables

Create a `.env_db` file for the PostgreSQL database with the following content:

```env
POSTGRES_DB=music_db
POSTGRES_USER=music_user
POSTGRES_PASSWORD=music_password
```
Replace the placeholders with your actual values.

## Build and Start the Services
### Clone this repository:

```bash
git clone https://github.com/yourusername/music-hub.git
cd music-hub
```
### Build and start the services:

```bash
docker-compose up --build
```
### The following services will be available:


* <strong>FastAPI</strong>: http://localhost:8000
* <strong>pgAdmin</strong>: http://localhost:5050
* <strong>Celery Flower</strong>: http://localhost:5555

### Accessing the Services
* <strong>FastAPI</strong>: Access the API documentation at http://localhost:8000/docs.
* <strong>pgAdmin</strong>: Visit http://localhost:5050, and log in with the default credentials:
```
Email: admin@admin.com
Password: admin
```

### Add a new server in pgAdmin to connect to the PostgreSQL database using the following details:
```
Host: music_database
Port: 5432
Username: The value from .env_db
Password: The value from .env_db
```
Celery Flower: Monitor your Celery workers and tasks at http://localhost:5555.