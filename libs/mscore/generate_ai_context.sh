{
    echo "========== DIRECTORY TREE =========="
    cmd //c "tree /A /F mscore\\auth"

    echo
    echo "========== PYTHON FILE CONTENTS =========="

    find mscore/auth -type f -name '*.py' -print0 |
    while IFS= read -r -d '' file; do
        printf '\n\n========== %s ==========\n' "$file"
        cat "$file"
    done
} > auth_context.txt
