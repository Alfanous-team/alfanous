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

_gitroot=https://github.com/Alfanous-team/alfanous.git
_gitname=alfanous

build() {
  cd "$srcdir"
  msg "Connecting to GIT server...."

  if [[ -d "$_gitname" ]]; then
    cd "$_gitname" && git pull origin
    msg "The local files are updated."
  else
    git clone "$_gitroot" "$_gitname"
  fi

  msg "GIT checkout done or server timeout"
  msg "Starting build..."
  
  rm -rf "$srcdir/$_gitname-build"
  git clone "$srcdir/$_gitname" "$srcdir/$_gitname-build"
  cd "$srcdir/$_gitname-build"
  mkdir -p  src/alfanous/dynamic_resources/ 
  cp src/alfanous/__init__.py	src/alfanous/dynamic_resources/
  make build_api DESTDIR="$pkgdir/"
  make build_desktop DESTDIR="$pkgdir/"
}

package() {
  cd "$srcdir/$_gitname-build"
  make install_api DESTDIR="$pkgdir/"
  make install_desktop DESTDIR="$pkgdir/"
}

