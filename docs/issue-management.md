# Issue Management Guide

## Overview

TheTally uses GitHub Issues for tracking bugs, feature requests, tasks, and questions. This guide explains how to effectively use our issue management system.

## Issue Types

### 🐛 Bug Reports
Use the **Bug Report** template for:
- Unexpected behavior or errors
- Performance issues
- Security vulnerabilities
- Broken functionality

**Template**: `bug_report.yml`

### ✨ Feature Requests
Use the **Feature Request** template for:
- New functionality ideas
- UI/UX improvements
- API enhancements
- Integration requests

**Template**: `feature_request.yml`

### 📋 Tasks
Use the **Task** template for:
- Specific work items
- Code improvements
- Documentation updates
- Refactoring work
- Testing tasks

**Template**: `task.yml`

### ❓ Questions
Use the **Question** template for:
- How-to questions
- Clarification requests
- Setup help
- Usage guidance

**Template**: `question.yml`

## Labels System

### Priority Labels
- `priority: critical` - Blocking issues that need immediate attention
- `priority: high` - Important issues that should be addressed soon
- `priority: medium` - Normal priority issues
- `priority: low` - Nice-to-have items

### Type Labels
- `bug` - Something isn't working
- `enhancement` - New feature or request
- `task` - Specific work item
- `question` - Question or help request
- `documentation` - Documentation related
- `testing` - Testing related

### Status Labels
- `needs-triage` - New issue, needs review
- `in-progress` - Currently being worked on
- `blocked` - Waiting on external dependency
- `ready-for-review` - Ready for code review
- `duplicate` - Duplicate of another issue
- `wontfix` - Will not be addressed
- `invalid` - Not a valid issue

### Component Labels
- `frontend` - React/TypeScript related
- `backend` - FastAPI/Python related
- `database` - Database related
- `security` - Security related
- `performance` - Performance related
- `ui/ux` - User interface related
- `api` - API related
- `devops` - Infrastructure related

### Effort Labels
- `effort: small` - 1-2 hours
- `effort: medium` - Half day
- `effort: large` - 1-2 days
- `effort: xlarge` - 1+ weeks

## Milestones

