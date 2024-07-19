-- Add scratch schema and scratch_admin user
CREATE SCHEMA scratch;

-- Create scratch_admin user (replace 'password' with a secure password)
CREATE USER scratch_admin WITH PASSWORD 'scratch_password';

-- Grant usage on scratch schema to scratch_admin
GRANT USAGE ON SCHEMA scratch TO scratch_admin;

-- Grant all privileges on all tables in scratch schema to scratch_admin
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA scratch TO scratch_admin;

-- Grant all privileges on all sequences in scratch schema to scratch_admin
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA scratch TO scratch_admin;

-- Set default privileges for scratch_admin in scratch schema
ALTER DEFAULT PRIVILEGES IN SCHEMA scratch
GRANT ALL PRIVILEGES ON TABLES TO scratch_admin;

ALTER DEFAULT PRIVILEGES IN SCHEMA scratch
GRANT ALL PRIVILEGES ON SEQUENCES TO scratch_admin;

-- Revoke access to other schemas from scratch_admin
REVOKE ALL ON SCHEMA public FROM scratch_admin;
REVOKE ALL ON SCHEMA auth FROM scratch_admin;
REVOKE ALL ON SCHEMA storage FROM scratch_admin;

-- Add db_reader user with read-only access to everything
CREATE USER db_reader WITH PASSWORD 'db_reader_password';

-- Grant usage on all schemas to db_reader
GRANT USAGE ON SCHEMA public, auth, storage, scratch TO db_reader;

-- Grant select privilege on all tables in all schemas to db_reader
GRANT SELECT ON ALL TABLES IN SCHEMA public, auth, storage, scratch TO db_reader;

-- Grant select privilege on all sequences in all schemas to db_reader
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public, auth, storage, scratch TO db_reader;

-- Set default privileges for db_reader in all schemas
ALTER DEFAULT PRIVILEGES IN SCHEMA public, auth, storage, scratch
GRANT SELECT ON TABLES TO db_reader;

ALTER DEFAULT PRIVILEGES IN SCHEMA public, auth, storage, scratch
GRANT SELECT ON SEQUENCES TO db_reader;