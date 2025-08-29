# Compliance Violation Test Samples

This directory contains sample code files with various privacy and regulatory compliance violations for testing the TikTok Compliance Analyzer VS Code extension.

## Files Overview

### 1. `privacy_violations.py` - Python Backend Violations
**Risk Level: HIGH**

**Violations Demonstrated:**
- Collecting personal data without explicit consent
- Storing sensitive data without encryption
- Age verification bypass for minors
- Location tracking without consent
- Sharing personal data with third parties
- Processing children's data without parental consent (COPPA violation)
- Behavioral tracking for advertising
- Device fingerprinting
- Exporting user data without user knowledge

**Expected Analysis Results:**
- Risk Level: HIGH
- Regulations: GDPR, COPPA, Privacy Framework
- Action Required: Immediate compliance review required

### 2. `tracking_violations.js` - JavaScript Frontend Violations
**Risk Level: HIGH**

**Violations Demonstrated:**
- Collecting personal data without consent on page load
- Device fingerprinting using canvas and browser APIs
- Location tracking without proper consent
- Behavioral tracking of all user interactions
- Sharing data with advertising partners
- Age verification issues
- Processing children's data without parental consent
- Real-time event tracking and analysis
- Creating advertising profiles

**Expected Analysis Results:**
- Risk Level: HIGH
- Regulations: GDPR, COPPA, Privacy Framework
- Action Required: Immediate compliance review required

### 3. `typescript_violations.ts` - TypeScript Violations
**Risk Level: HIGH**

**Violations Demonstrated:**
- Collecting personal data without explicit consent
- Location tracking without proper consent
- Sharing location data with third parties
- Behavioral tracking for profiling
- Creating user profiles for advertising
- Age verification and COPPA compliance issues
- Processing children's data without parental consent
- Device fingerprinting
- Exporting user data without user knowledge
- Creating comprehensive marketing profiles

**Expected Analysis Results:**
- Risk Level: HIGH
- Regulations: GDPR, COPPA, Privacy Framework
- Action Required: Immediate compliance review required

### 4. `react_violations.tsx` - React Component Violations
**Risk Level: HIGH**

**Violations Demonstrated:**
- Collecting user data without consent on component mount
- Location tracking without proper consent
- Behavioral tracking of all user interactions
- Sharing data with analytics without consent
- Sharing data with advertising networks
- Age verification issues
- Processing children's data without parental consent
- Device fingerprinting
- Exporting user data without user knowledge
- Creating marketing profiles

**Expected Analysis Results:**
- Risk Level: HIGH
- Regulations: GDPR, COPPA, Privacy Framework
- Action Required: Immediate compliance review required

### 5. `api_violations.py` - API Server Violations
**Risk Level: HIGH**

**Violations Demonstrated:**
- Storing sensitive data in plain text (passwords)
- Collecting user data without consent
- Device fingerprinting without consent
- Tracking user behavior without consent
- Sharing behavior data with third parties
- Exporting user data without proper authorization
- Age verification issues
- Processing children's data without parental consent
- Location tracking without consent
- Sharing location data with partners
- Storing IP addresses without consent

**Expected Analysis Results:**
- Risk Level: HIGH
- Regulations: GDPR, COPPA, Privacy Framework
- Action Required: Immediate compliance review required

## How to Test

1. **Open the Extension Development Host:**
   - Press `F5` in VS Code to launch the extension
   - Open one of the test files in the new window

2. **Run Compliance Analysis:**
   - Open Command Palette (`Ctrl+Shift+P`)
   - Run `TikTok Compliance: Analyze Current File`
   - Check the Output panel for results

3. **Test Different File Types:**
   - Try each file to ensure the extension analyzes different languages
   - Verify that violations are detected consistently

4. **Test Workspace Analysis:**
   - Run `TikTok Compliance: Analyze Workspace`
   - Should analyze all files in the test-samples directory

## Compliance Keywords Detected

The extension should detect these types of violations:

### Privacy Keywords
- `user_data`, `personal_data`, `user_profile`
- `age`, `location`, `tracking`, `geolocation`
- `collect_user`, `track_user`, `device_fingerprint`

### GDPR Keywords
- `gdpr`, `consent`, `data_processing`
- `personal_information`, `data_collection`
- `privacy_policy`, `user_consent`

### COPPA Keywords
- `coppa`, `under_13`, `age_verification`
- `parental_consent`, `child_data`, `minor`

## Expected Extension Behavior

### Output Panel Results
Each file should generate detailed analysis results showing:
- Total features analyzed
- Features requiring compliance
- High risk features
- Human review needed
- Detailed results for each violation found
- Applicable regulations
- Implementation notes
- Action required

### Risk Assessment
- **HIGH**: Files with multiple severe violations
- **MEDIUM**: Files with moderate violations
- **LOW**: Files with minor violations
- **MINIMAL**: Files with no significant violations

### Recommendations
The extension should provide actionable recommendations such as:
- Implement consent mechanisms
- Add age verification
- Encrypt sensitive data
- Review data sharing practices
- Establish data retention policies

## Troubleshooting

If the extension doesn't detect violations:

1. **Check Python Installation:**
   ```bash
   python --version
   ```

2. **Verify Extension Configuration:**
   - Check `tiktokCompliance.pythonPath` setting
   - Ensure Python is in system PATH

3. **Check Output Panel:**
   - Look for error messages in the Output panel
   - Verify the Python script is being called correctly

4. **Test with Simple File:**
   - Start with a file containing obvious violations
   - Gradually test more complex scenarios

## Adding New Test Cases

To add new test files:

1. Create a new file with compliance violations
2. Document the violations in this README
3. Specify expected analysis results
4. Test with the extension
5. Update the README with actual results

## Notes

- These files contain intentional violations for testing purposes
- Do not use this code in production applications
- The extension should flag all these violations as HIGH risk
- Files may contain TypeScript/JavaScript errors - this is expected for testing
