DROP TABLE IF EXISTS order_items;


CREATE TABLE order_items (
  order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER REFERENCES orders(order_id),
  menu_item_id INTEGER REFERENCES menu_items(menu_item_id),
  quantity INTEGER NOT NULL
);