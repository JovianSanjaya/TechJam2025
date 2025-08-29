# Publishing Guide for TikTok Compliance Analyzer

## Prerequisites

1. **Create a Microsoft Account** (if you don't have one)
2. **Create a Publisher Account** on [Visual Studio Marketplace](https://marketplace.visualstudio.com/manage/publishers)
3. **Install VSCE** (VS Code Extension Manager):
   ```bash
   npm install -g @vscode/vsce
   ```

## Step 1: Prepare Your Extension

### Update Publisher Information

Edit `package.json` and replace:
- `"publisher": "your-publisher-name"` with your actual publisher ID
- `"author": {"name": "Your Name"}` with your name
- Repository URLs with your actual GitHub repository

### Create Publisher Account

1. Go to [https://marketplace.visualstudio.com/manage/publishers](https://marketplace.visualstudio.com/manage/publishers)
2. Sign in with your Microsoft account
3. Create a new publisher (choose a unique ID)
4. Note down your publisher ID

## Step 2: Build and Package

### 1. Build the Extension
```bash
npm run package
```

### 2. Test the Package Locally
```bash
code --install-extension tiktok-compliance-analyzer-0.0.1.vsix
```

### 3. Verify Installation
- Open VS Code
- Check Extensions panel for your extension
- Test the commands work correctly

## Step 3: Publish to Marketplace

### Method 1: Using VSCE (Recommended)

```bash
# Login to your publisher account
vsce login your-publisher-id

# Publish the extension
vsce publish
```

### Method 2: Manual Upload

1. Go to [https://marketplace.visualstudio.com/manage/publishers/your-publisher-id](https://marketplace.visualstudio.com/manage/publishers/your-publisher-id)
2. Click "New Extension" → "Visual Studio Code"
3. Upload your `.vsix` file
4. Fill in the extension details
5. Submit for review

## Step 4: Post-Publishing

### Update Extension
When you make changes:
```bash
# Update version in package.json
# Build and publish
npm run package
vsce publish
```

### Manage Extension
- Monitor downloads and ratings
- Respond to user reviews
- Update extension metadata as needed

## Troubleshooting

### Common Issues

1. **Publisher ID not found**
   - Make sure you're logged in with the correct Microsoft account
   - Verify the publisher ID in package.json matches your marketplace publisher

2. **Extension rejected**
   - Check the extension guidelines
   - Ensure all required fields are filled
   - Test extension thoroughly before publishing

3. **VSCE login issues**
   ```bash
   vsce logout
   vsce login your-publisher-id
   ```

### Validation Checklist

- [ ] Publisher ID is correct in package.json
- [ ] All required fields are filled (name, description, version, etc.)
- [ ] Extension builds without errors
- [ ] Extension works in test environment
- [ ] README is user-friendly and informative
- [ ] Keywords are relevant and help with discoverability
- [ ] License is specified
- [ ] Repository links are working

## Extension Guidelines

Make sure your extension follows Microsoft's guidelines:

- **Content Policies**: No malicious code, respect user privacy
- **Technical Requirements**: Works on supported VS Code versions
- **User Experience**: Clear functionality, helpful documentation
- **Security**: No data collection without consent

## Getting Help

- [VS Code Extension Publishing](https://code.visualstudio.com/docs/extensions/publish-extension)
- [Marketplace Publisher Support](https://marketplace.visualstudio.com/support)
- [Extension Guidelines](https://code.visualstudio.com/docs/extensions/publish-extension#_extension-guidelines)

## Quick Commands Reference

```bash
# Install VSCE
npm install -g @vscode/vsce

# Login to publisher
vsce login your-publisher-id

# Package extension
npm run package

# Publish extension
vsce publish

# Check extension status
vsce show your-publisher-id.tiktok-compliance-analyzer
```

---

**Ready to share your extension with the world! 🚀**
