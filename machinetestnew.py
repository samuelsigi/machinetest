import mysql.connector
import random
import string
from datetime import datetime, timedelta
import re


def setup_database_and_tables(connection):
    db_cursor = connection.cursor()
    db_cursor.execute("CREATE DATABASE IF NOT EXISTS HotelReservation;")
    db_cursor.execute("USE HotelReservation;")

    # Updated Guests table with username and password columns
    db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS Guests (
        guest_id INT PRIMARY KEY AUTO_INCREMENT,
        full_name VARCHAR(50) NOT NULL,
        contact_number VARCHAR(15) NOT NULL,
        email_address VARCHAR(50) NOT NULL,
        username VARCHAR(20) NOT NULL UNIQUE,
        hashed_password VARCHAR(255) NOT NULL
    );
    """)

    db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS Accommodation (
        accommodation_id INT PRIMARY KEY AUTO_INCREMENT,
        room_number VARCHAR(10) NOT NULL,
        room_type VARCHAR(20) NOT NULL,
        daily_rate DECIMAL(10, 2) NOT NULL,
        availability ENUM('Occupied', 'Available') DEFAULT 'Available',
        per_hour_rate DECIMAL(10, 2)
    );
    """)

    db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS Reservations (
        reservation_id VARCHAR(10) PRIMARY KEY,
        guest_id INT,
        accommodation_id INT,
        booking_date DATE NOT NULL,
        checkin_date DATE NOT NULL,
        duration_of_stay INT,
        deposit DECIMAL(10, 2),
        tax_amount DECIMAL(10, 2),
        cleaning_fee DECIMAL(10, 2),
        additional_charges DECIMAL(10, 2),
        final_amount DECIMAL(10, 2),
        FOREIGN KEY (guest_id) REFERENCES Guests(guest_id),
        FOREIGN KEY (accommodation_id) REFERENCES Accommodation(accommodation_id)
    );
    """)

    print("Database and tables have been successfully set up.")


# Admin Module
class AdminModule:
    def __init__(self, connection):
        self.connection = connection
        self.admin_users = {
            'administrator': 'password@123'  # Predefined admin credentials
        }

    def login_admin(self, username, password):
        if username in self.admin_users and self.admin_users[username] == password:
            print("Admin successfully logged in!")
            return True
        else:
            print("Incorrect username or password.")
            return False

    def add_accommodation(self, room_number, type_index, daily_rate, per_hour_rate=None):
        # Define the room types
        room_types = ['Single', 'Double', 'Suite', 'Conference Rooms', 'Banquet Halls']
        # Validate the room type index
        if type_index < 1 or type_index > len(room_types):
            print("Invalid room type index.")
            return
        # Get the selected room type
        room_type = room_types[type_index - 1]

        db_cursor = self.connection.cursor()
        insert_query = "INSERT INTO Accommodation (room_number, room_type, daily_rate, per_hour_rate) VALUES (%s, %s, %s, %s)"
        db_cursor.execute(insert_query, (room_number, room_type, daily_rate, per_hour_rate))
        self.connection.commit()
        print("Accommodation added successfully.")

    def list_accommodations(self):
        db_cursor = self.connection.cursor()
        select_query = "SELECT * FROM Accommodation ORDER BY room_type, daily_rate"
        db_cursor.execute(select_query)
        accommodations = db_cursor.fetchall()
        print("List of Accommodations by Type and Rate:")
        print(f"{'ID':<10} {'Room Number':<15} {'Type':<20} {'Daily Rate':<15} {'Status':<20} {'Hourly Rate':<10}")

        for accommodation in accommodations:
            accommodation_id, room_number, room_type, daily_rate, availability, per_hour_rate = accommodation
            print(f"{accommodation_id:<10} {room_number:<15} {room_type:<20} {daily_rate:<15.2f} {availability:<20} {per_hour_rate if per_hour_rate is not None else 'N/A':<10}")

    def list_occupied_accommodations(self):
        db_cursor = self.connection.cursor()
        future_checkin = datetime.now() + timedelta(days=2)
        select_query = "SELECT room_number FROM Accommodation INNER JOIN Reservations ON Accommodation.accommodation_id = Reservations.accommodation_id WHERE checkin_date <= %s"
        db_cursor.execute(select_query, (future_checkin,))
        occupied_rooms = db_cursor.fetchall()
        print("Rooms Occupied Within the Next Two Days:")
        for room in occupied_rooms:
            print(room)

    def find_reservation_by_id(self, reservation_id):
        db_cursor = self.connection.cursor()
        search_query = """SELECT Guests.full_name, Guests.contact_number, Guests.email_address, Accommodation.room_number, Reservations.booking_date, 
                         Reservations.checkin_date, Reservations.duration_of_stay, Reservations.final_amount 
                         FROM Reservations 
                         INNER JOIN Guests ON Reservations.guest_id = Guests.guest_id
                         INNER JOIN Accommodation ON Reservations.accommodation_id = Accommodation.accommodation_id 
                         WHERE Reservations.reservation_id = %s"""
        db_cursor.execute(search_query, (reservation_id,))
        guest_details = db_cursor.fetchone()
        print("Guest Details Based on Reservation ID:")
        print(guest_details)

    def mark_as_available(self, room_number):
        db_cursor = self.connection.cursor()
        update_query = "UPDATE Accommodation SET availability = 'Available' WHERE room_number = %s"
        db_cursor.execute(update_query, (room_number,))
        self.connection.commit()
        print(f"Room {room_number} is now marked as available.")

    def list_available_rooms(self):
        db_cursor = self.connection.cursor()
        select_query = "SELECT room_number FROM Accommodation WHERE availability = 'Available'"
        db_cursor.execute(select_query)
        available_rooms = db_cursor.fetchall()
        print("Available Rooms:")
        for room in available_rooms:
            print(room)

    def save_reservations_to_file(self, file_name="reservations.txt"):
        db_cursor = self.connection.cursor()
        select_query = "SELECT * FROM Reservations"
        db_cursor.execute(select_query)
        all_reservations = db_cursor.fetchall()
        with open(file_name, 'w') as file:
            for reservation in all_reservations:
                file.write(str(reservation) + "\n")
        print(f"All reservation records have been saved to {file_name}.")


class Guest:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def check_name(self, full_name):
        return bool(re.match(r'^[A-Za-z\s]+$', full_name))

    def check_phone(self, contact_number):
        return contact_number.isdigit() and len(contact_number) == 10 and contact_number[0] in '6789'

    def check_email(self, email_address):
        return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email_address))

    def check_user_id(self, username):
        return bool(re.match(r'^[A-Za-z0-9_]+$', username))

    def check_password(self, user_password):
        return len(user_password) >= 8 and any(char.isdigit() for char in user_password) and any(
            char.isalpha() for char in user_password)

    def sign_up(self, full_name, contact_number, email_address, username, user_password):
        if not self.check_name(full_name):
            print("Invalid name. Only letters and spaces are allowed.")
            return
        if not self.check_phone(contact_number):
            print("Invalid phone number. It should be numeric and have 10 digits.")
            return
        if not self.check_email(email_address):
            print("Invalid email format.")
            return
        if not self.check_user_id(username):
            print("Invalid username. It should contain only alphanumeric characters and underscores.")
            return
        if not self.check_password(user_password):
            print("Password must be at least 8 characters long and contain both letters and numbers.")
            return

        cursor = self.db_connection.cursor()
        query = "INSERT INTO Customers (name, phone, email, user_id, password) VALUES (%s, %s, %s, %s, %s)"
        try:
            cursor.execute(query, (full_name, contact_number, email_address, username, user_password))
            self.db_connection.commit()
            print("Guest registered successfully.")
        except mysql.connector.Error as error:
            print(f"Error: {error}")

    def sign_in(self, username, user_password):
        cursor = self.db_connection.cursor()
        query = "SELECT customer_id FROM Customers WHERE user_id = %s AND password = %s"
        cursor.execute(query, (username, user_password))
        result = cursor.fetchone()
        if result:
            print("Login successful!")
            return result[0]  # Return customer_id after successful login
        else:
            print("Invalid username or password.")
            return None

    def display_available_rooms(self):
        cursor = self.db_connection.cursor()
        query = "SELECT room_no, category, rate_per_day FROM Rooms WHERE occupancy_status = 'Unoccupied'"
        cursor.execute(query)
        available_rooms = cursor.fetchall()
        print("Available Rooms:")
        print(f"{'room_no':<10} {'category':<20} {'rate_per_day':<15}")
        print("------------------------------------------------------")
        for room in available_rooms:
            room_no, category, rate_per_day = room
            print(f"{room_no:<10} {category:<20} {rate_per_day:<15.2f}")

    def select_room(self, room_category):
        cursor = self.db_connection.cursor()
        query = "SELECT room_no, rate_per_day, hourly_rate FROM Rooms WHERE category = %s AND occupancy_status = 'Unoccupied'"
        cursor.execute(query, (room_category,))
        available_rooms = cursor.fetchall()

        if not available_rooms:
            print(f"No rooms available in the category '{room_category}' at the moment. Please check other categories.")
            return None

        print(f"Available {room_category} Rooms:")
        print(f"{'room_no':<10} {'rate_per_day':<15} {'hourly_rate':<10}")
        print("---------------------------------------------------------------")
        for room in available_rooms:
            room_no, rate_per_day, hourly_rate = room
            print(f"{room_no:<10} {rate_per_day:<15.2f} {hourly_rate if hourly_rate is not None else 'N/A':<10}")

        selected_room_no = input("Enter the room number you want to book: ")
        return selected_room_no

    def process_payment(self, selected_room_no, guest_id, days_of_stay, advance_payment):
        cursor = self.db_connection.cursor()
        query = "SELECT room_id, rate_per_day, hourly_rate FROM Rooms WHERE room_no = %s"
        cursor.execute(query, (selected_room_no,))
        room = cursor.fetchone()

        room_id = room[0]
        rate_per_day = float(room[1])

        tax_amount = rate_per_day * days_of_stay * 0.18
        housekeeping_fee = 200.00
        additional_charges = 150.00
        final_total = rate_per_day * days_of_stay + tax_amount + housekeeping_fee + additional_charges - advance_payment

        booking_ref = ''.join(random.choices(string.ascii_uppercase, k=2)) + ''.join(random.choices(string.digits, k=5))

        query = """INSERT INTO Bookings (booking_id, customer_id, room_id, date_of_booking, date_of_occupancy, 
                    no_of_days, advance_received, tax, housekeeping_charges, misc_charges, total_amount) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (booking_ref, guest_id, room_id, datetime.now(), datetime.now(), days_of_stay,
                               advance_payment, tax_amount, housekeeping_fee, additional_charges, final_total))
        self.db_connection.commit()

        query = "UPDATE Rooms SET occupancy_status = 'Occupied' WHERE room_no = %s"
        cursor.execute(query, (selected_room_no,))
        self.db_connection.commit()

        print(f"Booking successful! Your Booking Reference is {booking_ref}. Total amount due: {final_total}")

