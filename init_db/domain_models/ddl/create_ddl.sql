CREATE OR REPLACE PROCEDURE public.create_ddl()
AS
$$
BEGIN
    EXECUTE 'CREATE SCHEMA IF NOT EXISTS movies';

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'roles_enum') THEN
        CREATE TYPE movies.roles_enum AS ENUM ('cinema_goer', 'employee');
    END IF;

    CREATE TABLE IF NOT EXISTS movies.users
    (
        username   VARCHAR(255) PRIMARY KEY,
        password   VARCHAR(255),
        user_role  movies.roles_enum,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS movies.genres
    (
        id         SERIAL PRIMARY KEY,
        genre_name VARCHAR(255) UNIQUE
    );

    CREATE TABLE IF NOT EXISTS movies.movies
    (
        id           SERIAL PRIMARY KEY,
        title        VARCHAR(255) UNIQUE,
        release_year INT,
        genre_id     INT REFERENCES movies.genres (id) ON DELETE RESTRICT
    );

    CREATE TABLE IF NOT EXISTS movies.actors
    (
        id         SERIAL PRIMARY KEY,
        first_name VARCHAR(255),
        last_name  VARCHAR(255),
        UNIQUE (first_name, last_name)
    );

    CREATE TABLE IF NOT EXISTS movies.movies_x_actors
    (
        movie_id INT,
        actor_id INT,
        PRIMARY KEY (movie_id, actor_id),
        FOREIGN KEY (movie_id) REFERENCES movies.movies (id) ON DELETE CASCADE,
        FOREIGN KEY (actor_id) REFERENCES movies.actors (id) ON DELETE CASCADE
    );

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tickets_state') THEN
        CREATE TYPE movies.tickets_state AS ENUM ('free', 'booked');
    END IF;

    CREATE TABLE IF NOT EXISTS movies.halls
    (
        hall_name  VARCHAR(255) PRIMARY KEY,
        seat_count SMALLINT
    );

    CREATE TABLE IF NOT EXISTS movies.sessions
    (
        id         SERIAL PRIMARY KEY,
        movie_id   INT REFERENCES movies.movies (id) ON DELETE RESTRICT,
        start_time TIMESTAMP,
        hall_name  VARCHAR(255) REFERENCES movies.halls (hall_name) ON DELETE RESTRICT,
        price      DECIMAL
    );

    CREATE TABLE IF NOT EXISTS movies.tickets
    (
        id         SERIAL PRIMARY KEY,
        session_id INT REFERENCES movies.sessions (id) ON DELETE RESTRICT,
        user_name  VARCHAR(255) REFERENCES movies.users (username) ON DELETE RESTRICT,
        place      INT,
        state      movies.tickets_state
    );

    CREATE TABLE IF NOT EXISTS movies.daily_report
    (
        calc_date    DATE PRIMARY KEY,
        tickets_booked INT
    );
END;
$$ LANGUAGE plpgsql;