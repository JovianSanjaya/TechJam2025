import * as vscode from 'vscode';
import * as path from 'path';
import * as cp from 'child_process';
import * as fs from 'fs';

interface LLMAnalysisResult {
    analysis_method: string;
    risk_score: number;
    compliance_patterns: any[];
    llm_insights?: {
        overall_assessment: string;
        key_risks: string[];
        regulatory_gaps: string[];
        implementation_suggestions: string[];
    };
    recommendations: string[];
    llm_raw_response?: string;
}

export class TikTokComplianceChatParticipant {
    private outputChannel: vscode.OutputChannel;

    constructor(context: vscode.ExtensionContext) {
        this.outputChannel = vscode.window.createOutputChannel('TikTok Compliance Chat');
    }

    async handleRequest(
        request: vscode.ChatRequest,
        context: vscode.ChatContext,
        stream: vscode.ChatResponseStream,
        token: vscode.CancellationToken
    ): Promise<vscode.ChatResult> {
        
        if (token.isCancellationRequested) {
            return {};
        }

        const command = request.command;
        const prompt = request.prompt;

        try {
            switch (command) {
                case 'analyze':
                    await this.handleAnalyzeCommand(prompt, stream, token);
                    break;
                case 'current-file':
                    await this.handleCurrentFileCommand(stream, token);
                    break;
                case 'help':
                    await this.handleHelpCommand(stream, token);
                    break;
                default:
                    await this.handleGeneralQuery(prompt, stream, token);
                    break;
            }
        } catch (error) {
            stream.markdown(`❌ **Error:** ${error}\n\n`);
            stream.markdown('Please try again or check the output channel for more details.');
        }

        return {};
    }

    private async handleAnalyzeCommand(
        code: string,
        stream: vscode.ChatResponseStream,
        token: vscode.CancellationToken
    ): Promise<void> {
        stream.progress('🔍 Analyzing code for compliance issues...');
        
        if (!code.trim()) {
            stream.markdown('❌ **No code provided**\n\nPlease provide code to analyze or use `/current-file` to analyze the active file.');
            return;
        }

        const result = await this.runLLMAnalysis(code, 'User provided code snippet');
        await this.displayAnalysisResults(result, stream, token);
    }

