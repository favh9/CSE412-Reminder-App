CREATE TABLE "user" (
  u_id SERIAL PRIMARY KEY,
  u_first_name TEXT,
  u_last_name TEXT,
  u_email TEXT,
  u_password TEXT
);

CREATE TABLE reminder (
  r_id SERIAL PRIMARY KEY,
  r_title TEXT,
  r_description TEXT,
  r_date DATE,
  r_time TIME,
  r_status TEXT,
  user_id INTEGER NOT NULL REFERENCES "user" (u_id),
  notified BOOLEAN DEFAULT FALSE
);

CREATE TABLE category (
  c_id SERIAL PRIMARY KEY,
  c_name TEXT,
  c_color TEXT,
  reminder_id INTEGER NOT NULL REFERENCES reminder (r_id)
);

CREATE TABLE notification (
  n_id SERIAL PRIMARY KEY,
  n_description TEXT,
  n_send_time TIMESTAMP NOT NULL,
  reminder_id INTEGER NOT NULL REFERENCES reminder (r_id)
);

CREATE TABLE file (
  f_id SERIAL PRIMARY KEY,
  f_name TEXT,
  f_type TEXT,
  f_size INTEGER,
  reminder_id INTEGER NOT NULL REFERENCES reminder (r_id)
);
