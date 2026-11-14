#!/bin/bash
# Run the in-tree kernel tests that cover files changed in this pull request.
# `--plan` only prints applicable=true or applicable=false.
# Set FILES_PATH to a newline-separated list to skip `git diff`.
set -eu

plan=0
if [ "${1:-}" = "--plan" ]; then
	plan=1
fi

if [ -n "${FILES_PATH:-}" ]; then
	files="$(cat "$FILES_PATH")"
else
	files="$(git diff --name-only "$BASE_SHA" HEAD)"
fi
ran=0

has() {
	printf '%s\n' "$files" | grep -Eq "$1"
}

run_dir() {
	local dir="$1"
	shift
	make -C "$dir" -j"$(nproc)"
	local bin
	for bin in "$@"; do
		( cd "$dir" && "./$bin" )
	done
}

consider() {
	local regex="$1"
	shift
	if has "$regex"; then
		ran=1
		if [ "$plan" -eq 0 ]; then
			run_dir "$@"
		fi
	fi
}

consider '^(lib/(radix-tree|xarray|maple_tree|idr|test_xarray|test_ida)\.c|include/linux/(xarray|maple_tree|radix-tree|idr)\.h|tools/testing/radix-tree/)' \
	tools/testing/radix-tree main xarray maple idr-test multiorder
consider '^(lib/(rbtree|interval_tree)\.c|include/linux/(rbtree|rbtree_types|rbtree_augmented|interval_tree)\.h|tools/testing/rbtree/)' \
	tools/testing/rbtree rbtree_test interval_tree_test
consider '^(mm/vma.*|tools/testing/vma/)' \
	tools/testing/vma vma
consider '^(mm/memblock\.c|include/linux/memblock\.h|tools/testing/memblock/)' \
	tools/testing/memblock main

if [ "$plan" -eq 1 ]; then
	if [ "$ran" -eq 1 ]; then
		echo "applicable=true"
	else
		echo "applicable=false"
	fi
	exit 0
fi

if [ "$ran" -eq 0 ]; then
	echo "No relevant kernel test applies to this diff."
fi
