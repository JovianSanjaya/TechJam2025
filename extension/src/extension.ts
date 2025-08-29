import * as vscode from 'vscode';
import * as path from 'path';
import * as cp from 'child_process';
import * as fs from 'fs';
import { registerChatParticipant } from './chatParticipant';

interface ComplianceResult {
    feature_id: string;
    feature_name: string;
    needs_compliance_logic: boolean;
    confidence: number;
    risk_level: string;
    action_required: string;
    applicable_regulations: any[];
    implementation_notes: string[];
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

export function activate(context: vscode.ExtensionContext) {
    console.log('TikTok Compliance Analyzer is now active!');

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

        // Get Python path from configuration
        const config = vscode.workspace.getConfiguration('tiktokCompliance');
        const pythonCmd = config.get<string>('pythonPath', 'python');
        
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
