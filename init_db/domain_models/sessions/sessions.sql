CREATE OR REPLACE FUNCTION movies.update_daily_report() RETURNS TRIGGER AS
$$
BEGIN
    IF NEW.state = 'booked'::movies.tickets_state THEN
        IF NOT EXISTS (SELECT calc_date FROM movies.daily_report where calc_date = current_date) THEN
            INSERT INTO movies.daily_report(calc_date, tickets_booked) VALUES (current_date, 1);
        ELSE
            UPDATE movies.daily_report
            SET tickets_booked = tickets_booked + 1
            WHERE calc_date = current_date;
        END IF;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER update_daily_report_trigger
    AFTER UPDATE
    ON movies.tickets
    FOR EACH ROW
EXECUTE PROCEDURE movies.update_daily_report();

CREATE OR REPLACE FUNCTION movies.add_new_hall(new_hall_name VARCHAR, hall_seat_count INT) RETURNS BOOLEAN
AS
$$
BEGIN
    IF EXISTS (SELECT 1 FROM movies.halls h WHERE h.hall_name = new_hall_name) THEN
        RETURN FALSE;
    ELSE
        INSERT INTO movies.halls (hall_name, seat_count) VALUES (new_hall_name, hall_seat_count);
        RETURN TRUE;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION movies.get_halls()
    RETURNS TABLE
            (
                hall VARCHAR
            )
AS
$$
BEGIN
    RETURN QUERY (SELECT hall_name from movies.halls);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION movies.get_bought_tickets_today() RETURNS INT
AS
$$
BEGIN
    RETURN (SELECT tickets_booked from movies.daily_report WHERE calc_date = current_date);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION movies.add_new_session(movie_name VARCHAR, movie_start_time TIMESTAMP, hall VARCHAR,
                                                  session_price DECIMAL) RETURNS BOOLEAN
AS
$$
DECLARE
    current_session_id INT;
BEGIN
    IF NOT EXISTS (SELECT id from movies.movies m where m.title = movie_name) OR
       NOT EXISTS (SELECT hall_name from movies.halls m where m.hall_name = hall) THEN
        RETURN FALSE;
    ELSE
        INSERT INTO movies.sessions (movie_id, start_time, hall_name, price)
        VALUES ((SELECT id from movies.movies m where m.title = movie_name), movie_start_time, hall, session_price)
        RETURNING id INTO current_session_id;
        INSERT INTO movies.tickets (session_id, user_name, place, state)
        SELECT current_session_id,
               NULL,
               generate_series(1, (select seat_count from movies.halls h where h.hall_name = hall)),
               'free'::movies.tickets_state;
        RETURN TRUE;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION movies.get_available_sessions()
    RETURNS TABLE
            (
                id               integer,
                session_hall     character varying,
                movie_title      character varying,
                genre            character varying,
                price            DECIMAL,
                movie_start_time TIMESTAMP,
                actors_list      json
            )
AS
$$
BEGIN
    RETURN QUERY
        with cte as (select session_id
                     from movies.tickets
                              join movies.sessions s on s.id = tickets.session_id
                     where tickets.state = 'free'
                     group by session_id)
        select sessions.id,
               hall_name,
               title,
               genre_name,
               sessions.price,
               sessions.start_time,
               json_agg(a.first_name || ' ' || a.last_name) as actors
        from movies.sessions
                 join movies.movies m on sessions.movie_id = m.id
                 join movies.genres g on g.id = m.genre_id
                 join movies.movies_x_actors mxa on m.id = mxa.movie_id
                 join movies.actors a on a.id = mxa.actor_id
        where sessions.id in (select session_id from cte)
        group by sessions.id, hall_name, title, genre_name, sessions.start_time, sessions.price;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE movies.buy_ticket(cur_session_id INT, visitor VARCHAR)
AS
$$
DECLARE
    ticket_id INT;
BEGIN
    ticket_id := (SELECT id from movies.tickets WHERE session_id = cur_session_id AND state = 'free' LIMIT 1);
    UPDATE movies.tickets t SET state = 'booked', user_name = visitor WHERE t.id = ticket_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION movies.get_tickets(visitor VARCHAR)
    RETURNS TABLE
            (
                id               INT,
                hall             VARCHAR,
                movie_name       VARCHAR,
                genre            VARCHAR,
                session_price    DECIMAL,
                movie_start_time TIMESTAMP,
                movie_actors     json
            )
AS
$$
BEGIN
    RETURN QUERY (select t.id,
                         hall_name,
                         title,
                         genre_name,
                         s.price,
                         s.start_time,
                         json_agg(a.first_name || ' ' || a.last_name) as actors
                  from movies.tickets t
                           join movies.sessions s on s.id = t.session_id
                           join movies.movies m on m.id = s.movie_id
                           join movies.genres g on g.id = m.genre_id
                           join movies.movies_x_actors mxa on m.id = mxa.movie_id
                           join movies.actors a on a.id = mxa.actor_id
                  where user_name = visitor
                  group by t.id, hall_name, title, genre_name, s.start_time, s.price);
END;
$$ LANGUAGE plpgsql;
