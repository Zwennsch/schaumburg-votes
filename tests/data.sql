INSERT INTO user (first_name, last_name, username, password_hash, class, vote_passed)
VALUES
    ('test_first_name','test_last_name','test_username','pbkdf2:sha256:260000$M0BmdefyOnOAiRWP$86fa6ba7259d598a5310ccb875c59cd2b3b334f1ca11030330f37815098c45fa','9a',1),
    ('other_first_name','other_last_name','other_username','pbkdf2:sha256:260000$M0BmdefyOnOAiRWP$86fa6ba7259d598a5310ccb875c59cd2b3b334f1ca11030330f37815098c45fa','8c',0);

INSERT INTO vote (user_id, date_created, first_vote, second_vote, third_vote)
VALUES 
    (1, '2023-03-09', 'Kurs1', 'Kurs4', 'Kurs5');

INSERT INTO admin (id, username, password_hash)
VALUES
    (1, 'test_admin','pbkdf2:sha256:260000$EuDStd4TQnnx8df5$70fd102d2e11298bfadcbccfd7811e1aad9a5b2ab0b26988100bf302001ba4fc');              