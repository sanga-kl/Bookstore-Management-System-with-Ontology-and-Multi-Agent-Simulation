import random
import uuid
from typing import List, Dict, Any
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import NetworkGrid
from mesa.datacollection import DataCollector
import networkx as nx

from message_bus import AgentCommunicator, MessageBus, MessageType, Message
from ontology import BookstoreOntology

class BookstoreAgent(Agent):
    
    def __init__(self, unique_id, model, ontology, message_bus):
        super().__init__(unique_id, model)
        self.ontology = ontology
        self.communicator = AgentCommunicator(str(unique_id), message_bus)
        self.active = True
        self.message_buffer = []
        
    def step(self):
        if not self.active:
            return
        
        # Process received messages
        self.process_messages()
        
        # Perform agent-specific actions
        self.agent_action()
    
    def process_messages(self):
        
        messages = self.communicator.get_messages(timeout=0.01)
        for message in messages:
            self.handle_message(message)
    
    def handle_message(self, message: Message):
        
        self.message_buffer.append(message)
    
    def agent_action(self):
        
        pass
    
    def cleanup(self):
        
        self.communicator.cleanup()

class CustomerAgent(BookstoreAgent):

    def __init__(self, unique_id, model, ontology, message_bus, name=None, budget=None):
        super().__init__(unique_id, model, ontology, message_bus)
        self.name = name or f"Customer_{unique_id}"
        self.budget = budget or random.uniform(20.0, 200.0)
        self.shopping_list = []
        self.purchased_books = []
        self.browse_probability = 0.3
        self.purchase_probability = 0.4
        self.satisfaction = 1.0
        self.visit_count = 0
        
        # Create customer in ontology
        self.onto_customer = ontology.create_customer(f"customer_{unique_id}", self.name, self.budget)
        
        print(f"Customer {self.name} created with budget ${self.budget:.2f}")
    
    def agent_action(self):
        
        self.visit_count += 1
        
        # Randomly decide to browse
        if random.random() < self.browse_probability:
            self.browse_books()
        
        # Randomly decide to make a purchase
        if random.random() < self.purchase_probability and self.shopping_list:
            self.attempt_purchase()
        
        # Occasionally check budget and adjust behavior
        if self.visit_count % 10 == 0:
            self.adjust_behavior()
    
    def browse_books(self):
        
        books = self.ontology.get_all_books()
        if not books:
            return
        
        # Select a random book to consider
        book = random.choice(books)
        
        if hasattr(book, 'hasPrice') and hasattr(book, 'bookTitle'):
            book_info = {
                'isbn': getattr(book, 'isbn', ''),
                'title': book.bookTitle,
                'price': book.hasPrice,
                'book_obj': book
            }
            
            # Check if affordable and not already in shopping list
            if (book.hasPrice <= self.budget and 
                not any(item['isbn'] == book_info['isbn'] for item in self.shopping_list)):
                
                self.shopping_list.append(book_info)
                print(f"{self.name} added '{book.bookTitle}' to shopping list")
                
                # Send customer inquiry message
                self.communicator.send_message(
                    MessageType.CUSTOMER_INQUIRY,
                    {
                        "action": "browsing",
                        "book_isbn": book_info['isbn'],
                        "customer_budget": self.budget
                    }
                )
    
    def attempt_purchase(self):
        
        if not self.shopping_list:
            return
        
        # Select a book from shopping list
        book_info = random.choice(self.shopping_list)
        book_isbn = book_info['isbn']
        book_price = book_info['price']
        
        # Check budget
        if book_price > self.budget:
            self.shopping_list.remove(book_info)
            print(f"{self.name} cannot afford '{book_info['title']}'")
            return
        
        # Check inventory availability
        book = self.ontology.get_book_by_isbn(book_isbn)
        if book and hasattr(book, 'hasInventory'):
            inventory = book.hasInventory[0] if book.hasInventory else None
            if inventory and hasattr(inventory, 'availableQuantity'):
                if inventory.availableQuantity > 0:
                    # Make the purchase
                    self.make_purchase(book_info, inventory)
                else:
                    print(f"{self.name} found '{book_info['title']}' out of stock")
                    self.shopping_list.remove(book_info)
    
    def make_purchase(self, book_info, inventory):
        
        book_price = book_info['price']
        book_isbn = book_info['isbn']
        
        # Update budget
        self.budget -= book_price
        self.onto_customer.customerBudget = self.budget
        
        # Update inventory
        new_quantity = inventory.availableQuantity - 1
        inventory.availableQuantity = new_quantity
        
        # Add to purchased books
        self.purchased_books.append(book_info)
        self.shopping_list.remove(book_info)
        
        # Create order in ontology
        order_id = f"order_{uuid.uuid4().hex[:8]}"
        order = self.ontology.create_order(
            order_id, 
            self.onto_customer, 
            [book_info['book_obj']], 
            book_price
        )
        
        print(f"{self.name} purchased '{book_info['title']}' for ${book_price:.2f}")
        print(f"{self.name} remaining budget: ${self.budget:.2f}")
        
        # Send purchase completed message
        self.communicator.send_message(
            MessageType.PURCHASE_COMPLETED,
            {
                "book_isbn": book_isbn,
                "price": book_price,
                "customer_name": self.name,
                "new_inventory": new_quantity,
                "order_id": order_id
            }
        )
        
        # Send inventory update
        self.communicator.send_inventory_update(book_isbn, new_quantity)
        
        # Update satisfaction
        self.satisfaction = min(1.0, self.satisfaction + 0.1)
    
    def adjust_behavior(self):
        
        if self.budget < 20:
            self.purchase_probability *= 0.5
            self.browse_probability *= 0.8
        elif self.budget > 100:
            self.purchase_probability = min(0.6, self.purchase_probability * 1.2)
            self.browse_probability = min(0.5, self.browse_probability * 1.1)
    
    def handle_message(self, message: Message):
        
        super().handle_message(message)
        
        if message.message_type == MessageType.RESTOCK_COMPLETED:
            # Maybe try to purchase restocked items
            if random.random() < 0.3:  # 30% chance
                self.browse_books()
        elif message.message_type == MessageType.SYSTEM_ALERT:
            content = message.content
            if content.get("type") == "sale":
                # Increase purchase probability during sales
                self.purchase_probability = min(0.8, self.purchase_probability * 1.5)
    
    def get_stats(self):
        
        return {
            "name": self.name,
            "budget": self.budget,
            "books_purchased": len(self.purchased_books),
            "shopping_list_size": len(self.shopping_list),
            "satisfaction": self.satisfaction,
            "total_spent": sum(book['price'] for book in self.purchased_books)
        }

