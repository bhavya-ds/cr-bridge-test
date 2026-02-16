# CR-Bridge Test Repository

Test repository for demonstrating automated CodeRabbit review + Claude Code fix loop.

## How It Works

1. Push code with vulnerabilities
2. CodeRabbit reviews and finds issues
3. cr-bridge fetches critical issues
4. Claude Code automatically fixes all issues
5. Loop continues until code is clean

**See WORKFLOW.md for complete documentation.**

## Installation

```bash
pip install flask
```

## Test the Automated Loop

In Claude Code, just say:

```
I added a new feature. Commit and push it.
```

Claude will automatically:

- Commit and push
- Wait for CodeRabbit
- Fetch issues via cr-bridge
- Fix all issues
- Loop until clean (max 5 iterations)
