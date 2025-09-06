# Session End Checklist

This checklist ensures comprehensive context preservation every time a development session ends.

## 🎯 **Session End Protocol**

When the user indicates they're ending a session, follow this checklist:

### 1. **Create Session Summary** 📝
- **File**: `docs/session-summaries/YYYY-MM-DD-HHMM-session-topic.md` (include timestamp for multiple daily sessions)
- **Include**:
  - **Date & Time**: Full timestamp (e.g., "2025-09-06 12:25 BST")
  - Session objectives and accomplishments
  - Technical changes made with code examples
  - Issues encountered and solutions
  - Lessons learned and best practices
  - Current status and next steps
  - Key links and references

### 2. **Update Troubleshooting Guide** 🔧
- **File**: `docs/troubleshooting/[relevant-topic]-issues.md`
- **Include**:
  - Specific error messages encountered
  - Step-by-step solutions
  - Code examples for fixes
  - Prevention strategies
  - Related documentation links

### 3. **Update Next Steps Issue** 📋
- **GitHub Issue**: Current "Next Steps" issue
- **Include**:
  - What was completed in this session
  - What's in progress
  - Immediate next steps for tomorrow
  - Any blockers or dependencies
  - Updated project health status

### 4. **Commit and Push Changes** 🚀
- **Commit Message**: Descriptive summary of session work
- **Push**: Ensure all changes are in the repository
- **Verify**: All documentation is accessible

### 5. **Provide Session Summary** 📊
- **Give User**: Quick overview of what was accomplished
- **Highlight**: Key next steps for tomorrow
- **Link**: Important resources and documentation
- **Confirm**: Everything is saved and accessible

## 📋 **Session Summary Template**

```markdown
# Session Summary: YYYY-MM-DD-HHMM
## [Session Topic]

**Date**: [Date]  
**Time**: [Time with timezone]  
**Duration**: [Duration]  
**Focus**: [Main focus areas]

## 🎯 **Session Objectives**
- [Objective 1]
- [Objective 2]
- [Objective 3]

## ✅ **Major Accomplishments**

### 1. **[Accomplishment 1]**
- **Technical Details**: [What was implemented]
- **Files Changed**: [List of files]
- **Code Examples**: [Key code snippets]

### 2. **[Accomplishment 2]**
- **Technical Details**: [What was implemented]
- **Files Changed**: [List of files]
- **Code Examples**: [Key code snippets]

## 🚨 **Issues Encountered & Solutions**

### 1. **[Issue 1]**
- **Error Message**: [Exact error]
- **Cause**: [Root cause]
- **Solution**: [How it was fixed]
- **Files Affected**: [Relevant files]

### 2. **[Issue 2]**
- **Error Message**: [Exact error]
- **Cause**: [Root cause]
- **Solution**: [How it was fixed]
- **Files Affected**: [Relevant files]

## 📚 **Documentation Created/Updated**

### New Files
- [File 1] - [Description]
- [File 2] - [Description]

### Updated Files
- [File 1] - [What was updated]
- [File 2] - [What was updated]

## 🎯 **Current Status**

### ✅ **Completed**
- [Task 1]
- [Task 2]

### 🔄 **In Progress**
- [Task 1]
- [Task 2]

### 🎯 **Next Steps**
1. **[Priority 1]** [Task description]
2. **[Priority 2]** [Task description]
3. **[Priority 3]** [Task description]

## 🔗 **Key Links**
- [PR #X]: [Description]
- [Issue #X]: [Description]
- [Documentation]: [Link]

## 💡 **Lessons Learned**

### 1. **[Topic 1]**
- [Key insight]
- [Best practice]

### 2. **[Topic 2]**
- [Key insight]
- [Best practice]

## 📊 **Project Health Status**

- **Security**: [Status - ✅/⚠️/❌]
- **Documentation**: [Status - ✅/⚠️/❌]
- **Branching**: [Status - ✅/⚠️/❌]
- **CI/CD**: [Status - ✅/⚠️/❌]
- **Database**: [Status - ✅/⚠️/❌]
- **Project Management**: [Status - ✅/⚠️/❌]

## 🎉 **Session Success**

[Summary of what was accomplished and current state]
```

## 🔧 **Troubleshooting Guide Template**

```markdown
# [Topic] Troubleshooting Guide

This document provides solutions for common [topic] issues encountered in TheTally.

## 🚨 **Common Issues**

### 1. **[Issue 1]**

#### **Error Message**
```
[Exact error message]
```

#### **Cause**
[Root cause explanation]

#### **Solution**
```[language]
[Code solution]
```

#### **Files Affected**
- [File 1]
- [File 2]

---

### 2. **[Issue 2]**

#### **Error Message**
```
[Exact error message]
```

#### **Cause**
[Root cause explanation]

#### **Solution**
```[language]
[Code solution]
```

#### **Files Affected**
- [File 1]
- [File 2]

---

## 🛠️ **Configuration**

### **[Configuration Section]**
```[language]
[Configuration code]
```

### **Running [Tool] Locally**
```bash
[Command 1]
[Command 2]
```

## 🔍 **Debugging**

### **Check [Status]**
```bash
[Debug command 1]
[Debug command 2]
```

### **Local Testing**
```bash
[Test command 1]
[Test command 2]
```

## 📋 **Checklist**

### **Before [Action]**
- [ ] [Check 1]
- [ ] [Check 2]

### **After [Action]**
- [ ] [Check 1]
- [ ] [Check 2]

## 🚀 **Quick Fixes**

### **Fix [Issue]**
```[language]
[Quick fix code]
```

### **Update [Configuration]**
```[language]
[Configuration update]
```

## 📚 **Related Documentation**

- [Link 1]
- [Link 2]

## 💡 **Best Practices**

1. [Practice 1]
2. [Practice 2]
3. [Practice 3]
```

## 🎯 **Next Steps Issue Template**

```markdown
## 🎯 Current Status (Updated: [DATE])

### ✅ Completed
- [List completed tasks with links to PRs/commits]

### 🔄 In Progress  
- [List current work with status]

### 🎯 Immediate Next Steps (Priority Order)
1. **[HIGH PRIORITY]** [Task description]
2. **[MEDIUM PRIORITY]** [Task description]  
3. **[LOW PRIORITY]** [Task description]

### 🔮 Future Development
- [List planned future work]

### 🚨 Blockers & Dependencies
- [List any blockers or dependencies]

### 📊 Project Health
- **Security**: [Status - ✅/⚠️/❌]
- **Documentation**: [Status - ✅/⚠️/❌]
- **Branching**: [Status - ✅/⚠️/❌]
- **CI/CD**: [Status - ✅/⚠️/❌]

### 🔗 Quick Links
- [Relevant PRs]
- [Important documentation]
- [Status pages]
- [Previous session issue]
```

## ✅ **Session End Confirmation**

After completing the checklist, provide the user with:

1. **Quick Summary**: What was accomplished
2. **Next Steps**: What to start with tomorrow
3. **Key Links**: Important resources
4. **Confirmation**: Everything is saved and accessible

## 📝 **Notes**

- Always use descriptive commit messages
- Include code examples in session summaries
- Link related issues and PRs
- Update project health status
- Preserve context for future sessions
- Make troubleshooting guides actionable

This protocol ensures no context is lost between sessions and provides a consistent experience for project continuity.
