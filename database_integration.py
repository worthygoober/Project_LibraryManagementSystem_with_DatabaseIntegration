import re

import mysql.connector
from mysql.connector import Error

def connect_database():
    db_name = "library_management_db"
    user = "root"
    password = "Doit4Pixie&Haribo"
    host = "localhost"

    try:
        conn = mysql.connector.connect(
            database = db_name,
            user = user,
            password = password,
            host = host
        )
        print("Connected to MySQL database successfully.")
        return conn
    except Error as e:
        print(f"Error: {e}")
        return None
    
def book_operations():
    while True:          
        print("\nBook Operations:")
        print("1. Add a new book\n2. Borrow a book\n3. Return a book\n4. Search for a book\n5. Display all books\n6. Return to menu")
        book_op_choice = input("Enter the operation to perform (1-6): ")
        if book_op_choice == "6":
            break
        try:
            if book_op_choice == "1":
                add_book()
            elif book_op_choice == "2":
                borrow_book()
            elif book_op_choice == "3":
                return_borrowed_book()
            elif book_op_choice == "4":
                search_for_book()
            elif book_op_choice == "5":
                display_all_books()
            else:
                print("Invalid choice. Please try again.")
        except Exception as e:
            print(f"Error: {e}")
    
def add_book():
    title = input("Enter the book's title: ")
    author_name = input("Enter the author's name: ")
    if not is_valid_name(author_name):
        print("Invalid name. Please enter only letters and spaces.")
        return
    isbn = input("Enter the book's ISBN: ")
    publication_date = input("Enter the publication date (YYYY-MM-DD): ")
    if not is_valid_date(publication_date):
        print("Invalid date format. Please enter the publication date in the format: YYYY-MM-DD.")
        return
    conn = connect_database()
    if conn is not None:
        try:
            cursor = conn.cursor()
            first_query = "SELECT id FROM authors WHERE name = %s;"
            cursor.execute(first_query, (author_name, ))
            result = cursor.fetchone()
            if result:
                author_id = result[0]
                second_query = "INSERT INTO books (title, author_id, isbn, publication_date, availability) VALUES (%s, %s, %s, %s, 1);"
                cursor.execute(second_query, (title, author_id, isbn, publication_date))
                conn.commit()
                print(f"Book '{title}' has been added to the library successfully.")
            else:
                print(f"'{author_name}' was not found in the library. Please add them to the Library Management System first.")
        except Error as e:
            print(f"Error adding new book: {e}")
        finally:
            cursor.close()
            conn.close()

def borrow_book():
    library_id = input("Enter your library ID: ")
    if not is_valid_library_id(library_id):
        print("Invalid ID. Library ID must begin with 'L' and be followed by 4 digits.")
        return
    title = input("Enter the book title to borrow: ")
    conn = connect_database()
    if conn is not None:
        try:
            cursor = conn.cursor()
            first_query = "SELECT id, availability FROM books WHERE title = %s;"
            cursor.execute(first_query, (title, ))
            result = cursor.fetchone()
            if result:
                book_id, availability = result
                if availability:
                    second_query = "INSERT INTO borrowed_books (user_id, book_id, borrow_date) VALUES (%s, %s, CURDATE());"
                    cursor.execute(second_query, (library_id, book_id))
                    third_query = "UPDATE books SET availability 0 WHERE id = %s;"
                    cursor.execute(third_query, (book_id, ))
                    conn.commit()
                    print(f"'{title}' has been successfully checked-out to ID: {library_id}.")
                else:
                    print(f"Apologies, but '{title}' is currently unavailable to check-out.")
            else:
                print(f"'{title}' was not found in the library.")
        except Error as e:
            print(f"Error borrowing book: {e}")
        finally:
            cursor.close()
            conn.close()

def return_borrowed_book():
    library_id = input("Enter your library ID: ")
    if not is_valid_library_id(library_id):
        print("Invalid ID. Library ID must begin with 'L' and be followed by 4 digits.")
        return
    title = input("Enter the book title to return: ")
    conn = connect_database()
    if conn is not None:
        try:
            cursor = conn.cursor()
            first_query = "SELECT book_id FROM borrowed_books WHERE user_id = %s;"
            cursor.execute(first_query, (library_id, ))
            result = cursor.fetchone()
            if result:
                book_id = result[0]
                second_query = "DELETE FROM borrowed_books WHERE user_id = %s AND book_id = %s;"
                cursor.execute(second_query, (library_id, book_id))
                third_query = "UPDATE books SET availability 1 WHERE id = %s;"
                cursor.execute(third_query, (book_id, ))
                conn.commit()
                print(f"'{title}' has been checked-in by ID: {library_id}.")
            else:
                print(f"'{title}' has not been checked-out or does not exist in the library.")
        except Error as e:
            print(f"Error borrowing book: {e}")
        finally:
            cursor.close()
            conn.close()

