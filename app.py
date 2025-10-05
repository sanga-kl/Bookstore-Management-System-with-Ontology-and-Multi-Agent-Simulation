import argparse
import sys
import os
from typing import Dict, Any
import json
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ontology import BookstoreOntology
from message_bus import MessageBus, get_message_bus
from simulation import BookstoreModel, run_bookstore_simulation
from dashboard import create_dashboard
from agents import CustomerAgent, EmployeeAgent, BookAgent


class BookstoreApp:
    
    def __init__(self):
        self.ontology = None
        self.message_bus = None
        self.model = None
        self.dashboard = None
        
    def initialize_system(self):
        print("🔧 Initializing Bookstore Management System...")
        
        try:
            # Initialize ontology
            print("📚 Loading ontology...")
            self.ontology = BookstoreOntology()
            self.ontology.create_sample_data()
            print("✅ Ontology loaded successfully")
            
            # Initialize message bus
            print("💬 Starting message bus...")
            self.message_bus = get_message_bus()
            self.message_bus.start()
            print("✅ Message bus started")
            
            print("🎉 System initialization complete!")
            return True
            
        except Exception as e:
            print(f"❌ System initialization failed: {e}")
            return False
    
    def run_cli_simulation(self, args):
        print("\n🚀 Starting CLI Simulation Mode")
        print("-" * 50)
        
        try:
            model, summary = run_bookstore_simulation(
                num_customers=args.customers,
                num_employees=args.employees,
                steps=args.steps,
                random_seed=args.seed
            )
            
            self.print_simulation_results(summary)
            
            if args.output:
                self.save_results(summary, args.output)
                
            return True
            
        except Exception as e:
            print(f"❌ Simulation failed: {e}")
            return False
    
    def run_web_interface(self, args):
        print("\n🌐 Starting Web Interface Mode")
        print("-" * 50)
        
        try:
            self.dashboard = create_dashboard()
            print(f"🌟 Dashboard will be available at: http://localhost:{args.port}")
            print("Use the web interface to control the simulation")
            print("⏹Press Ctrl+C to stop the server")
            
            self.dashboard.run_server(debug=args.debug, port=args.port)
            return True
            
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
            return True
        except Exception as e:
            print(f"❌ Web interface failed: {e}")
            return False
    
    def print_simulation_results(self, summary: Dict[str, Any]):
        print("\n" + "="*80)
        print("🏪 BOOKSTORE MANAGEMENT SYSTEM - SIMULATION RESULTS")
        print("="*80)
        
        # Simulation Overview
        sim_info = summary["simulation_info"]
        print(f"\n📊 SIMULATION OVERVIEW")
        print(f"   Status: {sim_info.get('simulation_status', 'completed').upper()}")
        print(f"   Steps Completed: {sim_info['steps_completed']}")
        print(f"   Simulation Time: {sim_info['simulation_time_seconds']:.2f} seconds")
        print(f"   Performance: {sim_info.get('steps_per_second', 0):.2f} steps/second")
        print(f"   Total Agents: {sim_info['agents_total']}")
        
        # Financial Metrics
        financial = summary["financial_metrics"]
        print(f"\n💰 FINANCIAL PERFORMANCE")
        print(f"   Total Sales: ${financial['total_sales']:.2f}")
        print(f"   Books Sold: {financial['total_books_sold']}")
        print(f"   Average Book Price: ${financial['average_book_price']:.2f}")
        print(f"   Total Budget Spent: ${financial.get('total_budget_spent', 0):.2f}")
        print(f"   Purchase Rate: {financial.get('purchase_rate_per_step', 0):.3f} books/step")
        
        # Customer Metrics
        customers = summary["customer_metrics"]
        print(f"\n👥 CUSTOMER ANALYTICS")
        print(f"   Total Customers: {customers['total_customers']}")
        print(f"   Average Satisfaction: {customers['average_satisfaction']:.2f}/10")
        print(f"   Average Budget Remaining: ${customers['average_budget_remaining']:.2f}")
        print(f"   Customer Engagement Rate: {customers.get('customer_engagement_rate', 0):.1%}")
        
        # Employee Metrics
        employees = summary["employee_metrics"]
        print(f"\n👨‍💼 EMPLOYEE PERFORMANCE")
        print(f"   Total Employees: {employees['total_employees']}")
        print(f"   Orders Processed: {employees['total_orders_processed']}")
        print(f"   Average Efficiency: {employees.get('average_efficiency', 0):.2f}/10")
        
        # Inventory Metrics
        inventory = summary["inventory_metrics"]
        print(f"\n📚 INVENTORY STATUS")
        print(f"   Total Books: {inventory['total_books']}")
        print(f"   Stock Remaining: {inventory['total_stock_remaining']}")
        print(f"   Average Popularity: {inventory.get('average_popularity', 0):.2f}/10")
        print(f"   Inventory Turnover: {inventory.get('inventory_turnover', 0):.1%}")
        
        # Communication Metrics
        comm = summary["communication_metrics"]
        print(f"\n📡 COMMUNICATION STATS")
        print(f"   Total Messages: {comm['total_messages']}")
        print(f"   Messages per Step: {comm.get('messages_per_step', 0):.2f}")
        print(f"   Active Agents: {comm['active_agents']}")
        
        # Performance Metrics
        if 'performance_metrics' in summary:
            perf = summary["performance_metrics"]
            print(f"\n⚡ SYSTEM PERFORMANCE")
            print(f"   Simulation Efficiency: {perf['simulation_efficiency']:.2f} steps/sec")
            print(f"   Agent Density: {perf['agent_density']:.3f} agents/step")
            print(f"   System Utilization: {perf['system_utilization']:.3f} messages/agent/step")
        
        # Top Performers
        print(f"\n🏆 TOP PERFORMERS")
        
        # Top customers by spending
        if customers.get('customer_details'):
            top_customers = sorted(customers['customer_details'], 
                                 key=lambda x: x.get('total_spent', 0), reverse=True)[:3]
            print(f"   Top Spending Customers:")
            for i, customer in enumerate(top_customers, 1):
                name = customer.get('name', f"Customer {customer.get('agent_id', i)}")
                spent = customer.get('total_spent', 0)
                print(f"     {i}. {name}: ${spent:.2f} spent")
        
        # Top employees by efficiency or orders
        if employees.get('employee_details'):
            employee_details = employees['employee_details']
            # Sort by efficiency if available, otherwise by orders processed
            if any('efficiency' in emp for emp in employee_details):
                top_employees = sorted(employee_details, 
                                     key=lambda x: x.get('efficiency', 0), reverse=True)[:3]
                print(f"   Most Efficient Employees:")
                for i, employee in enumerate(top_employees, 1):
                    name = employee.get('name', f"Employee {employee.get('agent_id', i)}")
                    efficiency = employee.get('efficiency', 0)
                    print(f"     {i}. {name}: {efficiency:.2f}/10 efficiency")
            else:
                top_employees = sorted(employee_details, 
                                     key=lambda x: len(x.get('orders_processed', [])), reverse=True)[:3]
                print(f"   Most Active Employees:")
                for i, employee in enumerate(top_employees, 1):
                    name = employee.get('name', f"Employee {employee.get('agent_id', i)}")
                    orders = len(employee.get('orders_processed', []))
                    print(f"     {i}. {name}: {orders} orders processed")
        
        # Top books by sales or popularity
        if inventory.get('book_details'):
            book_details = inventory['book_details']
            # Sort by sales count if available, otherwise by popularity
            if any('sales_count' in book for book in book_details):
                top_books = sorted(book_details, 
                                 key=lambda x: x.get('sales_count', 0), reverse=True)[:5]
                print(f"   Best Selling Books:")
                for i, book in enumerate(top_books, 1):
                    title = book.get('title', f"Book {i}")
                    sales = book.get('sales_count', 0)
                    print(f"     {i}. {title}: {sales} sales")
            elif any('popularity_score' in book for book in book_details):
                top_books = sorted(book_details, 
                                 key=lambda x: x.get('popularity_score', 0), reverse=True)[:5]
                print(f"   Most Popular Books:")
                for i, book in enumerate(top_books, 1):
                    title = book.get('title', f"Book {i}")
                    popularity = book.get('popularity_score', 0)
                    print(f"     {i}. {title}: {popularity:.2f}/10 popularity")
        
        # System Health
        print(f"\n🏥 SYSTEM HEALTH")
        # Calculate health score based on available metrics
        satisfaction_score = min(100, customers['average_satisfaction'] * 10)
        efficiency_score = min(100, employees.get('average_efficiency', 5) * 10)
        popularity_score = min(100, inventory.get('average_popularity', 5) * 10)
        performance_score = min(100, sim_info.get('steps_per_second', 1) * 10)
        
        health_score = (satisfaction_score + efficiency_score + popularity_score + performance_score) / 4
        print(f"   Overall System Health: {health_score:.1f}/100")
        
        if health_score >= 80:
            print(f"   Status: � EXCELLENT - System performing optimally")
        elif health_score >= 60:
            print(f"   Status: 🟡 GOOD - System performing well")
        elif health_score >= 40:
            print(f"   Status: 🟠 FAIR - Some areas need improvement")
        else:
            print(f"   Status: 🔴 POOR - System needs attention")
        
        # Message Type Breakdown
        if comm.get('message_types'):
            print(f"\n📨 MESSAGE TYPE BREAKDOWN")
            for msg_type, count in comm['message_types'].items():
                percentage = (count / comm['total_messages']) * 100 if comm['total_messages'] > 0 else 0
                print(f"   {msg_type}: {count} ({percentage:.1f}%)")
        
        print("\n" + "="*80)
        print("📋 SIMULATION COMPLETE - Thank you for using the Bookstore Management System!")
        print("="*80 + "\n")
    
    def save_results(self, summary: Dict[str, Any], filename: str):
        try:
            # Add timestamp to summary
            summary['export_timestamp'] = datetime.now().isoformat()
            
            with open(filename, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            print(f"💾 Results saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
    
    def inspect_ontology(self):
        print("\n🔍 ONTOLOGY INSPECTION")
        print("-" * 50)
        
        if not self.ontology:
            print("❌ No ontology loaded")
            return
        
        try:
            # Books
            books = self.ontology.get_all_books()
            print(f"📚 Books ({len(books)}):")
            for book in books:
                title = getattr(book, 'bookTitle', 'Unknown')
                price = getattr(book, 'hasPrice', 0)
                isbn = getattr(book, 'isbn', 'Unknown')
                
                # Get inventory
                stock = 0
                if hasattr(book, 'hasInventory') and book.hasInventory:
                    inventory = book.hasInventory[0]
                    stock = getattr(inventory, 'availableQuantity', 0)
                
                print(f"   - '{title}' (${price:.2f}) - Stock: {stock} - ISBN: {isbn}")
            
            # Customers
            customers = self.ontology.get_all_customers()
            print(f"\n👥 Customers ({len(customers)}):")
            for customer in customers:
                name = getattr(customer, 'customerName', 'Unknown')
                budget = getattr(customer, 'customerBudget', 0)
                print(f"   - {name}: Budget ${budget:.2f}")
            
            # Employees
            employees = self.ontology.get_all_employees()
            print(f"\n👔 Employees ({len(employees)}):")
            for employee in employees:
                name = getattr(employee, 'employeeName', 'Unknown')
                role = getattr(employee, 'employeeRole', 'Unknown')
                print(f"   - {name}: {role}")
            
            # Inventory status
            restock_needed = self.ontology.check_restock_needed()
            if restock_needed:
                print(f"\n⚠️  Items needing restock ({len(restock_needed)}):")
                for inv in restock_needed:
                    qty = getattr(inv, 'availableQuantity', 0)
                    reorder = getattr(inv, 'reorderLevel', 0)
                    print(f"   - Item with {qty} units (reorder at {reorder})")
            else:
                print("\n✅ All inventory levels are adequate")
                
        except Exception as e:
            print(f"❌ Error inspecting ontology: {e}")
    
    def cleanup(self):
        print("\n🧹 Cleaning up system resources...")
        
        if self.model:
            self.model.cleanup()
        
        if self.message_bus and self.message_bus.running:
            self.message_bus.stop()
        
        print("✅ Cleanup completed")


def main():
    parser = argparse.ArgumentParser(
        description="Bookstore Management System - Multi-Agent Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run web interface (default)
  python app.py

  # Run CLI simulation with custom parameters
  python app.py --mode cli --customers 15 --employees 4 --steps 200

  # Save results to file
  python app.py --mode cli --output results.json

  # Inspect ontology only
  python app.py --mode inspect
        """ 
    )
    
    parser.add_argument(
        '--mode', 
        choices=['web', 'cli', 'inspect'],
        default='web',
        help='Application mode (default: web)'
    )
    
    # Web interface options
    parser.add_argument(
        '--port',
        type=int,
        default=8050,
        help='Port for web interface (default: 8050)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode for web interface'
    )
    
    # CLI simulation options
    parser.add_argument(
        '--customers',
        type=int,
        default=10,
        help='Number of customer agents (default: 10)'
    )
    
    parser.add_argument(
        '--employees',
        type=int,
        default=3,
        help='Number of employee agents (default: 3)'
    )
    
    parser.add_argument(
        '--steps',
        type=int,
        default=100,
        help='Number of simulation steps (default: 100)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file for simulation results (CLI mode only)'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print("=" * 80)
    print("📚 BOOKSTORE MANAGEMENT SYSTEM")
    print("   Multi-Agent System with Ontology-Based Reasoning")
    print("=" * 80)
    
    # Create application instance
    app = BookstoreApp()
    
    try:
        # Initialize system
        if not app.initialize_system():
            sys.exit(1)
        
        # Run based on mode
        success = False
        if args.mode == 'web':
            success = app.run_web_interface(args)
        elif args.mode == 'cli':
            success = app.run_cli_simulation(args)
        elif args.mode == 'inspect':
            app.inspect_ontology()
            success = True
        
        if not success:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted by user")
    except Exception as e:
        print(f"❌ Application error: {e}")
        sys.exit(1)
    finally:
        app.cleanup()
    
    print("\n👋 Thank you for using Bookstore Management System!")


if __name__ == "__main__":
    main()