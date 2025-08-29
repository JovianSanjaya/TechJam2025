import * as vscode from 'vscode';
import * as path from 'path';
import * as cp from 'child_process';
import * as fs from 'fs';
import { registerChatParticipant } from './chatParticipant';

// Resolve python command: prefer configured path, then common Windows paths, then 'py', then 'python'
function resolvePythonCmd(configured: string): string {
    const tryCmd = (cmd: string): boolean => {
        try {
            console.log(`Testing Python command: ${cmd}`);
            const res = cp.spawnSync(cmd, ['--version'], { 
                encoding: 'utf8',
                timeout: 5000,
                windowsHide: true,
                shell: true  // Add shell option for Windows compatibility
            }) as cp.SpawnSyncReturns<string>;
            const success = res.status === 0;
            console.log(`Command ${cmd} result: ${success ? 'SUCCESS' : 'FAILED'}`);
            return success;
        } catch (e) {
            console.log(`Command ${cmd} error: ${e}`);
            return false;
        }
    };

    // Try configured path first (if it's a real path, not just 'python')
    if (configured && configured !== 'python' && configured !== 'py' && tryCmd(configured)) {
        console.log(`Using configured Python: ${configured}`);
        return configured;
    }

    // Common Windows Python paths to try (in order of preference)
    const commonPaths = [
        'C:\\Users\\58dya\\AppData\\Local\\Programs\\Python\\Python312\\python.exe',  // Known working path first
        'C:\\Users\\58dya\\anaconda3\\python.exe',
        'python',  // Try python in PATH
        'py',  // Try py.exe (Python Launcher)
        'C:\\Users\\58dya\\AppData\\Local\\Programs\\Python\\Launcher\\py.exe',
        'C:\\Users\\58dya\\AppData\\Local\\Programs\\Python\\Python311\\python.exe',
        'C:\\Users\\58dya\\AppData\\Local\\Programs\\Python\\Python310\\python.exe'
    ];

    for (const pythonPath of commonPaths) {
        if (tryCmd(pythonPath)) {
            console.log(`Found working Python: ${pythonPath}`);
            return pythonPath;
        }
    }

    // Fallback to configured value (will likely fail but gives better error message)
    console.log(`No working Python found, falling back to: ${configured || 'python'}`);
    return configured || 'python';
}

interface ComplianceResult {
    feature_id: string;
    feature_name: string;
    needs_compliance_logic: boolean;
    confidence: number;
    risk_level: string;
    action_required: string;
    applicable_regulations: any[];
    implementation_notes: string[];
    code_issues?: Array<{
        line_reference: string;
        problematic_code: string;
        violation_type: string;
        severity: string;
        regulation_violated: string;
        fix_description: string;
        suggested_replacement: string;
        testing_requirements: string;
    }>;
    timestamp: string;
}

interface AnalysisResults {
    analysis_summary: {
        total_features: number;
        features_requiring_compliance: number;
        high_risk_features: number;
        human_review_needed: number;
        analysis_timestamp: string;
        system_version: string;
    };
    detailed_results: ComplianceResult[];
    recommendations: string[];
}

// Global chat panel reference for persistence
let globalChatPanel: vscode.WebviewPanel | null = null;

// Global variables for diagnostics
let complianceDiagnostics: vscode.DiagnosticCollection;

export function activate(context: vscode.ExtensionContext) {
    console.log('TikTok Compliance Analyzer is now active!');

    // Create diagnostic collection for compliance issues
    complianceDiagnostics = vscode.languages.createDiagnosticCollection('tiktok-compliance');
    context.subscriptions.push(complianceDiagnostics);

    // Register chat participant
    registerChatParticipant(context);

    // Create output channel for compliance results
    const outputChannel = vscode.window.createOutputChannel('Compliance Analysis');
    
    // Register commands
    const analyzeFileCommand = vscode.commands.registerCommand('tiktok-compliance.analyzeFile', () => {
        analyzeCurrentFile(outputChannel, context);
    });

    const analyzeWorkspaceCommand = vscode.commands.registerCommand('tiktok-compliance.analyzeWorkspace', () => {
        analyzeWorkspace(outputChannel, context);
    });

    const showResultsCommand = vscode.commands.registerCommand('tiktok-compliance.showResults', () => {
        showComplianceResults(context);
    });

    context.subscriptions.push(analyzeFileCommand, analyzeWorkspaceCommand, showResultsCommand, outputChannel);

    // Status bar item
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "$(shield) Compliance";
    statusBarItem.tooltip = "TikTok Compliance Analyzer";
    statusBarItem.command = 'tiktok-compliance.analyzeFile';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
}

