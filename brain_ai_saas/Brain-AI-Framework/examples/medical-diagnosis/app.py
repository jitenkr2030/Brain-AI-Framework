#!/usr/bin/env python3
"""
Medical Diagnosis Assistant
Brain AI-powered medical diagnostic support with patient history and treatment recommendations
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
    generate_patient_record, generate_symptoms, generate_lab_results, generate_patient_batch
)
from web_components import WebComponents

# Pydantic models for API
class PatientRequest(BaseModel):
    name: str
    age: int
    gender: str
    symptoms: List[str]
    medical_history: List[str]
    current_medications: List[str]
    allergies: List[str]

class DiagnosisRequest(BaseModel):
    patient_id: str
    symptoms: List[str]
    lab_results: Dict[str, Any]
    urgency: str

class LabRequest(BaseModel):
    patient_id: str
    test_type: str
    results: Dict[str, Any]

class TreatmentRequest(BaseModel):
    patient_id: str
    diagnosis: str
    treatment_plan: str
    follow_up_date: str

# Initialize FastAPI app
app = FastAPI(
    title="Medical Diagnosis Assistant - Brain AI",
    description="🏥 AI-powered medical diagnostic support with persistent patient knowledge",
    version="1.0.0"
)

# Templates
templates = Jinja2Templates(directory="templates")

# Global Brain AI instance
brain_ai = BrainAIWrapper("MedicalDiagnosisAssistant")

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
demo_patients = {}
demo_diagnoses = {}
demo_treatments = {}
demo_lab_results = {}

# Initialize demo data
def initialize_demo_data():
    """Initialize demo data for the medical application"""
    logger.info("Initializing medical demo data...")
    
    # Generate patients
    patients = generate_patient_batch(15)
    for patient in patients:
        demo_patients[patient.id] = {
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "medical_history": patient.medical_history,
            "current_medications": patient.current_medications,
            "allergies": patient.allergies,
            "blood_type": patient.blood_type,
            "registration_date": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
        }
    
    # Generate sample diagnoses
    sample_diagnoses = [
        {
            "diagnosis_id": str(uuid.uuid4()),
            "patient_id": list(demo_patients.keys())[0],
            "primary_diagnosis": "Upper Respiratory Infection",
            "secondary_diagnoses": ["Allergic Rhinitis"],
            "confidence": 0.87,
            "symptoms": ["cough", "sore_throat", "nasal_congestion"],
            "treatment": "Supportive care, rest, increased fluids",
            "created_at": datetime.now().isoformat(),
            "status": "active"
        },
        {
            "diagnosis_id": str(uuid.uuid4()),
            "patient_id": list(demo_patients.keys())[1],
            "primary_diagnosis": "Hypertension",
            "secondary_diagnoses": ["Stage 1"],
            "confidence": 0.92,
            "symptoms": ["headache", "dizziness"],
            "treatment": "Lifestyle modifications, ACE inhibitor",
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
    ]
    
    for diagnosis in sample_diagnoses:
        demo_diagnoses[diagnosis["diagnosis_id"]] = diagnosis
    
    logger.info(f"Generated {len(demo_patients)} patients and {len(demo_diagnoses)} diagnoses")

# Application startup
@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    await brain_ai.initialize()
    initialize_demo_data()
    logger.info("🏥 Medical Diagnosis Assistant started successfully!")

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time medical updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Process different message types
            if message["type"] == "process_diagnosis":
                result = await process_diagnosis_websocket(message["data"])
                await websocket.send_text(json.dumps({
                    "type": "diagnosis_processed",
                    "data": result
                }))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# API Routes

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    html_content = WebComponents.get_base_html(
        "Medical Diagnosis Dashboard",
        "Medical Diagnosis Assistant",
        additional_css="""
        .patient-card {
            border-left: 4px solid #28a745;
            transition: all 0.3s ease;
        }
        .patient-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        }
        .diagnosis-confidence-high { border-left-color: #28a745; }
        .diagnosis-confidence-medium { border-left-color: #ffc107; }
        .diagnosis-confidence-low { border-left-color: #dc3545; }
        .symptom-tag {
            display: inline-block;
            padding: 4px 8px;
            margin: 2px;
            background-color: #e3f2fd;
            border-radius: 15px;
            font-size: 0.8rem;
            color: #1565c0;
        }
        .urgency-critical { background-color: #ffebee; border-left: 4px solid #f44336; }
        .urgency-high { background-color: #fff3e0; border-left: 4px solid #ff9800; }
        .urgency-medium { background-color: #f3e5f5; border-left: 4px solid #9c27b0; }
        .urgency-low { background-color: #e8f5e8; border-left: 4px solid #4caf50; }
        .medical-icon {
            font-size: 1.5rem;
            color: #2196f3;
        }
        """,
        additional_js="""
        // Medical Diagnosis specific JavaScript
        let currentPatient = null;
        let currentDiagnoses = [];
        
        async function loadMedicalData() {
            showLoading('dashboard-content');
            
            try {
                const [patientsResponse, diagnosesResponse, statsResponse] = await Promise.all([
                    apiCall('/api/patients'),
                    apiCall('/api/diagnoses'),
                    apiCall('/api/status')
                ]);
                
                renderMedicalDashboard(patientsResponse, diagnosesResponse, statsResponse);
            } catch (error) {
                console.error('Failed to load medical data:', error);
                showAlert('Failed to load dashboard data', 'danger');
            }
        }
        
        function renderMedicalDashboard(patients, diagnoses, stats) {
            const content = document.getElementById('dashboard-content');
            content.innerHTML = `
                <div class="row">
                    <div class="col-md-3 mb-4">
                        <div class="metric-card">
                            <i class="fas fa-user-injured brain-ai-icon"></i>
                            <div class="metric-value">${Object.keys(patients).length}</div>
                            <div>Total Patients</div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-4">
                        <div class="metric-card">
                            <i class="fas fa-stethoscope brain-ai-icon"></i>
                            <div class="metric-value">${Object.keys(diagnoses).length}</div>
                            <div>Active Diagnoses</div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-4">
                        <div class="metric-card">
                            <i class="fas fa-chart-line brain-ai-icon"></i>
                            <div class="metric-value">${calculateAverageConfidence(diagnoses)}</div>
                            <div>Avg Confidence</div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-4">
                        <div class="metric-card">
                            <i class="fas fa-heartbeat brain-ai-icon"></i>
                            <div class="metric-value">${getUrgentCasesCount(diagnoses)}</div>
                            <div>Urgent Cases</div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-md-8">
                        <div class="card card-brain-ai">
                            <div class="card-header">
                                <h5><i class="fas fa-user-md me-2"></i>Recent Diagnoses</h5>
                            </div>
                            <div class="card-body">
                                ${renderDiagnosesList(diagnoses)}
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card card-brain-ai">
                            <div class="card-header">
                                <h5><i class="fas fa-users me-2"></i>Patient Overview</h5>
                            </div>
                            <div class="card-body">
                                ${renderPatientsList(patients)}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-md-12">
                        <div class="card card-brain-ai">
                            <div class="card-header">
                                <h5><i class="fas fa-plus me-2"></i>New Patient Registration</h5>
                            </div>
                            <div class="card-body">
                                ${renderPatientRegistrationForm()}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-md-12">
                        <div class="card card-brain-ai">
                            <div class="card-header">
                                <h5><i class="fas fa-diagnoses me-2"></i>AI-Assisted Diagnosis</h5>
                            </div>
                            <div class="card-body">
                                ${renderDiagnosisForm(patients)}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        function calculateAverageConfidence(diagnoses) {
            const confidences = Object.values(diagnoses).map(d => d.confidence);
            const avg = confidences.reduce((a, b) => a + b, 0) / confidences.length;
            return (avg * 100).toFixed(1) + '%';
        }
        
        function getUrgentCasesCount(diagnoses) {
            return Object.values(diagnoses).filter(d => 
                d.symptoms.some(s => ['chest_pain', 'shortness_of_breath', 'severe_headache'].includes(s))
            ).length;
        }
        
        function renderDiagnosesList(diagnoses) {
            const diagnosesArray = Object.values(diagnoses).sort((a, b) => 
                new Date(b.created_at) - new Date(a.created_at)
            ).slice(0, 10);
            
            if (diagnosesArray.length === 0) {
                return '<p class="text-muted">No diagnoses found.</p>';
            }
            
            return diagnosesArray.map(diagnosis => `
                <div class="d-flex justify-content-between align-items-center border-bottom py-2 diagnosis-confidence-${getConfidenceClass(diagnosis.confidence)}">
                    <div>
                        <strong>${diagnosis.primary_diagnosis}</strong>
                        <br>
                        <small class="text-muted">
                            Patient: ${diagnosis.patient_id} • Confidence: ${(diagnosis.confidence * 100).toFixed(1)}%
                        </small>
                        <div class="mt-1">
                            ${diagnosis.symptoms.map(s => `<span class="symptom-tag">${s.replace('_', ' ')}</span>`).join('')}
                        </div>
                    </div>
                    <div class="text-end">
                        <span class="badge bg-${getConfidenceColor(diagnosis.confidence)}">${(diagnosis.confidence * 100).toFixed(0)}%</span>
                        <br>
                        <small class="text-muted">${formatDate(diagnosis.created_at)}</small>
                    </div>
                </div>
            `).join('');
        }
        
        function renderPatientsList(patients) {
            const patientsArray = Object.values(patients).slice(0, 8);
            
            return patientsArray.map(patient => `
                <div class="d-flex align-items-center border-bottom py-2 patient-card">
                    <div class="medical-icon me-3">
                        <i class="fas fa-${patient.gender === 'male' ? 'male' : 'female'}"></i>
                    </div>
                    <div>
                        <strong>${patient.name}</strong>
                        <br>
                        <small class="text-muted">Age: ${patient.age} • ${patient.gender}</small>
                        <br>
                        <small class="text-muted">Conditions: ${patient.medical_history.length}</small>
                    </div>
                </div>
            `).join('');
        }
        
        function renderPatientRegistrationForm() {
            const symptomsOptions = [
                'fever', 'headache', 'cough', 'sore_throat', 'nausea', 'vomiting',
                'abdominal_pain', 'chest_pain', 'shortness_of_breath', 'dizziness',
                'fatigue', 'joint_pain', 'rash', 'swelling'
            ].map(s => `<option value="${s}">${s.replace('_', ' ')}</option>`).join('');
            
            return `
                <form id="patient-form" onsubmit="registerPatient(event)">
                    <div class="row">
                        <div class="col-md-4">
                            <div class="form-floating">
                                <input type="text" class="form-control" id="patient-name" required>
                                <label for="patient-name">Patient Name</label>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="form-floating">
                                <input type="number" class="form-control" id="patient-age" min="1" max="120" required>
                                <label for="patient-age">Age</label>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="form-floating">
                                <select class="form-select" id="patient-gender" required>
                                    <option value="">Gender</option>
                                    <option value="male">Male</option>
                                    <option value="female">Female</option>
                                </select>
                                <label for="patient-gender">Gender</label>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="form-floating">
                                <select class="form-select" id="patient-blood-type" required>
                                    <option value="">Blood Type</option>
                                    <option value="A+">A+</option>
                                    <option value="A-">A-</option>
                                    <option value="B+">B+</option>
                                    <option value="B-">B-</option>
                                    <option value="AB+">AB+</option>
                                    <option value="AB-">AB-</option>
                                    <option value="O+">O+</option>
                                    <option value="O-">O-</option>
                                </select>
                                <label for="patient-blood-type">Blood Type</label>
                            </div>
                        </div>
                    </div>
                    <div class="row mt-3">
                        <div class="col-md-6">
                            <div class="form-floating">
                                <select class="form-select" id="patient-symptoms" multiple>
                                    ${symptomsOptions}
                                </select>
                                <label for="patient-symptoms">Current Symptoms</label>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-floating">
                                <select class="form-select" id="patient-history" multiple>
                                    <option value="hypertension">Hypertension</option>
                                    <option value="diabetes">Diabetes</option>
                                    <option value="asthma">Asthma</option>
                                    <option value="heart_disease">Heart Disease</option>
                                    <option value="arthritis">Arthritis</option>
                                </select>
                                <label for="patient-history">Medical History</label>
                            </div>
                        </div>
                    </div>
                    <div class="row mt-3">
                        <div class="col-md-6">
                            <div class="form-floating">
                                <input type="text" class="form-control" id="patient-medications">
                                <label for="patient-medications">Current Medications (comma separated)</label>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-floating">
                                <input type="text" class="form-control" id="patient-allergies">
                                <label for="patient-allergies">Allergies (comma separated)</label>
                            </div>
                        </div>
                    </div>
                    <div class="row mt-3">
                        <div class="col-md-12">
                            <button type="submit" class="btn btn-brain-ai">
                                <i class="fas fa-user-plus me-2"></i>Register Patient
                            </button>
                        </div>
                    </div>
                </form>
            `;
        }
        
        function renderDiagnosisForm(patients) {
            const patientsOptions = Object.values(patients).map(p => 
                `<option value="${p.id}">${p.name} (Age: ${p.age})</option>`
            ).join('');
            
            const urgencyOptions = [
                {value: 'low', label: 'Low Priority'},
                {value: 'medium', label: 'Medium Priority'},
                {value: 'high', label: 'High Priority'},
                {value: 'critical', label: 'Critical'}
            ];
            
            const symptomsOptions = [
                'fever', 'headache', 'cough', 'sore_throat', 'nausea', 'vomiting',
                'abdominal_pain', 'chest_pain', 'shortness_of_breath', 'dizziness',
                'fatigue', 'joint_pain', 'rash', 'swelling'
            ].map(s => `<option value="${s}">${s.replace('_', ' ')}</option>`).join('');
            
            return `
                <form id="diagnosis-form" onsubmit="processDiagnosis(event)">
                    <div class="row">
                        <div class="col-md-4">
                            <div class="form-floating">
                                <select class="form-select" id="diagnosis-patient" required>
                                    <option value="">Select Patient</option>
                                    ${patientsOptions}
                                </select>
                                <label for="diagnosis-patient">Patient</label>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="form-floating">
                                <select class="form-select" id="diagnosis-urgency" required>
                                    <option value="">Urgency Level</option>
                                    ${urgencyOptions.map(o => `<option value="${o.value}">${o.label}</option>`).join('')}
                                </select>
                                <label for="diagnosis-urgency">Urgency</label>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <button type="button" class="btn btn-outline-primary mt-2" onclick="generateLabResults()">
                                <i class="fas fa-vial me-2"></i>Generate Lab Results
                            </button>
                        </div>
                    </div>
                    <div class="row mt-3">
                        <div class="col-md-8">
                            <div class="form-floating">
                                <select class="form-select" id="diagnosis-symptoms" multiple required>
                                    ${symptomsOptions}
                                </select>
                                <label for="diagnosis-symptoms">Observed Symptoms</label>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div id="lab-results-display" class="mt-2">
                                <small class="text-muted">Lab results will appear here</small>
                            </div>
                        </div>
                    </div>
                    <div class="row mt-3">
                        <div class="col-md-12">
                            <button type="submit" class="btn btn-brain-ai">
                                <i class="fas fa-brain me-2"></i>AI-Assisted Diagnosis
                            </button>
                        </div>
                    </div>
                </form>
            `;
        }
        
        async function registerPatient(event) {
            event.preventDefault();
            
            const formData = {
                name: document.getElementById('patient-name').value,
                age: parseInt(document.getElementById('patient-age').value),
                gender: document.getElementById('patient-gender').value,
                symptoms: Array.from(document.getElementById('patient-symptoms').selectedOptions).map(o => o.value),
                medical_history: Array.from(document.getElementById('patient-history').selectedOptions).map(o => o.value),
                current_medications: document.getElementById('patient-medications').value.split(',').map(s => s.trim()).filter(s => s),
                allergies: document.getElementById('patient-allergies').value.split(',').map(s => s.trim()).filter(s => s),
                blood_type: document.getElementById('patient-blood-type').value
            };
            
            try {
                const response = await apiCall('/api/patients', 'POST', formData);
                showAlert('Patient registered successfully!', 'success');
                loadMedicalData();
                document.getElementById('patient-form').reset();
            } catch (error) {
                showAlert('Failed to register patient', 'danger');
            }
        }
        
        async function processDiagnosis(event) {
            event.preventDefault();
            
            const selectedSymptoms = Array.from(document.getElementById('diagnosis-symptoms').selectedOptions).map(o => o.value);
            
            const formData = {
                patient_id: document.getElementById('diagnosis-patient').value,
                symptoms: selectedSymptoms,
                urgency: document.getElementById('diagnosis-urgency').value,
                lab_results: await generateSampleLabResults()
            };
            
            try {
                const response = await apiCall('/api/diagnose', 'POST', formData);
                showAlert('Diagnosis completed!', 'success');
                displayDiagnosisResults(response);
                loadMedicalData();
            } catch (error) {
                showAlert('Failed to process diagnosis', 'danger');
            }
        }
        
        function generateLabResults() {
            const labResults = {
                "blood_pressure": `${randomInt(100, 140)}/${randomInt(60, 90)}`,
                "heart_rate": `${randomInt(60, 100)} bpm`,
                "temperature": `${(36.0 + Math.random() * 2).toFixed(1)}°C`,
                "oxygen_saturation": `${randomInt(95, 100)}%`
            };
            
            document.getElementById('lab-results-display').innerHTML = `
                <div class="card">
                    <div class="card-body">
                        <h6 class="card-title">Lab Results</h6>
                        <small class="text-muted">BP: ${labResults.blood_pressure} | HR: ${labResults.heart_rate} | Temp: ${labResults.temperature} | O2: ${labResults.oxygen_saturation}</small>
                    </div>
                </div>
            `;
        }
        
        async function generateSampleLabResults() {
            return {
                "blood_pressure": `${randomInt(100, 140)}/${randomInt(60, 90)}`,
                "heart_rate": `${randomInt(60, 100)} bpm`,
                "temperature": `${(36.0 + Math.random() * 2).toFixed(1)}°C`,
                "oxygen_saturation": `${randomInt(95, 100)}%`
            };
        }
        
        function displayDiagnosisResults(result) {
            const modal = document.createElement('div');
            modal.innerHTML = `
                <div class="modal fade" id="diagnosisModal" tabindex="-1">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">AI Diagnosis Results</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>Primary Diagnosis</h6>
                                        <p class="text-success">${result.data.primary_diagnosis}</p>
                                        <p><strong>Confidence:</strong> ${(result.data.confidence * 100).toFixed(1)}%</p>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>Secondary Diagnoses</h6>
                                        <ul>
                                            ${result.data.secondary_diagnoses.map(d => `<li>${d}</li>`).join('')}
                                        </ul>
                                    </div>
                                </div>
                                <div class="row mt-3">
                                    <div class="col-md-12">
                                        <h6>Recommended Treatment</h6>
                                        <p>${result.data.treatment}</p>
                                    </div>
                                </div>
                                <div class="row mt-3">
                                    <div class="col-md-12">
                                        <h6>AI Insights</h6>
                                        <ul>
                                            ${result.data.insights.map(insight => `<li>${insight}</li>`).join('')}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            const modalInstance = new bootstrap.Modal(modal.querySelector('.modal'));
            modalInstance.show();
        }
        
        function getConfidenceClass(confidence) {
            if (confidence >= 0.8) return 'high';
            if (confidence >= 0.6) return 'medium';
            return 'low';
        }
        
        function getConfidenceColor(confidence) {
            if (confidence >= 0.8) return 'success';
            if (confidence >= 0.6) return 'warning';
            return 'danger';
        }
        
        function formatDate(dateString) {
            return new Date(dateString).toLocaleDateString();
        }
        
        function randomInt(min, max) {
            return Math.floor(Math.random() * (max - min + 1)) + min;
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

@app.get("/api/patients")
async def get_patients():
    """Get all patients"""
    return create_success_response(demo_patients)

@app.post("/api/patients")
async def create_patient(request: PatientRequest):
    """Create a new patient record"""
    try:
        patient_id = str(uuid.uuid4())
        
        patient_data = {
            "id": patient_id,
            "name": request.name,
            "age": request.age,
            "gender": request.gender,
            "medical_history": request.medical_history,
            "current_medications": request.current_medications,
            "allergies": request.allergies,
            "blood_type": "Unknown",  # Could be added to request model
            "registration_date": datetime.now().isoformat(),
            "total_visits": 1,
            "status": "active"
        }
        
        # Store patient
        demo_patients[patient_id] = patient_data
        
        # Process through Brain AI
        brain_ai_data = {
            "patient_id": patient_id,
            "action": "patient_registration",
            "age": request.age,
            "gender": request.gender,
            "symptoms": request.symptoms,
            "medical_history": request.medical_history,
            "medications": request.current_medications,
            "allergies": request.allergies
        }
        
        brain_ai_result = await brain_ai.process_input(brain_ai_data, {
            "domain": "medical_diagnosis",
            "priority": "normal"
        })
        
        return create_success_response({
            "patient": patient_data,
            "brain_ai_analysis": brain_ai_result
        }, "Patient registered successfully")
        
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        return create_error_response(str(e))

@app.get("/api/diagnoses")
async def get_diagnoses():
    """Get all diagnoses"""
    return create_success_response(demo_diagnoses)

@app.post("/api/diagnose")
async def process_diagnosis(request: DiagnosisRequest):
    """Process medical diagnosis through Brain AI"""
    try:
        # Create diagnosis record
        diagnosis_id = str(uuid.uuid4())
        
        # Generate AI-powered diagnosis
        diagnosis_result = await brain_ai.process_input({
            "patient_id": request.patient_id,
            "symptoms": request.symptoms,
            "lab_results": request.lab_results,
            "urgency": request.urgency,
            "timestamp": datetime.now().isoformat()
        }, {
            "domain": "medical_diagnosis",
            "priority": request.urgency,
            "context": "clinical_decision_support"
        })
        
        # Simulate diagnosis logic (in real implementation, this would be more sophisticated)
        primary_diagnosis = generate_ai_diagnosis(request.symptoms)
        
        diagnosis_data = {
            "diagnosis_id": diagnosis_id,
            "patient_id": request.patient_id,
            "primary_diagnosis": primary_diagnosis["diagnosis"],
            "secondary_diagnoses": primary_diagnosis["secondary"],
            "confidence": diagnosis_result.get("reasoning_result", {}).get("confidence", 0.75),
            "symptoms": request.symptoms,
            "treatment": primary_diagnosis["treatment"],
            "urgency": request.urgency,
            "lab_results": request.lab_results,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "ai_insights": diagnosis_result.get("insights", [])
        }
        
        # Store diagnosis
        demo_diagnoses[diagnosis_id] = diagnosis_data
        
        return create_success_response(diagnosis_data, "Diagnosis completed successfully")
        
    except Exception as e:
        logger.error(f"Error processing diagnosis: {e}")
        return create_error_response(str(e))

@app.post("/api/lab-results")
async def submit_lab_results(request: LabRequest):
    """Submit lab test results"""
    try:
        lab_id = str(uuid.uuid4())
        
        lab_data = {
            "lab_id": lab_id,
            "patient_id": request.patient_id,
            "test_type": request.test_type,
            "results": request.results,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        demo_lab_results[lab_id] = lab_data
        
        # Process through Brain AI
        brain_ai_result = await brain_ai.process_input({
            "patient_id": request.patient_id,
            "lab_type": request.test_type,
            "lab_results": request.results,
            "timestamp": datetime.now().isoformat()
        }, {
            "domain": "medical_diagnosis",
            "context": "laboratory_analysis"
        })
        
        return create_success_response({
            "lab_data": lab_data,
            "ai_analysis": brain_ai_result
        }, "Lab results processed successfully")
        
    except Exception as e:
        logger.error(f"Error processing lab results: {e}")
        return create_error_response(str(e))

@app.post("/api/treatment")
async def create_treatment_plan(request: TreatmentRequest):
    """Create treatment plan"""
    try:
        treatment_id = str(uuid.uuid4())
        
        treatment_data = {
            "treatment_id": treatment_id,
            "patient_id": request.patient_id,
            "diagnosis": request.diagnosis,
            "treatment_plan": request.treatment_plan,
            "follow_up_date": request.follow_up_date,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        demo_treatments[treatment_id] = treatment_data
        
        # Provide feedback to Brain AI
        await brain_ai.provide_feedback(
            memory_id=request.patient_id,
            feedback_type="positive",
            outcome={
                "action": "treatment_plan_created",
                "diagnosis": request.diagnosis,
                "treatment": request.treatment_plan
            },
            source="physician"
        )
        
        return create_success_response(treatment_data, "Treatment plan created successfully")
        
    except Exception as e:
        logger.error(f"Error creating treatment plan: {e}")
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
        diagnoses_by_confidence = {"high": 0, "medium": 0, "low": 0}
        diagnoses_by_urgency = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        age_distribution = {"0-18": 0, "19-35": 0, "36-50": 0, "51-65": 0, "65+": 0}
        
        for diagnosis in demo_diagnoses.values():
            confidence = diagnosis.get("confidence", 0)
            if confidence >= 0.8:
                diagnoses_by_confidence["high"] += 1
            elif confidence >= 0.6:
                diagnoses_by_confidence["medium"] += 1
            else:
                diagnoses_by_confidence["low"] += 1
            
            urgency = diagnosis.get("urgency", "medium")
            diagnoses_by_urgency[urgency] = diagnoses_by_urgency.get(urgency, 0) + 1
        
        for patient in demo_patients.values():
            age = patient.get("age", 0)
            if age <= 18:
                age_distribution["0-18"] += 1
            elif age <= 35:
                age_distribution["19-35"] += 1
            elif age <= 50:
                age_distribution["36-50"] += 1
            elif age <= 65:
                age_distribution["51-65"] += 1
            else:
                age_distribution["65+"] += 1
        
        analytics = {
            "total_patients": len(demo_patients),
            "total_diagnoses": len(demo_diagnoses),
            "diagnoses_by_confidence": diagnoses_by_confidence,
            "diagnoses_by_urgency": diagnoses_by_urgency,
            "age_distribution": age_distribution,
            "average_confidence": sum(d.get("confidence", 0) for d in demo_diagnoses.values()) / len(demo_diagnoses) if demo_diagnoses else 0
        }
        
        return create_success_response(analytics)
    except Exception as e:
        return create_error_response(str(e))

# Helper functions
def generate_ai_diagnosis(symptoms: List[str]) -> Dict[str, Any]:
    """Generate AI-powered diagnosis based on symptoms"""
    # Simple symptom-to-diagnosis mapping for demo
    symptom_diagnosis_map = {
        frozenset(["fever", "cough", "sore_throat"]): {
            "diagnosis": "Upper Respiratory Infection",
            "secondary": ["Common Cold", "Viral Pharyngitis"],
            "treatment": "Supportive care, rest, increased fluids, symptom relief"
        },
        frozenset(["headache", "dizziness"]): {
            "diagnosis": "Hypertension",
            "secondary": ["Benign Essential Hypertension"],
            "treatment": "Lifestyle modifications, blood pressure monitoring, ACE inhibitor if needed"
        },
        frozenset(["chest_pain", "shortness_of_breath"]): {
            "diagnosis": "Acute Coronary Syndrome",
            "secondary": ["Possible Myocardial Infarction"],
            "treatment": "Immediate cardiology consultation, ECG, cardiac enzymes, oxygen therapy"
        },
        frozenset(["abdominal_pain", "nausea", "vomiting"]): {
            "diagnosis": "Acute Gastroenteritis",
            "secondary": ["Food Poisoning"],
            "treatment": "Bland diet, hydration, anti-emetics if severe"
        }
    }
    
    # Find matching diagnosis
    symptom_set = frozenset(symptoms)
    for symptom_pattern, diagnosis_info in symptom_diagnosis_map.items():
        if symptom_pattern.issubset(symptom_set):
            return diagnosis_info
    
    # Default diagnosis if no match found
    return {
        "diagnosis": "Symptoms require further evaluation",
        "secondary": ["Rule out multiple conditions"],
        "treatment": "Detailed history and physical examination, consider additional testing"
    }

# WebSocket processing function
async def process_diagnosis_websocket(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process diagnosis via WebSocket"""
    try:
        result = await brain_ai.process_input(data, {
            "domain": "medical_diagnosis",
            "source": "websocket"
        })
        return result
    except Exception as e:
        return {"error": str(e)}

# Main execution
if __name__ == "__main__":
    logger.info("🏥 Starting Medical Diagnosis Assistant...")
    logger.info("📡 Application will be available at: http://localhost:8001")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
