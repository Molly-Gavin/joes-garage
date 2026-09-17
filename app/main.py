from database import create_connection, create_table, get_all_cars


def show_menu():
    print("\nJoe's Garage")
    print("1. View garage")
    print("2. Quit")


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
            break
        else:
            print("That's not a valid option, try again.")

    connection.close()


if __name__ == "__main__":
    main()