def search_for_book():
    title = input("Enter the book title to search: ")
    conn = connect_database()
    if conn is not None:
        try:
            cursor = conn.cursor()
            query = """
            SELECT b.id, b.title, a.name, b.isbn, b.publication_date, b.availability
            FROM books b, authors a
            WHERE b.author_id = a.id AND b.title = %s;
            """
            cursor.execute(query, (title, ))
            found_book = cursor.fetchone()
            if found_book:
                print(f"Book ID: {found_book[0]}\n    Title: {found_book[1]}\n    Author name: {found_book[2]}\n    ISBN: {found_book[3]}\n    Publication Date: {found_book[4]}\n    Availability: {'Available' if found_book[5] else 'Borrowed'}")
            else:
                print(f"'{title}' was not found in the library.")
        except Error as e:
            print(f"Error searching for book: {e}")
        finally:
            cursor.close()
            conn.close()

def display_all_books():
    print("\nBook Catalog:")
    conn = connect_database()
    if conn is not None:
        try:
            cursor = conn.cursor()
            query = """
            SELECT b.id, b.title, a.name, b.isbn, b.publication_date, b.availability
            FROM books b, authors a
            WHERE b.author_id = a.id;
            """
            cursor.execute(query, )
            book_catalog = cursor.fetchall()
            if book_catalog:
                for book in book_catalog:
                    print(f"Book ID: {book[0]}\n    Title: {book[1]}\n    Author name: {book[2]}\n    ISBN: {book[3]}\n    Publication Date: {book[4]}\n    Availability: {'Available' if book[5] else 'Borrowed'}")
            else:
                print("There are no books currently in the library.")
        except Error as e:
            print(f"Error displaying books: {e}")
        finally:
            cursor.close()
            conn.close()

def user_operations():      
    while True:
        print("\nUser Operations:")
        print("1. Add a new user\n2. View user details\n3. Display all users\n4. Return to menu")
        user_op_choice = input("Enter the operation number to perform (1-4): ")
        if user_op_choice == "4":
            break
        try:
            if user_op_choice == "1":
                add_user()
            elif user_op_choice == "2":
                display_user_details()
            elif user_op_choice == "3":
                display_all_users()
            else:
                print("Invalid choice. Please try again.")
        except Exception as e:
            print(f"Error: {e}")

def add_user():
    name = input("Enter new user's name: ")
    if not is_valid_name(name):
        print("Invalid name. Please enter only letters and spaces.")
        return
    library_id = input("Enter new user's library ID (must begin with 'L' and be followed by 4 digits): ")
    if not is_valid_library_id(library_id):
        print("Invalid ID. Library ID must begin with 'L' and be followed by 4 digits.")
        return
    conn = connect_database()
    if conn is not None:
        try:
            cursor = conn.cursor()
            first_query = "SELECT id FROM users WHERE library_id = %s;"
            cursor.execute(first_query, (library_id, ))
            result = cursor.fetchone()
            if result:
                print(f"User with ID '{library_id}' already exists.")
            else:
                second_query = "INSERT INTO users (name, library_id) VALUES (%s, %s);"
                cursor.execute(second_query, (name, library_id))
                conn.commit()
                print(f"User '{name}' had been added with library ID: {library_id}.")
        except Error as e:
            print(f"Error adding new user: {e}")
        finally:
            cursor.close()
            conn.close()

def display_user_details():
    library_id = input("Enter the library ID to display: ")
    if not is_valid_library_id(library_id):
        print("Invalid ID. Library ID must begin with 'L' and be followed by 4 digits.")
        return
    conn = connect_database()
    if conn is not None:
        try:
            cursor = conn.cursor()
            query = "SELECT id, name, library_id FROM users WHERE library_id = %s;"
            cursor.execute(query, (library_id, ))
            user_details = cursor.fetchone()
            if user_details:
                print(f"User ID: {user_details[0]}\n    Name: {user_details[1]}\n    Library ID: {user_details[2]}")
            else:
                print(f"No user was found with library ID '{library_id}'. Please add them to the Library Management System first.")
        except Error as e:
            print(f"Error displaying user details: {e}")
        finally:
            cursor.close()
            conn.close()

