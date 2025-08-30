# 🛡️ TikTok Compliance Analyzer - VS Code Chat Integration

This VS Code extension integrates your LLM-powered compliance analyzer with VS Code's chat interface, providing AI-powered compliance analysis directly in your editor.

## ✨ Features

- **🤖 AI Chat Integration** - Analyze code through VS Code's chat interface
- **📊 RAG-Enhanced Analysis** - Retrieves relevant legal documents for context
- **🔍 Real-time Analysis** - Analyze current file or code snippets instantly
- **⚖️ Multi-Regulation Support** - COPPA, GDPR, CCPA, and platform-specific rules
- **💡 Actionable Recommendations** - Get specific implementation suggestions

## 🚀 Quick Start

### 1. Setup Extension
```bash
cd extension
npm install
npm run compile
```

### 2. Install in VS Code
- Press `F5` to launch Extension Development Host
- Or package and install: `vsce package && code --install-extension *.vsix`

### 3. Configure Python Environment
Update VS Code settings:
```json
{
    "tiktokCompliance.pythonPath": "C:/Users/58dya/anaconda3/envs/aichallenge/python.exe"
}
```

### 4. Configure API Keys
Ensure your `.env` file contains:
```
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=meta-llama/llama-4-maverick:free
```

## 💬 Chat Commands

### Analyze Current File
```
@tiktok-compliance /current-file
```

### Analyze Code Snippet
```
@tiktok-compliance /analyze
def verify_age(user_data):
    age = user_data.get('age')
    if age < 13:
        require_parental_consent()
    return age >= 13
```

### Get Help
```
@tiktok-compliance /help
```

### General Questions
```
@tiktok-compliance what compliance issues should I watch for?
```

## 📊 Example Output

The chat will provide structured analysis including:

- **Risk Score** - Overall compliance risk (0-100%)
- **AI Assessment** - LLM-powered analysis with legal context
- **Key Risks** - Specific compliance concerns identified
- **Regulatory Gaps** - Missing compliance requirements
- **Recommendations** - Actionable implementation steps
- **Compliance Patterns** - Detected patterns with confidence scores

## 🔧 Technical Details

### Architecture
- **Extension Host** - TypeScript VS Code extension
- **Python Backend** - RAG-enhanced LLM analyzer
- **Vector Store** - ChromaDB with legal document retrieval
- **LLM Provider** - OpenRouter (Moonshot KIMI)

### Data Flow
1. User submits code via chat
2. Extension creates temporary Python script
3. Python script runs RAG-enhanced analysis
4. Results formatted and displayed in chat

## 🛠️ Development

### Build Extension
```bash
npm run compile        # Compile TypeScript
npm run watch         # Watch mode for development
npm run package       # Create .vsix package
```

### Test Integration
```bash
python test_vscode_chat.py
```

### Debug
- Use VS Code Extension Development Host
- Check "TikTok Compliance Chat" output channel
- Monitor Python script execution

## 📝 Configuration

### Extension Settings
- `tiktokCompliance.pythonPath` - Python executable path
- `tiktokCompliance.maxFilesToAnalyze` - Max files for workspace analysis
- `tiktokCompliance.autoAnalyze` - Auto-analyze on file save

### Environment Variables
- `OPENROUTER_API_KEY` - OpenRouter API key
- `OPENROUTER_MODEL` - LLM model to use

## 🔒 Security Notes

- API keys stored in `.env` file (add to `.gitignore`)
- Temporary Python scripts cleaned up after execution
- No code sent to external services except configured LLM

## 🐛 Troubleshooting

### Common Issues

**Python Import Errors**
- Ensure `pythonPath` points to environment with dependencies
- Install: `pip install sentence-transformers chromadb requests`

**ChromaDB Initialization Fails**
- Falls back to SimpleFallbackStore automatically
- Check Python environment compatibility

**API Rate Limits**
- Free tier has usage limits
- Consider upgrading OpenRouter plan for production

**Chat Not Responding**
- Check "TikTok Compliance Chat" output channel
- Verify Python script execution permissions

## 📚 Related Files

- `src/extension.ts` - Main extension logic
- `src/chatParticipant.ts` - Chat integration
- `../code_analyzer_llm_clean.py` - Analysis engine
- `../vector_store.py` - RAG implementation
- `test_vscode_chat.py` - Integration test

## 🎯 Usage Tips

1. **Start Simple** - Use `/current-file` on open files
2. **Iterate** - Refine code based on recommendations
3. **Context Matters** - Provide file context for better analysis
4. **Review Suggestions** - AI recommendations need human validation
5. **Stay Updated** - Regulations change, keep legal knowledge current

Happy coding with compliant AI assistance! 🚀
