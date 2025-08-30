import * as vscode from 'vscode';
import * as path from 'path';
import * as cp from 'child_process';
import * as fs from 'fs';
import * as os from 'os';
import { registerChatParticipant } from './chatParticipant';

// ===== Python resolver (cross-platform, exhaustive) =====
const EXEC_TIMEOUT_MS = 2000;

function safeSpawnText(cmd: string, args: string[], useShell = false): { ok: boolean; out: string; err: string; code: number | null } {
    try {
        const res = cp.spawnSync(cmd, args, {
            encoding: 'utf8',
            timeout: EXEC_TIMEOUT_MS,
            windowsHide: true,
            shell: useShell
        }) as cp.SpawnSyncReturns<string>;
        return { ok: (res.status === 0), out: (res.stdout || ''), err: (res.stderr || ''), code: res.status };
    } catch (e: any) {
        return { ok: false, out: '', err: String(e?.message ?? e), code: null };
    }
}

function toExecutableCandidates(names: string[]): string[] {
    // Return raw command names; Node's spawn resolves them via PATH.
    return names.filter(Boolean);
}

function pathJoinIfExists(...parts: string[]): string | null {
    const p = path.join(...parts);
    try {
        if (fs.existsSync(p)) return p;
    } catch { /* ignore */ }
    return null;
}

function isExecutable(filePath: string): boolean {
    try {
        const st = fs.statSync(filePath);
        if (!st.isFile()) return false;
        if (process.platform === 'win32') return true; // on Windows just existing is enough for .exe
        fs.accessSync(filePath, fs.constants.X_OK);
        return true;
    } catch {
        return false;
    }
}

function dedupeKeepOrder(items: string[]): string[] {
    const seen = new Set<string>();
    const out: string[] = [];
    for (const it of items) {
        if (!it) continue;
        const norm = process.platform === 'win32' ? it.toLowerCase() : it;
        if (!seen.has(norm)) {
            seen.add(norm);
            out.push(it);
        }
    }
    return out;
}

function getActiveEnvCandidates(): string[] {
    const out: string[] = [];
    // venv
    const venv = process.env.VIRTUAL_ENV;
    if (venv) {
        const exe = process.platform === 'win32' ? pathJoinIfExists(venv, 'Scripts', 'python.exe') : pathJoinIfExists(venv, 'bin', 'python');
        if (exe) out.push(exe);
    }
    // conda activated
    const condaPrefix = process.env.CONDA_PREFIX;
    if (condaPrefix) {
        const exe = process.platform === 'win32' ? pathJoinIfExists(condaPrefix, 'python.exe') : pathJoinIfExists(condaPrefix, 'bin', 'python');
        if (exe) out.push(exe);
    }
    return out;
}

function getManagerCandidates(): string[] {
    const out: string[] = [];

    // 1) Windows py launcher inventory → absolute paths
    if (process.platform === 'win32') {
        const r = safeSpawnText('py', ['-0p']); // lists installed interpreters w/ paths
        if (r.ok) {
            for (const line of r.out.split(/\r?\n/)) {
                const p = line.trim();
                if (p && isExecutable(p)) out.push(p);
            }
        }
        // try default py (lets Node resolve via PATH) as a last resort command
        out.push('py');
    }

    // 2) Conda envs via `conda info --json`
    {
        const r = safeSpawnText('conda', ['info', '--json']);
        if (r.ok) {
            try {
                const info = JSON.parse(r.out);
                const envs: string[] = Array.isArray(info?.envs) ? info.envs : [];
                for (const envPath of envs) {
                    const exe = process.platform === 'win32'
                        ? pathJoinIfExists(envPath, 'python.exe')
                        : pathJoinIfExists(envPath, 'bin', 'python');
                    if (exe) out.push(exe);
                }
                // base
                const root = info?.root_prefix;
                if (root) {
                    const baseExe = process.platform === 'win32'
                        ? pathJoinIfExists(root, 'python.exe')
                        : pathJoinIfExists(root, 'bin', 'python');
                    if (baseExe) out.push(baseExe);
                }
            } catch {/* ignore bad json */}
        }
    }

    // 3) pyenv
    {
        // try the currently selected one
        const rWhich = safeSpawnText('pyenv', ['which', 'python']);
        if (rWhich.ok) {
            const p = rWhich.out.trim();
            if (p && isExecutable(p)) out.push(p);
        }
        // enumerate installed versions (best effort)
        const rVersions = safeSpawnText('pyenv', ['versions', '--bare']);
        if (rVersions.ok) {
            const home = os.homedir();
            for (const ver of rVersions.out.split(/\r?\n/)) {
                const v = ver.trim();
                if (!v) continue;
                const exe = pathJoinIfExists(home, '.pyenv', 'versions', v, 'bin', 'python');
                if (exe) out.push(exe);
            }
        }
    }

    // 4) asdf
    {
        const r = safeSpawnText('asdf', ['which', 'python']);
        if (r.ok) {
            const p = r.out.trim();
            if (p && isExecutable(p)) out.push(p);
        }
        // asdf shims live here; include the shim command so PATH can resolve
        const shim = path.join(os.homedir(), '.asdf', 'shims', 'python');
        if (fs.existsSync(shim)) out.push(shim);
    }

    // 5) Poetry
    {
        const r = safeSpawnText('poetry', ['env', 'info', '-p']);
        if (r.ok) {
            const envPath = r.out.trim();
            if (envPath) {
                const exe = process.platform === 'win32'
                    ? pathJoinIfExists(envPath, 'Scripts', 'python.exe')
                    : pathJoinIfExists(envPath, 'bin', 'python');
                if (exe) out.push(exe);
            }
        }
    }

    // 6) Pipenv
    {
        const r = safeSpawnText('pipenv', ['--py']);
        if (r.ok) {
            const p = r.out.trim();
            if (p && isExecutable(p)) out.push(p);
        }
    }

    return dedupeKeepOrder(out);
}

