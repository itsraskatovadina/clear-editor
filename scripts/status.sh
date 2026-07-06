#!/usr/bin/env bash
# Быстрый просмотр/редактирование статуса сессии
# Использование:
#   ./scripts/status.sh        — показать статус
#   ./scripts/status.sh edit   — открыть для редактирования (nano)

STATUS_FILE="docs/session_status.md"

case "${1:-}" in
    edit)
        ${EDITOR:-nano} "$STATUS_FILE"
        ;;
    *)
        cat "$STATUS_FILE"
        ;;
esac
