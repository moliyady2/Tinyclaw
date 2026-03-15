---
name: docker
description: Manage Docker containers, images, volumes, and networks. Use for container lifecycle operations, image building, compose deployments, and Docker troubleshooting.
metadata: {"nanobot":{"emoji":"🐳","requires":{"bins":["docker"]}}}
---

# Docker Skill

Use `docker` CLI and `docker-compose` for container management. Prefer official Docker commands over third-party tools.

## Quick Reference

| Task | Command |
|------|---------|
| List running containers | `docker ps` |
| List all containers | `docker ps -a` |
| Start/stop/restart | `docker start/stop/restart <container>` |
| View logs | `docker logs -f <container>` |
| Execute command | `docker exec -it <container> <cmd>` |
| Build image | `docker build -t <tag> .` |
| Run container | `docker run -d --name <name> <image>` |

## Container Management

### Lifecycle

```bash
# Run a new container
docker run -d --name myapp -p 8080:80 nginx

# Start/stop existing
docker start myapp
docker stop myapp
docker restart myapp

# Remove container
docker rm myapp
docker rm -f myapp  # force remove running

# View logs
docker logs myapp
docker logs -f myapp --tail 100  # follow last 100 lines
```

### Interactive Access

```bash
# Shell into running container
docker exec -it myapp /bin/sh
docker exec -it myapp bash  # if bash available

# Run one-off command
docker exec myapp ps aux
```

## Image Management

```bash
# List images
docker images

# Build from Dockerfile
docker build -t myapp:1.0 .
docker build -t myapp:1.0 -f Dockerfile.prod .

# Pull from registry
docker pull nginx:alpine
docker pull ghcr.io/user/repo:tag

# Remove image
docker rmi myapp:1.0
docker image prune -f  # remove dangling images
```

## Docker Compose

```bash
# Start services
docker-compose up -d
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f

# Scale service
docker-compose up -d --scale web=3

# Stop and remove
docker-compose down
docker-compose down -v  # remove volumes too

# Validate config
docker-compose config
```

## Troubleshooting

```bash
# Container stats
docker stats

# Inspect container
docker inspect myapp
docker inspect -f '{{.State.Status}}' myapp

# Resource usage
docker system df
docker system prune -f  # clean unused data

# Network debugging
docker network ls
docker network inspect bridge
```

## Common Patterns

### Port Mapping
```bash
docker run -d -p 8080:80 -p 8443:443 nginx
```

### Volume Mounts
```bash
docker run -d -v $(pwd)/data:/app/data -v app_logs:/var/log myapp
```

### Environment Variables
```bash
docker run -d -e DB_HOST=postgres -e DB_PORT=5432 myapp
```

### Restart Policies
```bash
docker run -d --restart unless-stopped myapp
# Options: no, on-failure, always, unless-stopped
```

## Tips

- Use `--rm` for one-off containers: `docker run --rm ubuntu echo hello`
- Use `-d` for background, omit for foreground with logs
- Container names must be unique; use IDs for scripts
- `docker-compose` commands work from compose file directory
