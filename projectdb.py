import mysql.connector
from tabulate import tabulate
from datetime import datetime, timedelta
from decimal import Decimal

# Connect to MySQL server
databaseobj = mysql.connector.connect(
    host='localhost',
    user='root',
    password='1234',
    database='HotelmangDB'
)
login = databaseobj.cursor()


# Create Rooms table
login.execute("""
CREATE TABLE IF NOT EXISTS Rooms(
    RoomID INT PRIMARY KEY,
    RoomType VARCHAR(20) NOT NULL,
    CostPerDay DECIMAL(10,2),
    CostPerHour DECIMAL(10,2)
)
""")

# Create PreBooking table
login.execute("""
CREATE TABLE IF NOT EXISTS PreBooking(
    BookingID VARCHAR(5) PRIMARY KEY ,
    CustomerName VARCHAR(30) NOT NULL,
    MobileNumber VARCHAR(10) NOT NULL,
    BookingDate DATE NOT NULL,
    OccupancyDate DATE NOT NULL,
    NumberOfDays INT NOT NULL,
    VacancyDate DATE NOT NULL,
    AdvancePayment DECIMAL(10,2) NOT NULL,
    StayCost DECIMAL(10,2) NOT NULL,
    RoomID INT,
    FOREIGN KEY (RoomID) REFERENCES Rooms(RoomID) ON DELETE CASCADE
)
""")

# Create BookedRoom table
login.execute("""
CREATE TABLE IF NOT EXISTS BookedRoom(
    BookingID VARCHAR(5),
    Status VARCHAR(30) NOT NULL,
    TotalCost DECIMAL(10,2) NOT NULL,
    PaymentPending DECIMAL(10,2) NOT NULL,
    RoomID INT,
    PRIMARY KEY (BookingID, RoomID),
    FOREIGN KEY (BookingID) REFERENCES PreBooking(BookingID) ON DELETE CASCADE,
    FOREIGN KEY (RoomID) REFERENCES Rooms(RoomID) ON DELETE CASCADE
)
""")

# Create Login table
login.execute("""
CREATE TABLE IF NOT EXISTS Login(
    UserName VARCHAR(25) PRIMARY KEY,
    Password VARCHAR(20) NOT NULL
)
""")

def start():
    while True:
        print("""    
                                               
                                                 HOTEL  MANAGEMENT 
                                             

                                                 1. Log In
                                                 2. Exit
                """)
        option = input("Enter the option [1/2]: ")
        if option == "1":
            login_user()
        elif option == "2":
            print("""                            
                                             
                                                    Thank you. Have a nice day!
                                                                     
                  """)
            exit()
        else:
            print("INVALID!!! Enter only numbers from 1/2.")

def login_user():
    global UserName
    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        UserName = input("Enter UserName: ")
        if UserName == "":
            print("This field cannot be empty.")
            attempts += 1
            remaining_attempts = max_attempts - attempts
            if remaining_attempts == 0:
                print("You have been logged out due to too many failed login attempts.")
                return
            print(f"You have {remaining_attempts} attempts left.")
            continue
        Password = input("Enter the password: ")
        if Password == "":
            print("This field cannot be empty.")
            attempts += 1
            remaining_attempts = max_attempts - attempts
            if remaining_attempts == 0:
                print("You have been logged out due to too many failed login attempts.")
                return
            print(f"You have {remaining_attempts} attempts left.")
            continue
        select_query = "SELECT * FROM Login WHERE UserName=%s COLLATE utf8mb4_bin AND Password=%s COLLATE utf8mb4_bin"
        login.execute(select_query, (UserName, Password))
        result = login.fetchone()
        if result is not None:
            print("""                            
                                                           
                                You have Logged in successful!!!
                                                                      
                              """)

            admin()
            return
        else:
            attempts += 1
            remaining_attempts = max_attempts - attempts
            if remaining_attempts <= 0:
                print("You have been logged out due to too many failed login attempts.")
                exit()
            else:
                print(f"Incorrect UserName or Password. You have {remaining_attempts} attempts left.")

def admin():
    global UserName
    while True:
        print(f"""                              
                                                
                                                 WELCOME {UserName}
                                                

                                                ->Choose an option to continue :

                                                1. Room Details
                                                2. Room Status
                                                3. Bookings
                                                4. Log out
        """)

        option = input("Choose an option [1 to 4]: ")
        if option == "1":
            Rooms()
        elif option == "2":
            RoomStatus()
        elif option == "3":
            Bookings()
        elif option == "4":
            print("""                            
                                                
                            You have successfully logged out... Have a nice day!!!
                                                                      
                  """)

            start()
        else:
            print("INVALID!!! Choose options from 1 to 4 only.")

