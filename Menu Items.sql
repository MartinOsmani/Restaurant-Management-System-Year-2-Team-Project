CREATE TABLE menu_items (
  menu_item_id SERIAL PRIMARY KEY,
  menu_item_name VARCHAR(255) NOT NULL,
  menu_item_description TEXT NOT NULL,
  menu_item_price NUMERIC(8,2) NOT NULL
);