### Phase 0: Foundation & DevOps
- [x] Set up GitHub repository with backend (FastAPI) and frontend (React) folder structure
- [x] Create basic "Hello World" endpoints and UI pages
- [ ] [Create service layer architecture](https://github.com/otherjamesbrown/TheTally/issues/1) - Implement services/, models/, and utils/ directories
- [ ] [Implement user registration and login API](https://github.com/otherjamesbrown/TheTally/issues/2) - JWTs and 2FA support
- [ ] [Set up PostgreSQL database on GCP](https://github.com/otherjamesbrown/TheTally/issues/4) - Database infrastructure
- [ ] [Dockerize frontend and backend applications](https://github.com/otherjamesbrown/TheTally/issues/5) - Containerization
- [ ] [Create GitHub Actions CI/CD pipeline](https://github.com/otherjamesbrown/TheTally/issues/6) - Automated deployment
- [ ] [Implement E2E tests for login flow](https://github.com/otherjamesbrown/TheTally/issues/7) - Quality assurance

### Phase 1: Core Functionality (MVP)
- [ ] [Create database models for accounts and transactions](https://github.com/otherjamesbrown/TheTally/issues/3) - Data models
- [ ] [Implement core service layer](https://github.com/otherjamesbrown/TheTally/issues/8) - Business logic services
- [ ] [Build file import component for CSV, OFX, and QIF files](https://github.com/otherjamesbrown/TheTally/issues/9) - Data import
- [ ] [Implement backend file parsing logic](https://github.com/otherjamesbrown/TheTally/issues/10) - File processing
- [ ] [Develop rules-based categorization engine](https://github.com/otherjamesbrown/TheTally/issues/11) - Auto-categorization
- [ ] [Create UI for managing categorization rules](https://github.com/otherjamesbrown/TheTally/issues/12) - Rule management
- [ ] [Build transaction table view in the UI](https://github.com/otherjamesbrown/TheTally/issues/13) - Data visualization

### Phase 2: Financial Modelling & Visualization
- [ ] [Create database models for investment pots](https://github.com/otherjamesbrown/TheTally/issues/14) - Investment tracking (Pensions, ISAs)
- [ ] [Build retirement projection calculator](https://github.com/otherjamesbrown/TheTally/issues/15) - Financial modeling
- [ ] Use Recharts to display the projection as a line graph
- [ ] [Create dashboard with spending visualization](https://github.com/otherjamesbrown/TheTally/issues/16) - Data visualization

### Phase 3 & Beyond: Future Enhancements
- [ ] Implement transaction splitting
- [ ] Integrate with an Open Banking API
- [ ] Evolve the categorization engine using ML
- [ ] Add budgeting features and goal setting

## Project Boards

### 🚀 Sprint Board
Track current sprint work with columns:
- **Backlog** - Ready to work on
- **In Progress** - Currently being worked on
- **Review** - Ready for code review
- **Testing** - In testing phase
- **Done** - Completed

### 🎯 Roadmap Board
Track long-term planning with columns:
- **Ideas** - Future possibilities
- **Planned** - Scheduled for future sprints
- **In Progress** - Currently in development
- **Completed** - Delivered

### 🐛 Bug Triage Board
Manage bug reports with columns:
- **New** - Just reported
- **Needs Info** - Waiting for more information
- **Confirmed** - Reproduced and confirmed
- **In Progress** - Being fixed
- **Fixed** - Ready for testing
- **Closed** - Resolved

## Workflow

### 1. Creating Issues
1. Choose the appropriate template
2. Fill out all required fields
3. Add relevant labels
4. Assign to appropriate milestone
5. Set priority and effort estimates

### 2. Triage Process
1. **New issues** are labeled `needs-triage`
2. Review and add appropriate labels
3. Assign priority and effort
4. Move to appropriate project board
5. Assign to team member if needed

### 3. Development Process
1. Move issue to "In Progress" when starting work
2. Create a branch named `issue-{number}-{description}`
3. Reference issue in commit messages: `Fixes #123`
4. Move to "Review" when PR is ready
5. Move to "Done" when merged and deployed

### 4. Closing Issues
- Use keywords in PR descriptions: `Fixes #123`, `Closes #123`, `Resolves #123`
- Add resolution comment explaining the fix
- Update labels and remove from active boards

## Best Practices

### For Issue Creators
- **Be specific** - Provide clear, detailed descriptions
- **Include context** - Explain the problem and desired outcome
- **Add labels** - Help with categorization and triage
- **Check duplicates** - Search existing issues first
- **Provide examples** - Include code snippets, screenshots, or steps

### For Issue Responders
- **Acknowledge quickly** - Respond within 24 hours
- **Ask clarifying questions** - Get the information you need
- **Update labels** - Keep categorization current
- **Set expectations** - Provide timeline estimates
- **Close when done** - Don't leave issues hanging

### For Maintainers
- **Regular triage** - Review new issues weekly
- **Update milestones** - Keep roadmap current
- **Monitor boards** - Ensure smooth workflow
- **Communicate changes** - Update issue status regularly

## Automation

### Auto-labeling
- Issues are automatically labeled based on templates
- PRs are automatically labeled based on changed files
- Milestones are automatically suggested based on content

### Notifications
- @mentions notify specific users
- Label changes trigger notifications
- Milestone updates send alerts
- Project board moves create activity

## Getting Help

- **Documentation**: Check the `/docs` folder first
- **Discussions**: Use GitHub Discussions for general questions
- **Security**: Use private security advisories for vulnerabilities
- **Contributing**: See `CONTRIBUTING.md` for development guidelines

---

**Remember**: Good issue management leads to better software and happier users! 🎯
