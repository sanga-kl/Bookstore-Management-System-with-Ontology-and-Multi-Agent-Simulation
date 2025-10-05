from owlready2 import *
import datetime
import os

class BookstoreOntology:
    def __init__(self):
        self.onto = get_ontology("http://bookstore.example.org/onto/bookstore")
        self.setup_ontology()
        
    def setup_ontology(self):
        with self.onto:
            # Define main classes
            class Entity(Thing):
                pass
            
            class Person(Entity):
                pass
            
            class Customer(Person):
                pass
            
            class Employee(Person):
                pass
            
            class Book(Entity):
                pass
            
            class Order(Entity):
                pass
            
            class Inventory(Entity):
                pass
            
            class Genre(Entity):
                pass
            
            class Author(Entity):
                pass
            
            class Transaction(Entity):
                pass
            
            class hasAuthor(ObjectProperty):
                domain = [Book]
                range = [Author]
            
            class hasGenre(ObjectProperty):
                domain = [Book]
                range = [Genre]
            
            class purchases(ObjectProperty):
                domain = [Customer]
                range = [Book]
            
            class worksAt(ObjectProperty):
                domain = [Employee]
                range = [Entity]
            
            class hasOrder(ObjectProperty):
                domain = [Customer]
                range = [Order]
            
            class containsBook(ObjectProperty):
                domain = [Order]
                range = [Book]
            
            class managedBy(ObjectProperty):
                domain = [Inventory]
                range = [Employee]
            
            class hasInventory(ObjectProperty):
                domain = [Book]
                range = [Inventory]
            
            class processedBy(ObjectProperty):
                domain = [Order]
                range = [Employee]
            
            class hasPrice(DataProperty, FunctionalProperty):
                domain = [Book]
                range = [float]
            
            class availableQuantity(DataProperty, FunctionalProperty):
                domain = [Inventory]
                range = [int]
            
            class reorderLevel(DataProperty, FunctionalProperty):
                domain = [Inventory]
                range = [int]
            
            class customerName(DataProperty, FunctionalProperty):
                domain = [Customer]
                range = [str]
            
            class employeeName(DataProperty, FunctionalProperty):
                domain = [Employee]
                range = [str]
            
            class bookTitle(DataProperty, FunctionalProperty):
                domain = [Book]
                range = [str]
            
            class isbn(DataProperty, FunctionalProperty):
                domain = [Book]
                range = [str]
            
            class authorName(DataProperty, FunctionalProperty):
                domain = [Author]
                range = [str]
            
            class genreName(DataProperty, FunctionalProperty):
                domain = [Genre]
                range = [str]
            
            class orderDate(DataProperty, FunctionalProperty):
                domain = [Order]
                range = [datetime.datetime]
            
            class orderStatus(DataProperty, FunctionalProperty):
                domain = [Order]
                range = [str]
            
            class totalAmount(DataProperty, FunctionalProperty):
                domain = [Order]
                range = [float]
            
            class quantity(DataProperty, FunctionalProperty):
                domain = [Order]
                range = [int]
            
            class customerBudget(DataProperty, FunctionalProperty):
                domain = [Customer]
                range = [float]
            
            class employeeRole(DataProperty, FunctionalProperty):
                domain = [Employee]
                range = [str]
            
            class lastRestocked(DataProperty, FunctionalProperty):
                domain = [Inventory]
                range = [datetime.datetime]
        
        self.onto.save("/Users/sanhindaliyanage/Desktop/CSAT Assignment/BookManagement/bookstore.owl")
    
    def create_sample_data(self):
        with self.onto:
            # Create genres
            fiction = self.onto.Genre("fiction")
            fiction.genreName = "Fiction"
            
            mystery = self.onto.Genre("mystery")
            mystery.genreName = "Mystery"
            
            scifi = self.onto.Genre("science_fiction")
            scifi.genreName = "Science Fiction"
            
            romance = self.onto.Genre("romance")
            romance.genreName = "Romance"
            
            # Create authors
            author1 = self.onto.Author("agatha_christie")
            author1.authorName = "Agatha Christie"
            
            author2 = self.onto.Author("isaac_asimov")
            author2.authorName = "Isaac Asimov"
            
            author3 = self.onto.Author("jane_austen")
            author3.authorName = "Jane Austen"
            
            author4 = self.onto.Author("stephen_king")
            author4.authorName = "Stephen King"
            
            # Create books
            book1 = self.onto.Book("murder_on_orient_express")
            book1.bookTitle = "Murder on the Orient Express"
            book1.isbn = "978-0-00-711931-7"
            book1.hasPrice = 15.99
            book1.hasAuthor = [author1]
            book1.hasGenre = [mystery]
            
            book2 = self.onto.Book("foundation")
            book2.bookTitle = "Foundation"
            book2.isbn = "978-0-553-29335-0"
            book2.hasPrice = 12.99
            book2.hasAuthor = [author2]
            book2.hasGenre = [scifi]
            
            book3 = self.onto.Book("pride_and_prejudice")
            book3.bookTitle = "Pride and Prejudice"
            book3.isbn = "978-0-14-143951-8"
            book3.hasPrice = 9.99
            book3.hasAuthor = [author3]
            book3.hasGenre = [romance]
            
            book4 = self.onto.Book("the_shining")
            book4.bookTitle = "The Shining"
            book4.isbn = "978-0-307-74365-9"
            book4.hasPrice = 13.99
            book4.hasAuthor = [author4]
            book4.hasGenre = [fiction]
            
            # Create inventory records
            inv1 = self.onto.Inventory("inv_murder_orient")
            inv1.availableQuantity = 25
            inv1.reorderLevel = 5
            inv1.lastRestocked = datetime.datetime.now()
            book1.hasInventory = [inv1]
            
            inv2 = self.onto.Inventory("inv_foundation")
            inv2.availableQuantity = 20
            inv2.reorderLevel = 5
            inv2.lastRestocked = datetime.datetime.now()
            book2.hasInventory = [inv2]
            
            inv3 = self.onto.Inventory("inv_pride_prejudice")
            inv3.availableQuantity = 30
            inv3.reorderLevel = 8
            inv3.lastRestocked = datetime.datetime.now()
            book3.hasInventory = [inv3]
            
            inv4 = self.onto.Inventory("inv_shining")
            inv4.availableQuantity = 15
            inv4.reorderLevel = 5
            inv4.lastRestocked = datetime.datetime.now()
            book4.hasInventory = [inv4]
            
            # Create employees
            emp1 = self.onto.Employee("emp_alice")
            emp1.employeeName = "Alice Johnson"
            emp1.employeeRole = "Manager"
            
            emp2 = self.onto.Employee("emp_bob")
            emp2.employeeName = "Bob Smith"
            emp2.employeeRole = "Sales Associate"
            
            emp3 = self.onto.Employee("emp_carol")
            emp3.employeeName = "Carol Brown"
            emp3.employeeRole = "Inventory Specialist"
            
            # Link inventory to employees
            inv1.managedBy = [emp3]
            inv2.managedBy = [emp3]
            inv3.managedBy = [emp3]
            inv4.managedBy = [emp3]
        
        self.onto.save("/Users/sanhindaliyanage/Desktop/CSAT Assignment/BookManagement/bookstore.owl")
        print("Sample data created and ontology saved.")
    
    def get_all_books(self):
        return list(self.onto.Book.instances())
    
    def get_all_customers(self):
        return list(self.onto.Customer.instances())
    
    def get_all_employees(self):
        return list(self.onto.Employee.instances())
    
    def get_all_inventory(self):
        return list(self.onto.Inventory.instances())
    
    def update_inventory_quantity(self, book_isbn, new_quantity):
        for book in self.onto.Book.instances():
            if hasattr(book, 'isbn') and book.isbn == book_isbn:
                for inv in book.hasInventory:
                    inv.availableQuantity = new_quantity
                    break
                break
    
    def check_restock_needed(self):
        restock_needed = []
        for inv in self.onto.Inventory.instances():
            if hasattr(inv, 'availableQuantity') and hasattr(inv, 'reorderLevel'):
                if inv.availableQuantity <= inv.reorderLevel:
                    restock_needed.append(inv)
        return restock_needed
    
    def get_book_by_isbn(self, isbn):
        for book in self.onto.Book.instances():
            if hasattr(book, 'isbn') and book.isbn == isbn:
                return book
        return None
    
    def create_customer(self, customer_id, name, budget):
        with self.onto:
            customer = self.onto.Customer(customer_id)
            customer.customerName = name
            customer.customerBudget = budget
            return customer
    
    def create_order(self, order_id, customer, books, total_amount):
        with self.onto:
            order = self.onto.Order(order_id)
            order.orderDate = datetime.datetime.now()
            order.orderStatus = "pending"
            order.totalAmount = total_amount
            order.containsBook = books
            customer.hasOrder.append(order)
            return order

if __name__ == "__main__":
    # Test the ontology
    onto_manager = BookstoreOntology()
    onto_manager.create_sample_data()
    print("Ontology created successfully!")