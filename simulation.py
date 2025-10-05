

import random
import time
from typing import List, Dict, Any
from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import networkx as nx

from ontology import BookstoreOntology
from message_bus import MessageBus, get_message_bus
from agents import create_agents, CustomerAgent, EmployeeAgent, BookAgent

def compute_total_sales(model):
    
    total = 0
    for agent in model.schedule.agents:
        if isinstance(agent, CustomerAgent):
            total += sum(book['price'] for book in agent.purchased_books)
    return total

def compute_total_books_sold(model):
    
    total = 0
    for agent in model.schedule.agents:
        if isinstance(agent, BookAgent):
            total += agent.sales_count
    return total

def compute_average_customer_satisfaction(model):
    
    customers = [agent for agent in model.schedule.agents if isinstance(agent, CustomerAgent)]
    if not customers:
        return 0
    return sum(customer.satisfaction for customer in customers) / len(customers)

def compute_inventory_status(model):
    
    books = [agent for agent in model.schedule.agents if isinstance(agent, BookAgent)]
    if not books:
        return {"total_stock": 0, "low_stock_items": 0}
    
    total_stock = sum(book.get_current_stock() for book in books)
    low_stock_items = sum(1 for book in books if book.get_current_stock() <= 5)
    
    return {"total_stock": total_stock, "low_stock_items": low_stock_items}

