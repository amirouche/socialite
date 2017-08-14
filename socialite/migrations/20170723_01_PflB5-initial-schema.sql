CREATE TABLE users (
       uid SERIAL PRIMARY KEY NOT NULL,
       username TEXT UNIQUE NOT NULL,  -- maybe index this
       password TEXT NOT NULL,
       bio TEXT NOT NULL
);

CREATE TABLE wiki (
       uid SERIAL PRIMARY KEY NOT NULL,
       title TEXT NOT NULL,
       body TEXT NOT NULL,
       created_at TIMESTAMP NOT NULL -- maybe index this
);

CREATE INDEX wiki_title_index ON wiki (title);
