CREATE TABLE user (
       id SERIAL PRIMARY KEY NOT NULL,
       username TEXT UNIQUE NOT NULL,
       password TEXT NOT NULL
);
       
