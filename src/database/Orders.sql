DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
  order_id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_date TIMESTAMP NOT NULL,
  email TEXT REFERENCES users(email),
  table_number INTEGER NOT NULL,
  total DECIMAL(8,2) NOT NULL,
  order_status TEXT,
  user_id INTEGER REFERENCES users(user_id),
  CHECK (order_status IN ('Order confirmed!',
                          'The order is in the kitchen!',
                          'The order is ready and will be with you shortly!',
                          'The order has been delivered!'))
);