function getPathSweepCandidates(): string[] {
    // Walk PATH and pick common python executable names
    const namesWin = ['python.exe', 'python3.exe', 'python3.12.exe', 'python3.11.exe', 'python3.10.exe'];
    const namesNix = ['python3.12', 'python3.11', 'python3.10', 'python3', 'python'];
    const names = process.platform === 'win32' ? namesWin : namesNix;

    const out: string[] = [];
    const PATHS = (process.env.PATH || '').split(path.delimiter).filter(Boolean);
    for (const dir of PATHS) {
        for (const nm of names) {
            const candidate = pathJoinIfExists(dir, nm);
            if (candidate && isExecutable(candidate)) out.push(candidate);
        }
    }
    // also include plain commands for Node to resolve via PATH
    out.push(...toExecutableCandidates(process.platform === 'win32' ? ['python', 'python3', 'py'] : ['python3', 'python']));
    return dedupeKeepOrder(out);
}

function getCommonInstallCandidates(userHome: string): string[] {
    const out: string[] = [];
    if (process.platform === 'win32') {
        const app = (rel: string) => pathJoinIfExists(userHome, 'AppData', ...rel.split('/'));
        const pushIf = (p: string | null) => { if (p) out.push(p); };

        // Microsoft Store stubs (works if installed)
        pushIf(app('Local/Microsoft/WindowsApps/python.exe'));
        pushIf(app('Local/Microsoft/WindowsApps/python3.exe'));

        // User installs
        pushIf(pathJoinIfExists(userHome, 'anaconda3', 'python.exe'));
        pushIf(pathJoinIfExists(userHome, 'miniconda3', 'python.exe'));

        // AppData standard installs
        ['Python312','Python311','Python310','Python39'].forEach(ver => {
            pushIf(pathJoinIfExists(userHome, 'AppData', 'Local', 'Programs', 'Python', ver, 'python.exe'));
        });

        // Program Files
        ['Python312','Python311','Python310','Python39'].forEach(ver => {
            pushIf(pathJoinIfExists('C:\\', 'Program Files', ver, 'python.exe'));
        });
    } else if (process.platform === 'darwin') {
        // Homebrew & Framework Pythons
        out.push(
            '/opt/homebrew/bin/python3',
            '/usr/local/bin/python3',
            '/Library/Frameworks/Python.framework/Versions/3.12/bin/python3',
            '/Library/Frameworks/Python.framework/Versions/3.11/bin/python3'
        );
        // Conda defaults
        out.push(
            path.join(userHome, 'anaconda3', 'bin', 'python'),
            path.join(userHome, 'miniconda3', 'bin', 'python')
        );
    } else {
        // Linux
        out.push(
            '/usr/bin/python3',
            '/usr/local/bin/python3',
            '/bin/python3',
            path.join(userHome, 'anaconda3', 'bin', 'python'),
            path.join(userHome, 'miniconda3', 'bin', 'python')
        );
    }
    return dedupeKeepOrder(out.filter(Boolean));
}

function testPythonAndReturn(cmdOrPath: string): string | null {
    // Quick check with --version (very fast)
    let ok = safeSpawnText(cmdOrPath, ['--version']).ok;
    if (!ok) return null;

    // Optional: ensure it can import stdlib & report its real path (handles shims)
    const probe = safeSpawnText(cmdOrPath, ['-c', 'import sys;print(sys.executable)']);
    if (probe.ok) {
        const resolved = probe.out.trim();
        if (resolved && fs.existsSync(resolved)) return resolved;
    }
    return cmdOrPath;
}

/**
 * Resolve python command: prefer configured path, then envs, managers, PATH sweep, and common installs.
 * Returns the first working absolute path (or command) that can run Python.
 */
