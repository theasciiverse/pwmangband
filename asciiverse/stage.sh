#!/bin/sh
# Lays out what av installs, in stage/: the server, the client, the start
# script, upstream's server settings and the game data the curses client and
# the server read (lib/, without its Makefiles). The archive and the system
# packages are both made from it. Run after asciiverse/build.sh.
set -eu
cd "$(dirname "$0")/.."
rm -rf stage && mkdir -p stage/lib/tiles
cp pwmangband pwmangclient asciiverse/pwmangband-play setup/mangband.cfg stage/
cp -R lib/customize lib/gamedata lib/help lib/screens stage/lib/
cp lib/tiles/list.txt stage/lib/tiles/
find stage/lib -name Makefile -exec rm {} +
cp docs/copying.rst stage/COPYING
cp README.md changes.txt stage/
