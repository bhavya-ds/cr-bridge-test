# CodeRabbit-Claude Bridge Workflow Guide

**Your automated code review system is now ready!**

---

## 🎯 Daily Workflow (Fully Automated Mode)

### 1. Make Changes & Say "Commit and Push"

**In Claude Code, just say:**

```
I added a new login feature. Commit and push it.
```

**That's it!** The entire workflow runs automatically:

### 2. Automated Fix Loop

```
┌─────────────────────────────────────────────────────────┐
│ ITERATION 1                                              │
├─────────────────────────────────────────────────────────┤
│ ✅ Claude: git commit + git push                         │
│ 🔧 Git wrapper: Triggers cr-bridge in background         │
│ 🤖 CodeRabbit: Reviews PR (30-90 seconds)                │
│ 📥 cr-bridge: Fetches issues → last-issues.txt           │
│ ⏳ Claude: Waits 2 minutes for CodeRabbit                │
│ 📖 Claude: Reads last-issues.txt                         │
│ ⚠️  Found: 3 CRITICAL issues                             │
│ 🔨 Claude: Fixes all 3 automatically                     │
│ ✅ Claude: git commit -m "Fix CodeRabbit iteration 1"    │
│ 🚀 Claude: git push (loop continues...)                  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ ITERATION 2                                              │
├─────────────────────────────────────────────────────────┤
│ 🔧 Git wrapper: Triggers cr-bridge again                 │
│ 🤖 CodeRabbit: Reviews fixes                             │
│ 📥 cr-bridge: Fetches new issues                         │
│ ⏳ Claude: Waits 60 seconds                              │
│ 📖 Claude: Reads last-issues.txt                         │
│ ⚠️  Found: 1 CRITICAL issue (rowcount validation)        │
│ 🔨 Claude: Fixes it                                      │
│ ✅ Claude: git commit -m "Fix CodeRabbit iteration 2"    │
│ 🚀 Claude: git push (loop continues...)                  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ ITERATION 3                                              │
├─────────────────────────────────────────────────────────┤
│ 🔧 Git wrapper: Triggers cr-bridge again                 │
│ 🤖 CodeRabbit: Reviews fixes                             │
│ 📥 cr-bridge: No issues found                            │
│ ⏳ Claude: Waits 60 seconds                              │
│ 📖 Claude: Reads last-issues.txt                         │
│ ✅ Found: 0 issues                                       │
│ 🎉 SUCCESS: All issues resolved in 2 iterations!         │
└─────────────────────────────────────────────────────────┘
```

### 3. What You See

**During the loop, Claude reports progress:**

```
Iteration 1: Found 3 CRITICAL issues
- SQL injection in transfer endpoint
- Missing input validation
- Non-atomic transaction
Fixing all issues...

✅ Fixed all 3 issues
Committed: "Fix CodeRabbit iteration 1"
Pushed. Waiting for CodeRabbit...

Iteration 2: Found 1 CRITICAL issue
- Missing rowcount validation
Fixing...

✅ Fixed issue
Committed: "Fix CodeRabbit iteration 2"
Pushed. Waiting for CodeRabbit...

Iteration 3: Found 0 issues
🎉 Success! All issues resolved in 2 iterations.
```

### 4. Safety Limits

- **Max 5 iterations** to prevent infinite loops
- **If issues remain after 5 iterations**: Manual review requested
- **No confirmation needed**: CRITICAL/MAJOR issues fixed automatically
- **NEEDS_REVIEW issues**: Claude uses judgment (may ask)

---

## 🔧 Manual Mode (When Needed)

### Run cr-bridge Manually

```bash
# Auto-detect PR from current branch
cr-bridge

# Specific PR number
cr-bridge --pr 123

# Show detailed logs
cr-bridge --verbose

# Use existing comments (don't wait)
cr-bridge --skip-wait
```

### Check What Was Found

```bash
cat ~/.config/cr-bridge/last-issues.txt
```

### Check Background Progress

```bash
tail -f /tmp/cr-bridge-last.log
```

---

## 📊 Understanding the Output

### Issue File Format

````
# Generated: 2026-02-16 10:30:45
# Total Issues: 3

PROMPT: Fix these issues. Do not ask for confirmation on obvious security fixes.

SEVERITY BREAKDOWN:
- CRITICAL: 2 (security vulnerabilities, data leaks, crashes)
- MAJOR: 1 (bugs, errors, incorrect behavior)
- NEEDS_REVIEW: 0 (negation detected, use your judgment)

======================================================================
ISSUE #1 [CRITICAL]
======================================================================
File: src/api/auth.py
Line: 45

SQL injection vulnerability in user authentication. The query uses
string concatenation instead of parameterized queries...

Context:
```diff
- query = f"SELECT * FROM users WHERE email = '{email}'"
+ # Should use parameterized query
````

````

### Severity Levels

**CRITICAL (score ≥ 5):**
- SQL injection, XSS, CSRF
- Authentication bypass
- Remote code execution
- Data leaks
- Memory leaks

**MAJOR (score ≥ 2):**
- Bugs, errors, exceptions
- Incorrect behavior
- Broken functionality

**NEEDS_REVIEW (borderline):**
- Has security keywords BUT negation detected
- Example: "This is NOT a security issue, but..."
- Claude + you decide if it's real

**MINOR (ignored):**
- Style suggestions
- Minor improvements
- Documentation typos

---

## 🚫 Escape Hatches

### Bypass Git Wrapper Temporarily

```bash
# Use this if wrapper has issues
command git push
````