function resolvePythonCmd(configured?: string): string {
    const tried: string[] = [];
    const pushTry = (arr: string[], label: string) => {
        for (const i of arr) {
            if (!i) continue;
            tried.push(i);
        }
        console.log(`Candidate batch [${label}]: ${arr.length} items`);
    };

    console.log('🔍 Starting Python path resolution (exhaustive)…');

    // 0) Configured path (if explicit path, not just generic command)
    const configuredIsGeneric = !configured || ['python','python3','py'].includes(configured.trim().toLowerCase());
    if (configured && !configuredIsGeneric) {
        pushTry([configured], 'configured');
    }

    // 1) Active environments
    pushTry(getActiveEnvCandidates(), 'active-env');

    // 2) Managers (py launcher, conda, pyenv, asdf, poetry, pipenv)
    pushTry(getManagerCandidates(), 'managers');

    // 3) PATH sweep
    pushTry(getPathSweepCandidates(), 'path-sweep');

    // 4) Common installs
    pushTry(getCommonInstallCandidates(os.homedir()), 'common-installs');

    // 5) Finally, generic configured or default
    pushTry([configured || (process.platform === 'win32' ? 'python' : 'python3')], 'fallback-configured/default');

    const candidates = dedupeKeepOrder(tried);
    console.log(`Total unique python candidates: ${candidates.length}`);

    for (let i = 0; i < candidates.length; i++) {
        const c = candidates[i];
        console.log(`[${i + 1}/${candidates.length}] Testing Python: ${c}`);
        const okPath = testPythonAndReturn(c);
        if (okPath) {
            console.log(`✅ Using Python: ${okPath}`);
            return okPath;
        }
    }

    console.log('❌ No working Python found; returning configured or generic command.');
    return configured || (process.platform === 'win32' ? 'python' : 'python3');
}

// Resolve python command: prefer configured path, then environment detection, then common paths
function resolvePythonCmdOld(configured?: string): string {
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
            if (success) {
                console.log(`Python version: ${res.stdout?.trim()}`);
            }
            return success;
        } catch (e) {
            console.log(`Command ${cmd} error: ${e}`);
            return false;
        }
    };

    // Get VS Code configuration
    const config = vscode.workspace.getConfiguration('tiktokCompliance');
    const configuredPath = configured || config.get<string>('pythonPath', '');
    const additionalPaths = config.get<string[]>('searchPaths', []);

    // Try configured path first (if it's a real path, not just 'python')
    if (configuredPath && configuredPath !== 'python' && configuredPath !== 'py' && tryCmd(configuredPath)) {
        console.log(`Using configured Python: ${configuredPath}`);
        return configuredPath;
    }

    // Combine all path sources
    const envPaths = getEnvironmentPythonPaths();
    const userHome = os.homedir();
    const commonPaths = getCommonPythonPaths(userHome);
    
    // Add additional search paths from configuration
    const additionalSearchPaths = additionalPaths.flatMap(searchPath => {
        const pythonExe = process.platform === 'win32' ? 'python.exe' : 'python';
        return [
            path.join(searchPath, pythonExe),
            path.join(searchPath, 'Scripts', pythonExe), // Windows venv
            path.join(searchPath, 'bin', pythonExe)      // Unix venv
        ];
    });

    // Combine all paths and remove duplicates
    const allPaths = [
        ...envPaths,
        ...additionalSearchPaths,
        ...commonPaths
    ];
    const uniquePaths = [...new Set(allPaths)];

    // Try each path
    for (const pythonPath of uniquePaths) {
        if (tryCmd(pythonPath)) {
            console.log(`Found working Python: ${pythonPath}`);
            return pythonPath;
        }
    }

    // Fallback to configured value (will likely fail but gives better error message)
    const fallback = configuredPath || 'python';
    console.log(`No working Python found, falling back to: ${fallback}`);
    return fallback;
}

function getEnvironmentPythonPaths(): string[] {
    const paths: string[] = [];
    
    // Priority 1: Check active conda environment
    const condaPath = process.env.CONDA_PREFIX;
    if (condaPath) {
        const pythonExe = process.platform === 'win32' ? 'python.exe' : 'python';
        paths.push(path.join(condaPath, pythonExe));
    }
    
    // Priority 2: Add the known working conda environment path
    const userHome = os.homedir();
    if (process.platform === 'win32') {
        const aiChallengeEnvPath = path.join(userHome, 'anaconda3', 'envs', 'aichallenge', 'python.exe');
        paths.push(aiChallengeEnvPath);
        console.log(`Added aichallenge conda env path: ${aiChallengeEnvPath}`);
        
        // Also add the absolute path that we know works as backup
        const knownWorkingPath = 'C:/Users/58dya/anaconda3/envs/aichallenge/python.exe';
        paths.push(knownWorkingPath);
        console.log(`Added known working path: ${knownWorkingPath}`);
    }
    
    // Priority 3: Check active virtual environment
    const virtualEnv = process.env.VIRTUAL_ENV;
    if (virtualEnv) {
        const pythonExe = process.platform === 'win32' ? 'python.exe' : 'python';
        const binDir = process.platform === 'win32' ? 'Scripts' : 'bin';
        paths.push(path.join(virtualEnv, binDir, pythonExe));
    }
    
    // Priority 4: Check PATH environment variable for Python installations
    const pathEnv = process.env.PATH;
    if (pathEnv) {
        const pathDirs = pathEnv.split(path.delimiter);
        for (const dir of pathDirs) {
            if (dir.toLowerCase().includes('python') || dir.toLowerCase().includes('anaconda')) {
                const pythonExe = process.platform === 'win32' ? 'python.exe' : 'python';
                const potentialPath = path.join(dir, pythonExe);
                if (!paths.includes(potentialPath)) {
                    paths.push(potentialPath);
                }
            }
        }
    }
    
    return paths;
}

