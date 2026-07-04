#!/usr/bin/env bash

# Directories to search
DIRS=("/home/nguyenduchoang/Documents/code" "/Volumes/data/code/")

echo "Starting git sync across specified directories..."

for DIR in "${DIRS[@]}"; do
    if [ ! -d "$DIR" ]; then
        echo "Directory $DIR does not exist, skipping."
        continue
    fi

    echo "Scanning $DIR for git repositories..."
    
    # Find all .git directories
    while IFS= read -r gitdir; do
        repo_dir=$(dirname "$gitdir")
        echo "----------------------------------------"
        echo "Syncing repository: $repo_dir"
        
        cd "$repo_dir" || continue
        
        # Check if there are uncommitted changes
        if ! git diff-index --quiet HEAD --; then
            echo "⚠️  Uncommitted changes detected in $repo_dir. Skipping auto-sync to prevent data loss."
            continue
        fi

        # Check if there are untracked files
        if [ -n "$(git status --porcelain)" ]; then
             echo "⚠️  Working tree is not clean in $repo_dir. Skipping auto-sync."
             continue
        fi
        
        # Pull latest changes (rebase to avoid merge commits if possible)
        echo "⬇️  Pulling latest changes..."
        if git pull --rebase; then
            echo "✅  Pull successful."
        else
            echo "❌  Pull failed. You may have conflicts."
            # Abort rebase if it failed
            git rebase --abort 2>/dev/null
            continue
        fi
        
        # Push changes
        echo "⬆️  Pushing changes..."
        if git push; then
            echo "✅  Push successful."
        else
            echo "❌  Push failed."
        fi
        
    done < <(find "$DIR" -name ".git" -type d -prune)
done

echo "----------------------------------------"
echo "Git sync complete."