    private async handleCurrentFileCommand(
        stream: vscode.ChatResponseStream,
        token: vscode.CancellationToken
    ): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            stream.markdown('❌ **No active file**\n\nPlease open a file to analyze.');
            return;
        }

        const document = editor.document;
        const code = document.getText();
        const fileName = path.basename(document.fileName);

        stream.progress(`🔍 Analyzing ${fileName}...`);
        
        const result = await this.runLLMAnalysis(code, `Analysis of ${fileName}`);
        await this.displayAnalysisResults(result, stream, token, fileName);
    }

    private async handleHelpCommand(
        stream: vscode.ChatResponseStream,
        token: vscode.CancellationToken
    ): Promise<void> {
        stream.markdown(`# 🛡️ TikTok Compliance Analyzer

This AI assistant helps you analyze code for compliance with regulations like COPPA, GDPR, and platform-specific requirements.

## Commands:
- \`/analyze <code>\` - Analyze provided code snippet
- \`/current-file\` - Analyze the currently open file
- \`/help\` - Show this help message

## Features:
- ✅ **RAG-Enhanced Analysis** - Uses legal document retrieval
- ✅ **LLM-Powered Insights** - AI analysis with Moonshot KIMI
- ✅ **Static + Dynamic Analysis** - Hybrid approach
- ✅ **Regulation Mapping** - COPPA, GDPR, CCPA compliance

## Example Usage:
\`\`\`
@tiktok-compliance /analyze
def verify_user_age(user_data):
    age = user_data.get('age')
    if age < 13:
        require_parental_consent()
    return age >= 13
\`\`\`

Just ask me to analyze any code and I'll provide detailed compliance insights!
`);
    }

    private async handleGeneralQuery(
        prompt: string,
        stream: vscode.ChatResponseStream,
        token: vscode.CancellationToken
    ): Promise<void> {
        // Handle general compliance questions
        if (prompt.toLowerCase().includes('analyze') || prompt.toLowerCase().includes('check')) {
            stream.markdown('I can help analyze code for compliance! Try:\n- `/analyze <your-code>` to analyze a code snippet\n- `/current-file` to analyze the active file\n- `/help` for more options');
            return;
        }

        stream.markdown(`I'm a TikTok compliance analyzer. I can help you:

🔍 **Analyze code** for regulatory compliance
📋 **Check current file** for compliance issues  
🛡️ **Identify risks** related to COPPA, GDPR, etc.

Try \`/help\` for available commands or \`/current-file\` to analyze your open file!`);
    }

    private async runLLMAnalysis(code: string, context: string): Promise<LLMAnalysisResult> {
        return new Promise((resolve, reject) => {
            // Get the workspace folder
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                reject(new Error('No workspace folder found'));
                return;
            }

            // Path to the Python script
            const scriptPath = path.join(workspaceFolder.uri.fsPath, 'run_llm_analysis.py');
            
            // Create a temporary Python script to run the analysis
            const pythonScript = `
import sys
import os
sys.path.append('${workspaceFolder.uri.fsPath.replace(/\\/g, '\\\\')}')

from code_analyzer_llm_clean import LLMCodeAnalyzer
from vector_store import get_vector_store
import json

def main():
    try:
        # Initialize vector store for RAG
        vector_store = get_vector_store()
        
        # Initialize analyzer with RAG
        analyzer = LLMCodeAnalyzer(use_llm=True, force_llm=True, vector_store=vector_store)
        
        # Analyze the code
        code = '''${code.replace(/'/g, "\\'")}'''
        context = '''${context.replace(/'/g, "\\'")}'''
        
        result = analyzer.analyze_code_snippet(code, context)
        
        # Output JSON result
        print("=== ANALYSIS_RESULT_START ===")
        print(json.dumps(result, indent=2, default=str))
        print("=== ANALYSIS_RESULT_END ===")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
`;

            // Write the temporary script
            fs.writeFileSync(scriptPath, pythonScript);

            // Execute the Python script
            const pythonPath = vscode.workspace.getConfiguration('tiktokCompliance').get('pythonPath', 'python');
            
            cp.exec(`"${pythonPath}" "${scriptPath}"`, { 
                cwd: workspaceFolder.uri.fsPath,
                timeout: 60000 // 60 second timeout
            }, (error, stdout, stderr) => {
                // Clean up temporary script
                try {
                    fs.unlinkSync(scriptPath);
                } catch (e) {
                    // Ignore cleanup errors
                }

                if (error) {
                    this.outputChannel.appendLine(`Error executing Python script: ${error.message}`);
                    this.outputChannel.appendLine(`Stderr: ${stderr}`);
                    reject(new Error(`Analysis failed: ${error.message}`));
                    return;
                }

                try {
                    // Extract JSON result from stdout
                    const startMarker = '=== ANALYSIS_RESULT_START ===';
                    const endMarker = '=== ANALYSIS_RESULT_END ===';
                    
                    const startIndex = stdout.indexOf(startMarker);
                    const endIndex = stdout.indexOf(endMarker);
                    
                    if (startIndex === -1 || endIndex === -1) {
                        throw new Error('Could not find analysis result markers in output');
                    }
                    
                    const jsonStr = stdout.substring(startIndex + startMarker.length, endIndex).trim();
                    const result = JSON.parse(jsonStr);
                    
                    resolve(result);
                } catch (parseError) {
                    this.outputChannel.appendLine(`Error parsing analysis result: ${parseError}`);
                    this.outputChannel.appendLine(`Raw stdout: ${stdout}`);
                    reject(new Error(`Failed to parse analysis result: ${parseError}`));
                }
            });
        });
    }

    private async displayAnalysisResults(
        result: LLMAnalysisResult,
        stream: vscode.ChatResponseStream,
        token: vscode.CancellationToken,
        fileName?: string
    ): Promise<void> {
        if (token.isCancellationRequested) {
            return;
        }

        const title = fileName ? `Analysis Results for ${fileName}` : 'Code Analysis Results';
        
        stream.markdown(`# 🛡️ ${title}\n\n`);

        // Analysis method and risk score
        stream.markdown(`**Analysis Method:** ${result.analysis_method || 'Unknown'}\n`);
        stream.markdown(`**Risk Score:** ${(result.risk_score * 100).toFixed(1)}% ${this.getRiskEmoji(result.risk_score)}\n\n`);

        // LLM Insights (if available)
        if (result.llm_insights) {
            stream.markdown(`## 🤖 AI Analysis\n\n`);
            
            if (result.llm_insights.overall_assessment) {
                stream.markdown(`**Assessment:** ${result.llm_insights.overall_assessment}\n\n`);
            }

            if (result.llm_insights.key_risks && result.llm_insights.key_risks.length > 0) {
                stream.markdown(`**🚨 Key Risks:**\n`);
                result.llm_insights.key_risks.forEach(risk => {
                    stream.markdown(`- ${risk}\n`);
                });
                stream.markdown(`\n`);
            }

            if (result.llm_insights.regulatory_gaps && result.llm_insights.regulatory_gaps.length > 0) {
                stream.markdown(`**📋 Regulatory Gaps:**\n`);
                result.llm_insights.regulatory_gaps.forEach(gap => {
                    stream.markdown(`- ${gap}\n`);
                });
                stream.markdown(`\n`);
            }
        }

        // Compliance patterns found
        if (result.compliance_patterns && result.compliance_patterns.length > 0) {
            stream.markdown(`## 🔍 Compliance Patterns Found\n\n`);
            result.compliance_patterns.forEach((pattern, index) => {
                stream.markdown(`**${index + 1}. ${pattern.pattern_name || 'Unknown Pattern'}**\n`);
                stream.markdown(`- Type: ${pattern.pattern_type || 'Unknown'}\n`);
                stream.markdown(`- Confidence: ${((pattern.confidence || 0) * 100).toFixed(1)}%\n`);
                if (pattern.description) {
                    stream.markdown(`- Description: ${pattern.description}\n`);
                }
                stream.markdown(`\n`);
            });
        }

        // Recommendations
        if (result.recommendations && result.recommendations.length > 0) {
            stream.markdown(`## 💡 Recommendations\n\n`);
            result.recommendations.forEach((rec, index) => {
                stream.markdown(`${index + 1}. ${rec}\n`);
            });
            stream.markdown(`\n`);
        }

        // Implementation suggestions from LLM
        if (result.llm_insights?.implementation_suggestions && result.llm_insights.implementation_suggestions.length > 0) {
            stream.markdown(`## 🚀 Implementation Suggestions\n\n`);
            result.llm_insights.implementation_suggestions.forEach((suggestion, index) => {
                stream.markdown(`${index + 1}. ${suggestion}\n`);
            });
        }

        stream.markdown(`\n---\n*Analysis completed using RAG-enhanced LLM with legal document retrieval*`);
    }

    private getRiskEmoji(riskScore: number): string {
        if (riskScore >= 0.8) {
            return '🔴';
        }
        if (riskScore >= 0.6) {
            return '🟠';
        }
        if (riskScore >= 0.4) {
            return '🟡';
        }
        return '🟢';
    }
}

export function registerChatParticipant(context: vscode.ExtensionContext): void {
    const participant = new TikTokComplianceChatParticipant(context);
    
    const chatParticipant = vscode.chat.createChatParticipant('tiktok-compliance', participant.handleRequest.bind(participant));
    chatParticipant.iconPath = vscode.Uri.file(path.join(context.extensionPath, 'icon.png'));
    
    context.subscriptions.push(chatParticipant);
}
