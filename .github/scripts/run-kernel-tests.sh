#!/bin/bash
# Run the in-tree kernel tests that cover files changed in this pull request.
set -eu

files="$(git diff --name-only "$BASE_SHA" HEAD)"
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

if has '^(lib/(radix-tree|xarray|maple_tree|idr|test_xarray|test_ida)\.c|include/linux/(xarray|maple_tree|radix-tree|idr)\.h|tools/testing/radix-tree/)'; then
	ran=1
	run_dir tools/testing/radix-tree main xarray maple idr-test multiorder
fi

if has '^(lib/(rbtree|interval_tree)\.c|include/linux/(rbtree|rbtree_types|rbtree_augmented|interval_tree)\.h|tools/testing/rbtree/)'; then
	ran=1
	run_dir tools/testing/rbtree rbtree_test interval_tree_test
fi

if has '^(mm/vma.*|tools/testing/vma/)'; then
	ran=1
	run_dir tools/testing/vma vma
fi

if has '^(mm/memblock\.c|include/linux/memblock\.h|tools/testing/memblock/)'; then
	ran=1
	run_dir tools/testing/memblock main
fi

if [ "$ran" -eq 0 ]; then
	echo "No relevant kernel test applies to this diff."
fi
