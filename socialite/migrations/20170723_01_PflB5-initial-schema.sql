CREATE TABLE users (
       uid SERIAL PRIMARY KEY NOT NULL,
       username TEXT UNIQUE NOT NULL,  -- maybe index this
       password TEXT NOT NULL
);
