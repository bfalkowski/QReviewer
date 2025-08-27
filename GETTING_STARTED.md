# 🚀 QReviewer Getting Started Guide

**Your first steps to AI-powered code reviews with Amazon Q CLI**

---

## 📋 **Quick Start Checklist**

- [ ] Install QReviewer
- [ ] Set up GitHub token
- [ ] Configure Amazon Q CLI (or fallback)
- [ ] Test configuration
- [ ] Train on your repository
- [ ] Run your first code review with learned standards
- [ ] Apply learned standards to future reviews

---

## 🛠️ **Step 1: Installation & Setup**

### **1.1 Install Dependencies**
```bash
# Clone the repository
git clone https://github.com/bryanfalkowski/QReviewer.git
cd QReviewer

# Install Python dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### **1.2 Set Up GitHub Token**
```bash
# Create GitHub Personal Access Token
# Go to: https://github.com/settings/tokens
# Select: repo, workflow, admin:org permissions

# Set environment variable
export GITHUB_TOKEN="ghp_your_token_here"

# Or add to your shell profile (~/.zshrc, ~/.bashrc)
echo 'export GITHUB_TOKEN="ghp_your_token_here"' >> ~/.zshrc
source ~/.zshrc
```

### **1.3 Configure LLM Backend**

#### **Option A: Amazon Q CLI (Recommended)**
```bash
# For local execution (same machine as Q CLI)
# No additional config needed - this is the default!

# For remote execution via SSH
export Q_CLI_HOST="192.168.1.100"
export Q_CLI_USER="bryan"
export Q_CLI_PORT="22"
export Q_CLI_KEY_PATH="~/.ssh/id_rsa"  # Optional
```

#### **Option B: AWS Bedrock (Fallback)**
```bash
export QREVIEWER_LLM_BACKEND="bedrock"
export AWS_REGION="us-east-1"
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export MODEL_ID="anthropic.claude-3-5-sonnet-20241022-v2:0"
```

#### **Option C: OpenAI (Fallback)**
```bash
export QREVIEWER_LLM_BACKEND="openai"
export OPENAI_API_KEY="sk-your_openai_key"
export OPENAI_MODEL="gpt-4"
```

---

## ✅ **Step 2: Verify Configuration**

### **2.1 Check Your Setup**
```bash
# Show current configuration
qrev config show

# Validate configuration
qrev config validate

# Test LLM connection
qrev config test
```

**Expected Output:**
```
🔧 QReviewer Configuration
========================================
LLM Backend: amazon_q
LLM Enabled: True
GitHub Token: ✅ Set
API Key: ❌ Not required

📱 Amazon Q CLI Configuration:
   Host: localhost
   User: 
   Port: None
   Key Path: Default SSH key
```

### **2.2 Troubleshoot Common Issues**

| Issue | Solution |
|-------|----------|
| `Q CLI command failed: bash: q: command not found` | Install Q CLI or use fallback backend |
| `GitHub API error: 401` | Check your GITHUB_TOKEN |
| `LLM backend not properly configured` | Set required environment variables |

---

## 🧠 **Step 3: Train on Your Repository**

### **3.1 Initial Training**
```bash
# Train on your own repository
qrev learn https://github.com/yourusername/yourrepo \
  --module src \
  --module tests \
  --max-prs-per-module 50 \
  --strategy representative \
  --output-dir my_training
```

**What This Does:**
- Analyzes your repository's PR history
- Learns your team's coding patterns
- Generates custom review standards
- Saves results to `my_training/` directory

### **3.2 Training Strategies**

| Strategy | Use Case | Command |
|----------|----------|---------|
| **Recent** | Current standards | `--strategy recent` |
| **Representative** | Balanced learning | `--strategy representative` |
| **High Impact** | Critical issues | `--strategy high_impact` |

### **3.3 Apply Learned Standards**
```bash
# Review with your learned standards
qrev review --inp pr-diff.json \
  --standards learned_python,learned_tests \
  --out findings.json
```

---

## 🎯 **Step 4: Your First Code Review**

### **4.1 Review a GitHub PR with Learned Standards**

#### **Option A: Review-Only Mode (Recommended for First-Time Users)**
```bash
# Review PR directly without fetching first (generates local report only)
qrev review-only --pr https://github.com/owner/repo/pull/123 \
  --standards learned_python,learned_tests \
  --out my-review.json \
  --format summary

# Generate HTML report for sharing
qrev review-only --pr https://github.com/owner/repo/pull/123 \
  --standards learned_python,learned_tests \
  --out my-review.json \
  --format html
```

#### **Option B: Traditional Two-Step Process**
```bash
# Fetch PR diff from any repository
qrev fetch --pr https://github.com/owner/repo/pull/123 --out pr-diff.json

# Review using your learned standards
qrev review --inp pr-diff.json \
  --standards learned_python,learned_tests \
  --out findings.json

# View results in human-readable format
qrev summarize --inp findings.json
```

### **4.2 Review with Custom Guidelines**
```bash
# Create guidelines file
cat > my-guidelines.md << EOF
# Project Guidelines

## Code Quality
- Use descriptive variable names
- Add docstrings to all functions
- Keep functions under 20 lines

## Security
- Never log sensitive information
- Validate all user inputs
- Use parameterized queries
EOF

# Review with guidelines
qrev review --inp pr-diff.json --guidelines my-guidelines.md --out findings.json
```

### **4.3 Review with Built-in Standards**
```bash
# Apply built-in standards
qrev review --inp pr-diff.json --standards security,performance --out findings.json