async function analyzeCurrentFile(outputChannel: vscode.OutputChannel, context: vscode.ExtensionContext) {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active editor found. Please open a file to analyze.');
        return;
    }

    const document = editor.document;
    const code = document.getText();
    const fileName = path.basename(document.fileName);

    outputChannel.clear();
    outputChannel.appendLine(`🔍 Analyzing file: ${fileName}`);
    outputChannel.appendLine('=' .repeat(50));
    outputChannel.show();

    // Open a dedicated chat-like panel for this analysis
    const chatPanel = getOrCreateChatPanel(context);
    renderChatMessage(chatPanel, 'user', `Analyze file: <strong>${fileName}</strong>`);

    try {
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Analyzing compliance...",
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0, message: "Initializing compliance system..." });

            const result = await runComplianceAnalysis([{
                id: `file_${Date.now()}`,
                feature_name: fileName,
                description: `Analysis of ${fileName}`,
                code: code
            }], context);

            progress.report({ increment: 100, message: "Analysis complete!" });

            if (result) {
                displayResults(result, outputChannel);
                // Create inline diagnostics for code issues
                createComplianceDiagnostics(document, result);
                // Render result into the chat panel
                renderChatMessage(chatPanel, 'assistant', formatResultAsHtml(result));
            }
        });
    } catch (error) {
        outputChannel.appendLine(`❌ Error during analysis: ${error}`);
        vscode.window.showErrorMessage(`Compliance analysis failed: ${error}`);
    }
}

async function analyzeWorkspace(outputChannel: vscode.OutputChannel, context: vscode.ExtensionContext) {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder found.');
        return;
    }

    outputChannel.clear();
    outputChannel.appendLine('🌐 Analyzing workspace for compliance issues...');
    outputChannel.appendLine('=' .repeat(50));
    outputChannel.show();

    try {
        // Find relevant files (Python, JavaScript, TypeScript, etc.)
        const files = await vscode.workspace.findFiles('**/*.{py,js,ts,jsx,tsx}', '**/node_modules/**', 50);
        
        if (files.length === 0) {
            vscode.window.showInformationMessage('No code files found in workspace.');
            return;
        }

        const features: any[] = [];
        for (let i = 0; i < Math.min(files.length, 10); i++) { // Limit to first 10 files for demo
            const file = files[i];
            const document = await vscode.workspace.openTextDocument(file);
            features.push({
                id: `workspace_${i}`,
                feature_name: path.basename(file.fsPath),
                description: `Analysis of ${path.basename(file.fsPath)}`,
                code: document.getText().substring(0, 2000) // Limit code length
            });
        }

        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Analyzing workspace compliance...",
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0, message: `Analyzing ${features.length} files...` });

            const result = await runComplianceAnalysis(features, context);

            progress.report({ increment: 100, message: "Workspace analysis complete!" });

            if (result) {
                displayResults(result, outputChannel);
                vscode.window.showInformationMessage(`Compliance analysis complete! Found ${result.analysis_summary.features_requiring_compliance} features requiring compliance review.`);
            }
        });
    } catch (error) {
        outputChannel.appendLine(`❌ Error during workspace analysis: ${error}`);
        vscode.window.showErrorMessage(`Workspace analysis failed: ${error}`);
    }
}

