#!/usr/bin/env python3
"""
Demo Data Generators
Realistic sample data generators for Brain AI example applications
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from faker import Faker
import json

fake = Faker()

# Common data generators

def generate_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())

def generate_timestamp(days_offset: int = 0) -> str:
    """Generate a timestamp with optional offset"""
    now = datetime.now()
    if days_offset != 0:
        now += timedelta(days=days_offset)
    return now.isoformat()

def generate_email(first_name: str = None, last_name: str = None) -> str:
    """Generate a realistic email address"""
    if not first_name or not last_name:
        first_name = fake.first_name()
        last_name = fake.last_name()
    domain = random.choice(['gmail.com', 'yahoo.com', 'outlook.com', 'company.com'])
    return f"{first_name.lower()}.{last_name.lower()}@{domain}"

# Customer Support Demo Data

@dataclass
class CustomerProfile:
    id: str
    name: str
    email: str
    phone: str
    account_created: str
    total_orders: int
    lifetime_value: float
    satisfaction_score: float
    preferences: Dict[str, Any]

def generate_customer_profile() -> CustomerProfile:
    """Generate a realistic customer profile"""
    first_name = fake.first_name()
    last_name = fake.last_name()
    
    return CustomerProfile(
        id=generate_id(),
        name=f"{first_name} {last_name}",
        email=generate_email(first_name, last_name),
        phone=fake.phone_number(),
        account_created=generate_timestamp(days_offset=-random.randint(30, 365)),
        total_orders=random.randint(1, 50),
        lifetime_value=round(random.uniform(100, 5000), 2),
        satisfaction_score=round(random.uniform(3.0, 5.0), 1),
        preferences={
            "communication_style": random.choice(["formal", "casual", "friendly"]),
            "preferred_contact": random.choice(["email", "phone", "chat"]),
            "language": "en",
            "timezone": "UTC"
        }
    )

def generate_support_ticket(customer_id: str = None) -> Dict[str, Any]:
    """Generate a realistic support ticket"""
    if not customer_id:
        customer_id = generate_id()
    
    issue_types = [
        "account_access", "payment_issue", "product_question", 
        "technical_support", "billing_inquiry", "feature_request",
        "bug_report", "delivery_issue"
    ]
    
    priorities = ["low", "medium", "high", "critical"]
    statuses = ["open", "in_progress", "waiting_customer", "resolved", "closed"]
    
    return {
        "ticket_id": generate_id(),
        "customer_id": customer_id,
        "subject": random.choice([
            "Unable to login to my account",
            "Payment was declined incorrectly",
            "Question about product features",
            "Website not loading properly",
            "Billing discrepancy on last invoice",
            "Feature request: Dark mode",
            "Bug in mobile app",
            "Delivery was delayed"
        ]),
        "description": fake.text(max_nb_chars=500),
        "issue_type": random.choice(issue_types),
        "priority": random.choice(priorities),
        "status": random.choice(statuses),
        "created_at": generate_timestamp(days_offset=-random.randint(0, 30)),
        "updated_at": generate_timestamp(),
        "agent_assigned": fake.name(),
        "customer_satisfaction": random.choice([None, 3, 4, 5]) if random.choice([True, False]) else None,
        "resolution_time_hours": round(random.uniform(1, 72), 1) if random.choice([True, False]) else None,
        "tags": random.sample(["urgent", "billing", "technical", "feature", "bug"], k=random.randint(1, 3))
    }

# Medical Diagnosis Demo Data

@dataclass
class PatientRecord:
    id: str
    name: str
    age: int
    gender: str
    medical_history: List[str]
    current_medications: List[str]
    allergies: List[str]
    blood_type: str

def generate_patient_record() -> PatientRecord:
    """Generate a realistic patient record"""
    first_name = fake.first_name()
    last_name = fake.last_name()
    
    medical_conditions = [
        "hypertension", "diabetes_type2", "asthma", "arthritis",
        "depression", "anxiety", "migraine", "back_pain",
        "allergies", "heart_disease", "kidney_disease"
    ]
    
    medications = [
        "lisinopril", "metformin", "albuterol", "ibuprofen",
        "sertraline", "omeprazole", "amoxicillin", "prednisone"
    ]
    
    allergies = [
        "penicillin", "shellfish", "nuts", "latex", "pollen",
        "dust", "mold", "eggs", "dairy", "soy"
    ]
    
    return PatientRecord(
        id=generate_id(),
        name=f"{first_name} {last_name}",
        age=random.randint(18, 85),
        gender=random.choice(["male", "female"]),
        medical_history=random.sample(medical_conditions, k=random.randint(0, 3)),
        current_medications=random.sample(medications, k=random.randint(0, 2)),
        allergies=random.sample(allergies, k=random.randint(0, 2)),
        blood_type=random.choice(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
    )

def generate_symptoms() -> List[str]:
    """Generate realistic symptom combinations"""
    symptom_sets = [
        ["fever", "headache", "fatigue"],
        ["chest_pain", "shortness_of_breath", "sweating"],
        ["abdominal_pain", "nausea", "vomiting"],
        ["joint_pain", "stiffness", "swelling"],
        ["dizziness", "nausea", "vision_problems"],
        ["cough", "fever", "shortness_of_breath"],
        ["rash", "itching", "swelling"],
        ["headache", "nausea", "sensitivity_to_light"],
        ["back_pain", "leg_numbness", "difficulty_walking"],
        ["fatigue", "weight_loss", "night_sweats"]
    ]
    
    return random.choice(symptom_sets)

def generate_lab_results() -> Dict[str, Any]:
    """Generate realistic lab test results"""
    return {
        "complete_blood_count": {
            "white_blood_cells": round(random.uniform(4.0, 11.0), 1),
            "red_blood_cells": round(random.uniform(4.2, 6.1), 1),
            "hemoglobin": round(random.uniform(12.0, 18.0), 1),
            "platelets": random.randint(150, 450)
        },
        "metabolic_panel": {
            "glucose": round(random.uniform(70, 200), 0),
            "sodium": random.randint(135, 145),
            "potassium": round(random.uniform(3.5, 5.0), 1),
            "creatinine": round(random.uniform(0.6, 1.2), 1)
        },
        "inflammatory_markers": {
            "c_reactive_protein": round(random.uniform(0.1, 10.0), 1),
            "erythrocyte_sedimentation_rate": random.randint(5, 50)
        }
    }

# Shopping Assistant Demo Data

def generate_user_profile() -> Dict[str, Any]:
    """Generate a realistic user profile for shopping"""
    first_name = fake.first_name()
    last_name = fake.last_name()
    
    return {
        "user_id": generate_id(),
        "name": f"{first_name} {last_name}",
        "email": generate_email(first_name, last_name),
        "age": random.randint(18, 70),
        "gender": random.choice(["male", "female", "prefer_not_to_say"]),
        "location": {
            "city": fake.city(),
            "state": fake.state(),
            "country": "United States",
            "zip_code": fake.zipcode()
        },
        "preferences": {
            "categories": random.sample([
                "electronics", "clothing", "books", "home_garden",
                "sports", "beauty", "automotive", "toys"
            ], k=random.randint(2, 4)),
            "brands": random.sample([
                "Apple", "Nike", "Amazon", "Samsung", "Sony",
                "Adidas", "Microsoft", "Google", "LG", "Canon"
            ], k=random.randint(1, 3)),
            "price_range": random.choice(["budget", "mid-range", "premium"]),
            "shopping_frequency": random.choice(["weekly", "monthly", "occasionally"])
        },
        "account_created": generate_timestamp(days_offset=-random.randint(30, 730)),
        "total_orders": random.randint(1, 100),
        "total_spent": round(random.uniform(50, 5000), 2)
    }

def generate_product_catalog() -> List[Dict[str, Any]]:
    """Generate a realistic product catalog"""
    categories = {
        "electronics": [
            {"name": "Smartphone", "base_price": 699, "brands": ["Apple", "Samsung", "Google"]},
            {"name": "Laptop", "base_price": 899, "brands": ["Apple", "Dell", "HP", "Lenovo"]},
            {"name": "Headphones", "base_price": 149, "brands": ["Sony", "Bose", "Apple", "Samsung"]},
            {"name": "Tablet", "base_price": 399, "brands": ["Apple", "Samsung", "Amazon"]},
            {"name": "Smart Watch", "base_price": 299, "brands": ["Apple", "Samsung", "Fitbit"]}
        ],
        "clothing": [
            {"name": "T-Shirt", "base_price": 25, "brands": ["Nike", "Adidas", "H&M", "Zara"]},
            {"name": "Jeans", "base_price": 65, "brands": ["Levi's", "Dockers", "Wrangler"]},
            {"name": "Sneakers", "base_price": 89, "brands": ["Nike", "Adidas", "New Balance"]},
            {"name": "Jacket", "base_price": 120, "brands": ["North Face", "Patagonia", "Columbia"]},
            {"name": "Dress", "base_price": 55, "brands": ["Zara", "H&M", "Forever 21"]}
        ],
        "home_garden": [
            {"name": "Coffee Maker", "base_price": 79, "brands": ["Keurig", "Cuisinart", "Breville"]},
            {"name": "Vacuum Cleaner", "base_price": 199, "brands": ["Dyson", "Shark", "Hoover"]},
            {"name": "Air Purifier", "base_price": 149, "brands": ["LEVOIT", "Coway", "Blueair"]},
            {"name": "Garden Tools Set", "base_price": 89, "brands": ["Fiskars", "Corona", "AMES"]},
            {"name": "Indoor Plant", "base_price": 35, "brands": ["The Sill", "Bloomscape", "Plants.com"]}
        ]
    }
    
    products = []
    product_id = 1
    
    for category, items in categories.items():
        for item in items:
            for _ in range(3):  # 3 products per item type
                brand = random.choice(item["brands"])
                price_variation = random.uniform(0.8, 1.3)
                
                products.append({
                    "product_id": f"PROD_{product_id:04d}",
                    "name": f"{brand} {item['name']}",
                    "category": category,
                    "brand": brand,
                    "price": round(item["base_price"] * price_variation, 2),
                    "description": fake.text(max_nb_chars=200),
                    "features": random.sample([
                        "Wireless", "Waterproof", "Energy Efficient",
                        "Easy to Use", "Durable", "Compact",
                        "High Quality", "Modern Design"
                    ], k=random.randint(2, 4)),
                    "rating": round(random.uniform(3.0, 5.0), 1),
                    "review_count": random.randint(10, 1000),
                    "in_stock": random.choice([True, True, True, False]),  # 75% in stock
                    "image_url": f"https://picsum.photos/300/300?random={product_id}",
                    "created_at": generate_timestamp(days_offset=-random.randint(1, 365))
                })
                product_id += 1
    
    return products

# Financial Risk Demo Data

def generate_loan_application() -> Dict[str, Any]:
    """Generate a realistic loan application"""
    first_name = fake.first_name()
    last_name = fake.last_name()
    
    employment_types = ["full_time", "part_time", "self_employed", "retired", "student"]
    loan_types = ["personal", "auto", "mortgage", "business", "student"]
    
    return {
        "application_id": generate_id(),
        "applicant": {
            "name": f"{first_name} {last_name}",
            "email": generate_email(first_name, last_name),
            "phone": fake.phone_number(),
            "ssn_last_4": f"{random.randint(1000, 9999)}",
            "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat(),
            "address": {
                "street": fake.street_address(),
                "city": fake.city(),
                "state": fake.state(),
                "zip_code": fake.zipcode()
            }
        },
        "employment": {
            "type": random.choice(employment_types),
            "employer": fake.company(),
            "job_title": fake.job(),
            "years_employed": random.randint(0, 20),
            "annual_income": random.randint(30000, 150000),
            "monthly_income": 0  # Will be calculated
        },
        "loan_details": {
            "type": random.choice(loan_types),
            "amount_requested": random.randint(5000, 500000),
            "purpose": random.choice([
                "debt_consolidation", "home_improvement", "business_expansion",
                "education", "medical_expenses", "vacation", "car_purchase"
            ]),
            "term_months": random.choice([12, 24, 36, 48, 60, 84, 120]),
            "collateral": random.choice([None, "vehicle", "real_estate", "savings"])
        },
        "financial_profile": {
            "credit_score": random.randint(300, 850),
            "debt_to_income_ratio": round(random.uniform(0.1, 0.8), 2),
            "monthly_expenses": random.randint(1000, 8000),
            "existing_debts": random.randint(0, 5),
            "bankruptcy_history": random.choice([True, False]),
            "criminal_history": random.choice([True, False])
        },
        "application_date": generate_timestamp(days_offset=-random.randint(0, 90)),
        "status": random.choice(["pending", "under_review", "approved", "rejected"]),
        "risk_score": round(random.uniform(0.1, 1.0), 3)
    }

# Quality Control Demo Data

def generate_production_batch() -> Dict[str, Any]:
    """Generate production batch data for quality control"""
    product_types = ["electronics", "automotive", "textiles", "food", "pharmaceutical"]
    defect_types = ["dimensional", "surface", "functional", "cosmetic", "material"]
    
    return {
        "batch_id": generate_id(),
        "product_type": random.choice(product_types),
        "product_name": fake.catch_phrase(),
        "production_line": f"LINE_{random.randint(1, 5)}",
        "batch_size": random.randint(100, 1000),
        "production_date": generate_timestamp(days_offset=-random.randint(0, 30)),
        "operator": fake.name(),
        "shift": random.choice(["day", "evening", "night"]),
        "quality_metrics": {
            "defect_rate": round(random.uniform(0.01, 0.15), 3),
            "first_pass_yield": round(random.uniform(0.85, 0.99), 3),
            "customer_returns": random.randint(0, 10),
            "cycle_time": round(random.uniform(2.5, 8.0), 1)
        },
        "defects": [
            {
                "type": random.choice(defect_types),
                "severity": random.choice(["minor", "major", "critical"]),
                "count": random.randint(1, 20),
                "description": fake.sentence()
            } for _ in range(random.randint(0, 5))
        ],
        "environmental_conditions": {
            "temperature": round(random.uniform(18, 25), 1),
            "humidity": round(random.uniform(40, 70), 1),
            "pressure": round(random.uniform(990, 1020), 1)
        },
        "equipment_status": random.choice(["operational", "maintenance_required", "down"]),
        "materials_used": random.sample([
            "steel", "plastic", "rubber", "electronics", "fabric",
            "adhesives", "coatings", "fasteners"
        ], k=random.randint(2, 4))
    }

# Cybersecurity Demo Data

def generate_security_event() -> Dict[str, Any]:
    """Generate cybersecurity event data"""
    event_types = [
        "malware_detection", "phishing_attempt", "unauthorized_access",
        "data_breach", "ddos_attack", "insider_threat", "vulnerability_scan"
    ]
    
    severity_levels = ["low", "medium", "high", "critical"]
    sources = ["email", "web", "network", "endpoint", "user_activity"]
    
    return {
        "event_id": generate_id(),
        "timestamp": generate_timestamp(),
        "event_type": random.choice(event_types),
        "severity": random.choice(severity_levels),
        "source": random.choice(sources),
        "source_ip": fake.ipv4(),
        "destination_ip": fake.ipv4(),
        "user_id": f"user_{random.randint(1000, 9999)}",
        "description": fake.text(max_nb_chars=300),
        "affected_systems": random.sample([
            "web_server", "database", "email_server", "file_server",
            "workstation", "mobile_device", "network_device"
        ], k=random.randint(1, 3)),
        "mitigation_actions": random.sample([
            "blocked_ip", "quarantined_file", "reset_password",
            "updated_firewall", "patched_system", "notified_admin"
        ], k=random.randint(1, 3)),
        "status": random.choice(["open", "investigating", "resolved", "false_positive"]),
        "analyst_notes": fake.text(max_nb_chars=200) if random.choice([True, False]) else None,
        "related_events": [generate_id() for _ in range(random.randint(0, 3))] if random.choice([True, False]) else []
    }

# Utility functions for batch data generation

def generate_customer_batch(count: int = 10) -> List[CustomerProfile]:
    """Generate a batch of customer profiles"""
    return [generate_customer_profile() for _ in range(count)]

def generate_ticket_batch(count: int = 20, customer_ids: List[str] = None) -> List[Dict[str, Any]]:
    """Generate a batch of support tickets"""
    if not customer_ids:
        customer_ids = [generate_id() for _ in range(count)]
    
    return [generate_support_ticket(random.choice(customer_ids)) for _ in range(count)]

def generate_patient_batch(count: int = 15) -> List[PatientRecord]:
    """Generate a batch of patient records"""
    return [generate_patient_record() for _ in range(count)]

def generate_loan_batch(count: int = 25) -> List[Dict[str, Any]]:
    """Generate a batch of loan applications"""
    return [generate_loan_application() for _ in range(count)]

def generate_batch_batch(count: int = 12) -> List[Dict[str, Any]]:
    """Generate a batch of production data"""
    return [generate_production_batch() for _ in range(count)]

def generate_security_batch(count: int = 30) -> List[Dict[str, Any]]:
    """Generate a batch of security events"""
    return [generate_security_event() for _ in range(count)]

# Export all generators
__all__ = [
    # Common generators
    'generate_id', 'generate_timestamp', 'generate_email',
    
    # Customer Support
    'generate_customer_profile', 'generate_support_ticket',
    'generate_customer_batch', 'generate_ticket_batch',
    
    # Medical
    'generate_patient_record', 'generate_symptoms', 'generate_lab_results',
    'generate_patient_batch',
    
    # Shopping
    'generate_user_profile', 'generate_product_catalog',
    
    # Financial
    'generate_loan_application', 'generate_loan_batch',
    
    # Quality Control
    'generate_production_batch', 'generate_batch_batch',
    
    # Cybersecurity
    'generate_security_event', 'generate_security_batch'
]
