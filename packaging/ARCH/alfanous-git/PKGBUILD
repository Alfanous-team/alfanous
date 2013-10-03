# Contributor: Sohaib Afifi <me@sohaibafifi.com>
pkgname=alfanous-git
pkgver=0.7
pkgrel=1
pkgdesc="Qur’an search engine (git version)"
url="http://www.alfanous.org/"
license=('AGPL')
groups=('arabic-extra-tools')
depends=( 'python2-pyqt' 'python2-pyparsing'  'python2-configobj' 'pyqt')
makedepends=('git' 'make')
provides=('alfanous')
conflicts=('alfanous')
replaces=()
backup=()
options=(!emptydirs)
install=
arch=('any')

_gitname=alfanous
source=("$pkgname"::'git+https://github.com/Alfanous-team/alfanous.git')
md5sums=('SKIP')

pkgver() {
	date +%Y%m%d
}

build() {
  cd "$pkgname"
  # fix the import problem (should be removed)
  mkdir -p src/alfanous/dynamic_resources/
  cp src/alfanous/__init__.py	src/alfanous/dynamic_resources/
  make build_api DESTDIR="$pkgdir/"
  make build_desktop DESTDIR="$pkgdir/"
}

package() {
  cd "$pkgname"
  make install_api DESTDIR="$pkgdir/"
  make install_desktop DESTDIR="$pkgdir/"
}

