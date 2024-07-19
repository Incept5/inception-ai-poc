# Supabase Docker

This is a Docker Compose setup for self-hosting Supabase. Follow the steps below to get started.

For more info see this page: https://supabase.com/docs/guides/self-hosting/docker

## Quick Start to get Supabase running

1. Navigate to the supabase docker folder:
   ```
   cd docker/supabase
   ```

2. Copy the example environment file:
   ```
   cp .env.example .env
   ```
   
3. Update the secrets in the .env file to secure your installation:

See: https://supabase.com/docs/guides/self-hosting/docker#securing-your-services


4. Pull the latest images:
   ```
   docker compose pull
   ```

5. Start the services in detached mode:
   ```
   docker compose up -d
   ```

## Accessing Supabase

- Dashboard: http://localhost:8000
  - Default credentials:
    - Username: supabase
    - Password: this_password_is_insecure_and_should_be_updated

- APIs:
  - REST: http://localhost:8000/rest/v1/
  - Auth: http://localhost:8000/auth/v1/
  - Storage: http://localhost:8000/storage/v1/
  - Realtime: http://localhost:8000/realtime/v1/

- Edge Functions: http://localhost:8000/functions/v1/<function-name>
  - The source for your edge functions is located at /code/supabase/functions

- Postgres: 
  - Host: 127.0.0.1
  - Port: 5432
  - Database: postgres
  - User: postgres
  - Default password: your-super-secret-and-long-postgres-password

## Important Security Steps

1. Generate new JWT_SECRET and API keys (ANON_KEY and SERVICE_ROLE_KEY).
2. Update secrets in the .env file, including:
   - POSTGRES_PASSWORD
   - JWT_SECRET
   - SITE_URL
   - SMTP_* (mail server credentials)
3. Update Dashboard authentication credentials:
   - DASHBOARD_USERNAME
   - DASHBOARD_PASSWORD

See the official Supabase documentation for more details: https://supabase.com/docs/guides/self-hosting/docker#securing-your-services

## Managing Services

- Restart services: 
  ```
  docker compose down
  docker compose up -d
  ```

- Stop all services:
  ```
  docker compose stop
  ```

- Uninstall and remove data:
  ```
  docker compose down -v
  rm -rf volumes/db/data/
  ```

## Advanced Configuration

- Email server configuration
- S3 Storage configuration
- Database log level adjustment
- Exposing Postgres to external connections
- Setting up logging with the Analytics server

For detailed instructions on advanced configuration and security best practices, please refer to the official Supabase documentation: https://supabase.com/docs/guides/hosting/docker

Remember to secure your installation before deploying to production!