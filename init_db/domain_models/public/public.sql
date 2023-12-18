CREATE OR REPLACE PROCEDURE public.create_role(role_name TEXT, pass TEXT)
AS
$$
DECLARE
    exec_me TEXT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = role_name) THEN
        exec_me := ('CREATE ROLE ' || role_name || ' WITH LOGIN PASSWORD ' || quote_literal(pass));
        EXECUTE exec_me;
    END IF;
END
$$
LANGUAGE plpgsql;