class BookstoreModel(Model):

    def __init__(self, num_customers=10, num_employees=3, random_seed=None):
        super().__init__()
        
        if random_seed:
            random.seed(random_seed)
        
        # Initialize core components
        self.num_customers = num_customers
        self.num_employees = num_employees
        self.ontology = BookstoreOntology()
        self.message_bus = get_message_bus()
        
        # Initialize ontology with sample data
        self.ontology.create_sample_data()
        
        # Start message bus
        if not self.message_bus.running:
            self.message_bus.start()
        
        # Initialize scheduler
        self.schedule = RandomActivation(self)
        
        # Create and add agents
        self.agents = create_agents(
            self, 
            self.ontology, 
            self.message_bus,
            num_customers,
            num_employees
        )
        
        for agent in self.agents:
            self.schedule.add(agent)
        
        # Initialize data collector
        self.datacollector = DataCollector(
            model_reporters={
                "Total Sales": compute_total_sales,
                "Books Sold": compute_total_books_sold,
                "Customer Satisfaction": compute_average_customer_satisfaction,
                "Total Stock": lambda m: compute_inventory_status(m)["total_stock"],
                "Low Stock Items": lambda m: compute_inventory_status(m)["low_stock_items"],
                "Active Customers": lambda m: len([a for a in m.schedule.agents if isinstance(a, CustomerAgent) and a.active]),
                "Active Employees": lambda m: len([a for a in m.schedule.agents if isinstance(a, EmployeeAgent) and a.active]),
                "Message Count": lambda m: len(m.message_bus.message_history)
            },
            agent_reporters={
                "Agent Type": lambda a: type(a).__name__,
                "Budget": lambda a: getattr(a, 'budget', 0) if isinstance(a, CustomerAgent) else 0,
                "Books Purchased": lambda a: len(getattr(a, 'purchased_books', [])) if isinstance(a, CustomerAgent) else 0,
                "Workload": lambda a: getattr(a, 'workload', 0) if isinstance(a, EmployeeAgent) else 0,
                "Sales Count": lambda a: getattr(a, 'sales_count', 0) if isinstance(a, BookAgent) else 0,
                "Popularity": lambda a: getattr(a, 'popularity_score', 0) if isinstance(a, BookAgent) else 0
            }
        )
        
        # Track simulation metrics
        self.step_count = 0
        self.running = True
        self.simulation_start_time = time.time()
        
        print(f"Bookstore simulation initialized with {num_customers} customers and {num_employees} employees")
        print(f"Books available: {len([a for a in self.agents if isinstance(a, BookAgent)])}")
        
        # Collect initial data
        self.datacollector.collect(self)
    
    def step(self):
        
        if not self.running:
            return
        
        self.step_count += 1
        
        # Let all agents perform their actions
        self.schedule.step()
        
        # Collect data
        self.datacollector.collect(self)
        
        # Periodic system events
        if self.step_count % 20 == 0:
            self.system_events()
        
        # Check for simulation end conditions
        if self.step_count % 50 == 0:
            self.check_simulation_status()
        
        # Print periodic status
        if self.step_count % 25 == 0:
            self.print_status()
    
    def system_events(self):
        
        # Random system events
        if random.random() < 0.1:  # 10% chance
            event_type = random.choice(["sale", "new_arrivals", "maintenance"])
            
            if event_type == "sale":
                # Boost customer purchase probability
                for agent in self.schedule.agents:
                    if isinstance(agent, CustomerAgent):
                        agent.purchase_probability = min(0.8, agent.purchase_probability * 1.3)
                print("🎉 SYSTEM EVENT: Store-wide sale started!")
            
            elif event_type == "new_arrivals":
                # Boost customer browse probability
                for agent in self.schedule.agents:
                    if isinstance(agent, CustomerAgent):
                        agent.browse_probability = min(0.6, agent.browse_probability * 1.2)
                print("📚 SYSTEM EVENT: New book arrivals!")
            
            elif event_type == "maintenance":
                # Reduce employee efficiency temporarily
                for agent in self.schedule.agents:
                    if isinstance(agent, EmployeeAgent):
                        agent.efficiency *= 0.8
                print("🔧 SYSTEM EVENT: Store maintenance in progress")
    
    def check_simulation_status(self):
        
        # Check if customers still have budget
        active_customers = [a for a in self.schedule.agents if isinstance(a, CustomerAgent) and a.budget > 10]
        
        # Check if there's stock available
        books_with_stock = [a for a in self.schedule.agents if isinstance(a, BookAgent) and a.get_current_stock() > 0]
        
        if len(active_customers) < 2 or len(books_with_stock) < 2:
            print("⚠️  Simulation conditions degraded - consider ending soon")
        
        # Automatic end after 500 steps
        if self.step_count >= 500:
            print("📊 Maximum simulation steps reached")
            self.running = False
    
    def print_status(self):
        
        customers = [a for a in self.schedule.agents if isinstance(a, CustomerAgent)]
        employees = [a for a in self.schedule.agents if isinstance(a, EmployeeAgent)]
        books = [a for a in self.schedule.agents if isinstance(a, BookAgent)]
        
        total_sales = sum(sum(book['price'] for book in customer.purchased_books) for customer in customers)
        total_books_sold = sum(book.sales_count for book in books)
        avg_satisfaction = sum(customer.satisfaction for customer in customers) / len(customers) if customers else 0
        
        print(f"\n📈 STEP {self.step_count} STATUS:")
        print(f"   💰 Total Sales: ${total_sales:.2f}")
        print(f"   📚 Books Sold: {total_books_sold}")
        print(f"   😊 Avg Customer Satisfaction: {avg_satisfaction:.2f}")
        print(f"   💬 Messages Sent: {len(self.message_bus.message_history)}")
        
        # Show top-selling book
        if books:
            top_book = max(books, key=lambda b: b.sales_count)
            print(f"   🏆 Best Seller: '{top_book.title}' ({top_book.sales_count} sales)")
    
    def get_simulation_summary(self):
        
        customers = [a for a in self.schedule.agents if isinstance(a, CustomerAgent)]
        employees = [a for a in self.schedule.agents if isinstance(a, EmployeeAgent)]
        books = [a for a in self.schedule.agents if isinstance(a, BookAgent)]
        
        # Calculate metrics
        total_sales = sum(sum(book['price'] for book in customer.purchased_books) for customer in customers)
        total_books_sold = sum(book.sales_count for book in books)
        avg_satisfaction = sum(customer.satisfaction for customer in customers) / len(customers) if customers else 0
        
        # Customer metrics
        customer_stats = [customer.get_stats() for customer in customers]
        avg_budget_remaining = sum(stats['budget'] for stats in customer_stats) / len(customer_stats) if customer_stats else 0
        total_budget_spent = sum(stats['total_spent'] for stats in customer_stats)
        
        # Employee metrics
        employee_stats = [employee.get_stats() for employee in employees]
        total_orders_processed = sum(len(emp.processed_orders) for emp in employees)
        avg_employee_efficiency = sum(emp.efficiency for emp in employees) / len(employees) if employees else 0
        
        # Book metrics
        book_stats = [book.get_stats() for book in books]
        total_stock = sum(stats['current_stock'] for stats in book_stats)
        avg_popularity = sum(stats['popularity_score'] for stats in book_stats) / len(book_stats) if book_stats else 0
        
        # Advanced analytics
        purchase_rate = total_books_sold / self.step_count if self.step_count > 0 else 0
        customer_engagement = sum(len(c.purchased_books) > 0 for c in customers) / len(customers) if customers else 0
        inventory_turnover = total_books_sold / (total_stock + total_books_sold) if (total_stock + total_books_sold) > 0 else 0
        
        # Message bus stats
        message_stats = self.message_bus.get_stats()
        
        simulation_time = time.time() - self.simulation_start_time
        
        # Performance indicators
        steps_per_second = self.step_count / simulation_time if simulation_time > 0 else 0
        
        summary = {
            "simulation_info": {
                "steps_completed": self.step_count,
                "simulation_time_seconds": simulation_time,
                "steps_per_second": steps_per_second,
                "agents_total": len(self.agents),
                "simulation_status": "completed" if not self.running else "running"
            },
            "financial_metrics": {
                "total_sales": total_sales,
                "total_books_sold": total_books_sold,
                "average_book_price": total_sales / total_books_sold if total_books_sold > 0 else 0,
                "total_budget_spent": total_budget_spent,
                "purchase_rate_per_step": purchase_rate
            },
            "customer_metrics": {
                "total_customers": len(customers),
                "average_satisfaction": avg_satisfaction,
                "average_budget_remaining": avg_budget_remaining,
                "customer_engagement_rate": customer_engagement,
                "customer_details": customer_stats
            },
            "employee_metrics": {
                "total_employees": len(employees),
                "total_orders_processed": total_orders_processed,
                "average_efficiency": avg_employee_efficiency,
                "employee_details": employee_stats
            },
            "inventory_metrics": {
                "total_books": len(books),
                "total_stock_remaining": total_stock,
                "average_popularity": avg_popularity,
                "inventory_turnover": inventory_turnover,
                "book_details": book_stats
            },
            "communication_metrics": {
                "total_messages": message_stats["total_messages"],
                "message_types": message_stats["message_types"],
                "active_agents": message_stats["active_agents"],
                "messages_per_step": message_stats["total_messages"] / self.step_count if self.step_count > 0 else 0
            },
            "performance_metrics": {
                "simulation_efficiency": steps_per_second,
                "agent_density": len(self.agents) / self.step_count if self.step_count > 0 else 0,
                "system_utilization": message_stats["total_messages"] / (len(self.agents) * self.step_count) if self.step_count > 0 and len(self.agents) > 0 else 0
            }
        }
        
        return summary
        
        return summary
    
    def run_simulation(self, steps=100):
        
        print(f"\n🚀 Starting bookstore simulation for {steps} steps...")
        
        for i in range(steps):
            if not self.running:
                print(f"Simulation ended early at step {self.step_count}")
                break
            
            self.step()
            
            # Brief pause to make it observable
            time.sleep(0.01)
        
        print(f"\n✅ Simulation completed after {self.step_count} steps")
        return self.get_simulation_summary()
    
    def cleanup(self):
        
        print("🧹 Cleaning up simulation...")
        
        # Cleanup all agents
        for agent in self.agents:
            if hasattr(agent, 'cleanup'):
                agent.cleanup()
        
        # Stop message bus
        if self.message_bus.running:
            self.message_bus.stop()
        
        print("✅ Simulation cleanup completed")