class EmployeeAgent(BookstoreAgent):

    def __init__(self, unique_id, model, ontology, message_bus, name=None, role=None):
        super().__init__(unique_id, model, ontology, message_bus)
        self.name = name or f"Employee_{unique_id}"
        self.role = role or random.choice(["Sales Associate", "Manager", "Inventory Specialist"])
        self.efficiency = random.uniform(0.7, 1.0)
        self.workload = 0
        self.max_workload = 10
        self.restock_amount = 20
        self.processed_orders = []
        
        print(f"Employee {self.name} ({self.role}) hired")
    
    def agent_action(self):
        
        # Reduce workload over time
        self.workload = max(0, self.workload - 0.5)
        
        # Check inventory levels if inventory specialist
        if self.role == "Inventory Specialist" and random.random() < 0.4:
            self.check_inventory_levels()
        
        # Process pending orders if sales associate or manager
        if self.role in ["Sales Associate", "Manager"] and random.random() < 0.3:
            self.process_orders()
        
        # Manager-specific actions
        if self.role == "Manager" and random.random() < 0.2:
            self.manager_actions()
    
    def check_inventory_levels(self):
        
        if self.workload >= self.max_workload:
            return
        
        restock_needed = self.ontology.check_restock_needed()
        
        for inventory in restock_needed:
            if self.workload >= self.max_workload:
                break
            
            # Find the book for this inventory
            book = None
            for b in self.ontology.get_all_books():
                if hasattr(b, 'hasInventory') and inventory in b.hasInventory:
                    book = b
                    break
            
            if book and hasattr(book, 'isbn'):
                self.restock_book(book.isbn, inventory)
    
    def restock_book(self, book_isbn, inventory):
        
        if self.workload >= self.max_workload:
            return
        
        old_quantity = inventory.availableQuantity
        new_quantity = old_quantity + self.restock_amount
        inventory.availableQuantity = new_quantity
        
        self.workload += 2  # Restocking takes effort
        
        book = self.ontology.get_book_by_isbn(book_isbn)
        book_title = book.bookTitle if book and hasattr(book, 'bookTitle') else book_isbn
        
        print(f"{self.name} restocked '{book_title}' from {old_quantity} to {new_quantity}")
        
        # Send restock completed message
        self.communicator.send_message(
            MessageType.RESTOCK_COMPLETED,
            {
                "book_isbn": book_isbn,
                "old_quantity": old_quantity,
                "new_quantity": new_quantity,
                "employee_name": self.name
            }
        )
        
        # Send inventory update
        self.communicator.send_inventory_update(book_isbn, new_quantity)
    
    def process_orders(self):
        
        if self.workload >= self.max_workload:
            return
        
        # Simulate processing orders
        if random.random() < 0.3:  # 30% chance of having orders to process
            order_id = f"order_{uuid.uuid4().hex[:8]}"
            self.processed_orders.append(order_id)
            self.workload += 1
            
            print(f"{self.name} processed order {order_id}")
            
            self.communicator.send_message(
                MessageType.ORDER_PROCESSED,
                {
                    "order_id": order_id,
                    "processed_by": self.name,
                    "employee_role": self.role
                }
            )
    
    def manager_actions(self):
        
        if self.workload >= self.max_workload:
            return
        
        # Occasionally send system alerts
        if random.random() < 0.1:  # 10% chance
            alert_types = ["sale", "promotion", "new_arrivals"]
            alert_type = random.choice(alert_types)
            
            self.communicator.broadcast(
                MessageType.SYSTEM_ALERT,
                {
                    "type": alert_type,
                    "message": f"Manager {self.name} announced a {alert_type}",
                    "sender_role": self.role
                }
            )
            
            print(f"Manager {self.name} sent system alert: {alert_type}")
            self.workload += 1
    
    def handle_message(self, message: Message):
        
        super().handle_message(message)
        
        if message.message_type == MessageType.RESTOCK_REQUEST:
            if self.role == "Inventory Specialist" and self.workload < self.max_workload:
                content = message.content
                book_isbn = content.get("book_isbn")
                if book_isbn:
                    book = self.ontology.get_book_by_isbn(book_isbn)
                    if book and hasattr(book, 'hasInventory'):
                        inventory = book.hasInventory[0] if book.hasInventory else None
                        if inventory:
                            self.restock_book(book_isbn, inventory)
        
        elif message.message_type == MessageType.PURCHASE_COMPLETED:
            if self.role in ["Sales Associate", "Manager"]:
                # Acknowledge the purchase
                content = message.content
                print(f"{self.name} acknowledged purchase of {content.get('book_isbn', 'unknown book')}")
    
    def get_stats(self):
        
        return {
            "name": self.name,
            "role": self.role,
            "efficiency": self.efficiency,
            "workload": self.workload,
            "orders_processed": len(self.processed_orders)
        }