async function runComplianceAnalysis(features: any[], context: vscode.ExtensionContext): Promise<AnalysisResults | null> {
    return new Promise((resolve, reject) => {
        const pythonScript = path.join(context.extensionPath, 'src', 'python', 'compliance_analyzer.py');
        const inputData = JSON.stringify({ features });

    // Resolve Python command (configured -> py -> python)
    const config = vscode.workspace.getConfiguration('tiktokCompliance');
    const configured = config.get<string>('pythonPath', 'python');
    const pythonCmd = resolvePythonCmd(configured);

    const child = cp.spawn(pythonCmd, [pythonScript], {
            cwd: path.join(context.extensionPath, 'src', 'python'),
            stdio: ['pipe', 'pipe', 'pipe']
        });

        let stdout = '';
        let stderr = '';

        child.stdout.on('data', (data) => {
            stdout += data.toString();
        });

        child.stderr.on('data', (data) => {
            stderr += data.toString();
        });

        child.on('close', (code) => {
            if (code === 0) {
                try {
                    const result = JSON.parse(stdout);
                    resolve(result);
                } catch (parseError) {
                    reject(`Failed to parse Python output: ${parseError}\nOutput: ${stdout}`);
                }
            } else {
                reject(`Python script failed with code ${code}:\nStderr: ${stderr}\nStdout: ${stdout}`);
            }
        });

        child.on('error', (error) => {
            reject(`Failed to start Python process: ${error.message}. Make sure Python is installed and accessible.`);
        });

        // Send input data to Python script
        try {
            child.stdin.write(inputData);
            child.stdin.end();
        } catch (writeError) {
            reject(`Failed to write to Python process: ${writeError}`);
        }
    });
}

function createComplianceDiagnostics(document: vscode.TextDocument, result: AnalysisResults) {
    const diagnostics: vscode.Diagnostic[] = [];
    const code = document.getText();
    
    for (const detailResult of result.detailed_results) {
        if (detailResult.code_issues) {
            for (const issue of detailResult.code_issues) {
                // Try to find the problematic code in the document
                const codeToFind = issue.problematic_code.trim();
                const codeIndex = code.indexOf(codeToFind);
                
                if (codeIndex !== -1) {
                    // Find the line and character position
                    const position = document.positionAt(codeIndex);
                    const endPosition = document.positionAt(codeIndex + codeToFind.length);
                    const range = new vscode.Range(position, endPosition);
                    
                    // Determine diagnostic severity
                    let severity: vscode.DiagnosticSeverity;
                    switch (issue.severity.toLowerCase()) {
                        case 'critical':
                            severity = vscode.DiagnosticSeverity.Error;
                            break;
                        case 'high':
                            severity = vscode.DiagnosticSeverity.Error;
                            break;
                        case 'medium':
                            severity = vscode.DiagnosticSeverity.Warning;
                            break;
                        default:
                            severity = vscode.DiagnosticSeverity.Information;
                    }
                    
                    const diagnostic = new vscode.Diagnostic(
                        range,
                        `[${issue.regulation_violated}] ${issue.fix_description}`,
                        severity
                    );
                    
                    diagnostic.code = issue.violation_type;
                    diagnostic.source = 'TikTok Compliance';
                    
                    // Add detailed information
                    diagnostic.relatedInformation = [
                        new vscode.DiagnosticRelatedInformation(
                            new vscode.Location(document.uri, range),
                            `Suggested fix: ${issue.suggested_replacement || 'See implementation notes'}`
                        )
                    ];
                    
                    diagnostics.push(diagnostic);
                } else {
                    // If exact code not found, create a general diagnostic for the line reference
                    const lineMatch = issue.line_reference.match(/line\s*(\d+)/i);
                    if (lineMatch) {
                        const lineNumber = parseInt(lineMatch[1]) - 1; // Convert to 0-based
                        if (lineNumber >= 0 && lineNumber < document.lineCount) {
                            const line = document.lineAt(lineNumber);
                            const diagnostic = new vscode.Diagnostic(
                                line.range,
                                `[${issue.regulation_violated}] ${issue.fix_description}`,
                                vscode.DiagnosticSeverity.Warning
                            );
                            diagnostic.code = issue.violation_type;
                            diagnostic.source = 'TikTok Compliance';
                            diagnostics.push(diagnostic);
                        }
                    }
                }
            }
        }
    }
    
    // Set diagnostics for the document
    complianceDiagnostics.set(document.uri, diagnostics);
}

