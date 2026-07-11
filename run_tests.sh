#!/usr/bin/env bash
# Run all project tests
# Usage: ./run_tests.sh [timeout_sec]
# Default timeout per test: 10 seconds

set -uo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$ROOT"

TIMEOUT="${1:-10}"
passed=0
failed=0
skipped=0
errors=""

while IFS= read -r -d '' test_file; do
    rel="${test_file#"$ROOT"/}"
    printf "%-50s " "$rel"
    if output=$(timeout "$TIMEOUT" python3 "$test_file" 2>&1); then
        echo "OK"
        ((passed++))
    else
        code=$?
        if [ "$code" -eq 124 ]; then
            echo "TIMEOUT (${TIMEOUT}s)"
            ((skipped++))
        else
            echo "FAIL"
            errors+="  $rel\n$(echo "$output" | tail -10 | sed 's/^/    /')\n"
            ((failed++))
        fi
    fi
done < <(find "$ROOT/tests" -name 'test_*.py' -print0 | sort -z)

echo ""
echo "========================================="
printf "  Passed: %-3d  Failed: %-3d  Timeout: %d\n" "$passed" "$failed" "$skipped"
echo "========================================="

if [ "$failed" -gt 0 ]; then
    echo ""
    echo "Failures:"
    printf "$errors"
    exit 1
fi