function getCommonPythonPaths(userHome: string): string[] {
    if (process.platform === 'win32') {
        return [
            // User-specific conda environments (prioritize aichallenge)
            path.join(userHome, 'anaconda3', 'envs', 'aichallenge', 'python.exe'),
            path.join(userHome, 'anaconda3', 'python.exe'),
            path.join(userHome, 'miniconda3', 'python.exe'),
            path.join(userHome, 'miniconda3', 'envs', 'aichallenge', 'python.exe'),
            // User-specific Python installations
            path.join(userHome, 'AppData', 'Local', 'Programs', 'Python', 'Python312', 'python.exe'),
            path.join(userHome, 'AppData', 'Local', 'Programs', 'Python', 'Python311', 'python.exe'),
            path.join(userHome, 'AppData', 'Local', 'Programs', 'Python', 'Python310', 'python.exe'),
            path.join(userHome, 'AppData', 'Local', 'Programs', 'Python', 'Python39', 'python.exe'),
            path.join(userHome, 'AppData', 'Local', 'Programs', 'Python', 'Python38', 'python.exe'),
            // PATH commands
            'python',
            'py',
            // System-wide installations
            'C:\\Program Files\\Python312\\python.exe',
            'C:\\Program Files\\Python311\\python.exe',
            'C:\\Program Files\\Python310\\python.exe',
            'C:\\Program Files\\Python39\\python.exe',
            'C:\\Program Files\\Python38\\python.exe'
        ];
    } else if (process.platform === 'darwin') {
        return [
            // User-specific conda installations
            path.join(userHome, 'anaconda3', 'envs', 'aichallenge', 'bin', 'python'),
            path.join(userHome, 'anaconda3', 'bin', 'python'),
            path.join(userHome, 'miniconda3', 'bin', 'python'),
            // System Python paths
            '/usr/local/bin/python3',
            '/opt/homebrew/bin/python3',
            '/usr/local/bin/python',
            '/opt/homebrew/bin/python',
            '/Library/Frameworks/Python.framework/Versions/3.12/bin/python3',
            '/Library/Frameworks/Python.framework/Versions/3.11/bin/python3',
            '/Library/Frameworks/Python.framework/Versions/3.10/bin/python3',
            'python3',
            'python'
        ];
    } else {
        // Linux and other Unix-like systems
        return [
            // User-specific conda installations
            path.join(userHome, 'anaconda3', 'envs', 'aichallenge', 'bin', 'python'),
            path.join(userHome, 'anaconda3', 'bin', 'python'),
            path.join(userHome, 'miniconda3', 'bin', 'python'),
            // System Python paths
            '/usr/bin/python3',
            '/usr/local/bin/python3',
            '/usr/bin/python',
            '/usr/local/bin/python',
            'python3',
            'python'
        ];
    }
}

