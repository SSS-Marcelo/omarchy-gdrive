# Maintainer: SSS-Marcelo
pkgname=omarchy-gdrive
pkgver=0.7.0
pkgrel=1
pkgdesc='Google Drive for Omarchy Files: My Drive synced locally with auto-save, Shared drives online until kept on this device'
arch=('any')
url='https://github.com/SSS-Marcelo/omarchy-gdrive'
license=('MIT')
depends=('rclone' 'inotify-tools' 'libnotify' 'fuse3' 'python' 'nautilus' 'nautilus-python')
makedepends=()
install=omarchy-gdrive.install
source=("$pkgname-$pkgver.tar.gz::$url/archive/v$pkgver.tar.gz")
sha256sums=('ef1b12cee91ad874ea3e7cc4786f1a2adc778187eed5a96c9a746af5f7df7429')

package() {
  install -Dm755 "$srcdir/$pkgname-$pkgver/omarchy-gdrive-setup" "$pkgdir/usr/bin/omarchy-gdrive-setup"
  install -Dm755 "$srcdir/$pkgname-$pkgver/omarchy-gdrive-sync" "$pkgdir/usr/bin/omarchy-gdrive-sync"
  install -Dm755 "$srcdir/$pkgname-$pkgver/omarchy-gdrive-mount" "$pkgdir/usr/bin/omarchy-gdrive-mount"
  install -Dm644 "$srcdir/$pkgname-$pkgver/omarchy-gdrive-nautilus.py" \
    "$pkgdir/usr/share/nautilus-python/extensions/omarchy-gdrive.py"
  install -Dm644 "$srcdir/$pkgname-$pkgver/omarchy-gdrive-setup.desktop" "$pkgdir/usr/share/applications/omarchy-gdrive-setup.desktop"
  local emblem
  for emblem in synced online syncing error paused; do
    install -Dm644 "$srcdir/$pkgname-$pkgver/omarchy-gdrive-$emblem.svg" \
      "$pkgdir/usr/share/icons/hicolor/scalable/emblems/omarchy-gdrive-$emblem.svg"
  done
  install -Dm644 "$srcdir/$pkgname-$pkgver/README.md" "$pkgdir/usr/share/doc/$pkgname/README.md"
  install -Dm644 "$srcdir/$pkgname-$pkgver/LICENSE" "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
