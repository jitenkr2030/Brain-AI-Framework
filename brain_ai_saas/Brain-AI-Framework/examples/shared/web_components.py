#!/usr/bin/env python3
"""
Shared Web Components
Reusable UI components for Brain AI example applications
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class WebComponents:
    """Shared web components for Brain AI examples"""
    
    @staticmethod
    def get_base_html(title: str, app_name: str, additional_css: str = "", additional_js: str = "") -> str:
        """Generate base HTML template"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Brain AI Framework</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <style>
        {WebComponents.get_base_css()}
        {additional_css}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-brain me-2"></i>
                Brain AI Framework - {app_name}
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">
                    <i class="fas fa-home me-1"></i>Home
                </a>
                <a class="nav-link" href="/status">
                    <i class="fas fa-chart-line me-1"></i>Status
                </a>
                <a class="nav-link" href="/memories">
                    <i class="fas fa-memory me-1"></i>Memories
                </a>
            </div>
        </div>
    </nav>

    <main class="container mt-4">
        {WebComponents.get_alert_containers()}
        <div id="main-content">
            <!-- Content will be loaded here -->
        </div>
    </main>

    <footer class="bg-light mt-5 py-3">
        <div class="container text-center">
            <small class="text-muted">
                <i class="fas fa-brain me-1"></i>
                Brain AI Framework Demo | Powered by {app_name}
                <span class="mx-2">•</span>
                Built with ❤️ by MiniMax Agent
            </small>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        {WebComponents.get_base_javascript()}
        {additional_js}
    </script>