# List available standards
qrev standards list
```

### **4.4 Output Formats for Review-Only Mode**

The `review-only` command supports multiple output formats:

| Format | Command | Output | Use Case |
|--------|---------|--------|----------|
| **JSON** | `--format json` | Structured data | Programmatic processing, CI/CD |
| **HTML** | `--format html` | Web report | Sharing with team, documentation |
| **Summary** | `--format summary` | Console summary + JSON | Quick review, command line |

**Example with all formats:**
```bash
# Generate all formats at once
qrev review-only --pr https://github.com/owner/repo/pull/123 \
  --standards learned_python,security \
  --out my-review \
  --format html

# This creates:
# - my-review.html (web report)
# - my-review.json (structured data)
```

---

## 🔄 **Step 5: Continuous Improvement**

### **5.1 Retrain Periodically**
```bash
# Retrain on recent changes
qrev learn https://github.com/yourusername/yourrepo \
  --module src \
  --strategy recent \
  --max-prs-per-module 25 \
  --output-dir updated_training
```

### **5.2 Compare Training Results**
```bash
# Compare old vs new standards
diff my_training/combined_learning_results.json updated_training/combined_learning_results.json
```

### **5.3 Update Your Workflow**
```bash
# Use learned standards in CI/CD
qrev review --inp pr-diff.json \
  --standards learned_python,security,performance \
  --out findings.json

# Check for critical issues
if grep -q '"severity": "critical"' findings.json; then
  echo "🚨 Critical issues found!"
  exit 1
fi
```

---

## 🚀 **Step 6: Advanced Usage**

### **6.1 API Server Mode**
```bash
# Start API server
python -m qrev.api.app

# In another terminal, test API
curl -X POST "http://localhost:8000/review_hunks" \
  -H "Content-Type: application/json" \
  -d '{"diffJson": {"pr": {"url": "https://github.com/owner/repo/pull/123", "number": 123, "repo": "owner/repo"}, "files": [{"path": "test.py", "status": "modified", "patch": "@@ -1,3 +1,6 @@\n def test(): pass\n", "additions": 1, "deletions": 0, "sha": "abc123"}]}}'
```

### **6.2 Module-Focused Learning**
```bash
# Focus on specific parts of your codebase
qrev learn https://github.com/yourusername/yourrepo \
  --module src/api \
  --module src/core \
  --module tests/unit \
  --max-prs-per-module 30 \
  --max-total-prs 150
```

### **6.3 Custom Standards Creation**
```bash
# Create custom standards file
cat > custom-standards.json << EOF
{
  "name": "my_team_standards",
  "description": "Custom standards for my team",
  "rules": [
    {
      "id": "CUSTOM_001",
      "category": "style",
      "pattern": "TODO|FIXME|HACK",
      "message": "Avoid TODO comments in production code",
      "severity": "minor"
    }
  ]
}
EOF

# Apply custom standards
qrev review --inp pr-diff.json --standards custom-standards.json --out findings.json
```

---

## 🧪 **Step 7: Testing & Validation**

### **7.1 Test on Your Own Code**
```bash
# Create a test PR in your repository
# Then test the review system
qrev fetch --pr https://github.com/yourusername/yourrepo/pull/TEST_PR_NUMBER
qrev review --inp pr-diff.json --out test-findings.json
qrev summarize --inp test-findings.json
```

### **7.2 Validate Learning Results**
```bash
# Check what was learned
cat my_training/combined_learning_results.json | jq '.learned_standards'

# View team preferences
cat my_training/combined_learning_results.json | jq '.team_preferences'
```

### **7.3 Performance Testing**
```bash
# Test with different PR sizes
qrev fetch --pr https://github.com/yourusername/yourrepo/pull/SMALL_PR
qrev fetch --pr https://github.com/yourusername/yourrepo/pull/LARGE_PR

# Compare review times and quality
time qrev review --inp small-pr.json --out small-findings.json
time qrev review --inp large-pr.json --out large-findings.json
```

---

## 🔧 **Troubleshooting**

### **Common Issues & Solutions**

| Problem | Error Message | Solution |
|---------|---------------|----------|
| **Q CLI not found** | `bash: q: command not found` | Install Q CLI or switch to fallback backend |
| **GitHub rate limit** | `GitHub API error: 403` | Wait for rate limit reset or use token with higher limits |
| **SSH connection failed** | `SSH command failed: Connection refused` | Check SSH config and network connectivity |
| **Invalid PR URL** | `Invalid GitHub repository URL` | Verify PR URL format and accessibility |
| **Configuration errors** | `LLM backend not properly configured` | Run `qrev config validate` and fix issues |

### **Debug Commands**
```bash
# Check configuration
qrev config show

# Validate setup
qrev config validate

# Test LLM connection
qrev config test

# Show environment variables needed
qrev config env
```

---

## 📚 **Next Steps**

### **What You've Accomplished:**
✅ Set up QReviewer with Amazon Q CLI  
✅ Verified configuration and connectivity  
✅ Trained on your repository's patterns  
✅ Run your first AI-powered code review with learned standards  
✅ Applied learned standards to reviews  
✅ Set up continuous improvement workflow  

### **Where to Go Next:**
- **Integrate with CI/CD**: Add QReviewer to your GitHub Actions
- **Team Adoption**: Share learned standards with your team
- **Custom Standards**: Create domain-specific review rules
- **API Integration**: Build custom tools using the REST API
- **Performance Tuning**: Optimize for your repository size

### **Resources:**
- **Full Documentation**: [README.md](README.md)
- **API Reference**: [qrev/api/app.py](qrev/api/app.py)
- **CLI Commands**: `qrev --help`
- **Configuration**: `qrev config --help`
- **Learning**: `qrev learn --help`

---

## 🎉 **Congratulations!**

You're now ready to use AI-powered code reviews with QReviewer! The system will learn from your codebase and continuously improve its review quality. 

**Happy coding and reviewing! 🚀**

---

*Need help? Check the troubleshooting section above or create an issue in the repository.*