class BookAgent(BookstoreAgent):

    def __init__(self, unique_id, model, ontology, message_bus, book_obj):
        super().__init__(unique_id, model, ontology, message_bus)
        self.book_obj = book_obj
        self.isbn = getattr(book_obj, 'isbn', str(unique_id))
        self.title = getattr(book_obj, 'bookTitle', f"Book_{unique_id}")
        self.price = getattr(book_obj, 'hasPrice', 10.0)
        self.sales_count = 0
        self.popularity_score = random.uniform(0.1, 1.0)
        self.demand_trend = random.choice([-1, 0, 1])  # -1 decreasing, 0 stable, 1 increasing
        
        print(f"Book agent created for '{self.title}' (${self.price:.2f})")
    
    def agent_action(self):
        
        # Randomly adjust popularity based on trend
        if random.random() < 0.1:  # 10% chance
            if self.demand_trend == 1:
                self.popularity_score = min(1.0, self.popularity_score + 0.05)
            elif self.demand_trend == -1:
                self.popularity_score = max(0.1, self.popularity_score - 0.02)
        
        # Occasionally change trend
        if random.random() < 0.05:  # 5% chance
            self.demand_trend = random.choice([-1, 0, 1])
        
        # Check if low stock and high popularity (could trigger promotion)
        if hasattr(self.book_obj, 'hasInventory'):
            inventory = self.book_obj.hasInventory[0] if self.book_obj.hasInventory else None
            if inventory and hasattr(inventory, 'availableQuantity'):
                if inventory.availableQuantity <= 5 and self.popularity_score > 0.7:
                    self.suggest_promotion()
    
    def suggest_promotion(self):
        
        if random.random() < 0.1:  # 10% chance to actually suggest
            self.communicator.broadcast(
                MessageType.SYSTEM_ALERT,
                {
                    "type": "promotion_suggestion",
                    "book_isbn": self.isbn,
                    "book_title": self.title,
                    "popularity": self.popularity_score,
                    "reason": "High demand, low stock"
                }
            )
            print(f"Book '{self.title}' suggested for promotion")
    
    def handle_message(self, message: Message):
        
        super().handle_message(message)
        
        if message.message_type == MessageType.PURCHASE_COMPLETED:
            content = message.content
            if content.get("book_isbn") == self.isbn:
                self.sales_count += 1
                # Increase popularity when sold
                self.popularity_score = min(1.0, self.popularity_score + 0.02)
                print(f"Book '{self.title}' recorded sale #{self.sales_count}")
        
        elif message.message_type == MessageType.INVENTORY_UPDATE:
            content = message.content
            if content.get("book_isbn") == self.isbn:
                new_quantity = content.get("new_inventory", 0)
                if new_quantity <= 3:  # Low stock
                    self.popularity_score = min(1.0, self.popularity_score + 0.01)
    
    def get_current_stock(self):
        
        if hasattr(self.book_obj, 'hasInventory'):
            inventory = self.book_obj.hasInventory[0] if self.book_obj.hasInventory else None
            if inventory and hasattr(inventory, 'availableQuantity'):
                return inventory.availableQuantity
        return 0
    
    def get_stats(self):
        
        # Get genre information
        genre_name = "Unknown"
        if hasattr(self.book_obj, 'hasGenre') and self.book_obj.hasGenre:
            genre_obj = self.book_obj.hasGenre[0]
            if hasattr(genre_obj, 'genreName'):
                genre_name = genre_obj.genreName
        
        # Get author information
        author_name = "Unknown Author"
        if hasattr(self.book_obj, 'hasAuthor') and self.book_obj.hasAuthor:
            author_obj = self.book_obj.hasAuthor[0]
            if hasattr(author_obj, 'authorName'):
                author_name = author_obj.authorName
        
        return {
            "title": self.title,
            "isbn": self.isbn,
            "price": self.price,
            "sales_count": self.sales_count,
            "popularity_score": self.popularity_score,
            "current_stock": self.get_current_stock(),
            "demand_trend": self.demand_trend,
            "genre": genre_name,
            "author": author_name
        }

def create_agents(model, ontology, message_bus, num_customers=10, num_employees=3):
    
    agents = []
    
    # Create customer agents
    for i in range(num_customers):
        customer = CustomerAgent(
            unique_id=f"customer_{i}",
            model=model,
            ontology=ontology,
            message_bus=message_bus,
            name=f"Customer_{chr(65+i)}",  # Customer_A, Customer_B, etc.
            budget=random.uniform(30.0, 150.0)
        )
        agents.append(customer)
    
    # Create employee agents
    roles = ["Manager", "Sales Associate", "Inventory Specialist"]
    for i in range(num_employees):
        role = roles[i % len(roles)]
        employee = EmployeeAgent(
            unique_id=f"employee_{i}",
            model=model,
            ontology=ontology,
            message_bus=message_bus,
            name=f"Employee_{chr(65+i)}",
            role=role
        )
        agents.append(employee)
    
    # Create book agents
    books = ontology.get_all_books()
    for i, book in enumerate(books):
        book_agent = BookAgent(
            unique_id=f"book_{i}",
            model=model,
            ontology=ontology,
            message_bus=message_bus,
            book_obj=book
        )
        agents.append(book_agent)
    
    return agents