#!/bin/bash

# Bookstore Management System - Startup Script
# This script helps launch the different modes of the system

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
PYTHON_EXEC="$VENV_DIR/bin/python"

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}📚 BOOKSTORE MANAGEMENT SYSTEM${NC}"
echo -e "${BLUE}=================================${NC}"

# Function to check if virtual environment exists
check_venv() {
    if [ ! -d "$VENV_DIR" ] || [ ! -f "$PYTHON_EXEC" ]; then
        echo -e "${RED}❌ Virtual environment not found!${NC}"
        echo -e "${YELLOW}💡 Run the following commands to set up:${NC}"
        echo "   python3 -m venv .venv"
        echo "   source .venv/bin/activate"
        echo "   pip install -r requirements.txt"
        exit 1
    fi
}

# Function to check if packages are installed
check_packages() {
    echo -e "${BLUE}🔍 Checking required packages...${NC}"
    if ! "$PYTHON_EXEC" -c "import mesa, owlready2, dash, flask" 2>/dev/null; then
        echo -e "${RED}❌ Required packages not installed!${NC}"
        echo -e "${YELLOW}💡 Installing packages...${NC}"
        "$VENV_DIR/bin/pip" install -r "$PROJECT_DIR/requirements.txt"
    else
        echo -e "${GREEN}✅ All packages installed${NC}"
    fi
}

# Function to show menu
show_menu() {
    echo ""
    echo -e "${YELLOW}Choose an option:${NC}"
    echo "1. 🌐 Launch Web Dashboard (Recommended)"
    echo "2. 💻 Run CLI Simulation"
    echo "3. 🧪 Run System Tests"
    echo "4. 🔍 Inspect Ontology"
    echo "5. 📖 Run Example Demo"
    echo "6. ❌ Exit"
    echo ""
}

# Function to launch web dashboard
launch_web() {
    echo -e "${GREEN}🌐 Starting Web Dashboard...${NC}"
    echo -e "${BLUE}📍 URL: http://localhost:8050${NC}"
    echo -e "${YELLOW}⏹️  Press Ctrl+C to stop${NC}"
    echo ""
    "$PYTHON_EXEC" "$PROJECT_DIR/app.py" --mode web --port 8050
}

# Function to run CLI simulation
run_cli() {
    echo -e "${GREEN}💻 Running CLI Simulation...${NC}"
    echo ""
    read -p "Number of customers (default: 10): " customers
    read -p "Number of employees (default: 3): " employees  
    read -p "Simulation steps (default: 100): " steps
    read -p "Output file (optional): " output
    
    # Set defaults
    customers=${customers:-10}
    employees=${employees:-3}
    steps=${steps:-100}
    
    # Build command
    cmd="$PYTHON_EXEC $PROJECT_DIR/app.py --mode cli --customers $customers --employees $employees --steps $steps"
    if [ ! -z "$output" ]; then
        cmd="$cmd --output $output"
    fi
    
    echo -e "${BLUE}🚀 Running: $cmd${NC}"
    echo ""
    eval $cmd
}

# Function to run tests
run_tests() {
    echo -e "${GREEN}🧪 Running System Tests...${NC}"
    echo ""
    "$PYTHON_EXEC" "$PROJECT_DIR/test_system.py"
}

# Function to inspect ontology
inspect_ontology() {
    echo -e "${GREEN}🔍 Inspecting Ontology...${NC}"
    echo ""
    "$PYTHON_EXEC" "$PROJECT_DIR/app.py" --mode inspect
}

# Function to run example
run_example() {
    echo -e "${GREEN}📖 Running Example Demo...${NC}"
    echo ""
    "$PYTHON_EXEC" "$PROJECT_DIR/example.py" --interactive
}

# Main execution
main() {
    cd "$PROJECT_DIR"
    
    check_venv
    check_packages
    
    if [ $# -eq 0 ]; then
        # Interactive mode
        while true; do
            show_menu
            read -p "Enter your choice (1-6): " choice
            
            case $choice in
                1)
                    launch_web
                    break
                    ;;
                2)
                    run_cli
                    ;;
                3)
                    run_tests
                    ;;
                4)
                    inspect_ontology
                    ;;
                5)
                    run_example
                    ;;
                6)
                    echo -e "${GREEN}👋 Goodbye!${NC}"
                    exit 0
                    ;;
                *)
                    echo -e "${RED}❌ Invalid choice. Please try again.${NC}"
                    ;;
            esac
            
            echo ""
            read -p "Press Enter to continue..."
        done
    else
        # Command line mode
        case $1 in
            "web")
                launch_web
                ;;
            "cli")
                shift
                "$PYTHON_EXEC" "$PROJECT_DIR/app.py" --mode cli "$@"
                ;;
            "test")
                run_tests
                ;;
            "inspect")
                inspect_ontology
                ;;
            "example")
                run_example
                ;;
            *)
                echo -e "${RED}❌ Unknown command: $1${NC}"
                echo -e "${YELLOW}Usage: $0 [web|cli|test|inspect|example]${NC}"
                exit 1
                ;;
        esac
    fi
}

# Trap Ctrl+C
trap 'echo -e "\n${YELLOW}🛑 Interrupted by user${NC}"; exit 0' INT

# Run main function
main "$@"