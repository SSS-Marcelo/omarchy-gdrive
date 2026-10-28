# Maintainer: SSS-Marcelo
pkgname=omarchy-gdrive
pkgver=0.2.0
pkgrel=1
pkgdesc='Google Drive integration for Omarchy Files via account-named rclone FUSE mounts'
arch=('any')
url='https://github.com/SSS-Marcelo/omarchy-gdrive'
license=('MIT')
depends=('rclone' 'fuse3' 'python' 'nautilus' 'nautilus-python')
makedepends=()
install=omarchy-gdrive.install
source=('omarchy-gdrive-setup'
        'omarchy-gdrive-nautilus.py'
        'omarchy-gdrive-setup.desktop'
        'README.md'
        'LICENSE')
sha256sums=('05d563751aace8fdd7cd5f7870a6be45878eee7a72e4a9024be0b2822994f346'
            '65b4d58450fbc57e3ccb6a40ed20ac0321b8ee923b5fea21f66a12f5f1c73fc6'
            '5cca605113b3aacc7aec55e72deddb368fd0711486cb4a5375964ad1a675210a'
            '86b762c86bec25940a464bbe8f89a9e825da94698abe8515d6037b674c5c2e4f'
            'd6646ba1fcc87c4e1d9213fa8e420e67b7188b1f7bd120af54d016f6e18f0e1f')

package() {
  install -Dm755 "$srcdir/omarchy-gdrive-setup" "$pkgdir/usr/bin/omarchy-gdrive-setup"
  install -Dm644 "$srcdir/omarchy-gdrive-nautilus.py" \
    "$pkgdir/usr/share/nautilus-python/extensions/omarchy-gdrive.py"
  install -Dm644 "$srcdir/omarchy-gdrive-setup.desktop" "$pkgdir/usr/share/applications/omarchy-gdrive-setup.desktop"
  install -Dm644 "$srcdir/README.md" "$pkgdir/usr/share/doc/$pkgname/README.md"
  install -Dm644 "$srcdir/LICENSE" "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
