#!/usr/bin/env bash
# Build the package and refresh the pacman repository in repo/x86_64.
#
#   ./make-repo.sh              unsigned database (SigLevel = Optional TrustAll)
#   ./make-repo.sh --sign       sign the database with the default GPG key
#   ./make-repo.sh --key KEY    sign the database with KEY
#
# Serve repo/ over HTTPS (or plain HTTP on a trusted network such as
# Tailscale) and point pacman at https://<host>/x86_64.
set -euo pipefail
shopt -s nullglob

here="$(cd -- "$(dirname -- "$0")" && pwd)"
repo="$here/repo/x86_64"
db="$repo/omarchy-gdrive.db.tar.gz"

sign=false
key=""
while (( $# > 0 )); do
  case "$1" in
    --sign) sign=true ;;
    --key) key="${2:-}"; [[ -n "$key" ]] || { printf 'error: --key needs a key id\n' >&2; exit 2; }; shift ;;
    -h|--help) sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) printf 'error: unknown argument: %s\n' "$1" >&2; exit 2 ;;
  esac
  shift
done

pkgname="$(sed -n 's/^pkgname=//p' "$here/PKGBUILD")"
pkgver="$(sed -n 's/^pkgver=//p' "$here/PKGBUILD")"
pkgrel="$(sed -n 's/^pkgrel=//p' "$here/PKGBUILD")"
packager="${PACKAGER:-$(git -C "$here" log -1 --format=%an 2>/dev/null || true)}"

( cd "$here" && PACKAGER="${packager:-Unknown}" makepkg -f --nodeps )

mkdir -p "$repo"
cp -f "$here/$pkgname-$pkgver-$pkgrel"-*.pkg.tar.zst "$repo/"
find "$repo" -maxdepth 1 -name "$pkgname-*.pkg.tar.zst" \
  ! -name "$pkgname-$pkgver-$pkgrel-*.pkg.tar.zst" -delete

args=(--remove)
if [[ "$sign" == true ]]; then
  args+=(--sign)
fi
if [[ -n "$key" ]]; then
  args+=(--key "$key")
fi

packages=("$repo"/*.pkg.tar.zst)
((${#packages[@]})) || { printf 'error: no packages in %s\n' "$repo" >&2; exit 1; }
repo-add "${args[@]}" "$db" "${packages[@]}"

# repo-add publishes omarchy-gdrive.db/.files as symlinks; static hosts such as
# GitHub Pages do not preserve them, so store real copies.
for link in "$repo"/*.db "$repo"/*.files; do
  [[ -L "$link" ]] || continue
  target="$(readlink -f "$link")"
  rm -f "$link"
  cp -p "$target" "$link"
done
find "$repo" -maxdepth 1 -name '*.old' -delete

printf '\nRepository refreshed in %s:\n' "$repo"
ls -1 "$repo"
printf '\nServer entry:\n  Server = https://<host>/x86_64\n'
