# Maintainer: Austin Adams <screamingmoron at gmail dot com>
pkgname=bookfinder-git
pkgver=bacon
pkgrel=1
pkgdesc="searches minecraft worlds for written books"
arch=("any")
url="https://github.com/ausbin/bookfinder"
license=('GPL2')
depends=("python2-nbt" "python2")
makedepends=('git')

_gitroot=git://github.com/ausbin/bookfinder.git
_gitname=bookfinder

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

  # nothing to build :)
}

package() {
  # well, that was easy
  install -Dm 755 bookfinder.py $pkgdir/usr/bin/bookfinder
}

# vim:set ts=2 sw=2 et:
