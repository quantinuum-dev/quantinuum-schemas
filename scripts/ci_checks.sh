#!/usr/bin/env bash
    
set -Eeuo pipefail
set -o xtrace
DIR=$(dirname "$(realpath "$0")")
SRC_DIR="${DIR}/../quantinuum_schemas"

uv run pyright "${SRC_DIR}" "${DIR}/../tests"
uv run mypy "${SRC_DIR}" "${DIR}/../tests" --namespace-packages
uv run pylint "${SRC_DIR}" "${DIR}/../tests" --rcfile="${DIR}/../pylintrc"

RUFF_FORMAT_ARGS=()
RUFF_CHECK_ARGS=()
if [[ "${CI:-}" == "true" ]]; then
    RUFF_FORMAT_ARGS+=(--check)
else
    RUFF_CHECK_ARGS+=(--fix)
fi

uv run ruff format "${RUFF_FORMAT_ARGS[@]}" "${SRC_DIR}" "${DIR}/../tests"
uv run ruff check "${RUFF_CHECK_ARGS[@]}" "${SRC_DIR}" "${DIR}/../tests"

grep "print(" "${SRC_DIR}" --include="*.py" --recursive --files-with-matches && (echo "Found print statement"; exit 1)

echo "Done"