import mysql.connector

# Main Function with login prompt
def main():
    db_connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='1234',
        database='Hotelbooking'
    )

    setup_database_and_tables(db_connection)

    while True:
        print("Welcome to the Hotel Room Booking System!")
        print("1. Admin")
        print("2. Guest")
        print("3. Exit")
        user_choice = int(input("Enter your choice: "))
        if user_choice == 1:
            admin = AdminModule(db_connection)
            # Admin login
            admin_user_id = input("Enter admin username: ")
            admin_password = input("Enter admin password: ")
            if admin.login_admin(admin_user_id, admin_password):
                while True:
                    print("\nAdmin Menu")
                    print("1. Add Room")
                    print("2. Display All Rooms")
                    print("3. View Occupied Rooms")
                    print("4. Search Room by Booking ID")
                    print("5. View Available Rooms")
                    print("6. Mark Room as Available")
                    print("7. Save Records to File")
                    print("8. Exit")
                    admin_choice = int(input("Enter your choice: "))

                    if admin_choice == 1:
                        room_number = input("Enter room number: ")

                        # Display category options
                        print("Select room category:")
                        print("1. Single")
                        print("2. Double")
                        print("3. Suite")
                        print("4. Convention Halls")
                        print("5. Ballrooms")
                        category_choice = int(input("Enter the number corresponding to the category: "))

                        daily_rate = float(input("Enter daily rate: "))
                        optional_hourly_rate = input("Enter hourly rate (optional): ")
                        optional_hourly_rate = float(optional_hourly_rate) if optional_hourly_rate else None

                        admin.add_accommodation(room_number, category_choice, daily_rate, optional_hourly_rate)
                    elif admin_choice == 2:
                        admin.list_accommodations()
                    elif admin_choice == 3:
                        admin.list_occupied_accommodations()
                    elif admin_choice == 4:
                        booking_id = input("Enter booking ID: ")
                        admin.find_reservation_by_id(booking_id)
                    elif admin_choice == 5:
                        admin.list_available_rooms()
                    elif admin_choice == 6:
                        room_number = input("Enter room number to mark as available: ")
                        admin.mark_as_available(room_number)
                    elif admin_choice == 7:
                        admin.save_reservations_to_file()
                    elif admin_choice == 8:
                        break
                    else:
                        print("Invalid choice, please try again.")
        elif user_choice == 2:
            guest = Guest(db_connection)
            while True:
                print("\nGuest Menu")
                print("1. Sign Up")
                print("2. Sign In")
                print("3. Exit")
                guest_choice = int(input("Enter your choice: "))

                if guest_choice == 1:
                    full_name = input("Enter your full name: ")
                    contact_number = input("Enter your phone number: ")
                    email_address = input("Enter your email address: ")
                    username = input("Enter a username: ")
                    user_password = input("Enter a password:")
                    user_password = input("Enter a password: ")
                    guest.sign_up(full_name, contact_number, email_address, username, user_password)
                elif guest_choice == 2:
                    username = input("Enter your username: ")
                    user_password = input("Enter your password: ")
                    guest_id = guest.sign_in(username, user_password)
                    if guest_id:
                        while True:
                            print("\nGuest Options")
                            print("1. View Available Rooms")
                            print("2. Book a Room")
                            print("3. Exit")
                            guest_action = int(input("Enter your choice: "))

                            if guest_action == 1:
                                guest.display_available_rooms()
                            elif guest_action == 2:
                                room_category = input("Enter the room category you want to book: ")
                                selected_room_number = guest.select_room(room_category)
                                if selected_room_number:
                                    number_of_days = int(input("Enter the number of days to book: "))
                                    advance_payment = float(input("Enter advance payment amount: "))
                                    guest.process_payment(selected_room_number, guest_id, number_of_days, advance_payment)
                                else:
                                    print("Booking could not be completed. Please try again with a different category.")
                            elif guest_action == 3:
                                break
                            else:
                                print("Invalid choice, please try again.")
                elif guest_choice == 3:
                    break
                else:
                    print("Invalid choice, please try again.")
        elif user_choice == 3:
            print("System exiting... Thanks for using the system !")
            break
        else:
            print("Invalid choice, please try again.")

            db_connection.close()

if __name__ == "__main__":
    main()