def display_all_users():
    print("\nAll Library Users:")
    conn = connect_database()
    if conn is not None:
        try:
            cursor = conn.cursor()
            query = "SELECT id, name, library_id FROM users"
            cursor.execute(query, )
            all_users = cursor.fetchall()
            if all_users:
                for user in all_users:
                    print(f"User ID: {user[0]}\n    Name: {user[1]}\n    Library ID: {user[2]}")
            else:
                print("There are currently no users in the Library Management System.")
        except Error as e:
            print(f"Error displaying details of all users: {e}")
        finally:
            cursor.close()
            conn.close()
            
def author_operations():
    while True:
        print("\nAuthor Operations:")
        print("1. Add a new author\n2. View author details\n3. Display all authors\n4. Return to menu")
        author_op_choice = input("Enter the operation number to perform (1-4): ")
        if author_op_choice == "4":
            break
        try:
            if author_op_choice == "1":
                add_author()
            elif author_op_choice == "2":
                display_author_details()
            elif author_op_choice == "3":
                display_all_authors()
            else:
                print("Invalid choice. Please try again.")
        except Exception as e:
            print(f"Error: {e}")

def add_author():
    author_name = input("Enter new author's name: ")
    if not is_valid_name(author_name):
        print("Invalid name. Please enter only letters and spaces.")
        return
    author_biography = input("Enter author's biographical information: ")
    conn = connect_database()
    if conn is not None:
        try:
            cursor = conn.cursor()
            first_query = "SELECT id FROM authors WHERE name = %s;"
            cursor.execute(first_query, (author_name, ))
            result = cursor.fetchone()
            if result:
                print(f"Author '{author_name}' already exists in the Library Management System.")
            else:
                second_query = "INSERT INTO authors (name, biography) VALUES (%s, %s);"
                cursor.execute(second_query, (author_name, author_biography))
                conn.commit()
                print(f"Author '{author_name}' has successfully been added to the Library Management System.")
        except Error as e:
            print(f"Error adding new author: {e}")
        finally:
            cursor.close()
            conn.close()

def display_author_details():
    author_name = input("Enter author's name to display: ")
    if not is_valid_name(author_name):
        print("Invalid name. Please enter only letters and spaces.")
        return
    conn = connect_database()
    if conn is not None:
        try:
            cursor = conn.cursor()
            query = "SELECT id, name, biography FROM authors WHERE name = %s;"
            cursor.execute(query, (author_name, ))
            author_details = cursor.fetchone()
            if author_details:
                print(f"Author ID: {author_details[0]}\n    Name: {author_details[1]}\n    Biography: {author_details[2]}")
            else:
                print(f"Author '{author_name}' was not found. Please add them to the Library Management System first.")
        except Error as e:
            print(f"Error displaying author details: {e}")
        finally:
            cursor.close()
            conn.close()

def display_all_authors():
    print("\nAll Authors in Library Management System:")
    conn = connect_database()
    if conn is not None:
        try:
            cursor = conn.cursor()
            query = "SELECT id, name, biography FROM authors;"
            cursor.execute(query, )
            all_authors = cursor.fetchall()
            if all_authors:
                for author in all_authors:
                    print(f"Author ID: {author[0]}\n    Name: {author[1]}\n    Biography: {author[2]}")
            else:
                print("There are currently no authors in the Library Management System.")
        except Error as e:
            print(f"Error displaying details of all authors: {e}")
        finally:
            cursor.close()
            conn.close()

def is_valid_name(name):
    return bool(re.match(r"^[A-Za-z\s]+$", name))

def is_valid_library_id(library_id):
    return bool(re.match(r"^L\d{4}$", library_id))

def is_valid_date(date):
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", date))

while True:
    print("Welcome to the Library Management System with Database Integration!\n****")
    print("Main Menu:\n1. Book Operations\n2. User Operations\n3. Author Operations\n4. Quit")
    choice = input("Enter the name of the Operations menu to access (book/user/author/quit): ")
    if choice.lower() == "quit":
        print("Thank you for using the Library Management System. The system is closing now.")
        break

    try:
        if choice.lower() == "book":
            book_operations()
        elif choice.lower() == "user":
            user_operations()
        elif choice.lower() == "author":
            author_operations()
        else:
            print("Invalid choice. Please try again.")
    except Exception as e:
        print(f"Error: {e}")