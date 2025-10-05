

import threading
import queue
import time
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
from enum import Enum

class MessageType(Enum):
    
    PURCHASE_REQUEST = "purchase_request"
    PURCHASE_COMPLETED = "purchase_completed"
    INVENTORY_UPDATE = "inventory_update"
    RESTOCK_REQUEST = "restock_request"
    RESTOCK_COMPLETED = "restock_completed"
    ORDER_CREATED = "order_created"
    ORDER_PROCESSED = "order_processed"
    CUSTOMER_INQUIRY = "customer_inquiry"
    EMPLOYEE_ACTION = "employee_action"
    SYSTEM_ALERT = "system_alert"

@dataclass
class Message:
    
    message_type: MessageType
    sender_id: str
    recipient_id: str = None  # None means broadcast
    content: Dict[str, Any] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.content is None:
            self.content = {}

class MessageBus:

    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[Message], None]]] = {}
        self.message_history: List[Message] = []
        self.lock = threading.Lock()
        self.running = False
        self.message_queue = queue.Queue()
        self.processor_thread = None
        
    def start(self):
        
        self.running = True
        self.processor_thread = threading.Thread(target=self._process_messages)
        self.processor_thread.daemon = True
        self.processor_thread.start()
        print("Message bus started")
    
    def stop(self):
        
        self.running = False
        if self.processor_thread:
            self.processor_thread.join(timeout=1.0)
        print("Message bus stopped")
    
    def subscribe(self, agent_id: str, callback: Callable[[Message], None]):
        
        with self.lock:
            if agent_id not in self.subscribers:
                self.subscribers[agent_id] = []
            self.subscribers[agent_id].append(callback)
        print(f"Agent {agent_id} subscribed to message bus")
    
    def unsubscribe(self, agent_id: str, callback: Callable[[Message], None] = None):
        
        with self.lock:
            if agent_id in self.subscribers:
                if callback:
                    if callback in self.subscribers[agent_id]:
                        self.subscribers[agent_id].remove(callback)
                else:
                    del self.subscribers[agent_id]
        print(f"Agent {agent_id} unsubscribed from message bus")
    
    def send_message(self, message: Message):
        
        self.message_queue.put(message)
    
    def _process_messages(self):
        
        while self.running:
            try:
                message = self.message_queue.get(timeout=0.1)
                self._deliver_message(message)
                self.message_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing message: {e}")
    
    def _deliver_message(self, message: Message):
        
        with self.lock:
            # Store message in history
            self.message_history.append(message)
            
            # Keep only last 1000 messages
            if len(self.message_history) > 1000:
                self.message_history = self.message_history[-1000:]
            
            # Deliver to specific recipient or broadcast
            if message.recipient_id:
                # Point-to-point delivery
                if message.recipient_id in self.subscribers:
                    for callback in self.subscribers[message.recipient_id]:
                        try:
                            callback(message)
                        except Exception as e:
                            print(f"Error delivering message to {message.recipient_id}: {e}")
            else:
                # Broadcast delivery (exclude sender)
                for agent_id, callbacks in self.subscribers.items():
                    if agent_id != message.sender_id:  # Don't send to sender
                        for callback in callbacks:
                            try:
                                callback(message)
                            except Exception as e:
                                print(f"Error broadcasting message to {agent_id}: {e}")
    
    def get_message_history(self, agent_id: str = None, message_type: MessageType = None, 
                           since: float = None, limit: int = 100) -> List[Message]:
        
        with self.lock:
            filtered_messages = self.message_history.copy()
            
            # Filter by agent
            if agent_id:
                filtered_messages = [
                    msg for msg in filtered_messages 
                    if msg.sender_id == agent_id or msg.recipient_id == agent_id
                ]
            
            # Filter by message type
            if message_type:
                filtered_messages = [
                    msg for msg in filtered_messages 
                    if msg.message_type == message_type
                ]
            
            # Filter by timestamp
            if since:
                filtered_messages = [
                    msg for msg in filtered_messages 
                    if msg.timestamp >= since
                ]
            
            # Apply limit
            return filtered_messages[-limit:] if limit else filtered_messages
    
    def get_stats(self) -> Dict[str, Any]:
        
        with self.lock:
            stats = {
                "total_messages": len(self.message_history),
                "subscribers": len(self.subscribers),
                "message_types": {},
                "active_agents": list(self.subscribers.keys())
            }
            
            # Count messages by type
            for message in self.message_history:
                msg_type = message.message_type.value
                stats["message_types"][msg_type] = stats["message_types"].get(msg_type, 0) + 1
            
            return stats

class AgentCommunicator:

    def __init__(self, agent_id: str, message_bus: MessageBus):
        self.agent_id = agent_id
        self.message_bus = message_bus
        self.received_messages = queue.Queue()
        
        # Subscribe to the message bus
        self.message_bus.subscribe(agent_id, self._on_message_received)
    
    def _on_message_received(self, message: Message):
        
        self.received_messages.put(message)
    
    def send_message(self, message_type: MessageType, content: Dict[str, Any], 
                    recipient_id: str = None):
        
        message = Message(
            message_type=message_type,
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            content=content
        )
        self.message_bus.send_message(message)
    
    def get_messages(self, timeout: float = None) -> List[Message]:
        
        messages = []
        try:
            while True:
                message = self.received_messages.get(timeout=timeout)
                messages.append(message)
                self.received_messages.task_done()
                timeout = 0  # Only wait for the first message
        except queue.Empty:
            pass
        return messages
    
    def broadcast(self, message_type: MessageType, content: Dict[str, Any]):
        
        self.send_message(message_type, content, recipient_id=None)
    
    def send_purchase_request(self, book_isbn: str, quantity: int):
        
        self.send_message(
            MessageType.PURCHASE_REQUEST,
            {"book_isbn": book_isbn, "quantity": quantity}
        )
    
    def send_restock_request(self, book_isbn: str, quantity: int):
        
        self.send_message(
            MessageType.RESTOCK_REQUEST,
            {"book_isbn": book_isbn, "quantity": quantity}
        )
    
    def send_inventory_update(self, book_isbn: str, new_quantity: int):
        
        self.broadcast(
            MessageType.INVENTORY_UPDATE,
            {"book_isbn": book_isbn, "new_quantity": new_quantity}
        )
    
    def cleanup(self):
        
        self.message_bus.unsubscribe(self.agent_id)

# Global message bus instance
global_message_bus = MessageBus()

def get_message_bus() -> MessageBus:
    
    return global_message_bus

if __name__ == "__main__":
    # Test the message bus
    bus = MessageBus()
    bus.start()
    
    # Create test communicators
    comm1 = AgentCommunicator("agent1", bus)
    comm2 = AgentCommunicator("agent2", bus)
    
    # Send test messages
    comm1.send_message(MessageType.PURCHASE_REQUEST, {"book": "test_book"}, "agent2")
    comm2.broadcast(MessageType.INVENTORY_UPDATE, {"book": "test_book", "quantity": 10})
    
    time.sleep(0.1)  # Allow processing
    
    # Check received messages
    messages1 = comm1.get_messages(0.1)
    messages2 = comm2.get_messages(0.1)
    
    print(f"Agent1 received {len(messages1)} messages")
    print(f"Agent2 received {len(messages2)} messages")
    print(f"Bus stats: {bus.get_stats()}")
    
    # Cleanup
    comm1.cleanup()
    comm2.cleanup()
    bus.stop()