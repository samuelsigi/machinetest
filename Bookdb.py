import mysql.connector
import re
import datetime
from _decimal import Decimal
from tabulate import tabulate

databaseobj = mysql.connector.connect(
    host='localhost',
    user='root',
    password='1234',
    database='ProjDB'
)

login = databaseobj.cursor()

login.execute("""
CREATE TABLE IF NOT EXISTS UserSignup(
    UserName VARCHAR(25) PRIMARY KEY,
    Password VARCHAR(20),
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Email VARCHAR(50)
    
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Login(
    Password VARCHAR(20),
    UserName VARCHAR(25),
    FOREIGN KEY (UserName) REFERENCES UserSignup(UserName)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Plan(
    PlanID INT  AUTO_INCREMENT PRIMARY KEY,
    Duration VARCHAR(20),
    Rate INT,
    Details VARCHAR(200)
)
""")





login.execute("""
CREATE TABLE IF NOT EXISTS Genre(
    GenreID INT PRIMARY KEY,
    GenreName VARCHAR(50)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Author(
    AuthorID INT PRIMARY KEY,
    AuthorName VARCHAR(50)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS BookHome(
    BookID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(200),
    GenreID INT,
    AuthorID INT,
    Details VARCHAR(200),
    Ratings DECIMAL(2,1),
    RentPrice DECIMAL(10,2),
    FOREIGN KEY (GenreID) REFERENCES Genre(GenreID),
    FOREIGN KEY (AuthorID) REFERENCES Author(AuthorID)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Rented(
    RentedID INT AUTO_INCREMENT PRIMARY KEY,
    BookID INT,
    Title VARCHAR(40),
    StartDate VARCHAR(30),
    EndDate VARCHAR(30),
    UserName VARCHAR(20),
    FOREIGN KEY (Username) REFERENCES UserSignup(Username),
    FOREIGN KEY (BookID) REFERENCES BookHome(BookID)
)
""")
login.execute("""
    CREATE TABLE IF NOT EXISTS Payment (
        PaymentID INT AUTO_INCREMENT PRIMARY KEY,
        UserID VARCHAR(50),
        Amount DECIMAL(10,2),
        PaymentDate DATE,
        PaymentMethod VARCHAR(255),
        FOREIGN KEY (UserID) REFERENCES Login(Username)
    )
""")
login.execute("""
    CREATE TABLE IF NOT EXISTS Checkout (
        CheckoutID INT AUTO_INCREMENT PRIMARY KEY,
        UserID VARCHAR(50),
        BookID INT,
        PlanID INT,
        Rating VARCHAR(255),
        ReviewDate DATE,
        FOREIGN KEY (UserID) REFERENCES Login(Username),
        FOREIGN KEY (BookID) REFERENCES BookHome(BookID),
        FOREIGN KEY (PlanID) REFERENCES Plan(PlanID)
    )
""")


