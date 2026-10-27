# Changes from upstream

This is the Asciiverse packaging of PWMAngband, the multiplayer Angband
variant by the MAngband and PWMAngband developers (draconisPW and others),
from [draconisPW/PWMAngband](https://github.com/draconisPW/PWMAngband)
(the `upstream` remote). The `asciiverse` branch starts at upstream's tag
`1.6.2-build-3` (2026-03-05, "Version 1.6.2 build 3"), the latest release;
our tags are `v1.6.2.3-av.<n>`, after the version the game itself reports
(1.6.2.3, shown as "1.6.2 (Build 3)").

Licence: `docs/copying.rst` offers the GNU GPL version 2 (no "or later")
or the non-commercial Angband licence. Asciiverse distributes it under
GPL-2.0-only. The free tiles, sounds and fonts upstream ships are not
packaged, because the curses client does not use them; this release has
no Shockbolt tiles in `lib/tiles` (only David Gervais', CC BY 3.0).

## Code

One commit, "the player's files in the XDG data folder, the game data
beside the programs":

- `src/common/z-file.c`, `z-file.h`: `player_data_path()` gives
  `$XDG_DATA_HOME/pwmangband` (`~/.local/share/pwmangband` when it is not
  set), and `exe_lib_path()` finds a `lib/` folder beside the running
  program (from `argv[0]`).
- `src/common/config.h`: on Unix the private user folder is that data
  folder instead of `~/.pwmangband`; `src/client/ui-init.c` and
  `src/server/init.c` use it as is, without upstream's extra `PWMAngband`
  level. The server keeps its world, accounts, characters (`save/`), daily
  logs and scores (`scores/`) and panic saves there; the client its pref
  files and character dumps.
- `src/client/ui-init.c`, `src/server/main.c`: both programs use a `lib/`
  beside themselves when there is one (an av install), otherwise the
  compiled-in `/usr/share/pwmangband` (the system packages). The server now
  saves `argv[0]` before it sets up its paths.
- `src/server/init.c`: `mangband.cfg` is read from the data folder first,
  then from the current folder as upstream does.
- `src/client/conf.c`: on Unix the client's settings (account name,
  password, metaserver) are `pwmangrc` in the data folder, read and written
  there, instead of `~/.pwmangrc` or `./.pwmangrc`.

## Packaging (new files)

- `asciiverse/pwmangband-play`: the start script. With no arguments it
  starts a server on this machine and connects the client to it, and stops
  the server (which saves on SIGTERM) when the client ends. The client
  keeps running when its terminal is closed, so it runs in the background
  of the script, whose trap stops both; a watcher covers the script being
  killed too. On the first game it copies upstream's `setup/mangband.cfg`
  to the data folder with the metaserver report and the remote console
  turned off; the player may edit it later. It takes port 18346, or the
  next even port when that is busy (the server retries a busy port forever
  without saying so, so the script reads its log). A second terminal
  joins the game already running instead of starting another server on
  the same files. With arguments it runs just the client:
  `pwmangband-play <host> [port]`, or `--list` for the mangband.org
  metaserver's list. Logs go to `~/.cache/asciiverse/pwmangband-server.log`.
- `asciiverse/build.sh`: static Linux builds in Alpine (ncurses linked
  in), macOS builds per architecture against the system ncurses (a
  `libncursesw` name pointing at the SDK's `libncurses`, untested so far).
  Curses frontend only: no SDL, SDL2, X11 or sound. `-fsigned-char` on all
  targets: upstream adds it only on 32-bit ARM, and aarch64 Linux makes
  `char` unsigned.
- `asciiverse/stage.sh`: lays out the av archive in `stage/`: the two
  programs, the start script, `mangband.cfg`, and `lib/customize`,
  `gamedata`, `help`, `screens` and `tiles/list.txt`.
- `asciiverse/nfpm.yaml`: .deb, .rpm, .apk and Arch packages; programs in
  `/usr/bin` under upstream's names (`pwmangband` the server,
  `pwmangclient` the client) plus `pwmangband-play`, data in
  `/usr/share/pwmangband`.
- `asciiverse/record-preview.py`, `asciiverse/pwmangband.cast`: the
  catalog preview, 100x30.
- `.github/workflows/release.yml`: builds all of it on a tag.

## Not built

- Windows: upstream's Windows clients are a Win32 GUI (`main-win.c`) and
  an SDL one, built with Borland C++ Builder (`src/makefile.*`); there is
  also a Borland curses client (`src/makefile.gcu`, PDCurses). A console
  build for the catalog would mean MinGW plus PDCurses for the client and
  the Windows server, with the same path changes for `%APPDATA%`.
- The SDL, SDL2 and X11 clients, the Cocoa app, the Android port, sound.

## Known upstream quirks

- The server listens on every interface (`INADDR_ANY`), so a local game
  can be joined from the network, like 0verkill's.
- The client sends the machine's host name to the server it joins.
- The client drops keys that arrive in a fast burst (pasted or scripted).

## Ours

- **How to play it, at the top of README.md.** A short note on installing and
  starting it with av, or from a release archive; the original text follows
  unchanged.
