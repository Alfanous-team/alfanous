# Maintainer: Walid Ziouche <01walid@gmail.com>
pkgname=alfanous
pkgver=0.7
pkgrel=1
pkgdesc="Qur’an search engine"
url="http://www.alfanous.org/"
license=('AGPL')
groups=('arabic-extra-tools')
depends=('make' 'python2-pyqt' 'python2-pyparsing' 'epydoc' 'python2-sphinx' 'python2-configobj' 'pyqt')
makedepends=()
provides=()
conflicts=()
replaces=()
backup=()
options=(!emptydirs)
install=
source=(http://downloads.sourceforge.net/sourceforge/${pkgname}/${pkgname}-${pkgver}-archlinux.tar.xz)
md5sums=('380c2a684e3110836f6e82114f49df72')
arch=('any')

build() {
  cd ${srcdir}/${pkgname}
  echo ${srcdir}
  make build_api DESTDIR="$pkgdir/"
  make build_desktop DESTDIR="$pkgdir/"
  make install_api DESTDIR="$pkgdir/"
  make install_desktop DESTDIR="$pkgdir/"
}
# vim:set ts=2 sw=2 et:
