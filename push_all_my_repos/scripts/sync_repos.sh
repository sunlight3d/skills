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
        
        # Convert HTTPS GitHub remote URL to SSH to allow passwordless push
        origin_url=$(git remote get-url origin 2>/dev/null || true)
        if [[ "$origin_url" =~ ^https://(www\.)?github\.com/ ]]; then
            ssh_url=$(echo "$origin_url" | sed 's|^https://github.com/|git@github.com:|; s|^https://www.github.com/|git@github.com:|')
            echo "🔄 Converting remote URL from HTTPS to SSH: $origin_url -> $ssh_url"
            git remote set-url origin "$ssh_url"
        fi
        
        # Check if there are changes (uncommitted or untracked)
        if [ -n "$(git status --porcelain)" ]; then
            echo "⚠️  Uncommitted changes/untracked files detected in $repo_dir. Auto-committing..."
            git add -A
            git commit -m "auto-sync: auto commit changes on $(date '+%Y-%m-%d %H:%M:%S')"
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
