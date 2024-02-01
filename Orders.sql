CREATE TABLE orders (
  order_id SERIAL PRIMARY KEY,
  order_date TIMESTAMP NOT NULL,
  email TEXT REFERENCES users(email),
  table_number INTEGER NOT NULL,
  total DECIMAL(8,2) NOT NULL,
  user_id INTEGER REFERENCES users(user_id)
);
