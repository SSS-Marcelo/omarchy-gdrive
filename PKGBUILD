# Maintainer: SSS-Marcelo
pkgname=omarchy-gdrive
pkgver=0.5.0
pkgrel=1
pkgdesc='Google Drive for Omarchy Files: locally synced folders per account with automatic upload'
arch=('any')
url='https://github.com/SSS-Marcelo/omarchy-gdrive'
license=('MIT')
depends=('rclone' 'inotify-tools' 'libnotify' 'fuse3' 'python' 'nautilus' 'nautilus-python')
makedepends=()
install=omarchy-gdrive.install
source=('omarchy-gdrive-setup'
        'omarchy-gdrive-sync'
        'omarchy-gdrive-mount'
        'omarchy-gdrive-nautilus.py'
        'omarchy-gdrive-setup.desktop'
        'README.md'
        'LICENSE')
sha256sums=('ab8dc9e2db150baa4f01d6a587c9a3c6ccf929365708906987d9a5b51e768daf'
            '259138c283dd3e3a7444bcb22530fb22bb912ee7ea5b9ba1de57a4d3d86da846'
            '1cb5b965e9a0f1845fdcabb2b5d33f9ceee94332261f89eb6878cdf7072ad906'
            '12e383dc663007a62e405eea5b9cc1cb296dfa247750972f721dbc41ed78f2cf'
            '5cca605113b3aacc7aec55e72deddb368fd0711486cb4a5375964ad1a675210a'
            '62f0abc7534c4dc9b6a095b722bac7f334f210a1f02c04cee8ecdd7678ee91ce'
            'd6646ba1fcc87c4e1d9213fa8e420e67b7188b1f7bd120af54d016f6e18f0e1f')

package() {
  install -Dm755 "$srcdir/omarchy-gdrive-setup" "$pkgdir/usr/bin/omarchy-gdrive-setup"
  install -Dm755 "$srcdir/omarchy-gdrive-sync" "$pkgdir/usr/bin/omarchy-gdrive-sync"
  install -Dm755 "$srcdir/omarchy-gdrive-mount" "$pkgdir/usr/bin/omarchy-gdrive-mount"
  install -Dm644 "$srcdir/omarchy-gdrive-nautilus.py" \
    "$pkgdir/usr/share/nautilus-python/extensions/omarchy-gdrive.py"
  install -Dm644 "$srcdir/omarchy-gdrive-setup.desktop" "$pkgdir/usr/share/applications/omarchy-gdrive-setup.desktop"
  install -Dm644 "$srcdir/README.md" "$pkgdir/usr/share/doc/$pkgname/README.md"
  install -Dm644 "$srcdir/LICENSE" "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
