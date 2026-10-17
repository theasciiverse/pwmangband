# PWMAngband (Asciiverse packaging)

PWMAngband, the multiplayer client/server Angband variant (MAngband and
PWMAngband developers), packaged for the Asciiverse catalog and as system
packages. Not our code: keep changes small and list every one in PATCHES.md.

- Remotes: `upstream` is github.com/draconisPW/PWMAngband, `origin` is
  github.com/theasciiverse/pwmangband.
- Branch `asciiverse` = upstream tag `1.6.2-build-3` plus our commits.
- Release: tag `v1.6.2.3-av.<n>` and push it.
- Local static build: `docker run --rm -v "$PWD":/src -w /src alpine:3.22
  sh asciiverse/build.sh`, then `sh asciiverse/stage.sh` (the av layout in
  `stage/`). Never run the top-level `make clean`: it deletes upstream's
  Windows DLLs.
- Always client and server, even alone: `pwmangband-play` runs a server on
  this machine; everything the player owns is in `~/.local/share/pwmangband`.
- Source files are CRLF (some mixed); keep line endings when editing.
- Preview: `python3 asciiverse/record-preview.py` after building and
  staging (needs tmux and asciinema 3).
