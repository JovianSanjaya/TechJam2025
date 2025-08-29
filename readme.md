# tiktok# TikTok Compliance Analyzer

A Visual Studio Code extension that analyzes code for TikTok compliance requirements, focusing on privacy regulations, data protection, and regulatory adherence.

## Features

- **🔍 File Analysis**: Analyze individual files for compliance issues
- **🌐 Workspace Analysis**: Scan entire workspace for regulatory concerns
- **📊 Detailed Reporting**: Comprehensive compliance reports with risk levels
- **⚖️ Multi-Regulation Support**: GDPR, COPPA, and privacy framework compliance
- **🎯 Smart Detection**: Identifies privacy-related code patterns and data handling

## Quick Start

1. **Install the Extension**: Install from the VS Code marketplace or compile from source
2. **Open a Code File**: Open any Python, JavaScript, or TypeScript file
3. **Run Analysis**: Use Command Palette (`Ctrl+Shift+P`) and run:
   - `TikTok Compliance: Analyze Current File`
   - `TikTok Compliance: Analyze Workspace`
   - `TikTok Compliance: Show Results`

## Commands

| Command | Description | Keyboard Shortcut |
|---------|-------------|-------------------|
| `TikTok Compliance: Analyze Current File` | Analyze the currently open file | - |
| `TikTok Compliance: Analyze Workspace` | Analyze all code files in workspace | - |
| `TikTok Compliance: Show Results` | Open compliance results dashboard | - |

## Configuration

Configure the extension through VS Code settings:

```json
{
    "tiktokCompliance.pythonPath": "python",
    "tiktokCompliance.maxFilesToAnalyze": 10,
    "tiktokCompliance.autoAnalyze": false
}
```

### Settings

- `tiktokCompliance.pythonPath`: Path to Python executable (default: "python")
- `tiktokCompliance.maxFilesToAnalyze`: Maximum files to analyze in workspace mode (default: 10)
- `tiktokCompliance.autoAnalyze`: Automatically analyze files on save (default: false)

## Analysis Results

The extension provides detailed analysis results including:

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

## Supported File Types

- Python (`.py`)
- JavaScript (`.js`)
- TypeScript (`.ts`)
- JSX (`.jsx`)
- TSX (`.tsx`)

## Requirements

- **Python**: Python 3.6+ must be installed and accessible
- **VS Code**: Version 1.103.0 or higher

## Installation from Source

1. Clone this repository
2. Run `npm install` to install dependencies
3. Run `npm run compile` to build the extension
4. Press `F5` to run the extension in a new Extension Development Host window

## Development

### Build Commands

```bash
npm run compile          # Compile TypeScript and bundle
npm run watch            # Watch mode for development
npm run package          # Create production build
npm run test             # Run tests
```

### Project Structure

```
├── src/
│   ├── extension.ts          # Main extension entry point
│   ├── python/
│   │   └── compliance_analyzer.py  # Python compliance analyzer
│   └── test/
│       └── extension.test.ts # Extension tests
├── .vscode/                  # VS Code configuration
├── package.json             # Extension manifest
└── README.md               # This file
```

## Privacy Detection Patterns

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

## Example Analysis

For code containing:
```python
def collect_user_data(user_id):
    personal_data = get_user_profile(user_id)
    if user_age < 13:
        require_parental_consent()
    return personal_data
```

The analyzer will identify:
- **Risk Level**: HIGH
- **Regulations**: GDPR, COPPA, Privacy Framework
- **Notes**: Implement age verification, ensure data encryption
- **Action**: Immediate compliance review required

## Troubleshooting

### Python Not Found
Ensure Python is installed and accessible:
```bash
python --version
# or
python3 --version
```

Update the `tiktokCompliance.pythonPath` setting if needed.

### No Analysis Results
1. Check the Output panel for error messages
2. Verify Python dependencies are available
3. Ensure the file contains analyzable code

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and feature requests, please create an issue in the GitHub repository.

---

**Note**: This extension is designed for TikTok compliance analysis but can be adapted for general privacy and regulatory compliance checking.pliance-analyzer README

This is the README for your extension "tiktok-compliance-analyzer". After writing up a brief description, we recommend including the following sections.

## Features

Describe specific features of your extension including screenshots of your extension in action. Image paths are relative to this README file.

For example if there is an image subfolder under your extension project workspace:

\!\[feature X\]\(images/feature-x.png\)

> Tip: Many popular extensions utilize animations. This is an excellent way to show off your extension! We recommend short, focused animations that are easy to follow.

## Requirements

If you have any requirements or dependencies, add a section describing those and how to install and configure them.

## Extension Settings

Include if your extension adds any VS Code settings through the `contributes.configuration` extension point.

For example:

This extension contributes the following settings:

* `myExtension.enable`: Enable/disable this extension.
* `myExtension.thing`: Set to `blah` to do something.

## Known Issues

Calling out known issues can help limit users opening duplicate issues against your extension.

## Release Notes

Users appreciate release notes as you update your extension.

### 1.0.0

Initial release of ...

### 1.0.1

Fixed issue #.

### 1.1.0

Added features X, Y, and Z.

---

## Following extension guidelines

Ensure that you've read through the extensions guidelines and follow the best practices for creating your extension.

* [Extension Guidelines](https://code.visualstudio.com/api/references/extension-guidelines)

## Working with Markdown

You can author your README using Visual Studio Code. Here are some useful editor keyboard shortcuts:

* Split the editor (`Cmd+\` on macOS or `Ctrl+\` on Windows and Linux).
* Toggle preview (`Shift+Cmd+V` on macOS or `Shift+Ctrl+V` on Windows and Linux).
* Press `Ctrl+Space` (Windows, Linux, macOS) to see a list of Markdown snippets.

## For more information

* [Visual Studio Code's Markdown Support](http://code.visualstudio.com/docs/languages/markdown)
* [Markdown Syntax Reference](https://help.github.com/articles/markdown-basics/)

**Enjoy!**
