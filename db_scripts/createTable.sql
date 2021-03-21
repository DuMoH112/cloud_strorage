CREATE TABLE public.version (version BIGINT DEFAULT 0);

CREATE TABLE logs_bad_query(
    id bigserial PRIMARY KEY,
    query text,
    text_error text,
    time timestamp without time zone
);

CREATE TABLE users
(
    id SERIAL PRIMARY KEY,
    username             varchar(40) not null,
    password             bytea,
    role                 smallint    not null,
    firstname            varchar(50),
    lastname             varchar(50),
    patronymic           varchar(50),
    number_phone         varchar(50),
    last_login           timestamp,
    free_space_kbyte     int,
    size_space_kbyte     int,
    status_active        boolean  default true,
    timer_blocked        timestamp,
    count_filed_password smallint default 0
);

CREATE TABLE users_salt(
    id bigserial PRIMARY KEY,
    user_id int REFERENCES users(id) ON DELETE CASCADE,
    salt text
);