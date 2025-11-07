---
name: Bug Report
about: Report a bug or issue with the scripts
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug Description
<!-- A clear and concise description of what the bug is -->

## Environment
- **Script Version**: <!-- e.g., v1.1.0, aws_infoblox_vpc_manager_complete_v1.py -->
- **Python Version**: <!-- e.g., Python 3.11.5 -->
- **Operating System**: <!-- e.g., macOS 14.1, Ubuntu 22.04, Windows 11 -->
- **InfoBlox Version**: <!-- e.g., WAPI 2.10 -->

## Steps to Reproduce
<!-- Provide detailed steps to reproduce the behavior -->
1.
2.
3.

## Expected Behavior
<!-- What you expected to happen -->

## Actual Behavior
<!-- What actually happened -->

## Error Messages
<!-- If applicable, paste error messages or logs -->
```
Paste error messages here
```

## Configuration
<!-- Redact sensitive information! -->
```env
GRID_MASTER=example.com
NETWORK_VIEW=default
CSV_FILE=vpc_data.csv
```

## Command Used
<!-- The exact command you ran -->
```bash
python aws_infoblox_vpc_manager_complete_v1.py -q --dry-run
```

## Log Output
<!-- Relevant portions of the log file -->
```
Paste relevant log output here
```

## Screenshots
<!-- If applicable, add screenshots to help explain the problem -->

## Additional Context
<!-- Add any other context about the problem here -->

## Checklist
- [ ] I have checked the [QUICKSTART.md](../QUICKSTART.md) troubleshooting section
- [ ] I have verified my configuration is correct
- [ ] I have tried with `--dry-run` mode
- [ ] I have checked the log file for additional details
- [ ] This bug is reproducible

## Possible Solution
<!-- Optional: If you have ideas on how to fix this -->
