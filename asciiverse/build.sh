#!/bin/sh
# Builds PWMAngband's server (pwmangband) and its curses client
# (pwmangclient). Linux: run inside alpine:3.22 for fully static binaries,
# ncurses included; macOS: run on the runner, with CC_ARCH set to x86_64 or
# arm64, linking the system ncurses.
#   docker run --rm -v "$PWD":/src -w /src alpine:3.22 sh asciiverse/build.sh
# Leaves pwmangband and pwmangclient in the repository root. Curses only: no
# SDL, SDL2 or X11 frontends, no sound. The data folder is compiled in as
# /usr/share/pwmangband (system packages); both programs first look for a
# lib/ folder beside themselves, which is how av runs them. The player's
# files go to $XDG_DATA_HOME/pwmangband (PATCHES.md).
set -eu
if [ -f /etc/alpine-release ]; then
  apk add --no-cache build-base autoconf automake git ncurses-dev ncurses-static >/dev/null
  ldflags="-static"
  # the build stamps git describe into the version string
  git config --global --add safe.directory "$PWD"
else
  # macOS has the wide-character ncurses under the plain name; configure
  # looks for -lncursesw, so point that name at the system library
  mkdir -p out/maclib
  ln -sf "$(xcrun --show-sdk-path)/usr/lib/libncurses.tbd" out/maclib/libncursesw.tbd
  ldflags="-L$PWD/out/maclib"
fi
cc="cc${CC_ARCH:+ -arch $CC_ARCH}"
./autogen.sh >/dev/null
# Upstream adds -fsigned-char only on 32-bit ARM; the code expects a signed
# char everywhere, and aarch64 Linux makes char unsigned.
./configure --prefix=/usr --bindir=/usr/bin --sysconfdir=/usr/share \
  --with-private-dirs --enable-curses --disable-x11 --disable-sdl \
  --disable-sdl2 --disable-sdl-mixer --disable-sdl2-mixer \
  CC="$cc" CFLAGS="-fsigned-char" LDFLAGS="$ldflags" >/dev/null
# (the top-level clean would delete the Windows DLLs in the repository)
make -C src clean >/dev/null 2>&1 || true
make -C src -j"$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 2)" pwmangband pwmangclient >/dev/null
mv src/pwmangband src/pwmangclient .
strip pwmangband pwmangclient
# autogen.sh rewrites a tracked file; keep the tree clean
git checkout -q -- src/autoconf.h.in 2>/dev/null || true
