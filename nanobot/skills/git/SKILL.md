---
name: git
description: Perform Git version control operations including commits, branches, merging, rebasing, history inspection, and repository management. Use for all Git workflows and repository maintenance.
metadata: {"nanobot":{"emoji":"📦","requires":{"bins":["git"]}}}
---

# Git Skill

Use `git` CLI for version control operations. Prefer standard Git commands; avoid aliases in scripts.

## Quick Reference

| Task | Command |
|------|---------|
| Check status | `git status` |
| Stage changes | `git add <file>` or `git add .` |
| Commit | `git commit -m "message"` |
| Push | `git push origin <branch>` |
| Pull | `git pull origin <branch>` |
| Switch branch | `git switch <branch>` or `git checkout <branch>` |
| Create branch | `git switch -c <branch>` |
| View log | `git log --oneline -10` |

## Basic Workflow

```bash
# Check current state
git status

# Stage and commit
git add .
git commit -m "feat: add user authentication"

# Push to remote
git push origin main

# Pull latest changes
git pull origin main
```

## Branching

```bash
# List branches
git branch              # local
git branch -r           # remote
git branch -a           # all

# Create and switch
git switch -c feature/login
git checkout -b feature/login  # older syntax

# Switch to existing
git switch main
git checkout main

# Rename branch
git branch -m old-name new-name

# Delete branch
git branch -d feature/login     # merged only
git branch -D feature/login     # force delete
```

## History & Inspection

```bash
# View commit history
git log --oneline -20
git log --graph --oneline --all -20
git log --since="1 week ago" --author="name"

# Show specific commit
git show abc123
git show --stat abc123

# View file history
git log -p --follow -- filename
git blame filename

# Diff changes
git diff                    # unstaged
git diff --staged           # staged
git diff HEAD~1             # last commit
```

## Undoing Changes

```bash
# Unstage files
git restore --staged <file>
git reset HEAD <file>       # older syntax

# Discard local changes
git restore <file>
git checkout -- <file>      # older syntax

# Amend last commit
git commit --amend -m "new message"
git commit --amend --no-edit  # keep message, add changes

# Reset to previous state
git reset --soft HEAD~1     # undo commit, keep changes staged
git reset --mixed HEAD~1    # undo commit, keep changes unstaged
git reset --hard HEAD~1     # discard commit and changes
```

## Merging & Rebasing

```bash
# Merge branch into current
git switch main
git merge feature/login

# Rebase current onto another
git switch feature/login
git rebase main

# Continue after resolving conflicts
git rebase --continue
git merge --continue

# Abort merge/rebase
git merge --abort
git rebase --abort
```

## Stashing

```bash
# Save changes temporarily
git stash push -m "work in progress"
git stash

# List stashes
git stash list

# Apply stash
git stash pop               # apply and remove
git stash apply             # apply but keep

# Apply specific stash
git stash apply stash@{1}

# Drop stash
git stash drop stash@{0}
```

## Remote Operations

```bash
# View remotes
git remote -v

# Add remote
git remote add origin https://github.com/user/repo.git

# Fetch from remote
git fetch origin
git fetch --all

# Push
git push origin main
git push -u origin feature  # set upstream

# Pull with rebase
git pull --rebase origin main

# Delete remote branch
git push origin --delete feature/login
```

## Tags

```bash
# List tags
git tag

# Create tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push tags
git push origin v1.0.0
git push origin --tags

# Delete tag
git tag -d v1.0.0
git push origin --delete v1.0.0
```

## Tips

- Use `git status` frequently to check state
- Write clear commit messages: `type: description`
- Commit types: feat, fix, docs, style, refactor, test, chore
- Pull before pushing to avoid conflicts
- Use `--dry-run` to preview destructive operations
