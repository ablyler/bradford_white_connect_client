#!/usr/bin/env bash
set -euo pipefail

tags="$(git tag --points-at HEAD)"

if [[ -z ${tags} ]]; then
	git describe --always --long --dirty | sed 's/^v//'
else
	printf '%s\n' "${tags}" | sed 's/^v//' | awk '{ print length, $0 }' | sort -n -s | cut -d" " -f2- | tail -n 1
fi
