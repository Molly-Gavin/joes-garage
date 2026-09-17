from database import create_connection, create_table, get_all_cars

connection = create_connection()
create_table(connection)

cars = get_all_cars(connection)
for car in cars:
    print(car)

connection.close()