#!/usr/bin/env node
/**
 * Test the generalized Python path resolution
 */

const os = require('os');
const path = require('path');
const cp = require('child_process');

function tryCmd(cmd) {
    try {
        console.log(`Testing Python command: ${cmd}`);
        const res = cp.spawnSync(cmd, ['--version'], { 
            encoding: 'utf8',
            timeout: 5000,
            windowsHide: true,
            shell: true
        });
        const success = res.status === 0;
        console.log(`Command ${cmd} result: ${success ? 'SUCCESS' : 'FAILED'}`);
        if (success && res.stdout) {
            console.log(`  Version: ${res.stdout.trim()}`);
        }
        return success;
    } catch (e) {
        console.log(`Command ${cmd} error: ${e.message}`);
        return false;
    }
}

function getEnvironmentPythonPaths() {
    const paths = [];
    
    // Check active conda environment
    const condaPath = process.env.CONDA_PREFIX;
    if (condaPath) {
        const pythonExe = process.platform === 'win32' ? 'python.exe' : 'python';
        paths.push(path.join(condaPath, pythonExe));
    }
    
    // Check active virtual environment
    const virtualEnv = process.env.VIRTUAL_ENV;
    if (virtualEnv) {
        const pythonExe = process.platform === 'win32' ? 'python.exe' : 'python';
        const binDir = process.platform === 'win32' ? 'Scripts' : 'bin';
        paths.push(path.join(virtualEnv, binDir, pythonExe));
    }
    
    return paths;
}

function getCommonPythonPaths(userHome) {
    if (process.platform === 'win32') {
        return [
            // User-specific installations (using dynamic user home)
            path.join(userHome, 'AppData', 'Local', 'Programs', 'Python', 'Python312', 'python.exe'),
            path.join(userHome, 'AppData', 'Local', 'Programs', 'Python', 'Python311', 'python.exe'),
            path.join(userHome, 'AppData', 'Local', 'Programs', 'Python', 'Python310', 'python.exe'),
            path.join(userHome, 'anaconda3', 'python.exe'),
            path.join(userHome, 'miniconda3', 'python.exe'),
            // PATH commands
            'python',
            'py',
            // System-wide installations
            'C:\\Program Files\\Python312\\python.exe',
            'C:\\Program Files\\Python311\\python.exe',
            'C:\\Program Files\\Python310\\python.exe'
        ];
    } else if (process.platform === 'darwin') {
        return [
            '/usr/local/bin/python3',
            '/opt/homebrew/bin/python3',
            '/Library/Frameworks/Python.framework/Versions/3.12/bin/python3',
            '/Library/Frameworks/Python.framework/Versions/3.11/bin/python3',
            path.join(userHome, 'anaconda3', 'bin', 'python'),
            path.join(userHome, 'miniconda3', 'bin', 'python'),
            'python3',
            'python'
        ];
    } else {
        // Linux and other Unix-like systems
        return [
            '/usr/bin/python3',
            '/usr/local/bin/python3',
            path.join(userHome, 'anaconda3', 'bin', 'python'),
            path.join(userHome, 'miniconda3', 'bin', 'python'),
            'python3',
            'python'
        ];
    }
}

console.log('🧪 Testing Generalized Python Path Resolution');
console.log('=' .repeat(60));
console.log(`Platform: ${process.platform}`);
console.log(`User Home: ${os.homedir()}`);
console.log(`User: ${os.userInfo().username}`);

// Test environment paths
console.log('\n🌍 Environment-based paths:');
const envPaths = getEnvironmentPythonPaths();
if (envPaths.length === 0) {
    console.log('  No environment paths found');
} else {
    for (const envPath of envPaths) {
        tryCmd(envPath);
    }
}

// Test common paths
console.log('\n📁 Common installation paths:');
const userHome = os.homedir();
const commonPaths = getCommonPythonPaths(userHome);

let foundWorking = null;
for (const pythonPath of commonPaths) {
    if (tryCmd(pythonPath)) {
        if (!foundWorking) {
            foundWorking = pythonPath;
        }
    }
}

console.log('\n✅ Result:');
if (foundWorking) {
    console.log(`Best Python found: ${foundWorking}`);
} else {
    console.log('No working Python found');
}

console.log('=' .repeat(60));
