#!/usr/bin/env python3
"""
Customer Support Assistant
Brain AI-powered customer service with persistent memory and intelligent resolution
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import uuid

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from loguru import logger
import uvicorn

# Import shared Brain AI utilities
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from brain_ai_integration import BrainAIWrapper, create_success_response, create_error_response
from demo_data import (
    generate_customer_profile, generate_support_ticket, generate_customer_batch,
    generate_ticket_batch, format_memory_for_display
)
from web_components import WebComponents

# Pydantic models for API
class TicketRequest(BaseModel):
    customer_id: str
    subject: str
    description: str
    issue_type: str
    priority: str

class CustomerRequest(BaseModel):
    name: str
    email: str
    phone: str
    issue_description: str

class FeedbackRequest(BaseModel):
    ticket_id: str
    satisfaction: int
    resolution_time: float
    comments: str

class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]

# Initialize FastAPI app
app = FastAPI(
    title="Customer Support Assistant - Brain AI",
    description="🧠 AI-powered customer service with persistent memory and intelligent resolution",
    version="1.0.0"
)

# Templates
templates = Jinja2Templates(directory="templates")

# Global Brain AI instance
brain_ai = BrainAIWrapper("CustomerSupportAssistant")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# Demo data storage
demo_customers = {}
demo_tickets = {}
demo_responses = {}

# Initialize demo data
def initialize_demo_data():
    """Initialize demo data for the application"""
    logger.info("Initializing demo data...")
    
    # Generate customers
    customers = generate_customer_batch(10)
    for customer in customers:
        demo_customers[customer.id] = {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone,
            "account_created": customer.account_created,
            "total_orders": customer.total_orders,
            "lifetime_value": customer.lifetime_value,
            "satisfaction_score": customer.satisfaction_score,
            "preferences": customer.preferences
        }
    
    # Generate support tickets
    customer_ids = list(demo_customers.keys())
    tickets = generate_ticket_batch(25, customer_ids)
    for ticket in tickets:
        demo_tickets[ticket["ticket_id"]] = ticket
    
    logger.info(f"Generated {len(demo_customers)} customers and {len(demo_tickets)} tickets")

# Application startup
@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    await brain_ai.initialize()
    initialize_demo_data()
    logger.info("🧠 Customer Support Assistant started successfully!")

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Process different message types
            if message["type"] == "process_ticket":
                result = await process_support_ticket_websocket(message["data"])
                await websocket.send_text(json.dumps({
                    "type": "ticket_processed",
                    "data": result
                }))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# API Routes

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    html_content = WebComponents.get_base_html(
        "Customer Support Dashboard",
        "Customer Support Assistant",
        additional_css="""
        .customer-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        .ticket-priority-critical { border-left: 4px solid #dc3545; }
        .ticket-priority-high { border-left: 4px solid #fd7e14; }
        .ticket-priority-medium { border-left: 4px solid #ffc107; }
        .ticket-priority-low { border-left: 4px solid #28a745; }
        """,
        additional_js="""
        // Customer Support specific JavaScript
        let currentCustomer = null;
        let currentTickets = [];
        
        async function loadCustomerSupportData() {
            showLoading('dashboard-content');
            
            try {
                const [customersResponse, ticketsResponse, statsResponse] = await Promise.all([
                    apiCall('/api/customers'),
                    apiCall('/api/tickets'),
                    apiCall('/api/status')
                ]);
                
                renderCustomerSupportDashboard(customersResponse, ticketsResponse, statsResponse);
            } catch (error) {
                console.error('Failed to load customer support data:', error);
                showAlert('Failed to load dashboard data', 'danger');
            }
        }
        
        function renderCustomerSupportDashboard(customers, tickets, stats) {
            const content = document.getElementById('dashboard-content');
            content.innerHTML = `
                <div class="row">
                    <div class="col-md-3 mb-4">
                        <div class="metric-card">
                            <i class="fas fa-users brain-ai-icon"></i>
                            <div class="metric-value">${Object.keys(customers).length}</div>
                            <div>Total Customers</div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-4">
                        <div class="metric-card">
                            <i class="fas fa-ticket-alt brain-ai-icon"></i>
                            <div class="metric-value">${Object.keys(tickets).length}</div>
                            <div>Support Tickets</div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-4">
                        <div class="metric-card">
                            <i class="fas fa-clock brain-ai-icon"></i>
                            <div class="metric-value">${getOpenTicketsCount(tickets)}</div>
                            <div>Open Tickets</div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-4">
                        <div class="metric-card">
                            <i class="fas fa-smile brain-ai-icon"></i>
                            <div class="metric-value">${calculateAverageSatisfaction(customers)}</div>
                            <div>Avg Satisfaction</div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-md-8">
                        <div class="card card-brain-ai">
                            <div class="card-header">
                                <h5><i class="fas fa-list me-2"></i>Recent Support Tickets</h5>
                            </div>
                            <div class="card-body">
                                ${renderTicketsList(tickets)}
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card card-brain-ai">
                            <div class="card-header">
                                <h5><i class="fas fa-users me-2"></i>Customer Overview</h5>
                            </div>
                            <div class="card-body">
                                ${renderCustomersList(customers)}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-md-12">
                        <div class="card card-brain-ai">
                            <div class="card-header">
                                <h5><i class="fas fa-plus me-2"></i>Create New Support Ticket</h5>
                            </div>
                            <div class="card-body">
                                ${renderTicketCreationForm(customers)}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        function getOpenTicketsCount(tickets) {
            return Object.values(tickets).filter(t => t.status === 'open' || t.status === 'in_progress').length;
        }
        
        function calculateAverageSatisfaction(customers) {
            const scores = Object.values(customers).map(c => c.satisfaction_score);
            const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
            return avg.toFixed(1);
        }
        
        function renderTicketsList(tickets) {
            const ticketsArray = Object.values(tickets).sort((a, b) => 
                new Date(b.created_at) - new Date(a.created_at)
            ).slice(0, 10);
            
            if (ticketsArray.length === 0) {
                return '<p class="text-muted">No tickets found.</p>';
            }
            
            return ticketsArray.map(ticket => `
                <div class="d-flex justify-content-between align-items-center border-bottom py-2 ticket-priority-${ticket.priority}">
                    <div>
                        <strong>${ticket.subject}</strong>
                        <br>
                        <small class="text-muted">
                            ${ticket.customer_id} • ${ticket.issue_type} • ${ticket.status}
                        </small>
                    </div>
                    <div class="text-end">
                        <span class="badge bg-${getPriorityColor(ticket.priority)}">${ticket.priority}</span>
                        <br>
                        <small class="text-muted">${formatDate(ticket.created_at)}</small>
                    </div>
                </div>
            `).join('');
        }
        
        function renderCustomersList(customers) {
            const customersArray = Object.values(customers).slice(0, 5);
            
            return customersArray.map(customer => `
                <div class="d-flex align-items-center border-bottom py-2">
                    <div class="customer-avatar me-3">
                        ${getInitials(customer.name)}
                    </div>
                    <div>
                        <strong>${customer.name}</strong>
                        <br>
                        <small class="text-muted">${customer.email}</small>
                    </div>
                </div>
            `).join('');
        }
        
        function renderTicketCreationForm(customers) {
            const customersOptions = Object.values(customers).map(c => 
                `<option value="${c.id}">${c.name} (${c.email})</option>`
            ).join('');
            
            return `
                <form id="ticket-form" onsubmit="createTicket(event)">
                    <div class="row">
                        <div class="col-md-4">
                            <div class="form-floating">
                                <select class="form-select" id="customer-select" required>
                                    <option value="">Select Customer</option>
                                    ${customersOptions}
                                </select>
                                <label for="customer-select">Customer</label>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="form-floating">
                                <input type="text" class="form-control" id="ticket-subject" placeholder="Subject" required>
                                <label for="ticket-subject">Subject</label>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="form-floating">
                                <select class="form-select" id="ticket-priority" required>
                                    <option value="">Priority</option>
                                    <option value="low">Low</option>
                                    <option value="medium">Medium</option>
                                    <option value="high">High</option>
                                    <option value="critical">Critical</option>
                                </select>
                                <label for="ticket-priority">Priority</label>
                            </div>
                        </div>
                    </div>
                    <div class="row mt-3">
                        <div class="col-md-12">
                            <div class="form-floating">
                                <textarea class="form-control" id="ticket-description" style="height: 100px" required></textarea>
                                <label for="ticket-description">Description</label>
                            </div>
                        </div>
                    </div>
                    <div class="row mt-3">
                        <div class="col-md-6">
                            <div class="form-floating">
                                <select class="form-select" id="ticket-type" required>
                                    <option value="">Issue Type</option>
                                    <option value="account_access">Account Access</option>
                                    <option value="payment_issue">Payment Issue</option>
                                    <option value="product_question">Product Question</option>
                                    <option value="technical_support">Technical Support</option>
                                    <option value="billing_inquiry">Billing Inquiry</option>
                                </select>
                                <label for="ticket-type">Issue Type</label>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <button type="submit" class="btn btn-brain-ai mt-2">
                                <i class="fas fa-plus me-2"></i>Create Ticket
                            </button>
                        </div>
                    </div>
                </form>
            `;
        }
        
        async function createTicket(event) {
            event.preventDefault();
            
            const formData = {
                customer_id: document.getElementById('customer-select').value,
                subject: document.getElementById('ticket-subject').value,
                description: document.getElementById('ticket-description').value,
                issue_type: document.getElementById('ticket-type').value,
                priority: document.getElementById('ticket-priority').value
            };
            
            try {
                const response = await apiCall('/api/tickets', 'POST', formData);
                showAlert('Ticket created successfully!', 'success');
                
                // Reload dashboard
                loadCustomerSupportData();
                
                // Clear form
                document.getElementById('ticket-form').reset();
            } catch (error) {
                showAlert('Failed to create ticket', 'danger');
            }
        }
        
        function getPriorityColor(priority) {
            const colors = {
                'low': 'success',
                'medium': 'warning',
                'high': 'danger',
                'critical': 'dark'
            };
            return colors[priority] || 'secondary';
        }
        
        function getInitials(name) {
            return name.split(' ').map(n => n[0]).join('').toUpperCase();
        }
        
        function formatDate(dateString) {
            return new Date(dateString).toLocaleDateString();
        }
        """
    )
    
    return HTMLResponse(content=html_content)

@app.get("/status")
async def get_status():
    """Get system status"""
    try:
        stats = brain_ai.get_statistics()
        return create_success_response(stats)
    except Exception as e:
        return create_error_response(str(e))

@app.get("/api/customers")
async def get_customers():
    """Get all customers"""
    return create_success_response(demo_customers)

@app.get("/api/tickets")
async def get_tickets():
    """Get all tickets"""
    return create_success_response(demo_tickets)

@app.post("/api/tickets")
async def create_ticket(request: TicketRequest):
    """Create a new support ticket"""
    try:
        # Create ticket
        ticket_data = {
            "ticket_id": str(uuid.uuid4()),
            "customer_id": request.customer_id,
            "subject": request.subject,
            "description": request.description,
            "issue_type": request.issue_type,
            "priority": request.priority,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "agent_assigned": "AI Assistant",
            "satisfaction": None,
            "resolution_time": None
        }
        
        # Store ticket
        demo_tickets[ticket_data["ticket_id"]] = ticket_data
        
        # Process through Brain AI
        brain_ai_data = {
            "ticket_id": ticket_data["ticket_id"],
            "customer_id": request.customer_id,
            "subject": request.subject,
            "description": request.description,
            "issue_type": request.issue_type,
            "priority": request.priority,
            "timestamp": datetime.now().isoformat()
        }
        
        brain_ai_result = await brain_ai.process_input(brain_ai_data, {
            "domain": "customer_support",
            "priority": request.priority,
            "issue_type": request.issue_type
        })
        
        return create_success_response({
            "ticket": ticket_data,
            "brain_ai_analysis": brain_ai_result
        }, "Ticket created successfully")
        
    except Exception as e:
        logger.error(f"Error creating ticket: {e}")
        return create_error_response(str(e))

@app.post("/api/process")
async def process_ticket(request: TicketRequest):
    """Process a support ticket through Brain AI"""
    try:
        # Prepare data for Brain AI processing
        brain_ai_data = {
            "ticket_id": request.customer_id,
            "customer_id": request.customer_id,
            "subject": request.subject,
            "description": request.description,
            "issue_type": request.issue_type,
            "priority": request.priority,
            "timestamp": datetime.now().isoformat()
        }
        
        # Process through Brain AI
        result = await brain_ai.process_input(brain_ai_data, {
            "domain": "customer_support",
            "priority": request.priority,
            "issue_type": request.issue_type
        })
        
        return create_success_response(result)
        
    except Exception as e:
        logger.error(f"Error processing ticket: {e}")
        return create_error_response(str(e))

@app.post("/api/feedback")
async def provide_feedback(request: FeedbackRequest):
    """Provide feedback on ticket resolution"""
    try:
        # Update ticket with feedback
        if request.ticket_id in demo_tickets:
            demo_tickets[request.ticket_id].update({
                "satisfaction": request.satisfaction,
                "resolution_time": request.resolution_time,
                "customer_feedback": request.comments,
                "updated_at": datetime.now().isoformat()
            })
        
        # Provide feedback to Brain AI
        result = await brain_ai.provide_feedback(
            memory_id=request.ticket_id,
            feedback_type="positive" if request.satisfaction >= 4 else "negative",
            outcome={
                "satisfaction": request.satisfaction,
                "resolution_time": request.resolution_time,
                "comments": request.comments
            },
            source="customer"
        )
        
        return create_success_response(result)
        
    except Exception as e:
        logger.error(f"Error providing feedback: {e}")
        return create_error_response(str(e))

@app.get("/api/memories")
async def get_memories(limit: int = 50):
    """Get stored memories"""
    try:
        memories = await brain_ai.get_memories(limit)
        formatted_memories = [format_memory_for_display(mem) for mem in memories]
        return create_success_response({
            "total": len(memories),
            "memories": formatted_memories
        })
    except Exception as e:
        return create_error_response(str(e))

@app.get("/api/analytics")
async def get_analytics():
    """Get analytics data"""
    try:
        # Generate analytics data
        tickets_by_priority = {}
        tickets_by_status = {}
        satisfaction_scores = []
        
        for ticket in demo_tickets.values():
            # Priority distribution
            priority = ticket.get("priority", "unknown")
            tickets_by_priority[priority] = tickets_by_priority.get(priority, 0) + 1
            
            # Status distribution
            status = ticket.get("status", "unknown")
            tickets_by_status[status] = tickets_by_status.get(status, 0) + 1
            
            # Satisfaction scores
            if ticket.get("satisfaction"):
                satisfaction_scores.append(ticket["satisfaction"])
        
        avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0
        
        analytics = {
            "tickets_by_priority": tickets_by_priority,
            "tickets_by_status": tickets_by_status,
            "average_satisfaction": round(avg_satisfaction, 2),
            "total_customers": len(demo_customers),
            "total_tickets": len(demo_tickets),
            "resolution_rate": len([t for t in demo_tickets.values() if t.get("status") == "resolved"]) / len(demo_tickets) * 100
        }
        
        return create_success_response(analytics)
    except Exception as e:
        return create_error_response(str(e))

# WebSocket processing function
async def process_support_ticket_websocket(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process support ticket via WebSocket"""
    try:
        result = await brain_ai.process_input(data, {
            "domain": "customer_support",
            "source": "websocket"
        })
        return result
    except Exception as e:
        return {"error": str(e)}

# Main execution
if __name__ == "__main__":
    logger.info("🚀 Starting Customer Support Assistant...")
    logger.info("📡 Application will be available at: http://localhost:8000")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
