

# Users
## roles
role_id 1 = Customer
role_id 2 = Kitchen Staff
role_id 3 = Waiter
role_id 4 = Manager

## How to add a user example
INSERT INTO users(name, username, password, role_id, email) 
VALUES ("Mike Hawk", "mikehawk", "0a45e13497b4cc360b44756349d32be2", 4 ,"mikehawk@mcdonalds.com"); -- Md5 for rubixcube1