# main.py is the original command line version of Joe's Garage.
# The web page replaced it for everyday use, but it still works.
# Run it with: python3 app/main.py

from database import (
    create_connection,
    get_all_cars,
    add_car,
    update_car,
    delete_car,
    get_cars_by_date,
    get_cars_by_rating,
    get_cars_by_location,
)
from datetime import date
from identify import identify_make


def show_menu():
    # Print the main menu. This function only prints. It makes no decisions.
    print("\nJoe's Garage")
    print("1. View garage")
    print("2. Add a car")
    print("3. Edit a car")
    print("4. Delete a car")
    print("5. Quit")


def main():
    # Open the database once and keep it open until the program ends.
    connection = create_connection()

    # This loop repeats until the user chooses 5, which runs break.
    while True:
        show_menu()
        # input() waits for the user to type something. It always gives back text.
        choice = input("Choose an option: ")

        if choice == "1":
            # A menu inside the menu, with letters so it looks different from the numbers.
            print("\nView by:")
            print("a. Everything")
            print("b. Newest first")
            print("c. Highest rated first")
            print("d. Location")
            view_choice = input("Choose an option: ")

            if view_choice == "a":
                cars = get_all_cars(connection)
            elif view_choice == "b":
                cars = get_cars_by_date(connection)
            elif view_choice == "c":
                cars = get_cars_by_rating(connection)
            elif view_choice == "d":
                location = input("Search location: ")
                cars = get_cars_by_location(connection, location)
            else:
                print("That's not a valid option, try again.")
                # An empty list keeps the loop below from crashing.
                cars = []

            for car in cars:
                print(car)

        elif choice == "2":
            # The model guesses the make from the photo. Everything else is typed in.
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
                # str() turns today's date into text like 2026-11-20.
                date_added=str(date.today()),
            )
            print("Car added.")

        elif choice == "3":
            # Show every car first, so the user can see the id numbers.
            cars = get_all_cars(connection)
            for car in cars:
                print(car)

            car_id = input("Enter the id of the car to edit: ")

            # Search the list for the car with this id. input() gives text,
            # so str(car[0]) turns the stored number into text for the comparison.
            existing_car = None
            for car in cars:
                if str(car[0]) == car_id:
                    existing_car = car

            if existing_car is None:
                print("No car found with that id.")
            else:
                print("Press Enter to keep the current value.")
                # "or" means: use what was typed, and if nothing was typed, use the old value.
                make = input(f"Make [{existing_car[1]}]: ") or existing_car[1]
                model = input(f"Model [{existing_car[2]}]: ") or existing_car[2]
                year = input(f"Year [{existing_car[3]}]: ") or existing_car[3]
                location = input(f"Where spotted [{existing_car[4]}]: ") or existing_car[4]
                note = input(f"Note [{existing_car[6]}]: ") or existing_car[6]
                rating = input(f"Rating [{existing_car[7]}]: ") or existing_car[7]

                update_car(
                    connection,
                    car_id=car_id,
                    make=make,
                    model=model,
                    year=year,
                    location=location,
                    # Positions 5 and 8 are photo_path and date_added. They stay the same.
                    photo_path=existing_car[5],
                    note=note,
                    rating=rating,
                    date_added=existing_car[8],
                )
                print("Car updated.")

        elif choice == "4":
            cars = get_all_cars(connection)
            for car in cars:
                print(car)

            car_id = input("Enter the id of the car to delete: ")

            car_to_delete = None
            for car in cars:
                if str(car[0]) == car_id:
                    car_to_delete = car

            if car_to_delete is None:
                print("No car found with that id.")
            else:
                # Ask before deleting, because a deleted car cannot be brought back.
                print(f"You are about to delete: {car_to_delete}")
                confirm = input("Type yes to confirm: ")

                # lower() accepts Yes, YES, and yes.
                if confirm.lower() == "yes":
                    delete_car(connection, car_id)
                    print("Car deleted.")
                else:
                    print("Delete canceled.")

        elif choice == "5":
            # break leaves the while loop, which ends the program.
            break

        else:
            print("That's not a valid option, try again.")

    # Close the database once, after the loop ends.
    connection.close()


# This runs main() only when the file is started directly, not when another file imports it.
if __name__ == "__main__":
    main()