INSERT INTO user (first_name, last_name, username, password_hash, class, vote_passed)
VALUES
    ('test_first_name','test_last_name','test_username','pbkdf2:sha256:260000$M0BmdefyOnOAiRWP$86fa6ba7259d598a5310ccb875c59cd2b3b334f1ca11030330f37815098c45fa','8a',1),
    ('other_first_name','other_last_name','other_username','pbkdf2:sha256:260000$M0BmdefyOnOAiRWP$86fa6ba7259d598a5310ccb875c59cd2b3b334f1ca11030330f37815098c45fa','8a',0);

INSERT INTO vote (user_id, date_created, first_vote, second_vote, third_vote)
VALUES 
    (1, '2023-03-09', 'Kurs1', 'Kurs2', 'Kurs3');