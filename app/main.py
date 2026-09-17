from database import create_connection, create_table, get_all_cars, add_car


def show_menu():
    print("\nJoe's Garage")
    print("1. View garage")
    print("2. Add a car")
    print("3. Quit")


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
            make = input("Make: ")
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
                photo_path="",
                note=note,
                rating=rating,
                date_added="2026-09-17"
            )
            print("Car added.")
        elif choice == "3":
            break
        else:
            print("That's not a valid option, try again.")

        connection.close()


if __name__ == "__main__":
    main()