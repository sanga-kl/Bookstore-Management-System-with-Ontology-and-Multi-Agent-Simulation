# 📚 Bookstore Management System (BMS)

A comprehensive **Multi-Agent System (MAS)** implementation using ontology-based reasoning for simulating bookstore operations. This system demonstrates complex interactions between customers, employees, and inventory through intelligent agents.

## 🎯 Project Overview

This project implements a **Bookstore Management System** using:
- **Owlready2** for ontology creation and management
- **Mesa** framework for agent-based modeling
- **Flask/Dash** for web-based visualization and control
- **SWRL-style rules** implemented in agent logic
- **Message Bus Architecture** for agent communication

## 🏗️ System Architecture

### Core Components

1. **Ontology Layer** (`ontology.py`)
   - Defines semantic structure for bookstore entities
   - Classes: Book, Customer, Employee, Order, Inventory, Genre, Author
   - Properties: hasAuthor, hasGenre, hasPrice, purchases, worksAt, etc.
   - Data persistence and reasoning capabilities

2. **Agent Layer** (`agents.py`)
   - **CustomerAgent**: Browses, selects, and purchases books
   - **EmployeeAgent**: Manages inventory, processes orders, handles restocking
   - **BookAgent**: Tracks popularity, sales, and suggests promotions

3. **Communication Layer** (`message_bus.py`)
   - Central message bus for agent communication
   - Point-to-point and broadcast messaging
   - Message types: purchase_request, restock_request, inventory_update, etc.

4. **Simulation Layer** (`simulation.py`)
   - Mesa-based model orchestrating all agents
   - Data collection and metrics tracking
   - Configurable simulation parameters

5. **Interface Layer** (`dashboard.py`, `app.py`)
   - Web-based dashboard with real-time monitoring
   - CLI interface for batch simulations
   - Data visualization and export capabilities

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Virtual environment (recommended)

### Installation

1. **Clone/Download the project**
```bash
cd BookManagement
```

2. **Create virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Running the System

#### 🌐 Web Interface (Recommended)
```bash
python app.py
```
Open your browser to `http://localhost:8050`

#### 💻 Command Line Interface
```bash
# Basic simulation
python app.py --mode cli

# Custom parameters
python app.py --mode cli --customers 15 --employees 4 --steps 200

# Save results
python app.py --mode cli --output simulation_results.json
```

#### 🔍 Ontology Inspection
```bash
python app.py --mode inspect
```

## 🎮 Using the Web Dashboard

The web interface provides comprehensive control and monitoring:

### Control Panel
- **Simulation Parameters**: Set number of customers, employees, and steps
- **Control Buttons**: Start, Pause, Stop, Reset simulation
- **Auto-refresh**: Toggle real-time updates

### Monitoring Features
- **Real-time Metrics**: Sales, satisfaction, inventory levels
- **Interactive Charts**: Sales trends, agent activity
- **Data Tables**: Customer details, inventory status
- **Message Log**: Live agent communication feed

### Key Metrics Displayed
- 💰 Total sales revenue
- 📚 Number of books sold
- 😊 Average customer satisfaction
- 💬 Message exchange count
- 📊 Inventory levels and stock alerts

## 🤖 Agent Behaviors

### Customer Agents
- **Browsing**: Randomly explore available books
- **Decision Making**: Consider budget, preferences, and availability
- **Purchasing**: Complete transactions and update inventory
- **Adaptation**: Adjust behavior based on satisfaction and budget

### Employee Agents
- **Inventory Management**: Monitor stock levels and reorder
- **Order Processing**: Handle customer purchases
- **Role-specific Actions**:
  - **Managers**: Send system alerts, oversee operations
  - **Sales Associates**: Process orders, assist customers
  - **Inventory Specialists**: Focus on restocking and stock management

### Book Agents
- **Popularity Tracking**: Monitor sales and demand trends
- **Trend Analysis**: Adjust popularity scores based on sales
- **Promotion Suggestions**: Recommend books for marketing

## 📊 Implemented SWRL-Style Rules

The system implements business logic through agent behaviors that mirror SWRL rules:

1. **Purchase Rule**: 
   - IF customer has sufficient budget AND book is in stock 
   - THEN complete purchase and update inventory

2. **Restock Rule**:
   - IF inventory quantity < reorder level 
   - THEN trigger restock request

3. **Order Processing Rule**:
   - IF order status is "pending" AND employee is available
   - THEN process order

