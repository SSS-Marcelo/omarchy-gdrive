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
source=('omarchy-gdrive-setup'
        'omarchy-gdrive-sync'
        'omarchy-gdrive-mount'
        'omarchy-gdrive-nautilus.py'
        'omarchy-gdrive-setup.desktop'
        'omarchy-gdrive-synced.svg'
        'omarchy-gdrive-online.svg'
        'omarchy-gdrive-syncing.svg'
        'omarchy-gdrive-error.svg'
        'omarchy-gdrive-paused.svg'
        'README.md'
        'LICENSE')
sha256sums=('9b42bfb20fb44249a70f947bce0bbe70815b067413fd3ee7e561266c29d029e6'
            '6fa055f50a92475b0ebac82377ace9f529a4a14dac7a0700b3619caab1297d02'
            '28061dc377dcb2af4f8e02c32d08bdaf78dd7486cb55b2991358ad38a98ca3c3'
            '8828068db09adfb0da82a3b632051e8cbb42f617fff2e796f85d7bf4cbb4fa10'
            '5cca605113b3aacc7aec55e72deddb368fd0711486cb4a5375964ad1a675210a'
            '7c9be72aa9a43748f44ce53f9c74cf2f91191131d7dc5f8163a132d168de1873'
            '38b8226dc262632d1d71b2319ef6b7f14d0cac4429fe0f4b367eae40ef4181fd'
            '50d386c63ef7d598432900f79a713f1d2ea05853aecc7ce4796a44348a406c35'
            '0320d4105f56c661859c7b255a6b2fcf2a804a69b89e9cc510dbd89bc88e0b6e'
            '58e8bc1c4463b6b04a3c7963593abbfa68a6f746e91b64850b59bc780800d5a6'
            'e768b4977a4bed8e26ae17978d2a456be425132150bad87e9cd0cbefe6bad277'
            'd6646ba1fcc87c4e1d9213fa8e420e67b7188b1f7bd120af54d016f6e18f0e1f')

package() {
  install -Dm755 "$srcdir/omarchy-gdrive-setup" "$pkgdir/usr/bin/omarchy-gdrive-setup"
  install -Dm755 "$srcdir/omarchy-gdrive-sync" "$pkgdir/usr/bin/omarchy-gdrive-sync"
  install -Dm755 "$srcdir/omarchy-gdrive-mount" "$pkgdir/usr/bin/omarchy-gdrive-mount"
  install -Dm644 "$srcdir/omarchy-gdrive-nautilus.py" \
    "$pkgdir/usr/share/nautilus-python/extensions/omarchy-gdrive.py"
  install -Dm644 "$srcdir/omarchy-gdrive-setup.desktop" "$pkgdir/usr/share/applications/omarchy-gdrive-setup.desktop"
  local emblem
  for emblem in synced online syncing error paused; do
    install -Dm644 "$srcdir/omarchy-gdrive-$emblem.svg" \
      "$pkgdir/usr/share/icons/hicolor/scalable/emblems/omarchy-gdrive-$emblem.svg"
  done
  install -Dm644 "$srcdir/README.md" "$pkgdir/usr/share/doc/$pkgname/README.md"
  install -Dm644 "$srcdir/LICENSE" "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
