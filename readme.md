# CanOrNot

A comprehensive compliance analysis platform for TikTok features, consisting of a **VS Code Extension**, **Web Application**, and **Backend API** that analyzes code and features for privacy regulations, data protection, and regulatory adherence.

## 🏗️ Architecture

This project consists of three main components:

- **🔌 VS Code Extension** (`Extension Host/`) - Code analysis extension for developers
- **🌐 Frontend Web App** (`FE/`) - React-based web interface for feature analysis
- **🔧 Backend API** (`BE/`) - Flask API with AI-powered compliance analysis
- **🐳 Docker Support** - Containerized deployment with docker-compose

## 🚀 Quick Start

### One-Command Setup
```bash
make all
```

This will:
- Install all dependencies (Node.js, Python, shadcn/ui components)
- Build the VS Code extension
- Build and start Docker containers
- Launch frontend and backend services

### Individual Commands
```bash
make setup        # Install dependencies and build everything
make run          # Start Docker services only
make run-all      # Start services + build extension
make health       # Check service status
make stop         # Stop all services
make clean        # Clean up everything
```

## 📱 Web Application (Frontend)

**Location**: `FE/`  
**Tech Stack**: React + TypeScript + Vite + Tailwind CSS + shadcn/ui  
**Port**: http://localhost:5173

### Features
- **📊 Feature Analysis Dashboard** - Submit features for compliance analysis
- **📁 CSV Batch Upload** - Analyze multiple features at once
- **🎨 Modern UI** - Built with shadcn/ui components and Tailwind CSS
- **📱 Responsive Design** - Works on desktop and mobile
- **🔄 Real-time Results** - Live analysis results with risk levels

### Key Components
- **Form Interface** - Feature name and description input
- **File Upload** - CSV batch processing with drag-and-drop
- **Results Display** - Risk levels, compliance requirements, and recommendations
- **Toast Notifications** - User feedback and error handling

### Development
```bash
make dev-frontend     # Start development server
cd FE && npm run dev  # Alternative direct command
```

## 🔧 Backend API

**Location**: `BE/`  
**Tech Stack**: Flask + Python + AI/LLM Integration  
**Port**: http://localhost:8000

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and status |
| `/health` | GET | Health check |
| `/analyze` | POST | Analyze single feature or batch |
| `/analyze/sample` | GET | Run sample analysis |

### Features
- **🤖 AI-Powered Analysis** - LLM-based compliance assessment
- **📊 Risk Assessment** - HIGH, MEDIUM, LOW, MINIMAL risk levels
- **⚖️ Multi-Regulation Support** - GDPR, COPPA, Privacy Framework
- **📦 Batch Processing** - Analyze multiple features simultaneously
- **🔍 Detailed Reports** - Confidence scores, implementation notes

### Analysis Input Format
```json
{
  "featureName": "Age Verification Gate",
  "description": "ASL verification system for users under 16"
}
```

### Batch Analysis Format
```json
{
  "items": [
    {
      "feature_name": "Feature 1",
      "description": "Description 1",
      "id": "optional_id_1"
    }
  ]
}
```

### Development
```bash
make dev-backend      # Start development server
cd BE && python3 app.py  # Alternative direct command
```

## 🔌 VS Code Extension

**Location**: `Extension Host/`  
**Tech Stack**: TypeScript + VS Code API + Python Integration

### Features
- **🔍 File Analysis** - Analyze individual files for compliance issues
- **🌐 Workspace Analysis** - Scan entire workspace for regulatory concerns
- **📊 Detailed Reporting** - Comprehensive compliance reports with risk levels
- **⚖️ Multi-Regulation Support** - GDPR, COPPA, and privacy framework compliance
- **🎯 Smart Detection** - Identifies privacy-related code patterns and data handling

### Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `TikTok Compliance: Analyze Current File` | Analyze the currently open file | Command Palette |
| `TikTok Compliance: Analyze Workspace` | Analyze all code files in workspace | Command Palette |
| `TikTok Compliance: Show Results` | Open compliance results dashboard | Command Palette |

### Configuration

Configure through VS Code settings:

```json
{
    "tiktokCompliance.pythonPath": "python",
    "tiktokCompliance.maxFilesToAnalyze": 10,
    "tiktokCompliance.autoAnalyze": false
}
```

### Settings
- `tiktokCompliance.pythonPath`: Path to Python executable (auto-configured from `.env`)
- `tiktokCompliance.maxFilesToAnalyze`: Maximum files to analyze in workspace mode
- `tiktokCompliance.autoAnalyze`: Automatically analyze files on save

### Installation
1. Build the extension: `make build-extension`
2. Install the `.vsix` file from `Extension Host/dist/`
3. Or use `make dev-extension` for development mode