4. **Satisfaction Rule**:
   - IF customer successfully purchases desired book
   - THEN increase satisfaction score

## 💬 Message Bus Communication

The system uses a sophisticated message bus for agent coordination:

### Message Types
- `PURCHASE_REQUEST`: Customer wants to buy a book
- `PURCHASE_COMPLETED`: Purchase transaction finished
- `INVENTORY_UPDATE`: Stock levels changed
- `RESTOCK_REQUEST`: Need to replenish inventory
- `RESTOCK_COMPLETED`: Restocking operation finished
- `ORDER_CREATED`: New customer order
- `SYSTEM_ALERT`: Important system notifications

### Communication Patterns
- **Point-to-Point**: Direct agent-to-agent messages
- **Broadcast**: System-wide announcements
- **Publish-Subscribe**: Agents subscribe to relevant message types

## 📈 Data Collection and Analysis

The system provides comprehensive analytics:

### Simulation Metrics
- Financial performance (sales, revenue)
- Operational efficiency (orders processed, restock events)
- Customer behavior (satisfaction, purchase patterns)
- Inventory management (stock levels, turnover)

### Export Capabilities
- JSON export of complete simulation results
- Real-time data streaming to dashboard
- Historical trend analysis

## 🔧 Configuration Options

### Simulation Parameters
- **Number of Agents**: Customers (1-50), Employees (1-10)
- **Simulation Length**: 10-1000 steps
- **Random Seed**: For reproducible results
- **Agent Behaviors**: Customizable probabilities and preferences

### Dashboard Settings
- **Auto-refresh Rate**: Real-time vs manual updates
- **Chart Types**: Various visualization options
- **Data Granularity**: Step-by-step or aggregated views

## 📚 Technical Implementation

### Ontology Structure
```
Entity (Thing)
├── Person
│   ├── Customer (has: name, budget, satisfaction)
│   └── Employee (has: name, role, efficiency)
├── Book (has: title, isbn, price, author, genre)
├── Order (has: date, status, total, quantity)
├── Inventory (has: quantity, reorderLevel, lastRestocked)
├── Genre (has: name)
└── Author (has: name)
```

### Agent Interaction Flow
1. **Initialization**: Agents register with message bus
2. **Simulation Loop**: 
   - Agents process messages
   - Execute behavioral rules
   - Send communication messages
   - Update ontology state
3. **Data Collection**: Metrics gathered at each step
4. **Cleanup**: Resources properly released

## 🧪 Example Simulation Output

```
📊 BOOKSTORE SIMULATION RESULTS
================================================================================
⏱️  Simulation completed in 12.34 seconds
📈 Total steps: 150
👥 Total agents: 21

💰 FINANCIAL PERFORMANCE:
   Total Sales: $847.52
   Books Sold: 67
   Average Book Price: $12.65

👥 CUSTOMER METRICS:
   Total Customers: 10
   Average Satisfaction: 0.84/1.0
   Average Budget Remaining: $23.45

📚 INVENTORY METRICS:
   Total Books: 4
   Total Stock Remaining: 43
   
🏆 Best Sellers:
   1. 'Murder on the Orient Express': 23 sales, 2 in stock
   2. 'Foundation': 18 sales, 7 in stock
   3. 'Pride and Prejudice': 15 sales, 22 in stock
```

## 🔍 Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all dependencies are installed
2. **Port Conflicts**: Change port with `--port` argument
3. **Memory Issues**: Reduce number of agents or simulation steps
4. **Slow Performance**: Disable auto-refresh or reduce update frequency

### Debugging
- Use `--debug` flag for detailed web interface logging
- Check console output for agent communication logs
- Inspect ontology state with `--mode inspect`

## 🚦 Future Enhancements

- **Advanced SWRL Rules**: Direct rule engine integration
- **Machine Learning**: Adaptive agent behaviors
- **Real-time Analytics**: Stream processing capabilities
- **Multi-store Support**: Distributed bookstore networks
- **Customer Personas**: More sophisticated customer modeling

## 📞 Support

This system demonstrates advanced concepts in:
- Multi-agent systems and distributed computing
- Ontology-based knowledge representation
- Real-time simulation and monitoring
- Web-based data visualization
- Message-oriented middleware

For technical questions or enhancements, refer to the code documentation and comments throughout the implementation.

---

**Built with ❤️ for Complex Systems and Agent Technology**