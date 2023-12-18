CREATE OR REPLACE PROCEDURE movies.truncate_all_tables()
AS
$$
BEGIN
    TRUNCATE TABLE movies.tickets CASCADE;
    TRUNCATE TABLE movies.sessions CASCADE;
    TRUNCATE TABLE movies.halls CASCADE;
    TRUNCATE TABLE movies.daily_report CASCADE;

    TRUNCATE TABLE movies.users CASCADE;

    TRUNCATE TABLE movies.genres CASCADE;
    TRUNCATE TABLE movies.movies CASCADE;
    TRUNCATE TABLE movies.actors CASCADE;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION movies.truncate_movies() RETURNS BOOLEAN
AS
$$
BEGIN
    IF NOT EXISTS (SELECT 1 from movies.sessions) THEN
        TRUNCATE TABLE movies.movies CASCADE;
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;