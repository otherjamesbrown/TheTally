# GitHub Project Boards Setup

## Overview

This document outlines the recommended GitHub Project Boards for managing TheTally development workflow.

## Board 1: 🚀 Sprint Board

**Purpose**: Track current sprint work and development progress

### Columns:
1. **Backlog** - Issues ready to be worked on
2. **In Progress** - Currently being worked on
3. **Review** - Ready for code review
4. **Testing** - In testing phase
5. **Done** - Completed and merged

### Automation:
- Move to "In Progress" when issue is assigned
- Move to "Review" when PR is created
- Move to "Done" when PR is merged

## Board 2: 🎯 Roadmap Board

**Purpose**: Long-term planning and feature roadmap

### Columns:
1. **Ideas** - Future possibilities and suggestions
2. **Planned** - Scheduled for future sprints
3. **In Progress** - Currently in development
4. **Completed** - Delivered to users

### Automation:
- Move to "Planned" when milestone is assigned
- Move to "In Progress" when work begins
- Move to "Completed" when milestone is closed

## Board 3: 🐛 Bug Triage Board

**Purpose**: Manage bug reports and issues

### Columns:
1. **New** - Just reported, needs triage
2. **Needs Info** - Waiting for more information
3. **Confirmed** - Reproduced and confirmed
4. **In Progress** - Being fixed
5. **Fixed** - Ready for testing
6. **Closed** - Resolved

### Automation:
- New bugs start in "New" column
- Move to "Needs Info" if more details required
- Move to "Confirmed" when reproduced
- Move to "In Progress" when assigned
- Move to "Fixed" when PR is ready
- Move to "Closed" when resolved

## Board 4: 🔒 Security Board

**Purpose**: Track security-related issues and improvements

### Columns:
1. **Reported** - Security issues reported
2. **Investigating** - Under investigation
3. **Fixing** - Being addressed
4. **Testing** - Security testing
5. **Resolved** - Fixed and verified

## Board 5: 📚 Documentation Board

**Purpose**: Track documentation tasks and improvements

### Columns:
1. **Needed** - Documentation gaps identified
2. **In Progress** - Being written
3. **Review** - Ready for review
4. **Published** - Live and accessible

## Setup Instructions

### 1. Create Project Boards

1. Go to your repository on GitHub
2. Click on "Projects" tab
3. Click "New project"
4. Choose "Board" template
5. Name the board (e.g., "Sprint Board")
6. Add the columns listed above
7. Repeat for each board

### 2. Configure Automation

1. Go to board settings
2. Click "Automation"
3. Set up rules for each column:
   - **When issue is assigned** → Move to "In Progress"
   - **When PR is created** → Move to "Review"
   - **When PR is merged** → Move to "Done"

### 3. Add Issues to Boards

1. Go to each issue
2. Click "Projects" on the right sidebar
3. Select appropriate board
4. Move to appropriate column

### 4. Set Up Filters

Create saved filters for common views:
- **My Issues**: `assignee:@me`
- **High Priority**: `label:priority:high OR label:priority:critical`
- **Bugs**: `label:bug`
- **Frontend**: `label:frontend`
- **Backend**: `label:backend`

## Best Practices

### For Project Managers
- **Regular Reviews**: Review boards weekly
- **Update Status**: Keep issue status current
- **Clear Priorities**: Ensure team knows what to work on
- **Capacity Planning**: Don't overload "In Progress"

### For Developers
- **Update Status**: Move issues as you work on them
- **Clear Communication**: Comment on issues with updates
- **Ask Questions**: Use issues for technical discussions
- **Link PRs**: Reference issues in pull requests

### For Contributors
- **Check Boards**: See what work is available
- **Pick Up Issues**: Look for "good first issue" labels
- **Ask Questions**: Use issues to ask for help
- **Provide Updates**: Keep maintainers informed

## Integration with Milestones

- **Phase 0**: Foundation & DevOps
- **Phase 1**: Core Functionality (MVP)
- **Phase 2**: Financial Modelling & Visualization
- **Phase 3**: Future Enhancements

Each milestone should have issues assigned and tracked on the appropriate boards.

## Metrics and Reporting

### Sprint Metrics
- **Velocity**: Issues completed per sprint
- **Cycle Time**: Time from start to completion
- **Lead Time**: Time from creation to completion
- **Burndown**: Progress toward sprint goals

### Quality Metrics
- **Bug Rate**: Bugs per feature
- **Rework**: Issues that need to be reopened
- **Test Coverage**: Percentage of code tested
- **Documentation**: Percentage of features documented

## Tools and Integrations

### GitHub CLI
```bash
# List issues
gh issue list --state open

# Create issue
gh issue create --title "Bug: Login not working" --body "Description"

# Close issue
gh issue close 123
```

### GitHub API
```bash
# Get issues for a milestone
curl -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/owner/repo/issues?milestone=1"

# Update issue labels
curl -X PATCH -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/owner/repo/issues/123" \
  -d '{"labels":["bug","priority:high"]}'
```

---

**Remember**: Good project management leads to successful software delivery! 🎯
