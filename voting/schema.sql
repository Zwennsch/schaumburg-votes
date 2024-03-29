DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS vote;
DROP TABLE IF EXISTS admin;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL UNIQUE CHECK(length(username) <= 30),
    password_hash TEXT NOT NULL,
    class TEXT NOT NULL,
    vote_passed INTEGER DEFAULT 0,
    final_course TEXT DEFAULT 'LEER'
);

CREATE TABLE vote (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date_created TEXT NOT NULL,
    first_vote TEXT,
    second_vote TEXT,
    third_vote TEXT,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL UNIQUE CHECK(length(username) <= 30),
    password_hash TEXT NOT NULL
);
    