### Supported File Types
- Python (`.py`)
- JavaScript (`.js`)
- TypeScript (`.ts`)
- JSX (`.jsx`)
- TSX (`.tsx`)

## 🐳 Docker Deployment

### Local Development
```bash
docker-compose up -d    # Start services
docker-compose logs -f  # View logs
docker-compose down     # Stop services
```

### Services
- **Backend**: Flask API on port 8000
- **Frontend**: React app on port 5173
- **Network**: Internal communication between services

### Environment Variables
```bash
BACKEND_PORT=8000
FRONTEND_PORT=5173
VITE_API_URL=http://localhost:8000
```

## 📊 Analysis Results

The system provides detailed analysis results including:

- **Risk Level**: HIGH, MEDIUM, LOW, or MINIMAL
- **Compliance Requirements**: Whether compliance logic is needed
- **Applicable Regulations**: GDPR, COPPA, Privacy Framework
- **Implementation Notes**: Specific recommendations
- **Confidence Score**: Reliability of the analysis

### Risk Levels
- **🚨 HIGH**: Immediate compliance review required
- **🔶 MEDIUM**: Compliance assessment recommended  
- **🔹 LOW**: Basic compliance check needed
- **✅ MINIMAL**: No immediate action required

## 🛠️ Development Workflow

### Setup Development Environment
```bash
git clone <repository>
cd TechJam2025
make all  # Complete setup
```

### Development Commands
```bash
make dev-backend      # Backend development server
make dev-frontend     # Frontend development server  
make dev-extension    # Extension development mode
make test            # Test API endpoints
make health          # Check service health
```

### Project Structure
```
TechJam2025/
├── BE/                     # Backend Flask API
│   ├── app/
│   │   ├── api/           # API routes and middleware
│   │   └── main.py        # Flask application factory
│   ├── core/              # Core analysis logic
│   ├── services/          # Business logic services
│   └── requirements.txt   # Python dependencies
├── FE/                     # Frontend React App
│   ├── src/
│   │   ├── components/    # UI components (shadcn/ui)
│   │   ├── screens/       # Main application screens
│   │   └── config/        # API configuration
│   └── package.json       # Node.js dependencies
├── Extension Host/         # VS Code Extension
│   ├── src/
│   │   ├── extension.ts   # Main extension entry
│   │   └── python/        # Python analysis scripts
│   └── package.json       # Extension manifest
├── docker-compose.yml      # Container orchestration
└── Makefile               # Build and deployment automation
```

## 🔍 Privacy Detection Patterns

The analyzer detects compliance issues by identifying:

### Privacy Keywords
- `user_data`, `personal_data`, `user_profile`
- `age`, `location`, `tracking`, `geolocation`
- `collect_user`, `track_user`

### GDPR Keywords
- `gdpr`, `consent`, `data_processing`
- `personal_information`, `data_collection`
- `privacy_policy`, `user_consent`

### COPPA Keywords
- `coppa`, `under_13`, `age_verification`
- `parental_consent`, `child_data`, `minor`

## 📝 Example Analysis

### Input Code
```python
def collect_user_data(user_id):
    personal_data = get_user_profile(user_id)
    if user_age < 13:
        require_parental_consent()
    return personal_data
```

### Analysis Output
```json
{
  "risk_level": "HIGH",
  "confidence": 0.95,
  "applicable_regulations": [
    {"name": "GDPR", "applies": true},
    {"name": "COPPA", "applies": true}
  ],
  "implementation_notes": [
    "Implement age verification",
    "Ensure data encryption",
    "Add parental consent flow"
  ],
  "action_required": "Immediate compliance review required"
}
```

## 🚨 Troubleshooting

### Common Issues

**Services not starting**
```bash
make health          # Check service status
make logs           # View error logs
make clean && make all  # Clean rebuild
```

**Python not found (Extension)**
- Check `BE/.env` file has `TIKTOK_PYTHON_PATH` set
- Run `make setup` to auto-configure Python path

**Frontend build errors**
```bash
cd FE && npm install  # Reinstall dependencies
make install-deps     # Install all dependencies
```

**Docker issues**
```bash
docker-compose down -v  # Remove volumes
docker system prune -f  # Clean Docker cache
make clean && make all  # Full rebuild
```

## 📋 Requirements

- **Node.js**: 18+ (for frontend and extension)
- **Python**: 3.8+ (for backend and analysis)
- **Docker**: Latest (for containerized deployment)
- **VS Code**: 1.99.0+ (for extension)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test with: `make test`
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Create an issue in the GitHub repository
- **API Documentation**: Visit http://localhost:8000 when running
- **Health Check**: http://localhost:8000/health
- **Frontend**: http://localhost:5173

---

**Note**: This platform is designed for TikTok compliance analysis but can be adapted for general privacy and regulatory compliance checking across various platforms and frameworks.