</body>
</html>
        """

    @staticmethod
    def get_base_css() -> str:
        """Generate base CSS styles"""
        return """
        .brain-ai-gradient {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .card-brain-ai {
            border: none;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }
        
        .card-brain-ai:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
        }
        
        .brain-ai-icon {
            font-size: 2rem;
            color: #667eea;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        
        .status-online { background-color: #28a745; }
        .status-offline { background-color: #dc3545; }
        .status-warning { background-color: #ffc107; }
        
        .memory-strength {
            height: 20px;
            border-radius: 10px;
            background-color: #e9ecef;
            position: relative;
            overflow: hidden;
        }
        
        .memory-strength-bar {
            height: 100%;
            border-radius: 10px;
            transition: width 0.5s ease;
        }
        
        .strength-low { background-color: #dc3545; }
        .strength-medium { background-color: #ffc107; }
        .strength-high { background-color: #28a745; }
        
        .insight-card {
            background: linear-gradient(45deg, #f8f9fa, #e9ecef);
            border-left: 4px solid #667eea;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        
        .pulse-animation {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .loading-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .brain-ai-nav {
            background: linear-gradient(90deg, #667eea, #764ba2);
        }
        
        .tab-content {
            border: 1px solid #dee2e6;
            border-top: none;
            border-radius: 0 0 0.25rem 0.25rem;
            padding: 20px;
        }
        
        .form-floating {
            margin-bottom: 15px;
        }
        
        .btn-brain-ai {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: white;
            border-radius: 25px;
            padding: 10px 30px;
            transition: all 0.3s;
        }
        
        .btn-brain-ai:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            color: white;
        }
        """

    @staticmethod
    def get_base_javascript() -> str:
        """Generate base JavaScript functions"""
        return """
        // Global variables
        let brainAI = null;
        let currentTab = 'overview';
        
        // Initialize the application
        document.addEventListener('DOMContentLoaded', function() {
            initializeBrainAI();
            loadDashboard();
        });
        
        // Initialize Brain AI connection
        async function initializeBrainAI() {
            try {
                const response = await axios.get('/api/status');
                brainAI = response.data;
                updateStatusIndicators();
            } catch (error) {
                console.error('Failed to initialize Brain AI:', error);
                showAlert('Failed to connect to Brain AI system', 'danger');
            }
        }
        
        // Load dashboard data
        async function loadDashboard() {
            showLoading('main-content');
            
            try {
                const [statusResponse, memoriesResponse] = await Promise.all([
                    axios.get('/api/status'),
                    axios.get('/api/memories?limit=10')
                ]);
                
                renderDashboard(statusResponse.data, memoriesResponse.data);
            } catch (error) {
                console.error('Failed to load dashboard:', error);
                showAlert('Failed to load dashboard data', 'danger');
            }
        }
        
        // Render dashboard
        function renderDashboard(status, memories) {
            const content = document.getElementById('main-content');
            content.innerHTML = `
                <div class="row">
                    <div class="col-md-3 mb-4">
                        <div class="metric-card">
                            <i class="fas fa-brain brain-ai-icon"></i>
                            <div class="metric-value">${status.brain_ai_system?.memory_count || 0}</div>
                            <div>Active Memories</div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-4">
                        <div class="metric-card">
                            <i class="fas fa-chart-line brain-ai-icon"></i>
                            <div class="metric-value">${status.brain_ai_system?.learning_stats?.total_learning_events || 0}</div>
                            <div>Learning Events</div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-4">
                        <div class="metric-card">
                            <i class="fas fa-bolt brain-ai-icon"></i>
                            <div class="metric-value">${status.brain_ai_system?.router_stats?.total_activations || 0}</div>
                            <div>Memory Activations</div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-4">
                        <div class="metric-card">
                            <i class="fas fa-check-circle brain-ai-icon"></i>
                            <div class="metric-value">${status.initialized ? 'ONLINE' : 'OFFLINE'}</div>
                            <div>System Status</div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-md-8">
                        <div class="card card-brain-ai">
                            <div class="card-header">
                                <h5><i class="fas fa-memory me-2"></i>Recent Memories</h5>
                            </div>
                            <div class="card-body">
                                ${renderMemoriesList(memories.memories || [])}
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card card-brain-ai">
                            <div class="card-header">
                                <h5><i class="fas fa-chart-bar me-2"></i>System Statistics</h5>
                            </div>
                            <div class="card-body">
                                ${renderSystemStats(status.brain_ai_system || {})}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        // Render memories list
        function renderMemoriesList(memories) {
            if (memories.length === 0) {
                return '<p class="text-muted">No memories stored yet. Start processing data to create memories.</p>';
            }
            
            return memories.map(memory => `
                <div class="d-flex justify-content-between align-items-center border-bottom py-2">
                    <div>
                        <strong>${memory.pattern_signature}</strong>
                        <br>
                        <small class="text-muted">${memory.memory_type} • ${memory.created_at}</small>
                    </div>
                    <div class="memory-strength" style="width: 100px;">
                        <div class="memory-strength-bar ${getStrengthClass(memory.strength)}" 
                             style="width: ${memory.strength * 100}%"></div>
                    </div>
                </div>
            `).join('');
        }
        
        // Render system statistics
        function renderSystemStats(stats) {
            return `
                <div class="row">
                    <div class="col-6">
                        <small class="text-muted">Pattern Types</small>
                        <div class="fw-bold">${Object.keys(stats.encoder_stats?.pattern_types || {}).length}</div>
                    </div>
                    <div class="col-6">
                        <small class="text-muted">Avg Confidence</small>
                        <div class="fw-bold">${(stats.encoder_stats?.avg_confidence || 0).toFixed(2)}</div>
                    </div>
                </div>
            `;
        }
        
        // Get strength CSS class
        function getStrengthClass(strength) {
            if (strength < 0.3) return 'strength-low';
            if (strength < 0.7) return 'strength-medium';
            return 'strength-high';
        }
        
        // Update status indicators
        function updateStatusIndicators() {
            const indicators = document.querySelectorAll('.status-indicator');
            indicators.forEach(indicator => {
                if (brainAI?.initialized) {
                    indicator.className = 'status-indicator status-online';
                } else {
                    indicator.className = 'status-indicator status-offline';
                }
            });
        }
        
        // Show loading spinner
        function showLoading(elementId) {
            const element = document.getElementById(elementId);
            element.innerHTML = '<div class="loading-spinner"></div>';
        }
        
        // Show alert
        function showAlert(message, type = 'info', duration = 5000) {
            const alertId = 'alert-' + Date.now();
            const alertHtml = `
                <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            
            const alertsContainer = document.getElementById('alerts-container');
            alertsContainer.insertAdjacentHTML('beforeend', alertHtml);
            
            // Auto-dismiss after duration
            setTimeout(() => {
                const alert = document.getElementById(alertId);
                if (alert) {
                    alert.remove();
                }
            }, duration);
        }
        
        // Generic API call function
        async function apiCall(endpoint, method = 'GET', data = null) {
            try {
                const config = {
                    method: method,
                    url: endpoint,
                    headers: {
                        'Content-Type': 'application/json'
                    }
                };
                
                if (data) {
                    config.data = data;
                }
                
                const response = await axios(config);
                return response.data;
            } catch (error) {
                console.error('API call failed:', error);
                throw error;
            }
        }
        
        // Format timestamp
        function formatTimestamp(timestamp) {
            return new Date(timestamp).toLocaleString();
        }
        
        // Copy to clipboard
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                showAlert('Copied to clipboard!', 'success', 2000);
            });
        }
        """

    @staticmethod
    def get_alert_containers() -> str:
        """Generate alert container HTML"""
        return """
        <div id="alerts-container" class="position-fixed top-0 end-0 p-3" style="z-index: 1050;">
            <!-- Alerts will be inserted here -->
        </div>
        """

    @staticmethod
    def get_dashboard_tab_content() -> str:
        """Generate dashboard tab content HTML"""
        return """
        <div class="tab-content">
            <div id="overview" class="tab-pane fade show active">
                <div id="overview-content">
                    <!-- Overview content will be loaded here -->
                </div>
            </div>
            
            <div id="memories" class="tab-pane fade">
                <div id="memories-content">
                    <!-- Memories content will be loaded here -->
                </div>
            </div>
            
            <div id="analytics" class="tab-pane fade">
                <div id="analytics-content">
                    <!-- Analytics content will be loaded here -->
                </div>
            </div>
            
            <div id="settings" class="tab-pane fade">
                <div id="settings-content">
                    <!-- Settings content will be loaded here -->
                </div>
            </div>
        </div>
        """

    @staticmethod
    def get_memory_card(memory: Dict[str, Any]) -> str:
        """Generate memory card HTML"""
        strength = memory.get('strength', 0)
        strength_class = 'strength-low' if strength < 0.3 else 'strength-medium' if strength < 0.7 else 'strength-high'
        
        return f"""
        <div class="card card-brain-ai mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="card-title">{memory.get('pattern_signature', 'Unknown Pattern')}</h6>
                        <p class="card-text text-muted">{memory.get('memory_type', 'Unknown')} • {memory.get('created_at', 'Unknown')}</p>
                        <small class="text-muted">Access Count: {memory.get('access_count', 0)}</small>
                    </div>
                    <div class="text-end">
                        <div class="memory-strength mb-2" style="width: 80px;">
                            <div class="memory-strength-bar {strength_class}" style="width: {strength * 100}%"></div>
                        </div>
                        <small class="text-muted">{strength:.2f}</small>
                    </div>
                </div>
            </div>
        </div>
        """

    @staticmethod
    def get_metric_card(title: str, value: str, icon: str, color: str = "primary") -> str:
        """Generate metric card HTML"""
        return f"""
        <div class="card card-brain-ai mb-3">
            <div class="card-body text-center">
                <i class="fas fa-{icon} brain-ai-icon text-{color}"></i>
                <div class="metric-value">{value}</div>
                <h6 class="card-title">{title}</h6>
            </div>
        </div>
        """

    @staticmethod
    def get_insight_card(icon: str, title: str, content: str, type: str = "info") -> str:
        """Generate insight card HTML"""
        return f"""
        <div class="insight-card border-{type}">
            <div class="d-flex">
                <i class="fas fa-{icon} me-3 text-{type} mt-1"></i>
                <div>
                    <h6 class="mb-1">{title}</h6>
                    <p class="mb-0 text-muted">{content}</p>
                </div>
            </div>
        </div>
        """

    @staticmethod
    def get_form_group(label: str, input_id: str, input_type: str = "text", 
                      placeholder: str = "", required: bool = False, options: List[Dict] = None) -> str:
        """Generate form group HTML"""
        required_attr = "required" if required else ""
        
        if options:
            options_html = "".join([f'<option value="{opt["value"]}">{opt["label"]}</option>' for opt in options])
            select_html = f"""
            <select class="form-select" id="{input_id}" {required_attr}>
                <option value="">Select {label}</option>
                {options_html}
            </select>
            """
            return f"""
            <div class="form-floating">
                {select_html}
                <label for="{input_id}">{label}</label>
            </div>
            """
        
        return f"""
        <div class="form-floating">
            <input type="{input_type}" class="form-control" id="{input_id}" 
                   placeholder="{placeholder}" {required_attr}>
            <label for="{input_id}">{label}</label>
        </div>
        """

    @staticmethod
    def get_button(text: str, icon: str = None, type: str = "primary", 
                  onclick: str = None, disabled: bool = False) -> str:
        """Generate button HTML"""
        icon_html = f'<i class="fas fa-{icon} me-2"></i>' if icon else ""
        onclick_attr = f'onclick="{onclick}"' if onclick else ""
        disabled_attr = "disabled" if disabled else ""
        
        return f"""
        <button type="button" class="btn btn-{type} btn-brain-ai" 
                {onclick_attr} {disabled_attr}>
            {icon_html}{text}
        </button>
        """

    @staticmethod
    def get_table(columns: List[str], data: List[Dict[str, Any]]) -> str:
        """Generate table HTML"""
        headers = "".join([f'<th scope="col">{col}</th>' for col in columns])
        rows = ""
        
        for row in data:
            cells = "".join([f'<td>{row.get(col.lower().replace(" ", "_"), "")}</td>' for col in columns])
            rows += f'<tr>{cells}</tr>'
        
        return f"""
        <div class="table-responsive">
            <table class="table table-striped">
                <thead>
                    <tr>{headers}</tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
        """

    @staticmethod
    def get_loading_spinner(size: str = "md") -> str:
        """Generate loading spinner HTML"""
        size_class = f"spinner-border-{size}" if size != "md" else "spinner-border"
        return f'<div class="{size_class}" role="status"><span class="visually-hidden">Loading...</span></div>'

    @staticmethod
    def get_progress_bar(value: float, max_value: float = 100, 
                        color: str = "primary", show_text: bool = True) -> str:
        """Generate progress bar HTML"""
        percentage = (value / max_value) * 100
        text_html = f'<span class="sr-only">{percentage:.1f}%</span>' if show_text else ""
        
        return f"""
        <div class="progress">
            <div class="progress-bar bg-{color}" role="progressbar" 
                 style="width: {percentage}%" aria-valuenow="{value}" 
                 aria-valuemin="0" aria-valuemax="{max_value}">
                {text_html}
            </div>
        </div>
        """

    @staticmethod
    def get_status_badge(status: str, type: str = "secondary") -> str:
        """Generate status badge HTML"""
        return f'<span class="badge bg-{type}">{status}</span>'

    @staticmethod
    def get_chart_container(chart_id: str, title: str) -> str:
        """Generate chart container HTML"""
        return f"""
        <div class="card card-brain-ai mb-3">
            <div class="card-header">
                <h6 class="mb-0"><i class="fas fa-chart-line me-2"></i>{title}</h6>
            </div>
            <div class="card-body">
                <canvas id="{chart_id}" width="400" height="200"></canvas>
            </div>
        </div>
        """

    @staticmethod
    def get_pagination(current_page: int, total_pages: int, page_size: int = 10) -> str:
        """Generate pagination HTML"""
        if total_pages <= 1:
            return ""
        
        prev_disabled = "disabled" if current_page <= 1 else ""
        next_disabled = "disabled" if current_page >= total_pages else ""
        
        prev_page = current_page - 1
        next_page = current_page + 1
        
        return f"""
        <nav aria-label="Page navigation">
            <ul class="pagination justify-content-center">
                <li class="page-item {prev_disabled}">
                    <a class="page-link" href="#" onclick="changePage({prev_page})">Previous</a>
                </li>
                <li class="page-item active">
                    <span class="page-link">{current_page} of {total_pages}</span>
                </li>
                <li class="page-item {next_disabled}">
                    <a class="page-link" href="#" onclick="changePage({next_page})">Next</a>
                </li>
            </ul>
        </nav>
        """


# Export the WebComponents class
__all__ = ['WebComponents']
