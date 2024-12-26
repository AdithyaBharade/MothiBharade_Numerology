-- DROP TABLE IF EXISTS profiles;

-- CREATE TABLE profiles (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     name TEXT NOT NULL,
--     phone_number TEXT NOT NULL,
--     gender TEXT NOT NULL,
--     dob TEXT NOT NULL,
--     result TEXT NOT NULL
-- );
DROP TABLE IF EXISTS profiles;

CREATE TABLE profiles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  phone_number TEXT NOT NULL,
  gender TEXT NOT NULL,
  dob TEXT NOT NULL,
  result TEXT NOT NULL
);



