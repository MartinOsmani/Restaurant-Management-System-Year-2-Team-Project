CREATE TABLE order_items (
  order_item_id SERIAL PRIMARY KEY,
  order_id INTEGER REFERENCES orders(order_id),
  item_price DECIMAL(8,2) NOT NULL,
  quantity INTEGER NOT NULL
);