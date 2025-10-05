

import sys
import os
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ontology import BookstoreOntology
from message_bus import MessageBus, get_message_bus
from simulation import run_bookstore_simulation

def simple_ontology_demo():
    
    print("\n🔍 ONTOLOGY DEMONSTRATION")
    print("-" * 50)
    
    # Create ontology
    ontology = BookstoreOntology()
    ontology.create_sample_data()
    
    # Show books
    books = ontology.get_all_books()
    print(f"📚 Available Books ({len(books)}):")
    for book in books:
        title = getattr(book, 'bookTitle', 'Unknown')
        price = getattr(book, 'hasPrice', 0)
        
        # Get stock
        stock = 0
        if hasattr(book, 'hasInventory') and book.hasInventory:
            stock = getattr(book.hasInventory[0], 'availableQuantity', 0)
        
        print(f"   📖 '{title}' - ${price:.2f} ({stock} in stock)")
    
    # Show customers
    customers = ontology.get_all_customers()
    print(f"\n👥 Customers ({len(customers)}):")
    for customer in customers:
        name = getattr(customer, 'customerName', 'Unknown')
        budget = getattr(customer, 'customerBudget', 0)
        print(f"   👤 {name}: ${budget:.2f} budget")
    
    # Show employees
    employees = ontology.get_all_employees()
    print(f"\n👔 Employees ({len(employees)}):")
    for employee in employees:
        name = getattr(employee, 'employeeName', 'Unknown')
        role = getattr(employee, 'employeeRole', 'Unknown')
        print(f"   🧑‍💼 {name}: {role}")
    
    # Check restock needs
    restock_needed = ontology.check_restock_needed()
    if restock_needed:
        print(f"\n⚠️  Items needing restock: {len(restock_needed)}")
    else:
        print("\n✅ All inventory levels adequate")

def simple_simulation_demo():
    
    print("\n🚀 SIMULATION DEMONSTRATION")
    print("-" * 50)
    
    print("Starting simulation with:")
    print("  👥 5 customers")
    print("  👔 2 employees") 
    print("  📚 4 books")
    print("  ⏱️  50 simulation steps")
    
    # Run simulation
    model, summary = run_bookstore_simulation(
        num_customers=5,
        num_employees=2,
        steps=50,
        random_seed=42
    )
    
    # Show key results
    print(f"\n📊 SIMULATION RESULTS:")
    print(f"   💰 Total Sales: ${summary['financial_metrics']['total_sales']:.2f}")
    print(f"   📚 Books Sold: {summary['financial_metrics']['total_books_sold']}")
    print(f"   😊 Customer Satisfaction: {summary['customer_metrics']['average_satisfaction']:.2f}")
    print(f"   💬 Messages Exchanged: {summary['communication_metrics']['total_messages']}")
    
    # Show best-selling book
    books = summary['inventory_metrics']['book_details']
    if books:
        best_seller = max(books, key=lambda x: x['sales_count'])
        print(f"   🏆 Best Seller: '{best_seller['title']}' ({best_seller['sales_count']} sales)")
    
    # Show top customer
    customers = summary['customer_metrics']['customer_details']
    if customers:
        top_customer = max(customers, key=lambda x: x['total_spent'])
        print(f"   🥇 Top Customer: {top_customer['name']} (${top_customer['total_spent']:.2f} spent)")

def interactive_demo():
    
    print("\n🎮 INTERACTIVE DEMONSTRATION")
    print("-" * 50)
    
    while True:
        print("\nChoose an option:")
        print("1. 🔍 Inspect Ontology")
        print("2. 🚀 Run Quick Simulation")
        print("3. 🎯 Run Custom Simulation")
        print("4. 🧪 Run System Tests")
        print("5. 🌐 Launch Web Interface")
        print("6. ❌ Exit")
        
        try:
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                simple_ontology_demo()
            
            elif choice == "2":
                simple_simulation_demo()
            
            elif choice == "3":
                print("\nCustom Simulation Parameters:")
                try:
                    customers = int(input("Number of customers (1-20): ") or "8")
                    employees = int(input("Number of employees (1-5): ") or "3")
                    steps = int(input("Simulation steps (10-200): ") or "100")
                    
                    print(f"\nRunning simulation with {customers} customers, {employees} employees, {steps} steps...")
                    model, summary = run_bookstore_simulation(customers, employees, steps, 42)
                    
                    print(f"💰 Sales: ${summary['financial_metrics']['total_sales']:.2f}")
                    print(f"📚 Books Sold: {summary['financial_metrics']['total_books_sold']}")
                    print(f"😊 Satisfaction: {summary['customer_metrics']['average_satisfaction']:.2f}")
                    
                except ValueError:
                    print("❌ Invalid input. Using default values.")
                    simple_simulation_demo()
            
            elif choice == "4":
                print("\n🧪 Running system tests...")
                from test_system import run_tests
                run_tests()
            
            elif choice == "5":
                print("\n🌐 Launching web interface...")
                print("💡 Run: python app.py")
                print("   Then open: http://localhost:8050")
                break
            
            elif choice == "6":
                print("\n👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    
    print("=" * 70)
    print("📚 BOOKSTORE MANAGEMENT SYSTEM - SIMPLE EXAMPLE")
    print("   Multi-Agent System with Ontology-Based Reasoning")
    print("=" * 70)
    
    print("\nThis example demonstrates the core functionality:")
    print("  🧠 Ontology-based knowledge representation")
    print("  🤖 Intelligent agent behaviors")
    print("  💬 Message-based communication")
    print("  📊 Real-time simulation and monitoring")
    
    try:
        # Check if user wants interactive mode
        if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
            interactive_demo()
        else:
            # Run automatic demonstration
            simple_ontology_demo()
            time.sleep(2)
            simple_simulation_demo()
            
            print("\n" + "=" * 70)
            print("🎉 DEMONSTRATION COMPLETE!")
            print("\nTo explore further:")
            print("  🎮 Interactive mode: python example.py --interactive")
            print("  🌐 Web interface:    python app.py")
            print("  💻 CLI simulation:   python app.py --mode cli")
            print("  🧪 Run tests:        python test_system.py")
            
    except KeyboardInterrupt:
        print("\n\n👋 Example interrupted by user")
    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n👋 Thank you for trying the Bookstore Management System!")

if __name__ == "__main__":
    main()