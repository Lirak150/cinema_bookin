CREATE OR REPLACE FUNCTION movies.get_actors(current_movie_id INT default null)
    RETURNS TABLE
            (
                id         INT,
                first_name VARCHAR,
                last_name  VARCHAR
            )
AS
$$
BEGIN
    IF current_movie_id IS NOT NULL THEN
        RETURN QUERY (SELECT a.id, a.first_name, a.last_name
                      from movies.actors a
                      WHERE a.id IN (SELECT mxa.actor_id
                                     from movies.movies_x_actors mxa
                                     where mxa.movie_id = current_movie_id));
    ELSE
        RETURN QUERY (SELECT a.id, a.first_name, a.last_name from movies.actors a);
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION movies.get_genres(movie_id INT default null)
    RETURNS TABLE
            (
                id   INT,
                name VARCHAR
            )
AS
$$
BEGIN
    IF movie_id IS NOT NULL THEN
        RETURN QUERY (SELECT g.id, g.genre_name
                      from movies.genres g
                      where g.id IN (SELECT genre_id from movies.movies m where m.id = movie_id));
    ELSE
        RETURN QUERY (SELECT g.id, g.genre_name from movies.genres g);
    END IF;

END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION movies.get_movies()
    RETURNS TABLE
            (
                id           INT,
                title        VARCHAR,
                release_year INT
            )
AS
$$
BEGIN
    RETURN QUERY (SELECT m.id, m.title, m.release_year from movies.movies m);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION movies.add_new_film(film_name VARCHAR, year INT, movie_genre_id INT,
                                               movie_actors_ids INT[]) RETURNS BOOLEAN
AS
$$
DECLARE
    film_id INT;
BEGIN
    IF EXISTS (SELECT id FROM movies.movies m WHERE m.title = film_name) THEN
        RETURN FALSE;
    ELSE
        INSERT INTO movies.movies (title, release_year, genre_id)
        VALUES (film_name, year, movie_genre_id)
        RETURNING id INTO film_id;
        INSERT INTO movies.movies_x_actors (movie_id, actor_id) SELECT film_id, unnest(movie_actors_ids);
        RETURN TRUE;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION movies.add_new_actor(actor_first_name VARCHAR, actor_last_name VARCHAR) RETURNS BOOLEAN
AS
$$
BEGIN
    IF EXISTS (SELECT id
               FROM movies.actors a
               WHERE a.first_name = actor_first_name
                 and a.last_name = actor_last_name) THEN
        RETURN FALSE;
    ELSE
        INSERT INTO movies.actors (first_name, last_name) VALUES (actor_first_name, actor_last_name);
        RETURN TRUE;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION movies.add_new_genre(new_genre VARCHAR) RETURNS BOOLEAN
AS
$$
BEGIN
    IF EXISTS (SELECT id FROM movies.genres g WHERE g.genre_name = new_genre) THEN
        RETURN FALSE;
    ELSE
        INSERT INTO movies.genres (genre_name) VALUES (new_genre);
        RETURN TRUE;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE movies.delete_movie(movie_id INT)
AS
$$
BEGIN
    DELETE FROM movies.movies m where m.id = movie_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE movies.update_movie(current_movie_id INT, new_release_year INT, genre_id_new INT,
                                                actor_ids INT[])
AS
$$
BEGIN
    UPDATE movies.movies
    SET genre_id     = genre_id_new,
        release_year = new_release_year
    WHERE id = current_movie_id;
    DELETE FROM movies.movies_x_actors mxa WHERE mxa.movie_id = current_movie_id;
    INSERT INTO movies.movies_x_actors (movie_id, actor_id) SELECT current_movie_id, unnest(actor_ids);
END;
$$ LANGUAGE plpgsql;