def Rooms():
    while True:
        print("""                            
                                                
                                    ROOM LIST
                                                

                                                Choose the option you want to:

                                                1. Category Wise Room List 
                                                2. All Rooms in Rate/day
                                                3. Add Room 
                                                4. Go Back                       
              """)
        choice = input("Enter a number from the above list: ")
        if choice == "1":
            categorywise()
        elif choice == "2":
            roombyrate()
        elif choice == "3":
            addroom()
        elif choice == "4":
            return
        else:
            print("INVALID!!! Choose options from 1 to 4 only.")

def categorywise():
    try:
        query = """
        SELECT RoomID, 
               RoomType, 
               CASE 
                   WHEN CostPerHour IS NOT NULL THEN CONCAT(CostPerHour, ' per Hour') 
                   ELSE CONCAT(CostPerDay, ' per Day') 
               END AS Cost 
        FROM Rooms
        """
        login.execute(query)
        rooms = login.fetchall()

        if rooms:
            headers = ["Room ID", "Room Type", "Cost"]
            print("Category-wise Room List with Rates:")
            print(tabulate(rooms, headers=headers, tablefmt="grid"))
        else:
            print("No rooms available.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def roombyrate():
    try:
        query = """
        SELECT RoomID,
               RoomType,
               CASE 
                   WHEN CostPerHour IS NOT NULL THEN CostPerHour * 24
                   ELSE CostPerDay 
               END AS CostPerDayEquivalent
        FROM Rooms
        ORDER BY CostPerDayEquivalent ASC
        """
        login.execute(query)
        rooms = login.fetchall()

        if rooms:
            headers = ["Room ID", "Room Type", "Cost per Day Equivalent"]
            print("Rooms in Increasing Order of Rate:")
            print(tabulate(rooms, headers=headers, tablefmt="grid"))
        else:
            print("No rooms available.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def addroom():
    predefined_room_types = ['Single', 'Double', 'Suite', 'BallRoom', 'ConventionHall']
    print("Available Room Types:")
    for i, room_type in enumerate(predefined_room_types, start=1):
        print(f"{i}. {room_type}")

    room_type_option = input("Enter the Room Type (or type 'new' to create a new type): ").strip()

    if room_type_option.lower() == 'new':
        room_type = input("Enter the new Room Type: ").strip()
    elif room_type_option.isdigit() and 1 <= int(room_type_option) <= len(predefined_room_types):
        room_type = predefined_room_types[int(room_type_option) - 1]
    else:
        print("Invalid option. Exiting.")
        return

    cost_per_day = None
    cost_per_hour = None

    if room_type in ['BallRoom', 'ConventionHall']:
        cost_per_hour = input("Enter the Cost per Hour: ").strip()
    else:
        cost_per_day = input("Enter the Cost per Day: ").strip()

    try:
        room_id = int(input("Enter the Room ID (unique): ").strip())
        if cost_per_day:
            cost_per_day = float(cost_per_day)
        if cost_per_hour:
            cost_per_hour = float(cost_per_hour)
        query = """
        INSERT INTO Rooms (RoomID, RoomType, CostPerDay, CostPerHour)
        VALUES (%s, %s, %s, %s)
        """
        login.execute(query, (room_id, room_type, cost_per_day, cost_per_hour))
        databaseobj.commit()

        print("New room added successfully!")
    except ValueError as ve:
        print("Error: Please enter numeric values for Room ID, Cost per Day, and Cost per Hour.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def RoomStatus():
    while True:
        print("""                            
                                               
                                             ROOM STATUS
                                                

                                                Choose the option you want to:

                                                1. Occupied Rooms
                                                2. Unoccupied Rooms  
                                                3. Go Back                       
              """)
        choice = input("Enter a number from the above list: ")
        if choice == "1":
            roomsoccupied()
        elif choice == "2":
            roomsunoccupied()
        elif choice == "3":
            return
        else:
            print("INVALID!!! Choose options from 1 to 3 only.")

def roomsoccupied():
    global headers
    try:
        # Fetch and display all occupied rooms
        query_all = """
        SELECT RoomID, CustomerName, OccupancyDate, VacancyDate 
        FROM PreBooking 
        WHERE DATE(VacancyDate) >= DATE(NOW())
        """
        login.execute(query_all)
        all_rooms = login.fetchall()

        if all_rooms:
            headers = ["Room ID", "Customer Name", "Occupancy Date", "Vacancy Date"]
            print("All Occupied Rooms:")
            print(tabulate(all_rooms, headers=headers, tablefmt="grid"))

            # Ask the user if they want to filter by a specific period
            filter_option = input("\nDo you want to filter by a specific period? (yes/no): ").strip().lower()

            if filter_option == 'yes':
                try:
                    days = int(input("Enter the number of days to check for room occupancy: "))
                    if days <= 0:
                        print("Number of days must be a positive integer.")
                        return

                    # Calculate start and end dates for the filter period
                    today = datetime.now().date()
                    end_date = today + timedelta(days=days)

                    # Query to filter rooms based on occupancy within the specified period
                    query_filtered = """
                    SELECT RoomID, CustomerName, OccupancyDate, VacancyDate 
                    FROM PreBooking 
                    WHERE DATE(VacancyDate) >= DATE(%s)
                      AND DATE(OccupancyDate) <= DATE(%s)
                    """
                    login.execute(query_filtered, (today, end_date))
                    filtered_rooms = login.fetchall()

                    if filtered_rooms:
                        print("\nRooms Occupied for the Specified Days:")
                        print(tabulate(filtered_rooms, headers=headers, tablefmt="grid"))
                    else:
                        print("No rooms are occupied for the specified period.")
                except ValueError:
                    print("Please enter a valid number of days.")
            elif filter_option != 'no':
                print("Invalid option. Exiting.")
        else:
            print("No rooms are currently occupied.")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def roomsoccupied():
    global headers
    try:
        # Fetch and display all occupied rooms
        query_all = """
        SELECT RoomID, CustomerName, OccupancyDate, VacancyDate,
               DATEDIFF(VacancyDate, OccupancyDate) AS DaysOccupied
        FROM PreBooking 
        WHERE DATE(VacancyDate) >= DATE(NOW())
        """
        login.execute(query_all)
        all_rooms = login.fetchall()

        if all_rooms:
            headers = ["Room ID", "Customer Name", "Occupancy Date", "Vacancy Date", "Days Occupied"]
            print("All Occupied Rooms:")
            print(tabulate(all_rooms, headers=headers, tablefmt="grid"))

            # Ask the user if they want to filter by a specific period
            filter_option = input("\nDo you want to filter by a specific period? (yes/no): ").strip().lower()

            if filter_option == 'yes':
                try:
                    days = int(input("Enter the number of days to check for room occupancy: "))
                    if days <= 0:
                        print("Number of days must be a positive integer.")
                        return

                    # Query to filter rooms based on the difference between occupancy and vacancy dates
                    query_filtered = """
                    SELECT RoomID, CustomerName, OccupancyDate, VacancyDate,
                           DATEDIFF(VacancyDate, OccupancyDate) AS DaysOccupied
                    FROM PreBooking 
                    WHERE DATEDIFF(VacancyDate, OccupancyDate) <= %s
                      AND DATE(VacancyDate) >= DATE(NOW())
                    """
                    login.execute(query_filtered, (days,))
                    filtered_rooms = login.fetchall()

                    if filtered_rooms:
                        print("\nRooms Occupied for the Specified Days:")
                        print(tabulate(filtered_rooms, headers=headers, tablefmt="grid"))
                    else:
                        print("No rooms are occupied for the specified period.")
                except ValueError:
                    print("Please enter a valid number of days.")
            elif filter_option != 'no':
                print("Invalid option. Exiting.")
        else:
            print("No rooms are currently occupied.")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



def Bookings():
    while True:
        print("""                            
                                    
                                         BOOKINGS
                                    

                                                Choose the option you want to:

                                                1. New Booking
                                                2. Booking Status
                                                3. View All Bookings
                                                4. Go Back                       
              """)
        choice = input("Enter a number from the above list: ")
        if choice == "1":
            newbooking()
        elif choice == "2":
            bookingstatus()
        elif choice == "3":
            viewbookings()
        elif choice == "4":
            return
        else:
            print("INVALID!!! Choose options from 1 to 4 only.")





def roomsunoccupied():
    try:
        # Query for unoccupied rooms
        query = """
        SELECT r.RoomID, r.RoomType, r.CostPerDay, r.CostPerHour
        FROM Rooms r
        LEFT JOIN PreBooking p ON r.RoomID = p.RoomID
        WHERE p.RoomID IS NULL
           OR (DATE(p.OccupancyDate) > DATE(NOW()) 
           OR DATE(p.VacancyDate) < DATE(NOW()))
        """
        login.execute(query)
        rooms = login.fetchall()

        if rooms:
            headers = ["Room ID", "Room Type", "Cost Per Day", "Cost Per Hour"]
            print("Unoccupied Rooms:")
            print(tabulate(rooms, headers=headers, tablefmt="grid"))
        else:
            print("All rooms are currently occupied.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def newbooking():
    try:
        # Input for other details
        customer_name = input("Enter Customer Name (at least 3 characters): ").strip()
        if len(customer_name) < 3:
            print("Customer name must be at least 3 characters long.")
            return

        mobile_number = input("Enter Mobile Number (exactly 10 digits): ").strip()
        if len(mobile_number) != 10 or not mobile_number.isdigit():
            print("Mobile number must be exactly 10 digits.")
            return

        booking_date = datetime.now()

        # Input for occupancy date
        occupancy_date_str = input("Enter Occupancy Date (YYYY-MM-DD): ").strip()
        try:
            occupancy_date_dt = datetime.strptime(occupancy_date_str, '%Y-%m-%d')
            if occupancy_date_dt.date() < booking_date.date():
                print("Occupancy date cannot be in the past.")
                return
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return

        number_of_days = int(input("Enter Number of Days: ").strip())
        if number_of_days <= 0:
            print("Number of days must be a positive integer.")
            return

        roomsunoccupied()

        room_id = int(input("Enter Room ID: ").strip())
        # Fetch the cost per day for the selected room
        query = "SELECT CostPerDay FROM Rooms WHERE RoomID = %s"
        login.execute(query, (room_id,))
        room_cost = login.fetchone()

        if room_cost is None:
            print("Invalid Room ID.")
            return

        cost_per_day = room_cost[0]

        # Ensure cost_per_day is a Decimal
        if not isinstance(cost_per_day, Decimal):
            cost_per_day = Decimal(cost_per_day)

        # Calculate stay cost and advance payment
        stay_cost = cost_per_day * Decimal(number_of_days)
        advance_payment = stay_cost * Decimal(0.10)

        # Display calculated values
        print(f"Stay Cost: {stay_cost:.2f}")
        print(f"Advance Payment (10% of Stay Cost): {advance_payment:.2f}")

        # Confirm and proceed with booking
        confirm = input("Do you want to proceed with this booking? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("Booking cancelled.")
            return

        # Generate Booking ID
        booking_id = f"ID{str(room_id).zfill(3)}"

        # Calculate vacancy date
        vacancy_date = (occupancy_date_dt + timedelta(days=number_of_days)).strftime('%Y-%m-%d')

        # Insert data into the database
        query = """
        INSERT INTO PreBooking (BookingID, CustomerName, MobileNumber, BookingDate, OccupancyDate, NumberOfDays, VacancyDate, AdvancePayment, StayCost, RoomID)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        login.execute(query, (
            booking_id, customer_name, mobile_number, booking_date.strftime('%Y-%m-%d'), occupancy_date_str, number_of_days, vacancy_date, advance_payment,
            stay_cost, room_id))
        databaseobj.commit()

        print("Booking added successfully!")

    except ValueError as ve:
        print("Error: Please enter valid values.")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")




def bookingstatus():
    query = "SELECT * FROM PreBooking"
    login.execute(query)
    bookings = login.fetchall()

    if bookings:
        headers = ["Booking ID", "Customer Name", "Mobile Number", "Booking Date", "Occupancy Date", "Number of Days", "Vacancy Date", "Advance Payment", "Stay Cost", "Room ID"]
        print("All Bookings:")
        print(tabulate(bookings, headers=headers, tablefmt="grid"))

        booking_id = input("Enter Booking ID: ").strip()
        query = """
            SELECT * FROM PreBooking
            WHERE BookingID = %s
            """
        login.execute(query, (booking_id,))
        booking = login.fetchone()

        if booking:
            headers = ["Booking ID", "Customer Name", "Mobile Number", "Booking Date", "Occupancy Date",
                       "Number of Days", "Vacancy Date", "Advance Payment", "Stay Cost", "Room ID"]
            print("Booking Details:")
            print(tabulate([booking], headers=headers, tablefmt="grid"))
        else:
            print("Booking ID not found.")
    else:
        print("No bookings available.")




def viewbookings():
    query = "SELECT * FROM PreBooking"
    login.execute(query)
    bookings = login.fetchall()

    if bookings:
        headers = ["Booking ID", "Customer Name", "Mobile Number", "Booking Date", "Occupancy Date", "Number of Days", "Vacancy Date", "Advance Payment", "Stay Cost", "Room ID"]
        print("All Bookings:")
        print(tabulate(bookings, headers=headers, tablefmt="grid"))
    else:
        print("No bookings available.")

if __name__ == "__main__":
    start()