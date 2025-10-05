

import unittest
import time
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ontology import BookstoreOntology
from message_bus import MessageBus, MessageType, Message, AgentCommunicator
from agents import CustomerAgent, EmployeeAgent, BookAgent
from simulation import BookstoreModel

class TestOntology(unittest.TestCase):

    def setUp(self):
        self.ontology = BookstoreOntology()
        self.ontology.create_sample_data()
    
    def test_ontology_creation(self):
        
        self.assertIsNotNone(self.ontology.onto)
    
    def test_book_creation(self):
        
        books = self.ontology.get_all_books()
        self.assertGreater(len(books), 0)
        
        # Check first book has required properties
        book = books[0]
        self.assertTrue(hasattr(book, 'bookTitle'))
        self.assertTrue(hasattr(book, 'hasPrice'))
    
    def test_inventory_management(self):
        
        books = self.ontology.get_all_books()
        if books:
            book = books[0]
            if hasattr(book, 'isbn'):
                original_quantity = None
                if hasattr(book, 'hasInventory') and book.hasInventory:
                    original_quantity = book.hasInventory[0].availableQuantity
                
                # Update inventory
                self.ontology.update_inventory_quantity(book.isbn, 50)
                
                # Verify update
                if book.hasInventory:
                    new_quantity = book.hasInventory[0].availableQuantity
                    self.assertEqual(new_quantity, 50)
    
    def test_restock_check(self):
        
        restock_needed = self.ontology.check_restock_needed()
        self.assertIsInstance(restock_needed, list)

class TestMessageBus(unittest.TestCase):

    def setUp(self):
        self.message_bus = MessageBus()
        self.message_bus.start()
        time.sleep(0.1)  # Allow startup
    
    def tearDown(self):
        self.message_bus.stop()
    
    def test_message_bus_startup(self):
        
        self.assertTrue(self.message_bus.running)
    
    def test_agent_communication(self):
        
        comm1 = AgentCommunicator("test_agent_1", self.message_bus)
        comm2 = AgentCommunicator("test_agent_2", self.message_bus)
        
        # Send message
        comm1.send_message(
            MessageType.PURCHASE_REQUEST,
            {"book": "test_book", "quantity": 1},
            "test_agent_2"
        )
        
        time.sleep(0.1)  # Allow message processing
        
        # Check received messages
        messages = comm2.get_messages(timeout=0.1)
        self.assertGreater(len(messages), 0)
        
        message = messages[0]
        self.assertEqual(message.message_type, MessageType.PURCHASE_REQUEST)
        self.assertEqual(message.sender_id, "test_agent_1")
        
        # Cleanup
        comm1.cleanup()
        comm2.cleanup()
    
    def test_broadcast_communication(self):
        
        comm1 = AgentCommunicator("broadcaster", self.message_bus)
        comm2 = AgentCommunicator("receiver1", self.message_bus)
        comm3 = AgentCommunicator("receiver2", self.message_bus)
        
        # Broadcast message
        comm1.broadcast(MessageType.SYSTEM_ALERT, {"alert": "test_alert"})
        
        time.sleep(0.1)  # Allow message processing
        
        # Check both receivers got the message
        messages2 = comm2.get_messages(timeout=0.1)
        messages3 = comm3.get_messages(timeout=0.1)
        
        self.assertGreater(len(messages2), 0)
        self.assertGreater(len(messages3), 0)
        
        # Cleanup
        comm1.cleanup()
        comm2.cleanup()
        comm3.cleanup()

class TestAgents(unittest.TestCase):

    def setUp(self):
        self.ontology = BookstoreOntology()
        self.ontology.create_sample_data()
        
        self.message_bus = MessageBus()
        self.message_bus.start()
        time.sleep(0.1)
    
    def tearDown(self):
        self.message_bus.stop()
    
    def test_customer_agent_creation(self):
        
        customer = CustomerAgent(
            unique_id="test_customer",
            model=None,
            ontology=self.ontology,
            message_bus=self.message_bus,
            name="Test Customer",
            budget=100.0
        )
        
        self.assertEqual(customer.name, "Test Customer")
        self.assertEqual(customer.budget, 100.0)
        self.assertIsNotNone(customer.onto_customer)
        
        customer.cleanup()
    
    def test_employee_agent_creation(self):
        
        employee = EmployeeAgent(
            unique_id="test_employee",
            model=None,
            ontology=self.ontology,
            message_bus=self.message_bus,
            name="Test Employee",
            role="Manager"
        )
        
        self.assertEqual(employee.name, "Test Employee")
        self.assertEqual(employee.role, "Manager")
        
        employee.cleanup()
    
    def test_book_agent_creation(self):
        
        books = self.ontology.get_all_books()
        if books:
            book_obj = books[0]
            book_agent = BookAgent(
                unique_id="test_book",
                model=None,
                ontology=self.ontology,
                message_bus=self.message_bus,
                book_obj=book_obj
            )
            
            self.assertIsNotNone(book_agent.title)
            self.assertGreater(book_agent.price, 0)
            
            book_agent.cleanup()

class TestSimulation(unittest.TestCase):

    def setUp(self):
        # Use small parameters for faster testing
        self.model = BookstoreModel(
            num_customers=2,
            num_employees=1,
            random_seed=42
        )
    
    def tearDown(self):
        if self.model:
            self.model.cleanup()
    
    def test_model_creation(self):
        
        self.assertIsNotNone(self.model)
        self.assertGreater(len(self.model.agents), 0)
    
    def test_simulation_step(self):
        
        initial_step = self.model.step_count
        self.model.step()
        self.assertEqual(self.model.step_count, initial_step + 1)
    
    def test_data_collection(self):
        
        # Run a few steps
        for _ in range(5):
            self.model.step()
        
        # Check data collection
        data = self.model.datacollector.get_model_vars_dataframe()
        self.assertGreater(len(data), 0)
    
    def test_simulation_summary(self):
        
        # Run simulation for a few steps
        for _ in range(10):
            self.model.step()
        
        summary = self.model.get_simulation_summary()
        
        # Check summary structure
        self.assertIn('simulation_info', summary)
        self.assertIn('financial_metrics', summary)
        self.assertIn('customer_metrics', summary)
        self.assertIn('employee_metrics', summary)
        self.assertIn('inventory_metrics', summary)
        self.assertIn('communication_metrics', summary)

class TestIntegration(unittest.TestCase):

    def test_full_system_integration(self):
        
        try:
            # Create model
            model = BookstoreModel(
                num_customers=3,
                num_employees=2,
                random_seed=42
            )
            
            # Run for a few steps
            for _ in range(20):
                model.step()
            
            # Verify system is functioning
            summary = model.get_simulation_summary()
            
            # Basic assertions
            self.assertGreater(summary['simulation_info']['steps_completed'], 0)
            self.assertGreaterEqual(summary['financial_metrics']['total_sales'], 0)
            self.assertGreater(summary['customer_metrics']['total_customers'], 0)
            self.assertGreater(summary['employee_metrics']['total_employees'], 0)
            self.assertGreater(summary['inventory_metrics']['total_books'], 0)
            
            print(f"Integration test passed - {summary['simulation_info']['steps_completed']} steps completed")
            print(f"Total sales: ${summary['financial_metrics']['total_sales']:.2f}")
            print(f"Messages exchanged: {summary['communication_metrics']['total_messages']}")
            
        finally:
            if 'model' in locals():
                model.cleanup()

def run_tests():
    
    print("🧪 Running Bookstore Management System Tests")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestOntology,
        TestMessageBus,
        TestAgents,
        TestSimulation,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)