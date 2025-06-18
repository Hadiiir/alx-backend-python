#!/bin/bash

# Build the Docker image
echo "Building Docker image..."
docker build -t messaging-app .

# Run the container
echo "Running container..."
docker run -d -p 8000:8000 --name messaging-app-container messaging-app

# Alternative: Use docker-compose for development
echo "Using docker-compose for development..."
docker-compose up -d

# View logs
echo "Viewing logs..."
docker logs messaging-app-container

# Stop and remove container
echo "To stop and remove container:"
echo "docker stop messaging-app-container"
echo "docker rm messaging-app-container"

# Or with docker-compose
echo "To stop docker-compose:"
echo "docker-compose down"
