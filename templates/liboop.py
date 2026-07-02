class Liberary :
    def __init__ (self) :
        self.books = [
    # --- PYTHON ---
            {
               "title": "Python Crash Course, 3rd Edition",
              "author": "Eric Matthes",
              "year": 2019
            },
            {
              "title": "Fluent Python, 2nd Edition",
              "author": "Luciano Ramalho",
              "year": 2022
     
            },
            {
           "title": "Automate the Boring Stuff with Python, 3rd Edition",
              "author": "Al Sweigart",
              "year": 2025
            },
            {
              "title": "Effective Python, 3rd Edition",
              "author": "Brett Slatkin",
              "year": 2024
            },
            {
              "title": "Head First Python, 2nd Edition",
              "author": "Paul Barry",
              "year": 2016
            },
            {
              "title": "Programming Python",
              "author": "Mark Lutz",
              "year": 2010
            },

    # --- JAVA ---
            {    
              "title": "Core Java, Volume I: Fundamentals, 13th Edition",
              "author": "Cay S. Horstmann",
              "year": 2024
            },
            {
              "title": "Effective Java, 3rd Edition",
              "author": "Joshua Bloch",
              "year": 2018
            },
            {
              "title": "Head First Java, 3rd Edition",
              "author": "Kathy Sierra, Bert Bates, Trisha Gee",
              "year": 2022
            },
            {
              "title": "Java: The Complete Reference, 13th Edition",
              "author": "Herbert Schildt, Dr. Danny Coward",
              "year": 2024
            },
            {
              "title": "The Java Programming Language, 3rd Edition",
              "author": "Ken Arnold, James Gosling, David Holmes",
              "year": 2000
            },

    # --- C++ ---
            {
              "title": "The C++ Programming Language, 4th Edition",
              "author": "Bjarne Stroustrup",
              "year": 2013
            },
            {
              "title": "Effective C++, 3rd Edition",
              "author": "Scott Meyers",
              "year": 2005
            },
            {
              "title": "The Design and Evolution of C++",
              "author": "Bjarne Stroustrup",
              "year": 1994
            },
            {
              "title": "The Annotated C++ Reference Manual",
              "author": "Margaret A. Ellis, Bjarne Stroustrup",
              "year": 1990
            },
            {
           "title" : "Programming: c++  Principles and Practice",
              "author": "Bjarne Stroustrup",
              "year": 2024
            },

    # --- DATA SCIENCE ---
            {
              "title": "Introduction to Data Science: Data Wrangling and Visualization with R",
              "author": "Rafael A. Irizarry",
              "year": None  # Year not specified in available sources
            },
            {
              "title": "Doing Data Science",
              "author": "Rachel Schutt, Cathy O'Neil",
              "year": 2013
            },
            {
              "title": "Data Science",
              "author": "John Kelleher, Brendan Tierney",
              "year": 2018
            },
            {
              "title": "Data Science and Analytics with Python",
              "author": "Various",
              "year": None  # Year not specified in available sources
            }
    ]
class Bookdetails (Liberary) :
    def show_book_details (self) :     
       for book in self.books:
              print(f"Title: {book['title']}")
              print(f"Author: {book['author']}")
              print(f"Year: {book['year']}")

class Issue (Liberary) :
    def issue_books(self):
        self.name = input("Enter your name: ").capitalize()
        self.id = input("Enter your id: ")
        self.book = input("Enter book name which you want: ")
        self.books.remove (self.book)

        found = False

        for book in self.books:
            if book["title"].lower() == self.book.lower():
                found = True
                break

        if found:
            import datetime

            issued_date = datetime.datetime.now()
            due_date = issued_date + datetime.timedelta(days=7)

            print(f"""
            Issued To : {self.name}
            ID        : {self.id}
            Book      : {self.book}
            Issue Date: {issued_date}
            Due Date  : {due_date}
            """)
        else:
            print("Book doesn't exist")
        self.book.remove (self.book)

class Find (Liberary) :
     def find_book(self, search = " "):
        self.search = input("Enter the book name which you want to search? ")
        for index, book in enumerate(self.books):
            if book["title"].lower() == self.search.lower():
                print(f"\nBook Found at Index {index}")
                print("Title :", book["title"])
                print("Author:", book["author"])
                print("Year  :", book["year"])
                return
            print("Sorry! This book is out of stock.")

class Add (Liberary) :
     def add_new_book (self) :
       import sys
       import os
       desktop_path = r"C:\Users\sande\OneDrive\Desktop\python\argumentsday4.py"
       sys.path.append (desktop_path)
       import argumentsday4
       self.add = argumentsday4.book_stock ()
       updated_book = self.books.append(self.add)
       print (updated_book)
     

print ("Liberary Menu :", 1, " Show Book Details: " , 
       2 , " Issue Book: ",
       3 , "Find Book: ",
       4, " Add new book: ",
       5 , "Quit" ) 

choice = int (input ("Enter your choice : "))
if choice == 1 :
       a = Bookdetails()
       a.show_book_details()

elif choice == 2 :
       a = Issue()
       a.issue_books()

elif choice == 3:
       a = Find()
       a.find_book()


elif choice == 4:
       a = Add()
       a.add_new_book()

elif choice == 5:
       print ("Thank you for using the liberary system.")

else :
       print ("Invalid input")