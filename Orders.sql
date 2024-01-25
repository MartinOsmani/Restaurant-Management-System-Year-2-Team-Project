CREATE TABLE restaurant (
  restaurant_id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  location VARCHAR(255) NOT NULL
);

CREATE TABLE menu_item (
  menu_item_id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  price NUMERIC(10,2) NOT NULL,
  restaurant_id INTEGER NOT NULL REFERENCES restaurant(restaurant_id)
);

CREATE TABLE orders (
  order_id SERIAL PRIMARY KEY,
  order_date TIMESTAMP NOT NULL,
  customer_name VARCHAR(255) NOT NULL,
  table_number INTEGER NOT NULL,
  restaurant_id INTEGER NOT NULL REFERENCES restaurant(restaurant_id)
);

CREATE TABLE order_item (
  order_item_id SERIAL PRIMARY KEY,
  menu_item_id INTEGER NOT NULL REFERENCES menu_item(menu_item_id),
  order_id INTEGER NOT NULL REFERENCES orders(order_id),
  quantity INTEGER NOT NULL
);

CREATE TABLE user_account (
  user_id SERIAL PRIMARY KEY,
  username VARCHAR(255) NOT NULL,
  password VARCHAR(255) NOT NULL,
  role VARCHAR(255) NOT NULL
);
