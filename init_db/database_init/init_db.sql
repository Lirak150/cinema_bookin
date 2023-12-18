CREATE EXTENSION IF NOT EXISTS dblink;

CREATE OR REPLACE FUNCTION public.check_db_exists(db_name TEXT) RETURNS BOOLEAN
AS
$$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_database WHERE datname = db_name) THEN
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE public.create_db(db_name TEXT, role_name TEXT)
AS
$$
BEGIN
    PERFORM dblink_exec('dbname=' || current_database()-- current db
        , 'CREATE DATABASE ' || quote_ident(db_name) || ' WITH OWNER ' || quote_ident(role_name));
END
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE PROCEDURE public.create_role(role_name TEXT, pass TEXT)
AS
$$
DECLARE
    create_role_query   TEXT;
    grant_connect_query TEXT;
    grant_execute_query TEXT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = role_name) THEN
        create_role_query :=
                ('CREATE ROLE ' || quote_ident(role_name) || ' WITH LOGIN PASSWORD ' || quote_literal(pass));
        grant_connect_query := ('GRANT CONNECT ON DATABASE ' || current_database() || ' TO ' || quote_ident(role_name));
        grant_execute_query :=
                ('GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO ' || quote_ident(role_name));
        EXECUTE create_role_query;
        EXECUTE grant_connect_query;
    END IF;
END
$$
    LANGUAGE plpgsql;


