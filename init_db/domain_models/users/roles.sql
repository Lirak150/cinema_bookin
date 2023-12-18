CREATE OR REPLACE FUNCTION movies.register_user(user_name VARCHAR, user_password VARCHAR, current_user_role VARCHAR) RETURNS BOOLEAN
AS
$$
BEGIN
    IF EXISTS (SELECT u.username FROM movies.users u WHERE u.username = user_name) then
        RETURN FALSE;
    ELSE
        INSERT INTO movies.users (username, password, user_role)
        VALUES (user_name, user_password, current_user_role::roles_enum);
        RETURN TRUE;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION movies.get_user_role(user_name VARCHAR) RETURNS VARCHAR
AS
$$
BEGIN
    RETURN (SELECT user_role from movies.users u where u.username = user_name);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION movies.login_user(user_name VARCHAR, user_password VARCHAR) RETURNS BOOLEAN
AS
$$
DECLARE
    correct_password VARCHAR;
BEGIN
    correct_password := (select password from movies.users u where u.username = user_name);
    IF correct_password IS NULL THEN
        RETURN FALSE;
    ELSE
        IF user_password = correct_password THEN
            RETURN TRUE;
        ELSE
            RETURN FALSE;
        END IF;
    END IF;
END;
$$ LANGUAGE plpgsql;