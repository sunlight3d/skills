---
name: pull_all_my_repos
description: Synchronize (pull only) all Git repositories found in specific local directories (/home/nguyenduchoang/Documents/code and /Volumes/data/code/). Trigger this skill when the user asks to "pull all my code", "pull my repos", or "sync my code directories" focusing on pulling.
---

# Git Pull All Skill

This skill automates the process of finding and pulling all Git repositories within the user's main code directories.

## Core Workflow

1. A bash script has been provided at `scripts/pull_repos.sh`.
2. When the user requests to pull their repositories, you must run this script using the `run_command` tool.
3. The script will output a detailed log of which repositories were updated, skipped, or failed.
4. After the script finishes, read the output and provide the user with a concise summary of the results.

## Execution

Run the script directly via bash:
`bash /Volumes/data/code/skills/pull_all_my_repos/scripts/pull_repos.sh`

Do not prompt the user for additional directories unless they explicitly ask to modify the script. The default directories are hardcoded for convenience.
