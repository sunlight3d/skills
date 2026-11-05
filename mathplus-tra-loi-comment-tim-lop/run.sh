#!/bin/bash
# MathPlus Trả Lời Comment Tìm Lớp - Runner Script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if command -v uv &> /dev/null; then
    uv run --with playwright python "$DIR/scripts/commenter.py" "$@"
else
    python3 "$DIR/scripts/commenter.py" "$@"
fi
