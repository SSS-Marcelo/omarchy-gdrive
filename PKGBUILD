# Maintainer: SSS-Marcelo
pkgname=omarchy-gdrive
pkgver=0.4.0
pkgrel=1
pkgdesc='Google Drive integration for Omarchy Files via account-named rclone FUSE mounts'
arch=('any')
url='https://github.com/SSS-Marcelo/omarchy-gdrive'
license=('MIT')
depends=('rclone' 'fuse3' 'python' 'nautilus' 'nautilus-python')
makedepends=()
install=omarchy-gdrive.install
source=('omarchy-gdrive-setup'
        'omarchy-gdrive-mount'
        'omarchy-gdrive-nautilus.py'
        'omarchy-gdrive-setup.desktop'
        'README.md'
        'LICENSE')
sha256sums=('6b47b23395c5a843ab64e88c9bc8d68290cfa2c64d2cb7167e7aac2482ba3c21'
            '18926240e603cd829ac7a486bfaa939a668a5d0d56ceaade2ae6753dcf495caf'
            '4ca4176c544ca1a7a2105306c3589060515e6403eeb6253eaf2c2204e44a5ddc'
            '5cca605113b3aacc7aec55e72deddb368fd0711486cb4a5375964ad1a675210a'
            '2d7167e1798c3636b79e4daf6b9dc649f7037af968e2ba75dd34e760224d40c6'
            'd6646ba1fcc87c4e1d9213fa8e420e67b7188b1f7bd120af54d016f6e18f0e1f')

package() {
  install -Dm755 "$srcdir/omarchy-gdrive-setup" "$pkgdir/usr/bin/omarchy-gdrive-setup"
  install -Dm755 "$srcdir/omarchy-gdrive-mount" "$pkgdir/usr/bin/omarchy-gdrive-mount"
  install -Dm644 "$srcdir/omarchy-gdrive-nautilus.py" \
    "$pkgdir/usr/share/nautilus-python/extensions/omarchy-gdrive.py"
  install -Dm644 "$srcdir/omarchy-gdrive-setup.desktop" "$pkgdir/usr/share/applications/omarchy-gdrive-setup.desktop"
  install -Dm644 "$srcdir/README.md" "$pkgdir/usr/share/doc/$pkgname/README.md"
  install -Dm644 "$srcdir/LICENSE" "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
