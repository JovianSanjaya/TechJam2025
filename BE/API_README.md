# TikTok Compliance Analysis API

This API provides compliance analysis for TikTok features, analyzing code and feature descriptions for legal compliance requirements including COPPA, GDPR, CCPA, and other regulations.

## Quick Start

### Using Docker Compose (Recommended)

1. Start the services:
```bash
docker-compose up
```

2. The API will be available at: `http://localhost:5001`

### Local Development

1. Install dependencies:
```bash
cd BE
pip install -r requirements.txt
```

2. Run the API server:
```bash
python app.py
```

3. The API will be available at: `http://localhost:5000`

## API Endpoints

### Health Check
```
GET /health
```
Returns the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "service": "TikTok Compliance Analysis API"
}
```

### Root Information
```
GET /
```
Returns API information and available endpoints.

### Sample Analysis
```
GET /analyze/sample
```
Runs a sample compliance analysis with predefined features for testing.

**Response:**
```json
{
  "status": "success",
  "timestamp": "2024-01-01T12:00:00",
  "analysis_results": {
    "analysis_summary": {
      "total_features": 2,
      "features_requiring_compliance": 1,
      "high_risk_features": 0,
      "human_review_needed": 0
    },
    "detailed_results": [...],
    "recommendations": [...]
  }
}
```

### Custom Feature Analysis
```
POST /analyze
```
Analyzes custom features for compliance requirements.

**Request Body:**
```json
{
  "features": [
    {
      "id": "feat_001",
      "feature_name": "Age Verification Gate",
      "description": "System for verifying user age",
      "code": "def verify_age(user): ..."
    }
  ],
  "include_code_analysis": true,
  "export_formats": ["json"]
}
```

**Required Fields:**
- `features`: Array of feature objects to analyze
- `features[].feature_name`: Name of the feature
- `features[].description`: Description of the feature

**Optional Fields:**
- `features[].id`: Unique identifier (auto-generated if not provided)
- `features[].code`: Code snippet to analyze
- `include_code_analysis`: Whether to perform code analysis (default: true)
- `export_formats`: Export formats for results (default: ["json"])

**Response:**
```json
{
  "status": "success",
  "timestamp": "2024-01-01T12:00:00",
  "analysis_results": {
    "analysis_summary": {
      "total_features": 1,
      "features_requiring_compliance": 1,
      "high_risk_features": 0,
      "human_review_needed": 0,
      "analysis_timestamp": "2024-01-01T12:00:00",
      "system_version": "Enhanced v2.0"
    },
    "detailed_results": [
      {
        "feature_id": "feat_001",
        "feature_name": "Age Verification Gate",
        "needs_compliance_logic": true,
        "confidence": 0.85,
        "risk_level": "medium",
        "action_required": "COMPLIANCE_IMPLEMENTATION",
        "applicable_regulations": [
          {
            "regulation": "COPPA",
            "relevance": "high",
            "requirements": [...]
          }
        ],
        "implementation_notes": [...],
        "code_analysis": {
          "risk_score": 0.6,
          "privacy_concerns_count": 2,
          "recommendations": [...]
        }
      }
    ],
    "recommendations": [
      "🔧 1 features require compliance implementation",
      "📚 Most relevant regulations: COPPA (1 features)"
    ]
  },
  "export_files": {
    "json": "/path/to/exported/file.json"
  },
  "request_summary": {
    "features_analyzed": 1,
    "include_code_analysis": true,
    "export_formats": ["json"]
  }
}
```

## Analysis Results

### Risk Levels
- `low`: Minimal compliance requirements
- `medium`: Some compliance implementation needed
- `high`: Significant compliance requirements

### Action Required
- `NO_ACTION`: No compliance action needed
- `COMPLIANCE_IMPLEMENTATION`: Implement compliance logic
- `URGENT_COMPLIANCE`: High-priority compliance required
- `HUMAN_REVIEW`: Manual review needed

### Applicable Regulations
The system analyzes features against various regulations including:
- **COPPA**: Children's Online Privacy Protection Act
- **GDPR**: General Data Protection Regulation
- **CCPA**: California Consumer Privacy Act
- **FERPA**: Family Educational Rights and Privacy Act
- And others based on feature context

## Testing

Run the test script to verify the API is working:

```bash
python test_api.py
```

This will test all endpoints and provide usage examples.

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid JSON or missing required fields)
- `500`: Internal Server Error

Error responses include:
```json
{
  "error": "Error description",
  "error_type": "ErrorType",
  "status": "error",
  "timestamp": "2024-01-01T12:00:00"
}
```

## Configuration

The system uses environment variables and configuration files:
- OpenRouter API key for LLM analysis
- Vector store configuration
- Export directory settings

See `config.py` for detailed configuration options.

## Architecture

The API is built using:
- **Flask**: Web framework
- **Enhanced Compliance System**: Core analysis engine
- **Multi-Agent Orchestrator**: Distributed analysis
- **LLM Code Analyzer**: Code-specific analysis
- **Vector Store**: Semantic search capabilities

## Development

To extend the API:
1. Add new endpoints in `app.py`
2. Extend analysis capabilities in `enhanced_main.py`
3. Add new agents in `agents.py`
4. Update configuration in `config.py`
