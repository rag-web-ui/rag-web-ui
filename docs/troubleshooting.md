# Troubleshooting Guide

## Database Issues

### 1. Database Tables Not Found

If you encounter "table not found" or similar database errors after starting your services, follow these steps:

#### Check if MySQL is Ready

```bash
# Check MySQL container status
docker ps | grep db

# Check MySQL logs
docker logs ragwebui-db-1
```

Make sure you see messages indicating MySQL is running successfully.

#### Check Database Connection

```bash
# Connect to MySQL container
docker exec -it ragwebui-db-1 mysql -u ragwebui -p

# Enter password when prompted: ragwebui

# Then check your database
mysql> USE ragwebui;
mysql> SHOW TABLES;
```

#### Check if Migrations Were Applied

```bash
# Check backend logs for migration messages
docker logs ragwebui-backend-1

# Enter container shell to check migration history
docker exec -it ragwebui-backend-1 sh
alembic history
alembic current

# If migrations need to be applied, run:
alembic upgrade head
exit
```

### 2. Database Connection Issues

#### Environment Variables

Verify your environment variables in `.env` file:

```dotenv
DB_HOST=db
DB_USER=ragwebui
DB_PASSWORD=ragwebui
DB_NAME=ragwebui
```

#### Service Order Problems

If the backend started before MySQL was ready:

```bash
# Restart backend service
docker compose -f docker-compose.yml restart backend
```

## Container and Service Issues

### 1. Container Startup Failures

#### Check Container Status

```bash
# View all container statuses
docker ps -a

# View specific container logs
docker logs <container-id>
```

#### Port Conflicts

```bash
# Check if ports are already in use
netstat -tuln | grep <port-number>

# Alternative port checking command
lsof -i :<port-number>
```

### 2. Network Issues

#### Check Network Connectivity

```bash
# List Docker networks
docker network ls

# Inspect network
docker network inspect ragwebui_default
```

#### Container Communication

```bash
# Test network connectivity between containers
docker exec ragwebui-backend-1 ping db
```

## Application-Specific Issues

### 1. Frontend Issues

#### Static Files Not Loading

- Check if the frontend container is running
- Verify nginx configuration
- Check console for CORS errors

#### Authentication Problems

- Clear browser cache and cookies
- Verify JWT token configuration
- Check backend logs for auth errors

### 2. Backend Issues

#### API Endpoints Not Responding

```bash
# Check backend logs
docker compose -f docker-compose.yml logs backend

# Verify backend health
curl http://localhost/api/health
```

#### Memory Issues

```bash
# Check container resource usage
docker stats

# View backend memory usage
docker exec ragwebui-backend-1 ps aux
```

## Complete Reset Procedure

If you need to start fresh:

1. Stop all containers:

    ```bash
    docker compose -f docker-compose.yml down
    ```

2. Remove volumes to clear database:

    ```bash
    docker compose -f docker-compose.yml down -v
    ```

3. Start everything again:

    ```bash
    docker compose -f docker-compose.yml up -d
    ```

4. Wait a minute for MySQL to initialize, then run migrations:

    ```bash
    docker exec -it ragwebui-backend-1 alembic upgrade head
    ```

## Debugging Tools

### 1. Logging

#### View All Service Logs

```bash
docker compose -f docker-compose.yml logs
```

#### Service-Specific Logs

```bash
docker compose -f docker-compose.yml logs backend
docker compose -f docker-compose.yml logs db
docker compose -f docker-compose.yml logs frontend
```

### 2. Database Debugging

#### Connect to Database CLI

```bash
docker exec -it ragwebui-db-1 mysql -u ragwebui -p
```

#### Backup and Restore

```bash
# Create backup
docker exec ragwebui-db-1 mysqldump -u ragwebui -p ragwebui > backup.sql

# Restore from backup
docker exec -i ragwebui-db-1 mysql -u ragwebui -p ragwebui < backup.sql
```

## Need More Help?

If you're still experiencing issues:

1. Check the application logs for specific error messages
2. Verify all environment variables are correctly set
3. Ensure all required services are running
4. Check system resources (CPU, memory, disk space)
5. Review recent changes that might have caused the issue

Remember: Most services need a few seconds to initialize after starting. If you get connection errors, wait a moment and try again.
