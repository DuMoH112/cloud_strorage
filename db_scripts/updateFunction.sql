-- Функция выдачи данных пользователя при авторизации
CREATE OR REPLACE FUNCTION get_data_login(username_ varchar)
RETURNS TABLE(
    user_id int,
    user_password bytea,
    user_role smallint,
    user_status_active boolean,
    salt text
) AS
$score$
   DECLARE
       count_failed_pass smallint;
       user_timer_blocked double precision;
   BEGIN
        count_failed_pass = (SELECT count_filed_password FROM users WHERE username=username_);
        user_timer_blocked = (SELECT EXTRACT(EPOCH FROM timer_blocked) FROM users WHERE username=username_);

        IF count_failed_pass >= 5 THEN
            -- 900 seconds is the user lock time
            UPDATE users SET (status_active, count_filed_password, timer_blocked)=(false, 0, to_timestamp(EXTRACT(EPOCH FROM now()) + 900)) WHERE username=username_;
        END IF;

        IF EXTRACT(EPOCH FROM now()) > user_timer_blocked THEN
            UPDATE users SET (status_active, timer_blocked)=(true, null) WHERE username=username_;
        END IF;
        RETURN QUERY
            SELECT
                u.id,
                u.password,
                u.role,
                u.status_active,
                us.salt
            FROM users u
            LEFT JOIN users_salt us on u.id = us.user_id
            WHERE u.username=username_;
   END
$score$
    LANGUAGE plpgsql;
--

select password from users;