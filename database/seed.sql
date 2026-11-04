-- Sample data for local PostgreSQL and the Docker database.
-- Add your own rows to the INSERT lists below. See "Load your own data" in the
-- README for how to run this file.
--
-- Safe to run repeatedly: existing tables are kept, and any row whose id (or,
-- for users, email) already exists is skipped, so editing a row here does not
-- update a copy that is already in the database.
--
-- Demo data only. Every sample user's password is: Password123!

\set ON_ERROR_STOP on
SET client_encoding = 'UTF8';

BEGIN;

-- Docker runs this file before the API has started, so the tables may not exist
-- yet. These must match database/models.py.
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR,
    description VARCHAR
);
CREATE INDEX IF NOT EXISTS ix_articles_id ON articles (id);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    hashed_password VARCHAR NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_users_id ON users (id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email);

-- Give each new row the next id number. A fixed id is what stops a row being
-- inserted again on the next run.

-- Articles:
INSERT INTO articles (id, title, description) VALUES
    (1, 'Getting started with FastAPI', 'Build a small REST API in Python.'),
    (2, 'Docker Compose basics', 'Run the API and its database together.'),
    (3, 'Giới thiệu về PostgreSQL', 'Những khái niệm cơ bản về cơ sở dữ liệu.'),
    (4, 'SQLAlchemy sessions explained', 'How sessions track and commit your changes.'),
    (5, 'Writing tests with pytest', 'Test API endpoints with fixtures and a test client.'),
    (6, 'CI with GitHub Actions', 'Run your tests automatically on every push.'),
    (7, 'Storing passwords safely', 'Why passwords are salted and hashed, never saved as text.'),
    (8, 'Validating data with Pydantic', 'Reject bad requests before they reach the database.'),
    (9, 'Tối ưu truy vấn với index', 'Khi nào nên tạo index và khi nào không cần.'),
    (10, 'Triển khai ứng dụng bằng Docker', 'Đóng gói ứng dụng thành image và chạy trên máy chủ.')
ON CONFLICT DO NOTHING;

-- Users: hashed_password must be a hash, or the account cannot log in once login
-- exists. Run this from the project root to make one:
--   python -c "from utils.passwords import hash_password; print(hash_password('your-password'))"
INSERT INTO users (id, email, name, hashed_password) VALUES
    (1, 'alice@example.com', 'Alice Nguyen', 'scrypt$16384$8$1$1v4nY2ZIZytBXYdi8XWOJA==$3LQkpK8CKifKUgDVvHvTzAhekYuad/T0HIAOAYJDa8nWvfsJr1f4bSBLgXon6KRwIgpLqdLSahF+uRv+/Py48Q=='),
    (2, 'bob@example.com', 'Bob Tran', 'scrypt$16384$8$1$H40eJBk+puOP01GaqS3ajw==$uyLquYV4iyH0ZQHU1j68xQlWECUuXyzKEngi5zfsiduuQlyVv3X6MOp2ExMx2a7PkV+s+wMlVNEOymqWdxCong=='),
    (3, 'chi@example.com', 'Chi Le', 'scrypt$16384$8$1$y/rw5nn5vRtHy27BVH2Exg==$CrJrRqDlIBaAoy8Wexg/4p30ln8yNa12adgGYs8jjxuc/lcB6Pfk+A2iwuGTOFvgxQwuKdrPowROiwjcnR0cJg=='),
    (4, 'dung@example.com', 'Dung Pham', 'scrypt$16384$8$1$OqM55dsCzTZdflc+48M1ow==$nUUV2LDzKmNnjC96edMa4z8v3482zINadiu7Ci5UuyvhSacZDMkrrTEpNTS5oRjLPN+uIjnF5cyqv0SseT/k5Q=='),
    (5, 'emma@example.com', 'Emma Vo', 'scrypt$16384$8$1$BO9YKaBDjmvge3/veVVoDA==$ZMJQsC4zrzrGOd4Q/ZFKp7GdA8nhqqFgFgEsdMm9+NpIswpqQvNfcVDc0bE95+xzMGxCWMBX9anK1aNa1Uq+dg==')
ON CONFLICT DO NOTHING;

-- Rows inserted with a fixed id do not advance the id counters, so move them past
-- the highest id. Otherwise the API's next insert would reuse an id and fail.
SELECT setval(pg_get_serial_sequence('articles', 'id'), (SELECT MAX(id) FROM articles));
SELECT setval(pg_get_serial_sequence('users', 'id'), (SELECT MAX(id) FROM users));

COMMIT;
