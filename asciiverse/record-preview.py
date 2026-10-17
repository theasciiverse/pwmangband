#!/usr/bin/env python3
"""Records asciiverse/pwmangband.cast, PWMAngband's catalog preview, at 100x30
(hub/RECORDING.md): a private game through asciiverse/pwmangband-play, a new
Elf Ranger called Ada (made before the recording starts), logged in, then
a walk through the town into four of its shops, read from the screen and
steered by breadth-first search, and a save and quit with Ctrl-X.

asciinema runs inside a tmux session of exactly 100x30, which this script
reads (capture-pane) to find Ada and the shop doors. The game gets a
throwaway HOME, so nothing of the recording machine ends up in the cast.
Usage, from the repo root after asciiverse/build.sh and asciiverse/stage.sh:
    python3 asciiverse/record-preview.py"""
import collections, json, os, shutil, subprocess, tempfile, time

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cast = f"{root}/asciiverse/pwmangband.cast"
home = tempfile.mkdtemp()
game = f"{home}/game"
shutil.copytree(f"{root}/stage", game)
sock = f"pwm-rec-{os.getpid()}"


def tmux(*args):
    return subprocess.run(["tmux", "-L", sock, *args], capture_output=True, text=True).stdout


def screen():
    return tmux("capture-pane", "-p", "-t", "rec").split("\n")


def keys(*ks, gap=0.35):
    # the client drops keys that come in a burst, so one at a time
    for k in ks:
        tmux("send-keys", "-t", "rec", k)
        time.sleep(gap)


env = {"HOME": home, "PATH": f"{game}:/usr/bin:/bin", "TERM": "xterm-256color",
       "COLORTERM": "truecolor", "LANG": "C.UTF-8", "USER": "player", "LOGNAME": "player"}
envargs = ["env", "-i", *[f"{k}={v}" for k, v in env.items()]]

# the account's name and password are in the client's settings, so the
# login is two presses of Enter
data = f"{home}/.local/share/pwmangband"
os.makedirs(data)
with open(f"{data}/pwmangrc", "w") as f:
    f.write("[MAngband]\nnick=Ada\npass=speakfriend\nmeta_address=mangband.org\n"
            "meta_port=8802\nDisableNumlock=1\nLighterBlue=1\nIntroMusic=0\n")


def wait_for(text, tries=60):
    for _ in range(tries):
        if any(text in l for l in screen()):
            return True
        time.sleep(0.5)
    return False


def until_gone():
    for _ in range(40):
        if not tmux("list-sessions"):
            return
        time.sleep(0.5)
    tmux("kill-server")


# First, unrecorded: Ada, a female Elf Ranger, is born and steps into the
# town, so the preview can start with the game itself
tmux("new-session", "-d", "-x", "100", "-y", "30", "-s", "rec", *envargs,
     "sh", "-c", f"cd {home} && pwmangband-play")
wait_for("Name")
keys("Enter", "Enter", gap=1)
keys("a", gap=1.5)                       # new character
keys("Enter", gap=1.5)                   # named Ada, as the account
keys("a", "c", "Enter", "i", "Enter", gap=1)   # female, Elf, Ranger
keys("Enter", "Enter", gap=1.2)          # point-based stats, accepted
keys("y", gap=3)                         # confirmed
keys("Space", gap=3)                     # past the splash screen
keys("C-x", gap=1)
until_gone()

# Then the recording: log in, pick Ada, and go shopping
cmd = ("asciinema rec --overwrite -q -i 2 --window-size 100x30 "
       "--capture-env TERM,COLORTERM,LANG --title PWMAngband "
       f"-c pwmangband-play {cast}")
tmux("new-session", "-d", "-x", "100", "-y", "30", "-s", "rec", *envargs,
     "sh", "-c", f"cd {home} && {cmd}")
wait_for("Name")
time.sleep(0.5)
keys("Enter", "Enter", gap=0.8)
wait_for("Ada")
keys("a", gap=2.5)
keys("Space", gap=2.5)

MOVES = {(-1, -1): "7", (0, -1): "8", (1, -1): "9", (-1, 0): "4",
         (1, 0): "6", (-1, 1): "1", (0, 1): "2", (1, 1): "3"}


def mapview():
    """The map part of the screen: columns 13 to 79, rows 1 to 22."""
    rows = screen()
    grid = {}
    for y in range(1, 23):
        line = rows[y] if y < len(rows) else ""
        for x in range(13, 80):
            grid[(x, y)] = line[x] if x < len(line) else " "
    return grid


# Blank cells are either walls (the shop buildings) or ground not seen yet;
# a blank cell Ada fails to step onto is a wall, remembered here by screen
# position until the map scrolls
walls = set()
# floor, unseen ground and the tavern's door: new characters start inside
# the tavern, a walled yard whose only way out is its door ('8')
FLOOR = ". 8"


def path_to(grid, targets):
    """First step of the shortest walk from Ada to any of targets, over
    FLOOR, and the target it leads to."""
    me = next((p for p, c in grid.items() if c == "@"), None)
    if not me:
        return None, None
    prev = {me: None}
    todo = collections.deque([me])
    while todo:
        p = todo.popleft()
        if grid[p] in targets:
            goal = grid[p]
            while prev[p] != me:
                p = prev[p]
            return (p[0] - me[0], p[1] - me[1]), goal
        if grid[p] not in FLOOR and p != me:
            continue
        for d in MOVES:
            q = (p[0] + d[0], p[1] + d[1])
            if q in grid and q not in prev and q not in walls and grid[q] in FLOOR + "".join(targets):
                prev[q] = p
                todo.append(q)
    return None, None


def visit(targets, limit=80):
    """Walks to the nearest shop door of targets; returns the shop once its
    screen ("Gold Remaining") has taken over."""
    goal = None
    for _ in range(limit):
        if any("Gold Remaining" in l for l in screen()):
            return goal
        grid = mapview()
        if not any(c == "@" for c in grid.values()):
            time.sleep(0.3)       # caught mid-redraw
            continue
        step, goal = path_to(grid, targets)
        if not step:
            return None
        me = next(p for p, c in grid.items() if c == "@")
        keys(MOVES[step], gap=0.15)
        # the move goes through the server; give the screen time to follow
        after = me
        for _ in range(8):
            after = next((p for p, c in mapview().items() if c == "@"), None)
            if after != me:
                break
            time.sleep(0.1)
        if after == me:
            walls.add((me[0] + step[0], me[1] + step[1]))
        elif after and after != (me[0] + step[0], me[1] + step[1]):
            walls.clear()         # the map scrolled
        time.sleep(0.15)
    return None


# the shops: 1 General Store, 2 Armoury, 3 Weaponsmith, 4 Bookseller,
# 5 Alchemy shop, 6 Magic shop, 7 Black market (8 is the tavern, no shop)
todo = set("1234567")
for _ in range(4):
    shop = visit(todo)
    if not shop:
        break
    todo.discard(shop)
    time.sleep(1.5)               # the shop's wares
    keys("Escape", gap=1.0)

time.sleep(1.5)
keys("C-x", gap=1)
until_gone()
tmux("kill-server")
# asciinema stores the recording terminal's version (tmux), which is not
# what viewers have
with open(cast) as f:
    lines = f.readlines()
header = json.loads(lines[0])
header.get("term", {}).pop("version", None)
lines[0] = json.dumps(header, separators=(",", ":")) + "\n"
with open(cast, "w") as f:
    f.writelines(lines)
shutil.rmtree(home, ignore_errors=True)
print(cast)