def register():
    while True:
        try:
            global Username
            print("Register Your Details Here.")
            while True:
                Username = input("Enter Your Username: ")
                if " " not in Username:
                    if re.fullmatch(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,16}$', Username):
                        break
                    else:
                        print("INVALID!!! Username should be an alpha-numeric character of length 5 to 25.")
                else:
                    print("INVALID!!! Username should not contain any space")

            while True:
                Password = input("Enter Your password: ")
                if " " not in Password:
                    if re.fullmatch(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@#$%^&+!_]).{6,16}$', Password):
                        ConfirmPassword = input("Confirm your password: ")
                        if Password == ConfirmPassword:
                            break
                        else:
                            print("Passwords do not match! Please try again.")
                    else:
                        print("""The password should contain at least 
                        - a capital letter
                        - a small letter 
                        - a number
                        - a special character [ @ # $ % ^ & + ! _ ]
                        Also should contain a minimum length of 5 characters to a maximum of 20 characters.""")
                else:
                    print("INVALID!!! Password should not contain space...")

            while True:
                FirstName = input("Enter the first name : ")
                if re.fullmatch("[A-Za-z]{3,25}", FirstName):
                    break
                else:
                    print("INVALID!!!Enter only alphabets of length 3 to 25.")

            while True:
                LastName = input("Enter the last name : ")
                if re.fullmatch("[A-Za-z]{1,25}", LastName):
                    break
                else:
                    print("INVALID!!!Enter only alphabets of length 1 to 25.")
            while True:
                Email = input("Enter the Email: ")
                if re.fullmatch(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", Email):
                    break
                else:
                    print("Invalid Email address! Please enter a valid email.")
            insert_query_reg = ("INSERT INTO UserSignup (UserName, Password, FirstName, LastName,Email) "
                                "VALUES (%s, %s, %s, %s, %s)")
            login.execute(insert_query_reg, (Username, Password, FirstName, LastName, Email))
            insert_query_user = ("INSERT INTO Login (UserName, Password, role) "
                                 "VALUES (%s, %s,'user')")
            login.execute(insert_query_user, (Username, Password))
            databaseobj.commit()
            print("""                            

                        You have successfully registered!!!

                    """)
            startpage()
            exit()
        except Exception as e:
            print(e)
            print("Username already exists.")


def viewbookuser():
    query = 'SELECT b.BookId,b.Title,b.Details,a.AuthorName,g.GenreName,b.Ratings FROM BookHome b INNER JOIN Author a ON b.AuthorID = a.AuthorID INNER JOIN Genre g ON b.GenreID = g.GenreID'
    login.execute(query)
    query_result = login.fetchall()
    if query_result:
        print(tabulate(query_result,
                       headers=["BookID","Title", "Details", "AuthorName", "GenreName", "Ratings"]))
    else:
        print("""                            

                    The Book List is empty.

              """)


def list_of_users():
    query = """
    SELECT l.UserName, u.Email from Login l JOIN UserSignup u ON l.UserName=u.UserName where l.role != "admin"
    """
    login.execute(query)
    query_result = login.fetchall()
    if query_result:
        print(tabulate(query_result, headers=["Username", "Email"]))
    else:
        print("The  list is empty.")
def viewbookadmin():
    query = 'SELECT b.BookID,b.Title,b.Details,a.AuthorID,a.AuthorName,g.GenreID,g.GenreName,b.Ratings FROM BookHome b INNER JOIN Author a ON b.AuthorID = a.AuthorID INNER JOIN Genre g ON b.GenreID = g.GenreID'
    login.execute(query)
    query_result = login.fetchall()
    if query_result:
        print(tabulate(query_result,
                       headers=["BookID", "Title", "Details", "AuthorID", "AuthorName", "GenreID", "GenreName",
                                "Ratings"]))
    else:
        print("""                            

                    The Book List is empty.

              """)

def checkout_plan(plan_id, user_id):
    # Retrieve the selected plan details for pricing
    login.execute("SELECT Rate FROM Plan WHERE PlanID = %s", (plan_id,))
    plan_cost = login.fetchone()[0]

    # Convert plan_cost to Decimal for accurate monetary calculations
    plan_cost = float(plan_cost)

    tax = float('3.50')  # Fixed tax amount
    service_fee = float('5.00')  # Fixed service fee
    total_amount = plan_cost + tax + service_fee

    print(f"\n\nService fee:                                  Rs. {service_fee:.2f}")
    print(f"Tax:                                          Rs. {tax:.2f}")
    print("--------------------------------------------------------------------------")
    print(f"Total Amount (including tax and service fee): Rs. {total_amount:.2f}")

    proceed = input("\n\tProceed to payment? (yes/no): ")

    if proceed.lower() == "yes":
        # Insert payment and checkout details
        payment_method = input("Enter payment method: ")
        payment_date = datetime.date.today()

        # Insert payment record
        insert_payment_query = """
        INSERT INTO Payment (UserID, Amount, PaymentDate, PaymentMethod) 
        VALUES (%s, %s, %s, %s)
        """
        login.execute(insert_payment_query, (user_id, total_amount, payment_date, payment_method))

        # Insert checkout record
        insert_checkout_query = """
        INSERT INTO Checkout (UserID, PlanID, ReviewDate)
        VALUES (%s, %s, %s)
        """
        login.execute(insert_checkout_query, (user_id, plan_id, payment_date))

        databaseobj.commit()
        print("Payment successful! You are now subscribed to the plan.")
    else:
        print("Payment cancelled. Returning to menu.")
def addbook():
    while True:
        try:
            global Title
            print("add your Book details ")
            while True:
                Title = input("Enter Book Title: ")
                if len(Title) >= 3:
                    break
                else:
                    print("Title must have atleast 3 characters")
            while True:
                Details = input("Enter Book Details: ")
                break
            while True:
                AuthorID = input("Enter the AuthorID: ")
                if len(AuthorID) <= 3:
                    break
                else:
                    print("AuthorID cannot be empty!!!")
            while True:
                GenreID = input("Enter the GenreID: ")
                if len(GenreID) <= 3:
                    break
                else:
                    print("GenreID cannot be empty!!!")
            while True:
                Ratings = float(input("Enter the Ratings: "))
                if type(Ratings) == float:
                    break
                else:
                    print("Rating Value cannot be empty!!!")

            insert_query = "INSERT INTO BookHome(Title, Details, AuthorID, GenreID, Ratings) VALUES (%s, %s, %s, %s, %s)"
            login.execute(insert_query, (Title, Details, int(AuthorID), int(GenreID), float(Ratings)))
            databaseobj.commit()
            print("""                            

                    Book Successfully Inserted!!!

                """)
            optionpageadmin()
        except Exception as e:
            print("Book cannot be inserted")


def update():
    global BookID
    query = 'SELECT BookID, Title, GenreId, AuthorId,  Details, Ratings FROM BookHome'
    login.execute(query)
    query_result = login.fetchall()
    if query_result:
        print(tabulate(query_result, headers=["BookID", "Title", "GenreId", "AuthorId", "Details", "Ratings"]))
        while True:
            BookID = input("Enter the Book ID to be edited: ")
            if BookID.isdigit():
                break
            else:
                print("BookID must be a number.")
        query = "SELECT * FROM BookHome WHERE BookID=%s"
        login.execute(query, (BookID,))
        result = login.fetchone()
        if result is None:
            print("INVALID!!! Book ID does not exist...Enter a valid Book ID")
        else:
            print("Details for the selected BookID are: ")
            print("BookID:", result[0], "\nTitle:", result[1], "\nGenreId:", result[2],
                  "\nAuthorId:", result[3], "\nDetails:", result[4], "\nRatings:", result[5])
            while True:
                print("""
                Choose an option you want to update:
                ------------------------------------
                1. Title
                2. Details
                3. Ratings
                4. Go back
                5. Main Menu
                """)
                choice = input("Enter a number from the above list: ")
                if choice == "1":
                    new_title = input("Enter New Title: ")
                    if len(new_title) >= 3:
                        update_book_detail("Title", new_title, BookID)
                    else:
                        print("Title must have atleast 3 characters")
                elif choice == "2":
                    new_details = input("Enter New description: ")
                    update_book_detail("Details", new_details, BookID)
                elif choice == "3":
                    new_rating = input("Enter New Rating: ")
                    update_book_detail("Ratings", new_rating, BookID)
                elif choice == "4":
                    update()
                elif choice == "5":
                    optionpageadmin()
    else:
        print("""                            
        !!!! Book Shelf is empty !!!!

              """)


def update_book_detail(field_name, new_value, BookID):
    query = f"UPDATE BookHome SET {field_name}=%s WHERE BookID=%s"
    login.execute(query, (new_value, BookID))
    databaseobj.commit()
    print(f"""                            
              -----You have successfully updated the {field_name} -----
                                 
          """)


def delete():
    global BookID
    query = 'SELECT BookID, Title, GenreId, AuthorId,  Details, Ratings FROM BookHome'
    login.execute(query)
    query_result = login.fetchall()
    if query_result:
        print(tabulate(query_result, headers=["BookID", "Title", "GenreId", "AuthorId", "Details", "Ratings"]))
        while True:
            BookID = input("Enter the Book ID to be deleted: ")
            if BookID.isdigit():
                break
            else:
                print("BookID must be a number.")
        query = "SELECT * FROM BookHome WHERE BookID=%s"
        login.execute(query, (BookID,))
        result = login.fetchone()
        if result is None:
            print("Book ID does not exist.")
        else:
            while True:
                print("""
                Are you sure you want to delete this book?
                ------------------------------------------
                1. Yes
                2. No
                """)
                choice = input("Enter an option from above choice: ")
                if choice == "1":
                    query = "DELETE FROM BookHome WHERE BookID=%s"
                    login.execute(query, (BookID,))
                    databaseobj.commit()
                    print("""                            

                          ==========  Book  deleted  successfully!! =========

                         """)
                    break

                elif choice == "2":
                    break
                else:
                    print("INVALID!!! Enter an option from above [1 or 2].")
    else:
        print("""                            

                  =======  The Book shelf is empty. ======

              """)


def search_by_name():
    search_title = input("Enter the Name to search: ").title()
    query = "SELECT BookId,Title,Details,Ratings FROM BookHome WHERE Title LIKE %s"
    login.execute(query, ('%' + search_title + '%',))
    query_result = login.fetchall()
    if query_result:
        print(tabulate(query_result, headers=["BookID", "Title", "Details", "Ratings"]))
    else:
        print("""                            

               ========== No book found with that name.!! =========

                 """)


def search_by_genre():
    search_book = input("Enter the Book to search by Genre: ").title()
    query = "SELECT b.BookID,b.Title,a.AuthorName,g.GenreName,b.Ratings FROM BookHome b INNER JOIN Author a ON b.AuthorID = a.AuthorID INNER JOIN Genre g ON b.GenreID = g.GenreID WHERE g.GenreName LIKE %s"

    login.execute(query, ('%' + search_book + '%',))
    query_result = login.fetchall()
    if query_result:
        print(tabulate(query_result, headers=["BookID", "Title", "AuthorName", "GenreName", "Ratings"]))
    else:
        print("""                            

               ==========  No Book found with that Genre..!! =========

                """)


def add_author():
    id = input("Enter author id")
    name = input("Enter author name: ")
    insert_query = "INSERT INTO Author ( AuthorID,AuthorName) VALUES (%s,%s)"
    login.execute(insert_query, (id, name))
    databaseobj.commit()
    print("Author added successfully!")


def view_authors():
    query = "SELECT * FROM Author"
    login.execute(query)
    result = login.fetchall()
    if result:
        print(tabulate(result, headers=["AuthorID", "Name"]))
    else:
        print("No authors found.")


# Function to add a new genre
def add_genre():
    id = input("Enter genre id: ")
    name = input("Enter genre name: ")
    insert_query = "INSERT INTO Genre (GenreID,GenreName) VALUES (%s,%s)"
    login.execute(insert_query, (id, name))
    databaseobj.commit()
    print("Genre added successfully!")


# Function to view all genres
def view_genres():
    query = "SELECT * FROM Genre"
    login.execute(query)
    result = login.fetchall()
    if result:
        print(tabulate(result, headers=["GenreID", "Name"]))
    else:
        print("No genres found.")


def Book():
    global option
    while True:
        print("""
        Choose Option:
        ----------------
        1. View All Books
        2. Add Book
        3. Edit Book
        4. Delete Book
        5. Back
        """)
        option = input("choose an option[1-5]")
        if option == "1":
            viewbookadmin()

        elif option == "2":
            addbook()

        elif option == "3":

            update()

        elif option == "4":

            delete()

        elif option == "5":

            optionpageadmin()



        else:
            print("INVALID!!! Choose options from 1 to 5 only.")


def author():
    global option
    while True:
        print("""
        Choose Option:
        --------------
        1. Add Author
        2. View Author
        3. Back
        """)
        option = input("choose an option[1-3]")
        if option == "1":
            add_author()

        elif option == "2":
            view_authors()

        elif option == "3":

            optionpageadmin()

        else:
            print("INVALID!!! Choose options from 1 to 3 only.")


def genre():
    global option
    while True:
        print("""
        Choose Option:
        --------------
        1. Add Genre
        2. View Genre
        3. Back
        """)
        option = input("choose an option[1-3]")
        if option == "1":
            add_genre()

        elif option == "2":
            view_genres()

        elif option == "3":

            optionpageadmin()

        else:
            print("INVALID!!! Choose options from 1 to 3 only.")


def search():
    global option
    while True:
        print("""
        Choose Option:
        --------------
        1. Search by Title
        2. Search by Genre
        3. Back
        """)
        option = input("choose an option[1-3]")
        if option == "1":
            search_by_name()

        elif option == "2":
            search_by_genre()

        elif option == "3":

            optionpageadmin()

        else:
            print("INVALID!!! Choose options from 1 to 3 only.")


def view_plan():
    query = 'SELECT * FROM Plan'
    login.execute(query)
    query_result = login.fetchall()
    # Checks if there are any results returned by the query.
    if query_result:
        print(
            # Uses the tabulate function from the tabulate library to format the query results into a table.
            tabulate(query_result,
                     headers=["Duration", "Rate", "Details"]))
    else:
        print("The plan is empty.")




def add_plan():
    try:

        Details = input("Enter the Details of the Plan: ")
        if Details == "":
            raise Exception("\nThis Details field cannot be empty !!")
        Duration = input("Enter the duration: ")
        if Duration == "":
            raise Exception("This duration field cannot be empty !!")
        Rate = int(input("Enter the Price: "))
        if Rate != int(Rate):
            raise Exception("Rate cannot be empty !!")

        insert_query = "insert into Plan ( Duration, Rate, Details)values(%s,%s,%s)"
        login.execute(insert_query, (Duration, Rate, Details))
        databaseobj.commit()
        print("You have successfully added new plan... :)")
    except Exception as e:
        print(e)
        add_plan()

def update_plan():
    headers = ["Duration", "Rate", "Details"]
    while True:
        print("""\n                                                   
                    ========= UPDATE CURRENTLY PLANS =========
                                                      """)

        print("""
                                  Choose an option :
                                 1.Continue Updating
                                 2.Go Back""")
        choice = input("""                Enter a number from above list : """)
        if choice == '1':
            index = int(input("Enter the Column no of the Table to Update: "))
            if headers[index - 1]:
                planid = input(f"Enter the Plan ID to update the {headers[index - 1]}: ")
                value = input(f"Enter the {headers[index - 1]} to update: ")
                login.execute(f"Update Plan set {headers[index - 1]}=%s where PlanId=%s", (value, int(planid)))
                databaseobj.commit()
            else:
                print("Invalid number")
            print(f"{headers[index - 1]} updated successfully!!!\n")
        if choice == '2':
            break
def remove_plan():
    while True:
        print("""\n                                                      
                        ======= DISCARD  PLANS =======
                                                      """)

        print("""
                                  Choose an option :
                                 1.Continue Removing
                                 2.Go Back""")
        choice = input("""                Enter a number from above list : """)
        if choice == '1':
            planid = input(f"Enter the Plan ID to remove: ")
            login.execute("DELETE from Plan where PlanId=%s", (int(planid),))
            databaseobj.commit()
            print("Plan has been deleted successfully!!!\n")
        if choice == '2':
            break

def manage_plan():
    while True:
        print("""\n                                         
                    ========== MANAGE PLANS =============
                                         
                      Choose an option :
                     1.Add Plan
                     2.Update Plan
                     3.View all Plan
                     4.Remove Plan
                     5.Go Back""")
        choice = input("""                Enter a number from above list : """)

        if choice == '1':
            add_plan()
        elif choice == '2':
            update_plan()
        elif choice == '3':
            print("""\n
                                                       
                        ============== CURRENT PLANS =============
                                                      
                     """)
            view_plan()
        elif choice == '4':
            remove_plan()
        elif choice == '5':
            optionpageadmin()
        else:
            print("Invalid choice")


def view_payments():
    query = "SELECT * FROM Payment"
    try:
        login.execute(query)
        payments = login.fetchall()


        if payments:
            headers = ["Payment ID", "Customer ID", "Amount", "Date"]
            table = []
            for payment in payments:
                payment_id = payment[0]
                customer_id = payment[1]
                amount = payment[2]
                date = payment[3]
                table.append([payment_id, customer_id, amount, date])

            print("\nPayments:")
            print(tabulate(table, headers=headers, tablefmt="grid"))
        else:
            print("No payments available.")
    except Exception as e:
        print("Error:", e)



from datetime import date, timedelta

def rent_book():
    global Username
    viewbookuser()  # Show the list of books to help the customer choose which one to rent

    book_id = int(input("Enter the BookID of the book you want to rent: "))  # Assuming the user is logged in

    try:
        login.execute("SELECT Title,RentPrice FROM BookHome WHERE BookID = %s", (book_id,))
        result = login.fetchone()
        rent_price = result[1]
        Title = result[0]

        # Convert rent_price to Decimal for accurate monetary calculations
        rent_price = Decimal(rent_price / 100)
        tax = Decimal('3.50')  # Fixed tax amount
        service_fee = Decimal('5.00')  # Fixed service fee

        rentedtill = int(input("Enter days to be rented: "))
        payment_date = date.today()
        end_date = (payment_date + timedelta(days=rentedtill)).strftime("%Y-%m-%d")

        total_amount = (rent_price * Decimal(rentedtill)) + tax + service_fee
        rating = input("Enter your rating (optional): ")
        print(f"Total Amount (including tax and service fee): Rs. {total_amount:.2f}")
        payment_method = input("Enter payment method: ")
        proceed = input("Proceed to payment page....? (yes/no): ")

        if proceed.lower() == "yes":
            # Insert payment record
            insert_payment_query = """
            INSERT INTO Payment (UserID, Amount, PaymentDate, PaymentMethod) 
            VALUES (%s, %s, %s, %s)
            """
            login.execute(insert_payment_query, (Username, total_amount, payment_date, payment_method))

            # Insert checkout record
            insert_checkout_query = """
            INSERT INTO Checkout (UserID, BookID, Rating, ReviewDate)
            VALUES (%s, %s, %s, %s)
            """
            login.execute(insert_checkout_query, (Username, book_id, rating, payment_date))

            # Insert rented book record
            insert_rented_query = """
                        INSERT INTO Rented (BookID,Title,StartDate,EndDate,Username)
                        VALUES (%s, %s, %s, %s, %s)
                        """
            login.execute(insert_rented_query, (book_id, Title, payment_date, end_date, Username))

            databaseobj.commit()
            print("Payment successful! Enjoy your book.")
        else:
            print("Payment cancelled. Returning to menu.")
    except Exception as e:
        print("Error:", e)




from datetime import datetime
def view_rent_book():
    global Username
    print("""\n                                                     
                                             
                =========== VIEW RENTED BOOKS ================= 
                                                       
                       """)

    login.execute(
        'SELECT BookID, Title, StartDate, EndDate FROM Rented WHERE Username=%s', (Username,))
    query_result = login.fetchall()

    if query_result:
        # Dictionary to store the combined results
        combined_books = {}

        for book_id, title, start_date, end_date in query_result:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            if book_id not in combined_books:
                combined_books[book_id] = {"Title": title, "StartDate": start_date, "EndDate": end_date}
            else:
                combined_books[book_id]["StartDate"] = min(combined_books[book_id]["StartDate"], start_date)
                combined_books[book_id]["EndDate"] = max(combined_books[book_id]["EndDate"], end_date)

        # Convert the combined dictionary to a list for tabulate
        combined_list = [(book_id, data["Title"], data["StartDate"].strftime("%Y-%m-%d"), data["EndDate"].strftime("%Y-%m-%d"))
                         for book_id, data in combined_books.items()]

        print(tabulate(combined_list, headers=["BookID", "Title", "StartDate", "EndDate"]))
    else:
        print("No Rented Books. Explore!!")

def optionpageadmin():
    global Username
    while True:
        print(f"""                       
        WELCOME,ADMIN {Username}                          
        ->Choose an option to continue :
        1. Book  
        2. Author
        3. Genre
        4. Search
        5. Plans
        6. List of Users
        7. Log out
        """)
        option = input("Choose an option [1 to 7]: ")
        if option == "1":
            Book()

        elif option == "2":
            author()

        elif option == "3":

            genre()

        elif option == "4":

            search()

        elif option == "5":
            manage_plan()

        elif option == "6":
            list_of_users()



        elif option == "7":
            print("""                            
                       =========== Logged out Success!!! ============

                  """)
            print("")

            startpage()

        else:
            print("INVALID!!! Choose options from 1 to 7 only.")


def optionpageuser():
    global Username
    while True:
        print(f"""                              
                    WELCOME {Username}                   

        ->Choose an option to continue :
        Customer Menu
        1. View Books
        2. View Authors
        3. View Genre
        4. Rent Book
        5. View Rented Books
        6. Search by Name
        7. Search by Genre
        8. View Payment 
        9. Logout
        """)
        option = input("Choose an option [1 to 9]: ")
        if option == "1":
            viewbookuser()
        elif option == "2":
            view_authors()

        elif option == "3":
            view_genres()
        elif option == "4":
            rent_book()
        elif option == "5":
            view_rent_book()
        elif option == "6":
            search_by_name()
        elif option == "7":
            search_by_genre()
        elif option == "8":
            view_payments()
        elif option == "9":
            print("""                            

                   ============= You have successfully logged out ============

                  """)
            print("")
            startpage()
        else:
            print("INVALID!!! Choose options from 1 to 9 only.")


def loginpageuser():
    global Username
    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        Username = input("Enter Username: ")
        if Username == "":
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

        select_query = "SELECT * FROM Login WHERE Username=%s COLLATE utf8mb4_bin AND Password=%s COLLATE utf8mb4_bin and role='user'"
        login.execute(select_query, (Username, Password))
        result = login.fetchone()

        if result is not None:
            print("""                            

                      ============  You have Logged in successful!!! ==========

                     """)
            optionpageuser()
            return
        else:
            attempts += 1
            remaining_attempts = max_attempts - attempts
            if remaining_attempts <= 0:
                print("You have been logged out due to too many failed login attempts.")
                exit()
            else:
                print(f"Incorrect Username or Password. You have {remaining_attempts} attempts left.")


def loginpageadmin():
    global Username
    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        Username = input("Enter Username: ")
        if Username == "":
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

        select_query = "SELECT * FROM Login WHERE Username=%s COLLATE utf8mb4_bin AND Password=%s COLLATE utf8mb4_bin and role='admin'"
        login.execute(select_query, (Username, Password))
        result = login.fetchone()

        if result is not None:
            print("""                            

                   ============= You have Logged in successful!!! ===========

                    """)
            optionpageadmin()
            return
        else:
            attempts += 1
            remaining_attempts = max_attempts - attempts
            if remaining_attempts <= 0:
                print("You have been logged out due to too many failed login attempts.")
                exit()
            else:
                print(f"Incorrect Username or Password. You have {remaining_attempts} attempts left.")


def role():
    while True:
        print("""    

                    LIBRARY MANAGEMENT SYSTEM
                   ============================= 

                    1. Log In As User
                    2. Log In As Admin
                    3. Go Back

                """)
        print("User / Admin / ")
        option = input("Enter the option [1/2/3]: ")
        if option == "1":
            loginpageuser()
        elif option == "2":
            loginpageadmin()
        elif option == "3":
            startpage()
        else:
            print("INVALID!!! Enter only numbers from 1 to 3.")


def startpage():
    while True:
        print("""    

                    LIBRARY MANAGEMENT SYSTEM
                   ===========================
                    
                    1. Log In
                    2. Register
                    3. Exit

                """)
        option = input("Enter the option [1/2/3]: ")
        if option == "1":
            role()
        elif option == "2":
            register()
        elif option == "3":
            print("""                            

                   =========== Thank you for using the LIBRARY. Have a nice day!  =========== 

                  """)
            exit()
        else:
            print("INVALID!!! Enter only numbers from 1 to 3.")


if __name__ == "__main__":
    startpage()