function displayResults(results: AnalysisResults, outputChannel: vscode.OutputChannel) {
    const summary = results.analysis_summary;
    
    outputChannel.appendLine('\n📊 COMPLIANCE ANALYSIS SUMMARY');
    outputChannel.appendLine('=' .repeat(50));
    outputChannel.appendLine(`📁 Total features analyzed: ${summary.total_features}`);
    outputChannel.appendLine(`⚖️  Features requiring compliance: ${summary.features_requiring_compliance}`);
    outputChannel.appendLine(`🚨 High risk features: ${summary.high_risk_features}`);
    outputChannel.appendLine(`👥 Human review needed: ${summary.human_review_needed}`);
    outputChannel.appendLine(`🕒 Analysis timestamp: ${summary.analysis_timestamp}`);
    outputChannel.appendLine(`🔖 System version: ${summary.system_version}`);

    if (results.detailed_results.length > 0) {
        outputChannel.appendLine('\n📋 DETAILED RESULTS');
        outputChannel.appendLine('=' .repeat(50));
        
        results.detailed_results.forEach((result, index) => {
            outputChannel.appendLine(`\n${index + 1}. ${result.feature_name} (${result.feature_id})`);
            outputChannel.appendLine(`   Risk Level: ${result.risk_level}`);
            outputChannel.appendLine(`   Compliance Required: ${result.needs_compliance_logic ? 'YES' : 'NO'}`);
            outputChannel.appendLine(`   Confidence: ${(result.confidence * 100).toFixed(1)}%`);
            outputChannel.appendLine(`   Action Required: ${result.action_required}`);
            
            if (result.applicable_regulations.length > 0) {
                outputChannel.appendLine(`   Applicable Regulations: ${result.applicable_regulations.length} found`);
            }
            
            if (result.implementation_notes.length > 0) {
                outputChannel.appendLine(`   Implementation Notes:`);
                result.implementation_notes.forEach(note => {
                    outputChannel.appendLine(`   • ${note}`);
                });
            }

            // Display code issues with highlighting information
            if (result.code_issues && result.code_issues.length > 0) {
                outputChannel.appendLine(`   🚩 Code Issues Found: ${result.code_issues.length}`);
                result.code_issues.forEach((issue, issueIndex) => {
                    outputChannel.appendLine(`   ${issueIndex + 1}. [${issue.severity.toUpperCase()}] ${issue.violation_type}`);
                    outputChannel.appendLine(`      Location: ${issue.line_reference}`);
                    outputChannel.appendLine(`      Problematic Code: ${issue.problematic_code}`);
                    outputChannel.appendLine(`      Regulation: ${issue.regulation_violated}`);
                    outputChannel.appendLine(`      Fix: ${issue.fix_description}`);
                    if (issue.suggested_replacement) {
                        outputChannel.appendLine(`      Suggested: ${issue.suggested_replacement}`);
                    }
                });
            }
        });
    }

    if (results.recommendations.length > 0) {
        outputChannel.appendLine('\n💡 RECOMMENDATIONS');
        outputChannel.appendLine('=' .repeat(50));
        results.recommendations.forEach((rec, index) => {
            outputChannel.appendLine(`${index + 1}. ${rec}`);
        });
    }
}

function showComplianceResults(context: vscode.ExtensionContext) {
    const panel = vscode.window.createWebviewPanel(
        'complianceResults',
        'Compliance Analysis Results',
        vscode.ViewColumn.One,
        {
            enableScripts: true,
            retainContextWhenHidden: true
        }
    );

    panel.webview.html = getWebviewContent();
}