### Stop cr-bridge Background Run

```bash
# If it's stuck or you want to cancel
ps aux | grep cr-bridge
kill <PID>
```

### Remove Stale Lockfile

```bash
# Usually auto-recovers via PID check
# Manual removal if needed:
rm ~/.config/cr-bridge/cr-bridge.lock
```

### Unload Git Wrapper

```bash
# Temporarily disable auto-run
unalias git
# Re-enable
source ~/.bashrc
```

---

## 🎯 Tips for Best Results

### 1. Make CodeRabbit Focus on Security

In your `.coderabbit.yaml`:

```yaml
reviews:
  high_level_summary: true
  poem: false
  review_status: true
  auto_review:
    enabled: true
    drafts: false

  # Focus on security/bugs
  tools:
    shellcheck:
      enabled: true
    ruff:
      enabled: true
    markdownlint:
      enabled: true
```

### 2. Give Claude Clear Context

When asking Claude to fix, be specific:

**Good:**

```
Fix the issues in ~/.config/cr-bridge/last-issues.txt
Focus on the SQL injection first, then the XSS vulnerability.
```

**Even Better:**

```
Fix the issues in ~/.config/cr-bridge/last-issues.txt

For the SQL injection in auth.py:
- Use SQLAlchemy parameterized queries
- Add input validation
- Add unit tests

Do not ask for confirmation on security fixes.
```

### 3. Review Before Pushing

Always review Claude's fixes:

```bash
# See what changed
git diff

# Review specific file
git diff src/api/auth.py

# If satisfied
git commit -am "Fix CodeRabbit issues"
git push
```

---

## 🔍 Troubleshooting

### "No PR found"

```bash
# Check if PR exists for current branch
gh pr view

# Create PR first
gh pr create

# Or specify PR number
cr-bridge --pr 123
```

### "No CodeRabbit comments found"

**Reasons:**

1. CodeRabbit not installed on repo
2. CodeRabbit still reviewing (wait longer)
3. Branch has no changes vs base

**Check:**

```bash
# See if CodeRabbit reviewed
gh pr view --web
# Look for CodeRabbit comments
```

### "GitHub CLI not authenticated"

```bash
gh auth login
# Follow prompts
gh auth status  # Verify
```

### No Desktop Notification

**Linux:** Install notify-send

```bash
sudo apt install libnotify-bin
```

**macOS:** Built-in (osascript)

**Not critical:** You can still check the file manually

---

## 📁 File Locations

```
~/.config/cr-bridge/
├── last-issues.txt     # Latest CodeRabbit issues (read by Claude)
├── cr-bridge.lock      # PID lockfile (prevents concurrent runs)
└── version             # Installed version (2.3.0)

/tmp/cr-bridge-last.log # Background run logs (for debugging)

/usr/local/bin/cr-bridge # The main script
```

---

## ⚡ Quick Reference

```bash
# Normal workflow (automatic)
git push                    # cr-bridge runs in background
# ... wait for notification ...
claude                      # Open Claude Code
# > Fix the issues in ~/.config/cr-bridge/last-issues.txt

# Manual workflow
cr-bridge                   # Run manually
cat ~/.config/cr-bridge/last-issues.txt  # Check what was found
claude                      # Fix with Claude

# Debugging
cr-bridge --verbose         # See detailed logs
tail -f /tmp/cr-bridge-last.log  # Watch background run
command git push            # Bypass wrapper if needed
```

---

## 🎓 Example Session (Fully Automated)

```bash
$ cd ~/my-project
$ git checkout -b fix/sql-injection
$ vim src/api/auth.py  # Make changes

$ claude
Claude Code> I added a new auth endpoint. Commit and push it.

┌─────────────────────────────────────────────────────────┐
│ Claude Code Automated Workflow                           │
└─────────────────────────────────────────────────────────┘

✅ Committed: "Add new auth endpoint"
🚀 Pushed to origin/fix/sql-injection

🔧 Git wrapper triggered cr-bridge in background...
⏳ Waiting 2 minutes for CodeRabbit to review...

─────────────────────────────────────────────────────────
🔄 Iteration 1
─────────────────────────────────────────────────────────

📥 Fetching CodeRabbit issues...
⚠️  Found 2 CRITICAL issues:
    1. SQL injection in auth.py:45
    2. Missing input validation in auth.py:52

🔨 Fixing all issues...
    ✓ Fixed SQL injection (parameterized query)
    ✓ Added input validation

✅ Committed: "Fix CodeRabbit iteration 1"
🚀 Pushed. Waiting 60 seconds for CodeRabbit...

─────────────────────────────────────────────────────────
🔄 Iteration 2
─────────────────────────────────────────────────────────

📥 Fetching CodeRabbit issues...
✅ Found 0 issues

🎉 Success! All issues resolved in 1 iteration.
Your code is clean and ready to merge!

# You did nothing manually - it all happened automatically!
```

## 🎓 Example Session (Manual Control)

If you prefer manual control, you can still use the old workflow:

```bash
$ cd ~/my-project
$ git add . && git commit -m "Add feature"
$ git push

# ... wait for notification or run manually ...

$ cr-bridge --verbose
$ cat ~/.config/cr-bridge/last-issues.txt

$ claude
Claude Code> Fix the issues in ~/.config/cr-bridge/last-issues.txt

# Review and push manually
$ git diff
$ git commit -am "Fix CodeRabbit issues"
$ git push
```

---

**You're all set! Push some code and watch the automation happen.** 🚀