function getPythonScriptPath(context: vscode.ExtensionContext): string {
    // Try multiple possible locations for the Python script
    const possiblePaths = [
        path.join(context.extensionPath, 'src', 'python', 'compliance_analyzer.py'),
        path.join(context.extensionPath, 'python', 'compliance_analyzer.py'),
        path.join(context.extensionPath, 'scripts', 'compliance_analyzer.py')
    ];
    
    for (const scriptPath of possiblePaths) {
        if (fs.existsSync(scriptPath)) {
            console.log(`Using Python script: ${scriptPath}`);
            return scriptPath;
        }
    }
    
    // Fallback to the most likely location
    const defaultPath = path.join(context.extensionPath, 'src', 'python', 'compliance_analyzer.py');
    console.log(`Python script not found in expected locations, using default: ${defaultPath}`);
    return defaultPath;
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

    // Log extension version for runtime verification
    try {
        const pkg = require(path.join(context.extensionPath, 'package.json'));
        const extVersion = pkg?.version || 'unknown';
        console.log(`TikTok Compliance Analyzer version: ${extVersion}`);
    } catch (e) {
        console.log('Unable to read package.json for version');
    }

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

    // New: command to show which Python the extension will use and its version
    const showPythonPathCommand = vscode.commands.registerCommand('tiktok-compliance.showPythonPath', async () => {
        const outputChannelLocal = outputChannel; // reuse existing channel
        outputChannelLocal.appendLine('🔎 Resolving Python path...');
        try {
            // Read user/workspace configured python path
            const cfg = vscode.workspace.getConfiguration('tiktokCompliance');
            const configuredPath = cfg.get<string>('pythonPath') || undefined;

            // Try to read VS Code Python extension common keys
            const pythonExtCfgKeys = [
                'python.defaultInterpreterPath',
                'python.pythonPath',
                'python.path'
            ];
            let pythonExtConfigured: string | undefined = undefined;
            for (const key of pythonExtCfgKeys) {
                try {
                    const val = vscode.workspace.getConfiguration().get<string>(key);
                    if (val && val.trim().length > 0) { pythonExtConfigured = val; break; }
                } catch (e) { /* ignore */ }
            }

            const finalConfigured = pythonExtConfigured || configuredPath;
            const resolved = resolvePythonCmd(finalConfigured);

            outputChannelLocal.appendLine(`Configured override: ${finalConfigured || 'none'}`);
            outputChannelLocal.appendLine(`Resolved python command: ${resolved}`);

            // Run version check
            if (!resolved) {
                outputChannelLocal.appendLine('No python candidate resolved.');
                return;
            }

            if (process.platform === 'win32' && resolved === 'py') {
                outputChannelLocal.appendLine('Running: py -3 --version');
                const r = cp.spawnSync('py', ['-3', '--version'], { encoding: 'utf8', shell: true });
                outputChannelLocal.appendLine(r.stdout?.trim() || r.stderr?.trim() || `Exit code: ${r.status}`);
            } else {
                // If resolved contains spaces and shell is needed, run via shell
                const useShell = resolved.includes(' ');
                outputChannelLocal.appendLine(`Running: ${resolved} --version`);
                const r = cp.spawnSync(resolved, ['--version'], { encoding: 'utf8', shell: useShell });
                outputChannelLocal.appendLine(r.stdout?.trim() || r.stderr?.trim() || `Exit code: ${r.status}`);
            }
        } catch (err) {
            outputChannel.appendLine(`Error while probing python path: ${err}`);
        }
        outputChannelLocal.show(true);
    });

    context.subscriptions.push(analyzeFileCommand, analyzeWorkspaceCommand, showResultsCommand, showPythonPathCommand, outputChannel);

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
        const pythonScript = getPythonScriptPath(context);
        const inputData = JSON.stringify({ features });

    // Read configured pythonPath from user/workspace settings (allows hardcoding)
    const cfg = vscode.workspace.getConfiguration('tiktokCompliance');
    const configuredPath = cfg.get<string>('pythonPath') || undefined;

    // Attempt to read VS Code Python extension settings (if user uses the Python extension)
    const pythonExtCfgKeys = [
        'python.defaultInterpreterPath', // VS Code newer key
        'python.pythonPath', // older Python extension key
        'python.path' // fallback
    ];

    let pythonExtConfigured: string | undefined = undefined;
    for (const key of pythonExtCfgKeys) {
        try {
            const val = vscode.workspace.getConfiguration().get<string>(key);
            if (val && val.trim().length > 0) {
                pythonExtConfigured = val;
                break;
            }
        } catch (e) {
            // ignore
        }
    }

    // Use VS Code Python extension interpreter if available
    const finalConfigured = pythonExtConfigured || configuredPath;

    // Resolve python command: prefer finalConfigured, else fallback to resolver
    let pythonCmd = resolvePythonCmd(finalConfigured);
    let pythonArgs: string[] = [pythonScript];
    let useShell = false;

    // If VS Code configured interpreter is a full path and contains spaces, enable shell
    if (finalConfigured && finalConfigured.includes(' ')) {
        useShell = true;
    }

    // If resolver returned 'py' (Windows launcher) and no configured interpreter, use -3 to force Python 3
    if (process.platform === 'win32' && (!finalConfigured) && (pythonCmd === 'py' || pythonCmd === undefined)) {
        pythonCmd = 'py';
        pythonArgs = ['-3', pythonScript];
        useShell = true; // py launcher works well with shell
    } else if (!finalConfigured && pythonCmd && pythonCmd.includes(' ')) {
        // If the resolved path contains spaces and nothing configured, enable shell to handle quoting
        useShell = true;
    }

    // Log which python will be used for easier debugging
    console.log(`Resolved python command: ${pythonCmd} (configured override: ${finalConfigured || 'none'})`);

    const child = cp.spawn(pythonCmd, pythonArgs, {
            cwd: path.join(context.extensionPath, 'src', 'python'),
            stdio: ['pipe', 'pipe', 'pipe'],
            shell: useShell
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
    let html = '';
    
    // Analysis Summary Section
    if (results.analysis_summary) {
        const summary = results.analysis_summary;
        html += `<div class="analysis-summary">
            <h2>📊 COMPLIANCE ANALYSIS SUMMARY</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <span class="label">📁 Total features analyzed:</span>
                    <span class="value">${summary.total_features}</span>
                </div>
                <div class="summary-item">
                    <span class="label">⚖️ Features requiring compliance:</span>
                    <span class="value">${summary.features_requiring_compliance}</span>
                </div>
                <div class="summary-item">
                    <span class="label">🚨 High risk features:</span>
                    <span class="value">${summary.high_risk_features}</span>
                </div>
                <div class="summary-item">
                    <span class="label">👥 Human review needed:</span>
                    <span class="value">${summary.human_review_needed}</span>
                </div>
                <div class="summary-item">
                    <span class="label">🤖 LLM enabled:</span>
                    <span class="value">${summary.llm_enabled ? 'YES' : 'NO'}</span>
                </div>
                <div class="summary-item">
                    <span class="label">📚 RAG enabled:</span>
                    <span class="value">${summary.rag_enabled ? 'YES' : 'NO'}</span>
                </div>
            </div>
        </div>`;
    } else {
        // Legacy format fallback
        html += `<div class="analysis-summary">
            <h2>📊 COMPLIANCE ANALYSIS SUMMARY</h2>
            <p>Analyzed: 1 feature(s). High risk: ${results.risk_score >= 0.8 ? 1 : 0}.</p>
        </div>`;
    }
    
    // Detailed Results Section
    html += '<div class="detailed-results"><h2>📋 DETAILED RESULTS</h2>';
    
    if (results.detailed_results && results.detailed_results.length > 0) {
        results.detailed_results.forEach((r: any, idx: number) => {
            const riskEmoji = getRiskEmojiForHtml(r.llm_analysis?.risk_score || 0);
            html += `<div class="feature-analysis">
                <h3>${idx + 1}. ${r.feature_name} ${riskEmoji}</h3>
                <div class="feature-details">
                    <div class="detail-item">
                        <span class="label">Risk Level:</span>
                        <span class="value risk-${r.risk_level.toLowerCase()}">${r.risk_level}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Compliance Required:</span>
                        <span class="value">${r.needs_compliance_logic ? 'YES' : 'NO'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Confidence:</span>
                        <span class="value">${(r.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Action Required:</span>
                        <span class="value">${r.action_required}</span>
                    </div>
                </div>`;
            
            // Code Issues Section
            if (r.code_issues && r.code_issues.length > 0) {
                html += '<div class="code-issues"><h4>🚩 Code Issues Found:</h4>';
                r.code_issues.forEach((issue: any, issueIdx: number) => {
                    html += `<div class="code-issue">
                        <div class="issue-header">
                            <span class="issue-number">${issueIdx + 1}.</span>
                            <span class="issue-severity severity-${issue.severity.toLowerCase()}">[${issue.severity.toUpperCase()}]</span>
                            <span class="issue-type">${issue.violation_type}</span>
                        </div>
                        <div class="issue-details">
                            <div class="issue-location"><strong>Location:</strong> ${issue.line_reference}</div>
                            <div class="issue-regulation"><strong>Regulation:</strong> ${issue.regulation_violated}</div>
                            <div class="problematic-code">
                                <strong>Problematic Code:</strong>
                                <pre><code>${escapeHtml(issue.problematic_code)}</code></pre>
                            </div>
                            <div class="fix-description"><strong>Fix:</strong> ${issue.fix_description}</div>`;
                    
                    if (issue.suggested_replacement) {
                        html += `<div class="suggested-code">
                            <strong>Suggested Replacement:</strong>
                            <pre><code>${escapeHtml(issue.suggested_replacement)}</code></pre>
                        </div>`;
                    }
                    html += '</div></div>';
                });
                html += '</div>';
            }
            
            // LLM Analysis Section
            if (r.llm_analysis?.llm_insights) {
                const insights = r.llm_analysis.llm_insights;
                html += '<div class="llm-insights"><h4>🤖 AI Analysis:</h4>';
                
                if (insights.overall_assessment) {
                    html += `<div class="assessment"><strong>Assessment:</strong> ${insights.overall_assessment}</div>`;
                }
                
                if (insights.key_risks && insights.key_risks.length > 0) {
                    html += '<div class="key-risks"><strong>Key Risks:</strong><ul>';
                    insights.key_risks.forEach((risk: string) => {
                        html += `<li>${risk}</li>`;
                    });
                    html += '</ul></div>';
                }
                
                if (insights.implementation_suggestions && insights.implementation_suggestions.length > 0) {
                    html += '<div class="implementation-suggestions"><strong>Implementation Suggestions:</strong><ul>';
                    insights.implementation_suggestions.forEach((suggestion: string) => {
                        html += `<li>${suggestion}</li>`;
                    });
                    html += '</ul></div>';
                }
                html += '</div>';
            }
            
            html += '</div>'; // Close feature-analysis
        });
    } else {
        // Legacy format fallback
        html += `<div class="feature-analysis">
            <h3>1. Code Analysis</h3>
            <div class="feature-details">
                <div class="detail-item">
                    <span class="label">Risk Level:</span>
                    <span class="value">${getRiskLevelForHtml(results.risk_score || 0)}</span>
                </div>
                <div class="detail-item">
                    <span class="label">Confidence:</span>
                    <span class="value">${((results.risk_score || 0) * 100).toFixed(1)}%</span>
                </div>
            </div>`;
        
        // Legacy code issues
        if (results.code_issues && results.code_issues.length > 0) {
            html += '<div class="code-issues"><h4>🚩 Code Issues Found:</h4>';
            results.code_issues.forEach((issue: any, issueIdx: number) => {
                html += `<div class="code-issue">
                    <div class="issue-header">
                        <span class="issue-number">${issueIdx + 1}.</span>
                        <span class="issue-severity severity-${issue.severity.toLowerCase()}">[${issue.severity.toUpperCase()}]</span>
                        <span class="issue-type">${issue.violation_type}</span>
                    </div>
                    <div class="issue-details">
                        <div class="issue-location"><strong>Location:</strong> ${issue.line_reference}</div>
                        <div class="problematic-code">
                            <strong>Problematic Code:</strong>
                            <pre><code>${escapeHtml(issue.problematic_code)}</code></pre>
                        </div>
                        <div class="fix-description"><strong>Fix:</strong> ${issue.fix_description}</div>`;
                
                if (issue.suggested_replacement) {
                    html += `<div class="suggested-code">
                        <strong>Suggested Replacement:</strong>
                        <pre><code>${escapeHtml(issue.suggested_replacement)}</code></pre>
                    </div>`;
                }
                html += '</div></div>';
            });
            html += '</div>';
        }
        html += '</div>';
    }
    
    html += '</div>'; // Close detailed-results
    
    // Recommendations Section
    if (results.recommendations && results.recommendations.length > 0) {
        html += '<div class="recommendations"><h2>💡 RECOMMENDATIONS</h2><ul>';
        results.recommendations.forEach((rec: string) => {
            // Parse and format recommendations
            if (rec.includes('CRITICAL')) {
                html += `<li class="recommendation critical">🚨 <strong>CRITICAL:</strong> ${rec.replace(/^\[CRITICAL\]|🚨 CRITICAL:?/gi, '').trim()}</li>`;
            } else if (rec.includes('HIGH')) {
                html += `<li class="recommendation high">🔴 <strong>HIGH:</strong> ${rec.replace(/^\[HIGH\]|🔴 HIGH:?/gi, '').trim()}</li>`;
            } else if (rec.includes('💡')) {
                html += `<li class="recommendation suggestion">💡 ${rec.replace(/💡/g, '').trim()}</li>`;
            } else {
                html += `<li class="recommendation">${rec}</li>`;
            }
        });
        html += '</ul></div>';
    }
    
    // Action buttons
    html += `<div class="action-buttons">
        <button onclick="copyResult('${escapeForJs(JSON.stringify(results))}')">📋 Copy JSON</button>
        <button onclick="exportJson('${escapeForJs(JSON.stringify(results))}')">💾 Export JSON</button>
    </div>`;
    
    return html;
}

function getRiskEmojiForHtml(riskScore: number): string {
    if (riskScore >= 0.8) { return '🔴'; }
    if (riskScore >= 0.6) { return '🟠'; }
    if (riskScore >= 0.4) { return '🟡'; }
    return '🟢';
}

function getRiskLevelForHtml(riskScore: number): string {
    if (riskScore >= 0.8) { return 'HIGH'; }
    if (riskScore >= 0.6) { return 'MEDIUM'; }
    if (riskScore >= 0.4) { return 'LOW'; }
    return 'MINIMAL';
}

function escapeHtml(text: string): string {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#x27;');
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
    body { 
      font-family: var(--vscode-font-family); 
      padding: 12px; 
      color: var(--vscode-foreground); 
      background: var(--vscode-editor-background); 
      margin: 0; 
      line-height: 1.5;
    }
    .chat-container { display: flex; flex-direction: column; height: 100vh; }
    .messages { flex: 1; overflow-y: auto; padding-bottom: 20px; }
    .message { margin: 8px 0; padding: 8px 12px; border-radius: 8px; }
    .message.user { background: rgba(64,128,255,0.08); border: 1px solid rgba(64,128,255,0.12); }
    .message.assistant { background: rgba(120,120,120,0.06); border: 1px solid rgba(120,120,120,0.08); }
    
    /* Enhanced Analysis Formatting */
    .analysis-summary { 
      background: rgba(0,150,136,0.1); 
      border: 1px solid rgba(0,150,136,0.2); 
      border-radius: 8px; 
      padding: 16px; 
      margin-bottom: 16px; 
    }
    .analysis-summary h2 { 
      margin: 0 0 12px 0; 
      color: var(--vscode-foreground); 
      font-size: 18px; 
    }
    .summary-grid { 
      display: grid; 
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
      gap: 8px; 
    }
    .summary-item { 
      display: flex; 
      justify-content: space-between; 
      padding: 4px 0; 
    }
    .summary-item .label { 
      color: var(--vscode-descriptionForeground); 
    }
    .summary-item .value { 
      font-weight: bold; 
      color: var(--vscode-foreground); 
    }
    
    .detailed-results { 
      margin: 16px 0; 
    }
    .detailed-results h2 { 
      margin: 0 0 12px 0; 
      color: var(--vscode-foreground); 
      font-size: 18px; 
    }
    
    .feature-analysis { 
      background: rgba(255,255,255,0.02); 
      border: 1px solid rgba(120,120,120,0.2); 
      border-radius: 8px; 
      padding: 16px; 
      margin-bottom: 16px; 
    }
    .feature-analysis h3 { 
      margin: 0 0 12px 0; 
      color: var(--vscode-foreground); 
      font-size: 16px; 
    }
    
    .feature-details { 
      display: grid; 
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
      gap: 8px; 
      margin-bottom: 12px; 
    }
    .detail-item { 
      display: flex; 
      justify-content: space-between; 
      padding: 4px 0; 
    }
    .detail-item .label { 
      color: var(--vscode-descriptionForeground); 
    }
    .detail-item .value { 
      font-weight: bold; 
    }
    .detail-item .value.risk-high { color: #f14c4c; }
    .detail-item .value.risk-medium { color: #ff9800; }
    .detail-item .value.risk-low { color: #4caf50; }
    .detail-item .value.risk-minimal { color: #4caf50; }
    
    .code-issues { 
      margin: 16px 0; 
      background: rgba(244,67,54,0.1); 
      border: 1px solid rgba(244,67,54,0.2); 
      border-radius: 6px; 
      padding: 12px; 
    }
    .code-issues h4 { 
      margin: 0 0 12px 0; 
      color: #f44336; 
    }
    
    .code-issue { 
      background: rgba(255,255,255,0.05); 
      border: 1px solid rgba(120,120,120,0.2); 
      border-radius: 6px; 
      padding: 12px; 
      margin-bottom: 12px; 
    }
    .issue-header { 
      display: flex; 
      align-items: center; 
      gap: 8px; 
      margin-bottom: 8px; 
      font-weight: bold; 
    }
    .issue-number { 
      color: var(--vscode-descriptionForeground); 
    }
    .issue-severity { 
      padding: 2px 8px; 
      border-radius: 4px; 
      font-size: 12px; 
    }
    .severity-critical { background: #f44336; color: white; }
    .severity-high { background: #ff9800; color: white; }
    .severity-medium { background: #ffeb3b; color: black; }
    .severity-low { background: #4caf50; color: white; }
    
    .issue-details { 
      margin-top: 8px; 
    }
    .issue-location, .issue-regulation, .fix-description { 
      margin: 4px 0; 
      color: var(--vscode-descriptionForeground); 
    }
    
    .problematic-code, .suggested-code { 
      margin: 8px 0; 
    }
    .problematic-code pre, .suggested-code pre { 
      background: rgba(0,0,0,0.3); 
      border: 1px solid rgba(120,120,120,0.3); 
      border-radius: 4px; 
      padding: 8px; 
      overflow-x: auto; 
      margin: 4px 0; 
    }
    .problematic-code code, .suggested-code code { 
      font-family: var(--vscode-editor-font-family); 
      font-size: var(--vscode-editor-font-size); 
      color: var(--vscode-editor-foreground); 
    }
    
    .llm-insights { 
      background: rgba(63,81,181,0.1); 
      border: 1px solid rgba(63,81,181,0.2); 
      border-radius: 6px; 
      padding: 12px; 
      margin: 12px 0; 
    }
    .llm-insights h4 { 
      margin: 0 0 8px 0; 
      color: #3f51b5; 
    }
    .assessment { 
      margin: 8px 0; 
      font-style: italic; 
    }
    .key-risks, .implementation-suggestions { 
      margin: 8px 0; 
    }
    .key-risks ul, .implementation-suggestions ul { 
      margin: 4px 0; 
      padding-left: 20px; 
    }
    
    .recommendations { 
      margin: 16px 0; 
      background: rgba(76,175,80,0.1); 
      border: 1px solid rgba(76,175,80,0.2); 
      border-radius: 8px; 
      padding: 16px; 
    }
    .recommendations h2 { 
      margin: 0 0 12px 0; 
      color: #4caf50; 
      font-size: 18px; 
    }
    .recommendations ul { 
      list-style: none; 
      padding: 0; 
      margin: 0; 
    }
    .recommendations li { 
      padding: 6px 0; 
      border-bottom: 1px solid rgba(120,120,120,0.1); 
    }
    .recommendations li:last-child { 
      border-bottom: none; 
    }
    .recommendation.critical { 
      color: #f44336; 
      font-weight: bold; 
    }
    .recommendation.high { 
      color: #ff9800; 
      font-weight: bold; 
    }
    .recommendation.suggestion { 
      color: var(--vscode-foreground); 
    }
    
    /* Legacy support */
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
