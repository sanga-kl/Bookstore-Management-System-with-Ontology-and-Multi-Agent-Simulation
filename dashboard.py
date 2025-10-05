
import dash
from dash import dcc, html, Input, Output, State, callback_context, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
import threading
import time
import json
from datetime import datetime
import queue

from simulation import BookstoreModel, run_bookstore_simulation
from message_bus import MessageType

class BookstoreDashboard:

    def __init__(self):
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
        self.model = None
        self.simulation_thread = None
        self.simulation_queue = queue.Queue()
        self.is_running = False
        self.auto_refresh = True  # Enable auto-refresh by default
        
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_layout(self):
        
        self.app.layout = dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H1("📚 Bookstore Management System", 
                           className="text-center mb-4",
                           style={"color": "#00bc8c", "textShadow": "2px 2px 4px rgba(0,0,0,0.8)"}),
                    html.P("Multi-Agent System Simulation Dashboard", 
                          className="text-center",
                          style={"color": "#adb5bd", "fontSize": "1.2rem"})
                ])
            ], className="mb-4"),
            
            # Control Panel
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("🎮 Simulation Controls", className="card-title"),
                            
                            # Simulation Parameters
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Number of Customers"),
                                    dbc.Input(id="num-customers", type="number", value=10, min=1, max=50)
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Number of Employees"),
                                    dbc.Input(id="num-employees", type="number", value=3, min=1, max=10)
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Simulation Steps"),
                                    dbc.Input(id="sim-steps", type="number", value=100, min=10, max=1000)
                                ], width=4)
                            ], className="mb-3"),
                            
                            # Control Buttons
                            dbc.Row([
                                dbc.Col([
                                    dbc.ButtonGroup([
                                        dbc.Button("▶️ Start", id="start-btn", color="success", className="me-2"),
                                        dbc.Button("⏸️ Pause", id="pause-btn", color="warning", className="me-2"),
                                        dbc.Button("⏹️ Stop", id="stop-btn", color="danger", className="me-2"),
                                        dbc.Button("🔄 Reset", id="reset-btn", color="info")
                                    ])
                                ], width=12),  # Changed from width=8 to width=12
                                dbc.Col([
                                    dbc.Switch(
                                        id="auto-refresh",
                                        label="Auto Refresh",
                                        value=True,  # Set to True by default
                                        style={"display": "none"}  # Hide the toggle button
                                    )
                                ], width=4, className="d-flex align-items-center", style={"display": "none"})
                            ])
                        ])
                    ])
                ])
            ], className="mb-4"),
            
            # Status Row
            dbc.Row([
                dbc.Col([
                    dbc.Alert(id="status-alert", children="Ready to start simulation", color="info")
                ])
            ], className="mb-4"),
            
            # Metrics Cards Row 1
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(id="total-sales", children="$0.00", className="text-success",
                                   style={"fontSize": "1.8rem", "fontWeight": "bold"}),
                            html.P("Total Sales", className="card-text", style={"color": "#adb5bd"})
                        ])
                    ], style={"background": "linear-gradient(135deg, #0f4c3a, #1a5745)", 
                             "border": "1px solid #00bc8c", "borderRadius": "10px"})
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(id="books-sold", children="0", className="text-primary",
                                   style={"fontSize": "1.8rem", "fontWeight": "bold"}),
                            html.P("Books Sold", className="card-text", style={"color": "#adb5bd"})
                        ])
                    ], style={"background": "linear-gradient(135deg, #1a365d, #2c5282)", 
                             "border": "1px solid #3182ce", "borderRadius": "10px"})
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(id="step-count", children="0", style={"color": "#e9ecef", "fontSize": "1.8rem", "fontWeight": "bold"}),
                            html.P("Simulation Steps", className="card-text", style={"color": "#adb5bd"})
                        ])
                    ], style={"background": "linear-gradient(135deg, #2d3748, #4a5568)", 
                             "border": "1px solid #718096", "borderRadius": "10px"})
                ], width=3)
            ], className="mb-3"),
            
            # Metrics Cards Row 2
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(id="messages-sent", children="0", className="text-info",
                                   style={"fontSize": "1.8rem", "fontWeight": "bold"}),
                            html.P("Messages Sent", className="card-text", style={"color": "#adb5bd"})
                        ])
                    ], style={"background": "linear-gradient(135deg, #065666, #0987a0)", 
                             "border": "1px solid #17a2b8", "borderRadius": "10px"})
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(id="inventory-status", children="0", style={"color": "#f8f9fa", "fontSize": "1.8rem", "fontWeight": "bold"}),
                            html.P("Items in Stock", className="card-text", style={"color": "#adb5bd"})
                        ])
                    ], style={"background": "linear-gradient(135deg, #2d3748, #4a5568)", 
                             "border": "1px solid #718096", "borderRadius": "10px"})
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(id="active-employees", children="0", className="text-warning",
                                   style={"fontSize": "1.8rem", "fontWeight": "bold"}),
                            html.P("Employees Restocking", className="card-text", style={"color": "#adb5bd"})
                        ])
                    ], style={"background": "linear-gradient(135deg, #744210, #975a16)", 
                             "border": "1px solid #f6e05e", "borderRadius": "10px"})
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(id="simulation-time", children="0.0s", style={"color": "#e9ecef", "fontSize": "1.8rem", "fontWeight": "bold"}),
                            html.P("Simulation Time", className="card-text", style={"color": "#adb5bd"})
                        ])
                    ], style={"background": "linear-gradient(135deg, #2d3748, #4a5568)", 
                             "border": "1px solid #718096", "borderRadius": "10px"})
                ], width=3)
            ], className="mb-4"),
            
            # Detailed Data Row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div(id="customer-table")
                        ], style={'padding': '15px'})
                    ])
                ], width=12)
            ], className="mb-4"),
            
            # Book Inventory Row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div(id="inventory-table")
                        ], style={'padding': '15px'})
                    ])
                ], width=12)
            ], className="mb-4"),
            
            # Message Log
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("💬 Message Log"),
                            html.Div(id="message-log", style={"height": "300px", "overflow-y": "scroll"})
                        ])
                    ])
                ])
            ], className="mb-4"),
            
            # Comprehensive Summary Section (appears when simulation completes)
            html.Div(id="simulation-summary-section", children=[], style={"display": "none"}),
            
            # Hidden div to store data
            html.Div(id="simulation-data", style={"display": "none"}),
            
            # Auto-refresh interval
            dcc.Interval(
                id="interval-component",
                interval=2000,  # Update every 2 seconds
                n_intervals=0,
                disabled=False  # Enable auto-refresh by default
            )
            
        ], fluid=True)
    
    def setup_callbacks(self):

        @self.app.callback(
            [Output("status-alert", "children"),
             Output("status-alert", "color"),
             Output("start-btn", "disabled"),
             Output("pause-btn", "disabled"),
             Output("stop-btn", "disabled")],
            [Input("start-btn", "n_clicks"),
             Input("pause-btn", "n_clicks"),
             Input("stop-btn", "n_clicks"),
             Input("reset-btn", "n_clicks")],
            [State("num-customers", "value"),
             State("num-employees", "value"),
             State("sim-steps", "value")]
        )
        def control_simulation(start_clicks, pause_clicks, stop_clicks, reset_clicks,
                             num_customers, num_employees, sim_steps):
            
            ctx = callback_context
            if not ctx.triggered:
                return "Ready to start simulation", "info", False, True, True
            
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            
            if button_id == "start-btn":
                if not self.is_running:
                    self.start_simulation(num_customers, num_employees, sim_steps)
                    return "Simulation running...", "success", True, False, False
                else:
                    return "Simulation already running", "warning", True, False, False
            
            elif button_id == "pause-btn":
                if self.is_running:
                    self.pause_simulation()
                    return "Simulation paused", "warning", False, True, False
                else:
                    return "No simulation to pause", "warning", False, True, True
            
            elif button_id == "stop-btn":
                if self.is_running:
                    self.stop_simulation()
                    return "Simulation stopped", "danger", False, True, True
                else:
                    return "No simulation to stop", "info", False, True, True
            
            elif button_id == "reset-btn":
                self.reset_simulation()
                return "Simulation reset", "info", False, True, True
            
            return "Ready to start simulation", "info", False, True, True
        
        @self.app.callback(
            Output("interval-component", "disabled"),
            Input("auto-refresh", "value")
        )
        def toggle_auto_refresh(auto_refresh):
            
            self.auto_refresh = auto_refresh
            return not auto_refresh
        
        @self.app.callback(
            [Output("total-sales", "children"),
             Output("books-sold", "children"),
             Output("step-count", "children"),
             Output("messages-sent", "children"),
             Output("inventory-status", "children"),
             Output("active-employees", "children"),
             Output("simulation-time", "children"),
             Output("customer-table", "children"),
             Output("inventory-table", "children"),
             Output("message-log", "children")],
            [Input("interval-component", "n_intervals"),
             Input("start-btn", "n_clicks"),
             Input("stop-btn", "n_clicks")]
        )
        def update_dashboard(n_intervals, start_clicks, stop_clicks):
            
            if not self.model:
                return ("$0.00", "0", "0", "0", "0", "0", "0.0s", "No data", "No data", "No messages")
            
            try:
                # Get current data
                summary = self.model.get_simulation_summary()
                
                # Update metrics
                total_sales = f"${summary['financial_metrics']['total_sales']:.2f}"
                books_sold = str(summary['financial_metrics']['total_books_sold'])
                step_count = str(summary['simulation_info']['steps_completed'])
                messages = str(summary['communication_metrics']['total_messages'])
                inventory_total = str(summary['inventory_metrics']['total_stock_remaining'])
                active_employees = str(len([emp for emp in summary['employee_metrics']['employee_details'] if emp.get('role') == 'Inventory Specialist' and emp.get('workload', 0) > 0]))
                sim_time = f"{summary['simulation_info']['simulation_time_seconds']:.1f}s"
                
                # Create sales over time graph (removed detailed logic)
                if hasattr(self.model, 'datacollector'):
                    model_data = self.model.datacollector.get_model_vars_dataframe()
                    if not model_data.empty:
                        sales_fig = go.Figure()
                        sales_fig.update_layout(title="Sales Over Time - Removed")
                    else:
                        sales_fig = go.Figure()
                        sales_fig.update_layout(title="Sales Over Time - Removed")
                else:
                    sales_fig = go.Figure()
                    sales_fig.update_layout(title="Sales Over Time - Removed")

                # Create customer cards
                customer_data = summary['customer_metrics']['customer_details']
                if customer_data:
                    # Create customer cards
                    customer_cards = []
                    for customer in customer_data:
                        # Determine satisfaction level color
                        satisfaction = customer.get('satisfaction', 0)
                        if satisfaction >= 0.8:
                            satisfaction_color = 'success'
                        elif satisfaction >= 0.6:
                            satisfaction_color = 'warning'
                        else:
                            satisfaction_color = 'danger'
                        
                        # Determine budget status
                        budget = customer.get('budget', 0)
                        total_spent = customer.get('total_spent', 0)
                        budget_remaining = budget - total_spent
                        budget_percentage = (budget_remaining / budget * 100) if budget > 0 else 0
                        
                        # Create compact customer card
                        card = dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H6(customer.get('name', 'Unknown Customer'), 
                                           className="card-title mb-2", 
                                           style={'fontWeight': 'bold', 'fontSize': '14px'}),
                                    
                                    html.Div([
                                        html.Small(f"Budget: ${budget:.0f}", className="text-muted d-block"),
                                        html.Small(f"Spent: ${total_spent:.0f}", className="text-muted d-block"),
                                        html.Small(f"Books: {customer.get('books_purchased', 0)}", className="text-muted d-block mb-2"),
                                    ]),
                                    
                                    # Compact satisfaction indicator
                                    dbc.Badge(f"Satisfaction: {satisfaction:.1f}", 
                                            color=satisfaction_color, 
                                            className="w-100",
                                            style={'fontSize': '11px'})
                                ], style={'padding': '12px'})
                            ], style={
                                'height': '140px',
                                'margin': '5px',
                                'borderRadius': '8px',
                                'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
                                'border': '1px solid #e0e0e0'
                            })
                        ], width=3, className="mb-2")
                        
                        customer_cards.append(card)
                    
                    # Create the customer display with header
                    customer_table = html.Div([
                        html.Div([
                            html.H5("👥 Customer Details", 
                                   className="mb-3",
                                   style={'color': '#28a745', 'fontWeight': 'bold'})
                        ]),
                        dbc.Row(customer_cards, className="g-1")
                    ])
                else:
                    customer_table = html.Div([
                        html.H5("👥 Customer Details", className="mb-3"),
                        html.P("No customer data available", className="text-muted")
                    ])
                
                # Create inventory cards
                book_data = summary['inventory_metrics']['book_details']
                if book_data:
                    # Create book cards
                    book_cards = []
                    for book in book_data:
                        # Determine genre color
                        genre = book.get('genre', 'Unknown')
                        if genre.lower() == 'fiction':
                            genre_color = 'success'
                        elif genre.lower() == 'mystery':
                            genre_color = 'warning'
                        elif genre.lower() in ['science fiction', 'sci-fi']:
                            genre_color = 'info'
                        elif genre.lower() == 'romance':
                            genre_color = 'danger'
                        elif genre.lower() == 'fantasy':
                            genre_color = 'secondary'
                        else:
                            genre_color = 'primary'
                        
                        # Determine stock status
                        stock = book.get('current_stock', 0)
                        stock_color = 'success' if stock > 5 else 'warning' if stock > 0 else 'danger'
                        stock_text = f"{stock} units"
                        
                        # Create progress bar for stock
                        max_stock = 50  # Assume max stock is 50 for visual reference
                        stock_percentage = min(100, (stock / max_stock) * 100)
                        
                        # Create the book card
                        card = dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H6(book.get('title', 'Unknown Title'), 
                                           className="card-title mb-2", 
                                           style={'fontWeight': 'bold', 'fontSize': '16px'}),
                                    html.P(f"by {book.get('author', 'Unknown Author')}", 
                                          className="text-muted small mb-2"),
                                    
                                    # Genre badge
                                    dbc.Badge(genre, color=genre_color, className="mb-3"),
                                    
                                    # Price
                                    html.H5(f"${book.get('price', 0):.2f}", 
                                           className="text-primary mb-3",
                                           style={'fontWeight': 'bold'}),
                                    
                                    # Stock section
                                    html.Div([
                                        html.P("Stock:", className="mb-1 small text-muted"),
                                        dbc.Badge(stock_text, color=stock_color, className="mb-2"),
                                        dbc.Progress(value=stock_percentage, 
                                                   color=stock_color, 
                                                   className="mb-2",
                                                   style={'height': '8px'}),
                                    ]),
                                    
                                    # Status
                                    html.Div([
                                        html.P("Status:", className="mb-1 small text-muted"),
                                        dbc.Badge("In Stock" if stock > 0 else "Out of Stock", 
                                                color="success" if stock > 0 else "danger"),
                                    ])
                                ], style={'padding': '20px'})
                            ], style={
                                'height': '350px',
                                'margin': '10px',
                                'borderRadius': '10px',
                                'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
                                'border': '1px solid #e0e0e0'
                            })
                        ], width=4, className="mb-3")
                        
                        book_cards.append(card)
                    
                    # Create the inventory display with header
                    inventory_table = html.Div([
                        html.Div([
                            html.H5("📚 Book Inventory", 
                                   className="mb-3",
                                   style={'color': '#6f42c1', 'fontWeight': 'bold'})
                        ]),
                        dbc.Row(book_cards, className="g-3")
                    ])
                else:
                    inventory_table = html.Div([
                        html.H5("📚 Book Inventory", className="mb-3"),
                        html.P("No inventory data available", className="text-muted")
                    ])
                
                # Create message log
                recent_messages = self.model.message_bus.get_message_history(limit=10)
                message_elements = []
                for msg in recent_messages[-10:]:  # Show last 10 messages
                    timestamp = datetime.fromtimestamp(msg.timestamp).strftime("%H:%M:%S")
                    message_elements.append(
                        html.P(f"[{timestamp}] {msg.sender_id}: {msg.message_type.value}", 
                              className="mb-1 small")
                    )
                
                message_log = message_elements if message_elements else [html.P("No messages yet")]
                
                return (total_sales, books_sold, step_count, messages, 
                       inventory_total, active_employees, sim_time, customer_table, inventory_table, message_log)
                
            except Exception as e:
                print(f"Error updating dashboard: {e}")
                return ("Error", "Error", "Error", "Error", "Error", "Error", "Error", 
                       "Error loading data", "Error loading data", "Error loading messages")

        @self.app.callback(
            [Output("simulation-summary-section", "children"),
             Output("simulation-summary-section", "style")],
            [Input("interval-component", "n_intervals")]
        )
        def update_simulation_summary(n_intervals):
            
            if not self.model or self.is_running:
                return [], {"display": "none"}
            
            try:
                # Check if simulation is actually complete (not just paused)
                if hasattr(self.model, 'step_count') and self.model.step_count > 0:
                    summary = self.model.get_simulation_summary()
                    
                    # Create comprehensive summary layout
                    summary_content = [
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader([
                                        html.H3("🏆 SIMULATION COMPLETE - COMPREHENSIVE SUMMARY", 
                                               className="text-center",
                                               style={"color": "#00bc8c", "textShadow": "2px 2px 4px rgba(0,0,0,0.8)"})
                                    ], style={"background": "linear-gradient(135deg, #0f4c3a, #1a5745)",
                                             "border": "none"}),
                                    dbc.CardBody([
                                        # Executive Summary
                                        dbc.Row([
                                            dbc.Col([
                                                html.H4("📊 Executive Summary", style={"color": "#00bc8c"}),
                                                html.P([
                                                    f"Simulation completed successfully with ",
                                                    html.Strong(f"{summary['simulation_info']['steps_completed']} steps", 
                                                               style={"color": "#00bc8c"}),
                                                    f" in {summary['simulation_info']['simulation_time_seconds']:.2f} seconds. ",
                                                    f"Generated ${summary['financial_metrics']['total_sales']:.2f} in sales ",
                                                    f"across {summary['financial_metrics']['total_books_sold']} book transactions."
                                                ], style={"fontSize": "1.1rem", "color": "#e9ecef"}),
                                            ])
                                        ], className="mb-4"),
                                        
                                        # Key Performance Indicators
                                        dbc.Row([
                                            dbc.Col([
                                                html.H5("🎯 Key Performance Indicators", style={"color": "#3182ce"}),
                                                dbc.Row([
                                                    dbc.Col([
                                                        dbc.Card([
                                                            dbc.CardBody([
                                                                html.H6("Revenue Efficiency", style={"color": "#adb5bd"}),
                                                                html.H5(f"${summary['financial_metrics']['total_sales'] / summary['simulation_info']['steps_completed']:.2f}/step", 
                                                                        style={"color": "#00bc8c"})
                                                            ])
                                                        ], style={"background": "#2d3748", "border": "1px solid #4a5568"})
                                                    ], width=3),
                                                    dbc.Col([
                                                        dbc.Card([
                                                            dbc.CardBody([
                                                                html.H6("Customer Engagement", style={"color": "#adb5bd"}),
                                                                html.H5(f"{summary['customer_metrics'].get('customer_engagement_rate', 0):.1%}", 
                                                                        style={"color": "#3182ce"})
                                                            ])
                                                        ], style={"background": "#2d3748", "border": "1px solid #4a5568"})
                                                    ], width=3),
                                                    dbc.Col([
                                                        dbc.Card([
                                                            dbc.CardBody([
                                                                html.H6("System Efficiency", style={"color": "#adb5bd"}),
                                                                html.H5(f"{summary['simulation_info'].get('steps_per_second', 0):.1f} steps/sec", 
                                                                        style={"color": "#f6e05e"})
                                                            ])
                                                        ], style={"background": "#2d3748", "border": "1px solid #4a5568"})
                                                    ], width=3),
                                                    dbc.Col([
                                                        dbc.Card([
                                                            dbc.CardBody([
                                                                html.H6("Inventory Turnover", style={"color": "#adb5bd"}),
                                                                html.H5(f"{summary['inventory_metrics'].get('inventory_turnover', 0):.1%}", 
                                                                        style={"color": "#17a2b8"})
                                                            ])
                                                        ], style={"background": "#2d3748", "border": "1px solid #4a5568"})
                                                    ], width=3)
                                                ])
                                            ])
                                        ], className="mb-4"),
                                        
                                        # Top Performers
                                        dbc.Row([
                                            dbc.Col([
                                                html.H5("🏆 Top Performers", style={"color": "#f6e05e"}),
                                                dbc.Row([
                                                    dbc.Col([
                                                        html.H6("💰 Top Customers", style={"color": "#00bc8c"}),
                                                        self._create_top_performers_list(
                                                            summary['customer_metrics'].get('customer_details', []),
                                                            'total_spent', 3, True
                                                        )
                                                    ], width=4),
                                                    dbc.Col([
                                                        html.H6("👨‍💼 Best Employees", style={"color": "#3182ce"}),
                                                        self._create_top_performers_list(
                                                            summary['employee_metrics'].get('employee_details', []),
                                                            'efficiency', 3, False
                                                        )
                                                    ], width=4),
                                                    dbc.Col([
                                                        html.H6("📚 Popular Books", style={"color": "#f6e05e"}),
                                                        self._create_top_performers_list(
                                                            summary['inventory_metrics'].get('book_details', []),
                                                            'popularity_score', 3, False
                                                        )
                                                    ], width=4)
                                                ])
                                            ])
                                        ], className="mb-4"),
                                        
                                        # System Health & Recommendations
                                        dbc.Row([
                                            dbc.Col([
                                                html.H5("🏥 System Health Analysis", style={"color": "#17a2b8"}),
                                                self._create_health_analysis(summary)
                                            ], width=8),
                                            dbc.Col([
                                                html.H5("💡 Recommendations", style={"color": "#f6e05e"}),
                                                self._create_recommendations(summary)
                                            ], width=4)
                                        ])
                                    ], style={"background": "linear-gradient(135deg, #1a202c, #2d3748)",
                                             "border": "none"})
                                ], style={"border": "2px solid #00bc8c", "borderRadius": "15px"})
                            ])
                        ], className="mb-4")
                    ]
                    
                    return summary_content, {"display": "block"}
                
            except Exception as e:
                print(f"Error creating summary: {e}")
                return [], {"display": "none"}
            
            return [], {"display": "none"}
    
    def _create_top_performers_list(self, data, key, limit, is_currency=False):
        
        if not data:
            return html.P("No data available", style={"color": "#adb5bd"})
        
        sorted_data = sorted(data, key=lambda x: x.get(key, 0), reverse=True)[:limit]
        items = []
        
        for i, item in enumerate(sorted_data, 1):
            value = item.get(key, 0)
            name = item.get('name', item.get('title', f"Item {i}"))
            
            if is_currency:
                display_value = f"${value:.2f}"
            elif isinstance(value, float):
                display_value = f"{value:.2f}"
            else:
                display_value = str(value)
            
            items.append(
                html.P([
                    html.Strong(f"{i}. ", style={"color": "#f6e05e"}),
                    f"{name}: ",
                    html.Strong(display_value, style={"color": "#00bc8c"})
                ], style={"color": "#e9ecef", "margin": "5px 0"})
            )
        
        return items
    
    def _create_health_analysis(self, summary):
        
        # Calculate health scores
        efficiency_score = min(100, summary['employee_metrics'].get('average_efficiency', 5) * 10)
        popularity_score = min(100, summary['inventory_metrics'].get('average_popularity', 5) * 10)
        performance_score = min(100, summary['simulation_info'].get('steps_per_second', 1) * 10)
        
        overall_health = (efficiency_score + popularity_score + performance_score) / 3
        
        # Health indicators
        health_items = [
            ("Employee Efficiency", efficiency_score, "#3182ce"),
            ("Book Popularity", popularity_score, "#f6e05e"),
            ("System Performance", performance_score, "#17a2b8")
        ]
        
        health_display = []
        for name, score, color in health_items:
            health_display.append(
                dbc.Progress(
                    value=score,
                    label=f"{name}: {score:.1f}%",
                    color="success" if score >= 70 else "warning" if score >= 40 else "danger",
                    style={"margin": "5px 0"}
                )
            )
        
        # Overall status
        if overall_health >= 80:
            status_color = "#00bc8c"
            status_text = "🟢 EXCELLENT"
            status_desc = "System performing optimally"
        elif overall_health >= 60:
            status_color = "#f6e05e"
            status_text = "🟡 GOOD"
            status_desc = "System performing well"
        elif overall_health >= 40:
            status_color = "#fd7e14"
            status_text = "🟠 FAIR"
            status_desc = "Some areas need improvement"
        else:
            status_color = "#e74c3c"
            status_text = "🔴 POOR"
            status_desc = "System needs attention"
        
        return [
            html.H6(f"Overall Health: {overall_health:.1f}/100", 
                    style={"color": status_color, "fontSize": "1.2rem"}),
            html.P([
                html.Strong(status_text, style={"color": status_color}),
                f" - {status_desc}"
            ], style={"color": "#e9ecef"}),
            html.Div(health_display, className="mt-3")
        ]
    
    def _create_recommendations(self, summary):
        
        recommendations = []
        
        # Analyze and create recommendations
        efficiency = summary['employee_metrics'].get('average_efficiency', 5)
        turnover = summary['inventory_metrics'].get('inventory_turnover', 0)
        
        if efficiency < 5:
            recommendations.append("⚡ Enhance employee training and efficiency")
        
        if turnover < 0.3:
            recommendations.append("📦 Optimize inventory management")
        
        sales_per_step = summary['financial_metrics']['total_sales'] / summary['simulation_info']['steps_completed']
        if sales_per_step < 1:
            recommendations.append("💰 Focus on increasing sales conversion")
        
        if not recommendations:
            recommendations.append("✅ System is performing well across all metrics")
        
        rec_items = []
        for i, rec in enumerate(recommendations, 1):
            rec_items.append(
                html.P([
                    html.Strong(f"{i}. ", style={"color": "#f6e05e"}),
                    rec
                ], style={"color": "#e9ecef", "margin": "8px 0"})
            )
        
        return rec_items

    def start_simulation(self, num_customers, num_employees, sim_steps):
        
        def run_sim():
            try:
                self.model = BookstoreModel(
                    num_customers=num_customers,
                    num_employees=num_employees,
                    random_seed=42
                )
                self.is_running = True
                
                for step in range(sim_steps):
                    if not self.is_running:
                        break
                    
                    self.model.step()
                    time.sleep(0.1)  # Small delay for real-time feel
                
                self.is_running = False
                
            except Exception as e:
                print(f"Simulation error: {e}")
                self.is_running = False
        
        if not self.is_running:
            self.simulation_thread = threading.Thread(target=run_sim)
            self.simulation_thread.daemon = True
            self.simulation_thread.start()
    
    def pause_simulation(self):
        
        self.is_running = False
    
    def stop_simulation(self):
        
        self.is_running = False
        if self.model:
            self.model.cleanup()
    
    def reset_simulation(self):
        
        self.stop_simulation()
        self.model = None
    
    def run_server(self, debug=True, port=8050):
        
        print(f"🌐 Starting Bookstore Dashboard on http://localhost:{port}")
        self.app.run_server(debug=debug, port=port, host='0.0.0.0')

def create_dashboard():
    
    return BookstoreDashboard()

if __name__ == "__main__":
    dashboard = create_dashboard()
    dashboard.run_server(debug=True, port=8050)