function getWebviewContent(): string {
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TikTok Compliance Analysis</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            padding: 20px;
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
        }
        .header {
            border-bottom: 1px solid var(--vscode-panel-border);
            padding-bottom: 20px;
            margin-bottom: 20px;
        }
        .summary-card {
            background-color: var(--vscode-editor-inactiveSelectionBackground);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        .risk-high { border-left: 4px solid #f14c4c; }
        .risk-medium { border-left: 4px solid #ffb454; }
        .risk-low { border-left: 4px solid #89d185; }
        .metric {
            display: inline-block;
            margin: 10px 20px 10px 0;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: var(--vscode-charts-blue);
        }
        .metric-label {
            display: block;
            font-size: 0.9em;
            color: var(--vscode-descriptionForeground);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ TikTok Compliance Analysis Dashboard</h1>
        <p>Comprehensive compliance analysis for TikTok features and regulations</p>
    </div>
    
    <div class="summary-card">
        <h2>📊 Analysis Summary</h2>
        <div class="metric">
            <span class="metric-value">0</span>
            <span class="metric-label">Features Analyzed</span>
        </div>
        <div class="metric">
            <span class="metric-value">0</span>
            <span class="metric-label">Compliance Required</span>
        </div>
        <div class="metric">
            <span class="metric-value">0</span>
            <span class="metric-label">High Risk</span>
        </div>
        <div class="metric">
            <span class="metric-value">0</span>
            <span class="metric-label">Review Needed</span>
        </div>
    </div>

    <div class="summary-card">
        <h2>🚀 Quick Actions</h2>
        <p>Use the Command Palette (Ctrl+Shift+P) to run:</p>
        <ul>
            <li><code>TikTok Compliance: Analyze Current File</code> - Analyze the currently open file</li>
            <li><code>TikTok Compliance: Analyze Workspace</code> - Analyze all files in the workspace</li>
            <li><code>TikTok Compliance: Show Results</code> - View detailed results in this panel</li>
        </ul>
    </div>

    <div class="summary-card">
        <h2>📋 Recent Analysis</h2>
        <p>No analysis results available. Run a compliance analysis to see detailed results here.</p>
    </div>
</body>
</html>`;
}

export function deactivate() {}

// --- Chat panel helpers ---
function getOrCreateChatPanel(context: vscode.ExtensionContext): vscode.WebviewPanel {
    if (globalChatPanel && !globalChatPanel.visible) {
        globalChatPanel.reveal();
        return globalChatPanel;
    }
    
    if (!globalChatPanel) {
        globalChatPanel = vscode.window.createWebviewPanel(
            'complianceChat',
            'Compliance Chat',
            vscode.ViewColumn.Beside,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        // Handle panel disposal
        globalChatPanel.onDidDispose(() => {
            globalChatPanel = null;
        });

        // Handle messages from webview
        globalChatPanel.webview.onDidReceiveMessage(
            message => {
                switch (message.type) {
                    case 'followUpQuery':
                        handleFollowUpQuery(message.query, context);
                        break;
                    case 'copyResult':
                        vscode.env.clipboard.writeText(message.content);
                        vscode.window.showInformationMessage('Copied to clipboard!');
                        break;
                    case 'exportJson':
                        exportResultAsJson(message.data);
                        break;
                }
            },
            undefined,
            context.subscriptions
        );

        // Initialize content
        globalChatPanel.webview.html = getChatWebviewContent();
    }
    
    return globalChatPanel;
}

function openChatPanel(title: string): vscode.WebviewPanel {
        const panel = vscode.window.createWebviewPanel(
                'complianceChat',
                title,
                vscode.ViewColumn.Beside,
                {
                        enableScripts: true,
                        retainContextWhenHidden: true
                }
        );

        // Initialize content
        panel.webview.html = getChatWebviewContent();
        return panel;
}

function renderChatMessage(panel: vscode.WebviewPanel, role: 'user' | 'assistant', htmlContent: string) {
        try {
                panel.webview.postMessage({ type: 'appendMessage', role, content: htmlContent });
        } catch (e) {
                console.error('Failed to post message to chat panel', e);
        }
}

function formatResultAsHtml(results: any): string {
    // simple HTML formatting for the analysis results
    const summary = results.analysis_summary;
    let html = `<div class="result-summary"><strong>Summary</strong><p>Analyzed: ${summary.total_features} feature(s). High risk: ${summary.high_risk_features}.</p></div>`;
    html += '<div class="result-details">';
    results.detailed_results.forEach((r: any, idx: number) => {
        html += `<div class="feature"><h3>${idx + 1}. ${r.feature_name} — ${r.risk_level}</h3>`;
        html += `<p>Confidence: ${(r.confidence * 100).toFixed(1)}%</p>`;
        if (r.implementation_notes && r.implementation_notes.length) {
            html += '<ul>' + r.implementation_notes.map((n: string) => `<li>${n}</li>`).join('') + '</ul>';
        }
        html += '</div>';
    });
    html += '</div>';
    
    // Add action buttons
    html += `<div class="action-buttons">
        <button onclick="copyResult('${escapeForJs(JSON.stringify(results))}')">📋 Copy JSON</button>
        <button onclick="exportJson('${escapeForJs(JSON.stringify(results))}')">💾 Export JSON</button>
    </div>`;
    
    return html;
}

async function handleFollowUpQuery(query: string, context: vscode.ExtensionContext) {
    try {
        const chatPanel = getOrCreateChatPanel(context);
        renderChatMessage(chatPanel, 'user', `<strong>Follow-up:</strong> ${query}`);
        
        // Simple follow-up analysis using the query as code
        const result = await runComplianceAnalysis([{
            id: `followup_${Date.now()}`,
            feature_name: 'Follow-up Query',
            description: `Follow-up analysis: ${query}`,
            code: query
        }], context);
        
        if (result) {
            renderChatMessage(chatPanel, 'assistant', formatResultAsHtml(result));
        }
    } catch (error) {
        vscode.window.showErrorMessage(`Follow-up analysis failed: ${error}`);
    }
}

async function exportResultAsJson(data: any) {
    try {
        const uri = await vscode.window.showSaveDialog({
            defaultUri: vscode.Uri.file('compliance-analysis.json'),
            filters: {
                'JSON Files': ['json']
            }
        });
        
        if (uri) {
            const content = JSON.stringify(data, null, 2);
            await vscode.workspace.fs.writeFile(uri, Buffer.from(content, 'utf8'));
            vscode.window.showInformationMessage(`Analysis exported to ${uri.fsPath}`);
        }
    } catch (error) {
        vscode.window.showErrorMessage(`Export failed: ${error}`);
    }
}

function escapeForJs(str: string): string {
    return str.replace(/'/g, "\\'").replace(/"/g, '\\"').replace(/\n/g, '\\n');
}

function getChatWebviewContent(): string {
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Compliance Chat</title>
  <style>
    body { font-family: var(--vscode-font-family); padding: 12px; color: var(--vscode-foreground); background: var(--vscode-editor-background); margin: 0; }
    .chat-container { display: flex; flex-direction: column; height: 100vh; }
    .messages { flex: 1; overflow-y: auto; padding-bottom: 20px; }
    .message { margin: 8px 0; padding: 8px 12px; border-radius: 8px; }
    .message.user { background: rgba(64,128,255,0.08); border: 1px solid rgba(64,128,255,0.12); }
    .message.assistant { background: rgba(120,120,120,0.06); border: 1px solid rgba(120,120,120,0.08); }
    .result-summary { margin-bottom: 8px; }
    .feature h3 { margin: 6px 0; }
    .input-container { border-top: 1px solid var(--vscode-panel-border); padding: 10px 0; }
    .input-row { display: flex; gap: 8px; }
    .input-row input { flex: 1; padding: 6px 8px; background: var(--vscode-input-background); color: var(--vscode-input-foreground); border: 1px solid var(--vscode-input-border); border-radius: 4px; }
    .input-row button, .action-buttons button { padding: 6px 12px; background: var(--vscode-button-background); color: var(--vscode-button-foreground); border: none; border-radius: 4px; cursor: pointer; margin-right: 6px; }
    .input-row button:hover, .action-buttons button:hover { background: var(--vscode-button-hoverBackground); }
    .action-buttons { margin-top: 12px; }
  </style>
</head>
<body>
  <div class="chat-container">
    <div id="messages" class="messages"></div>
    <div class="input-container">
      <div class="input-row">
        <input type="text" id="followUpInput" placeholder="Ask a follow-up question about compliance..." />
        <button onclick="sendFollowUp()">Send</button>
      </div>
    </div>
  </div>

  <script>
    const vscode = acquireVsCodeApi();
    
    window.addEventListener('message', event => {
      const msg = event.data;
      if (msg.type === 'appendMessage') {
        const container = document.getElementById('messages');
        const div = document.createElement('div');
        div.className = 'message ' + (msg.role === 'user' ? 'user' : 'assistant');
        div.innerHTML = msg.content;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
      }
    });
    
    function sendFollowUp() {
      const input = document.getElementById('followUpInput');
      const query = input.value.trim();
      if (query) {
        vscode.postMessage({ type: 'followUpQuery', query: query });
        input.value = '';
      }
    }
    
    function copyResult(jsonStr) {
      vscode.postMessage({ type: 'copyResult', content: jsonStr });
    }
    
    function exportJson(jsonStr) {
      try {
        const data = JSON.parse(jsonStr);
        vscode.postMessage({ type: 'exportJson', data: data });
      } catch (e) {
        console.error('Failed to parse JSON for export', e);
      }
    }
    
    // Handle Enter key in input
    document.getElementById('followUpInput').addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        sendFollowUp();
      }
    });
  </script>
</body>
</html>`;
}
