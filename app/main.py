from database import create_connection, create_table, get_all_cars, add_car, update_car, delete_car
from datetime import date
from identify import identify_make


def show_menu():
    print("\nJoe's Garage")
    print("1. View garage")
    print("2. Add a car")
    print("3. Edit a car")
    print("4. Delete a car")
    print("5. Quit")


def main():
    connection = create_connection()
    create_table(connection)

    while True:
        show_menu()
        choice = input("Choose an option: ")

        if choice == "1":
            cars = get_all_cars(connection)
            for car in cars:
                print(car)
        elif choice == "2":
            photo_path = input("Path to the photo: ")
            make = identify_make(photo_path)
            print(f"Detected make: {make}")

            model = input("Model: ")
            year = input("Year: ")
            location = input("Where did you spot it: ")
            note = input("Note: ")
            rating = input("Rating (1 to 5): ")

            add_car(
                connection,
                make=make,
                model=model,
                year=year,
                location=location,
                photo_path=photo_path,
                note=note,
                rating=rating,
                date_added=str(date.today())
            )
            print("Car added.")
        elif choice == "3":
            cars = get_all_cars(connection)
            for car in cars:
                print(car)

            car_id = input("Enter the id of the car to edit: ")

            existing_car = None
            for car in cars:
                if str(car[0]) == car_id:
                    existing_car = car

            make = input("Make: ")
            model = input("Model: ")
            year = input("Year: ")
            location = input("Where did you spot it: ")
            note = input("Note: ")
            rating = input("Rating (1 to 5): ")

            update_car(
                connection,
                car_id=car_id,
                make=make,
                model=model,
                year=year,
                location=location,
                photo_path="",
                note=note,
                rating=rating,
                date_added=existing_car[8]
            )
            print("Car updated.")
        elif choice == "4":
            cars = get_all_cars(connection)
            for car in cars:
                print(car)

            car_id = input("Enter the id of the car to delete: ")
            delete_car(connection, car_id)
            print("Car deleted.")
        elif choice == "5":
            break
        else:
            print("That's not a valid option, try again.")

    connection.close()


if __name__ == "__main__":
    main()