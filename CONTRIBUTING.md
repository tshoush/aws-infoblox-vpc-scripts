# Contributing to AWS InfoBlox VPC Scripts

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Documentation](#documentation)
- [Issue Guidelines](#issue-guidelines)
- [Pull Request Guidelines](#pull-request-guidelines)

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment, discrimination, or derogatory comments
- Trolling, insulting, or inappropriate behavior
- Publishing others' private information
- Any conduct inappropriate in a professional setting

## How Can I Contribute?

### Reporting Bugs

1. **Check existing issues** - Search to see if the bug has already been reported
2. **Use the bug report template** - Fill out all sections
3. **Provide details**:
   - Script version
   - Python version
   - Operating system
   - Steps to reproduce
   - Error messages
   - Log output

**Create bug report**: [New Bug Report](https://github.com/tshoush/aws-infoblox-vpc-scripts/issues/new?template=bug_report.md)

### Suggesting Features

1. **Check existing feature requests** - See if it's already been suggested
2. **Use the feature request template** - Explain the use case
3. **Provide examples** - Show how it would be used

**Create feature request**: [New Feature Request](https://github.com/tshoush/aws-infoblox-vpc-scripts/issues/new?template=feature_request.md)

### Improving Documentation

Documentation improvements are always welcome!

- Fix typos or errors
- Clarify confusing sections
- Add examples
- Improve explanations
- Update outdated information

**Report documentation issue**: [New Documentation Issue](https://github.com/tshoush/aws-infoblox-vpc-scripts/issues/new?template=documentation.md)

### Writing Code

We welcome code contributions! See the sections below for guidelines.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv)
- Access to InfoBlox for testing (optional)

### Setting Up Your Development Environment

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/aws-infoblox-vpc-scripts.git
cd aws-infoblox-vpc-scripts

# 3. Add upstream remote
git remote add upstream https://github.com/tshoush/aws-infoblox-vpc-scripts.git

# 4. Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install dependencies
pip install -r setup/requirements_v1.txt

# 6. Create a branch for your work
git checkout -b feature/my-new-feature
```

## Making Changes

### Code Style

- Follow PEP 8 style guidelines
- Use meaningful variable names
- Add comments for complex logic
- Keep functions focused and small
- Use type hints where appropriate

**Example:**
```python
def parse_vpc_data(csv_file: str) -> pd.DataFrame:
    """
    Parse VPC data from CSV file.

    Args:
        csv_file: Path to CSV file containing VPC data

    Returns:
        DataFrame with parsed VPC data

    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV format is invalid
    """
    # Implementation
```

### Testing

Always test your changes:

```bash
# Test with dry-run
python aws_infoblox_vpc_manager_complete_v1.py --dry-run

# Test different scenarios
python script.py --csv-file test_data.csv --dry-run

# Check for errors in logs
grep -i error *.log
```

### Updating Documentation

When making changes:

1. **Update README.md** if adding new features
2. **Update CHANGELOG.md** with your changes
3. **Update QUICKSTART.md** if changing setup/usage
4. **Update ARCHITECTURE.md** if changing system design
5. **Add code comments** for clarity

### Commit Messages

Write clear, descriptive commit messages:

**Good:**
```
Add network overlap detection to v1 script

- Implemented CIDR overlap checking
- Added automatic container creation
- Updated tests for new functionality
- Fixed bug in network comparison logic

Fixes #42
```

**Bad:**
```
fixed stuff
```

**Format:**
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

## Submitting Changes

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### Creating a Pull Request

1. **Push your branch**:
   ```bash
   git push origin feature/my-new-feature
   ```

2. **Create PR on GitHub**:
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Select your feature branch
   - Fill out the PR template

3. **PR Description Should Include**:
   - What changes were made
   - Why the changes were made
   - How to test the changes
   - Related issues (if any)
   - Screenshots (if UI changes)

**Example PR Description:**
```markdown
## Description
Added network overlap detection feature to v1 script.

## Changes
- Implemented CIDR overlap checking logic
- Added automatic container creation for overlaps
- Updated documentation
- Added example usage

## Testing
- Tested with sample VPC data
- Verified overlap detection works correctly
- Confirmed containers are created properly
- Dry-run mode tested

## Related Issues
Fixes #42
Relates to #38

## Screenshots
[Add if applicable]
```

### Pull Request Review Process

1. **Automated checks** will run on your PR
2. **Maintainers will review** your code
3. **Address feedback** by making additional commits
4. **Once approved**, maintainers will merge your PR

## Documentation

### Documentation Standards

- Use clear, simple language
- Include examples
- Add code snippets where helpful
- Keep formatting consistent
- Test all commands/examples

### Updating CHANGELOG

When making changes, update `CHANGELOG.md`:

```markdown
## [Unreleased]

### Added
- Network overlap detection feature (#42)

### Fixed
- Bug in CSV parsing for special characters (#45)
```

### Creating Release Notes

For major changes, update `CONFLUENCE_RELEASE_NOTES.md`:

```markdown
## Version X.Y.Z - Feature Name

**Release Date**: YYYY-MM-DD

### Summary
Brief description of changes

### Detailed Changes
- Change 1
- Change 2

### Jira/Confluence Section
[Copy-paste ready content for tickets]
```

## Issue Guidelines

### Good Issue Characteristics

- **Clear title** - Descriptive and specific
- **Complete information** - All template sections filled
- **Reproducible** - Steps to reproduce provided
- **Relevant details** - Versions, OS, logs included
- **One issue per report** - Don't combine multiple issues

### Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `question` - Further information requested
- `wontfix` - This will not be worked on
- `duplicate` - This issue already exists

## Pull Request Guidelines

### PR Checklist

Before submitting your PR:

- [ ] Branch is up to date with main
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Commit messages are descriptive
- [ ] PR description is complete

### PR Review Process

1. **Submission** - You submit the PR
2. **Automated Checks** - CI/CD runs tests
3. **Code Review** - Maintainer reviews code
4. **Feedback** - You address any comments
5. **Approval** - Maintainer approves
6. **Merge** - Maintainer merges PR

### After Your PR is Merged

- Delete your feature branch (if desired)
- Update your local repository:
  ```bash
  git checkout main
  git pull upstream main
  ```
- Celebrate! 🎉

## Development Workflow

### Typical Workflow

```bash
# 1. Sync with upstream
git checkout main
git pull upstream main

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Make changes
# ... edit files ...

# 4. Test changes
python script.py --dry-run

# 5. Commit changes
git add .
git commit -m "feat: add new feature"

# 6. Push to your fork
git push origin feature/my-feature

# 7. Create PR on GitHub

# 8. Address review feedback
# ... make more commits ...
git push origin feature/my-feature

# 9. After merge, clean up
git checkout main
git branch -d feature/my-feature
```

## Questions?

If you have questions:

1. Check [QUICKSTART.md](./QUICKSTART.md) for common issues
2. Check [existing issues](https://github.com/tshoush/aws-infoblox-vpc-scripts/issues)
3. Check [ARCHITECTURE.md](./ARCHITECTURE.md) for technical details
4. Open a new issue with your question

## Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort! 🙏

---

**Additional Resources:**
- [Quick Start Guide](./QUICKSTART.md)
- [Architecture Documentation](./ARCHITECTURE.md)
- [Scripts Comparison](./SCRIPTS_COMPARISON.md)
- [Changelog](./CHANGELOG.md)
- [Release Notes](./CONFLUENCE_RELEASE_NOTES.md)
