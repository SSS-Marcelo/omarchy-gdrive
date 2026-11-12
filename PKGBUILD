# Maintainer: SSS-Marcelo
pkgname=omarchy-gdrive
pkgver=0.6.0
pkgrel=1
pkgdesc='Google Drive for Omarchy Files: My Drive synced locally with auto-save, Shared drives online until kept on this device'
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
sha256sums=('9b42bfb20fb44249a70f947bce0bbe70815b067413fd3ee7e561266c29d029e6'
            '6fa055f50a92475b0ebac82377ace9f529a4a14dac7a0700b3619caab1297d02'
            '28061dc377dcb2af4f8e02c32d08bdaf78dd7486cb55b2991358ad38a98ca3c3'
            '043b26549877b487605cb78c57049f78f2c80c6304bab6e6c0f171055beb9671'
            '5cca605113b3aacc7aec55e72deddb368fd0711486cb4a5375964ad1a675210a'
            'c4939e3481a1bf3016d21f6cf172b998bf1b892b6466dbab113eab2e6983e52f'
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
