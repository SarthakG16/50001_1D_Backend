DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS poster;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  privilege INTEGER
);

CREATE TABLE poster (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uploader_id TEXT,
  title TEXT,
  status TEXT,

  serialized_image_data TEXT,
  description TEXT,
  link TEXT,
  category TEXT,
  locations TEXT,

  contact_name TEXT,
  contact_email TEXT,
  contact_number TEXT,

  date_submitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  date_approved TIMESTAMP DEFAULT NULL,
  date_posted TIMESTAMP DEFAULT NULL,
  date_expiry TIMESTAMP DEFAULT NULL
);