def run_bookstore_simulation(num_customers=10, num_employees=3, steps=100, random_seed=42):
    
    print("=" * 60)
    print("📚 BOOKSTORE MANAGEMENT SYSTEM SIMULATION")
    print("=" * 60)
    
    # Create and run simulation
    model = BookstoreModel(
        num_customers=num_customers,
        num_employees=num_employees,
        random_seed=random_seed
    )
    
    try:
        summary = model.run_simulation(steps)
        return model, summary
    finally:
        model.cleanup()

if __name__ == "__main__":
    # Run a test simulation
    model, summary = run_bookstore_simulation(
        num_customers=8,
        num_employees=3,
        steps=150,
        random_seed=42
    )
    
    print("\n" + "=" * 60)
    print("📊 SIMULATION SUMMARY")
    print("=" * 60)
    
    print(f"💰 Total Sales: ${summary['financial_metrics']['total_sales']:.2f}")
    print(f"📚 Books Sold: {summary['financial_metrics']['total_books_sold']}")
    print(f"😊 Customer Satisfaction: {summary['customer_metrics']['average_satisfaction']:.2f}")
    print(f"💬 Messages Exchanged: {summary['communication_metrics']['total_messages']}")
    print(f"⏱️  Simulation Time: {summary['simulation_info']['simulation_time_seconds']:.2f}s")