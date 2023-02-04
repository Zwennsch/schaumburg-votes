DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS vote;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE vote (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    created TEXT NOT NULL,
    first_vote TEXT,
    second_vote TEXT,
    third_vote TEXT,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

