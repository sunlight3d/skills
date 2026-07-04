---
name: push_all_my_repos
description: Synchronize (pull and push) all Git repositories found in specific local directories (/home/nguyenduchoang/Documents/code and /Volumes/data/code/). Trigger this skill when the user asks to "sync git", "update my repos", "push all my code", or "sync my code directories".
---

# Git Sync All Skill

This skill automates the process of finding and synchronizing all Git repositories within the user's main code directories.

## Core Workflow

1. A bash script has been provided at `scripts/sync_repos.sh`.
2. When the user requests to sync their repositories, you must run this script using the `run_command` tool.
3. The script will output a detailed log of which repositories were updated, skipped (due to uncommitted changes), or failed.
4. After the script finishes, read the output and provide the user with a concise summary of the results.

## Execution

Run the script directly via bash:
`bash /Users/hoangnd/.gemini/config/skills/push_all_my_repos/scripts/sync_repos.sh`

Do not prompt the user for additional directories unless they explicitly ask to modify the script. The default directories are hardcoded for convenience.
