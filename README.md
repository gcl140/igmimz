# igmimz

A small Instagram auto-poster. Every run it picks one unused photo and/or
video from `posts/`, pairs it with an unused caption from `captions.csv`,
and uploads it via [instagrapi](https://github.com/subzeroid/instagrapi).
A local SQLite database remembers what's already been posted so nothing
repeats until the whole pool has cycled through.

## How it works

- **Media selection** — `newai.py` scans `posts/` for images (`.jpg`,
  `.jpeg`, `.png`) and videos (`.mp4`, `.mov`), and picks one of each at
  random, excluding anything already marked as posted in `state.db`.
  Once every file in a category has been used, that category's history
  resets and the cycle starts over — so it never runs dry.
- **Captions** — same idea, independently: a random unused line from
  `captions.csv` is picked, tracked separately in `state.db`, and reset
  once the whole caption list has been used. Media and captions are
  tracked independently, so a caption won't repeat just because it's
  paired with a new video, and a video won't repeat just because it gets
  a new caption.
- **State** — `state.db` (SQLite, created automatically on first run)
  holds two tables: `used_media` and `used_captions`. A file/caption is
  only marked used after a successful upload, so a failed post doesn't
  burn its pick.
- **Session reuse** — `session.json` is created on first login and reused
  after that, so the script doesn't log in fresh (and risk a challenge/
  checkpoint) every single day.

## Project layout

```
igmimz/
├── newai.py            # the whole bot - single entry point
├── requirements.txt
├── captions.csv         # one caption per line, pool to draw from
├── posts/               # drop the photos/videos you want posted here
├── logs/                # cron output lands here (run.log)
├── run.sh               # wrapper script cron calls
├── cron/igmimz.cron      # crontab template - 8am daily
├── .env.example          # copy to .env and fill in credentials
├── .env                  # your real credentials (gitignored, not committed)
├── session.json          # generated on first login (gitignored)
└── state.db              # generated automatically (gitignored)
```

## Setup

1. **Clone and create a virtualenv**

   ```bash
   git clone https://github.com/gcl140/igmimz.git
   cd igmimz
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure credentials**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and fill in `IG_USERNAME` / `IG_PASSWORD`. This file is
   gitignored — never commit it.

3. **Add media and captions**

   Drop photos/videos into `posts/`. Add or edit lines in `captions.csv`
   (one caption per line, no header).

4. **First run (interactive, generates the session)**

   ```bash
   python newai.py
   ```

   This logs in with your username/password and writes `session.json`.
   Instagram may prompt for a verification code on first login from a new
   IP — handle that once, and subsequent runs reuse the saved session
   instead of logging in fresh.

## Scheduling: post every day at 8am

This project is meant to run unattended on a server via cron.

1. Make sure the venv path in [run.sh](run.sh) matches your setup (it
   assumes `venv/` lives inside the project folder).
2. Check the server's timezone — cron runs on the system clock, so "8am"
   means 8am in whatever timezone the machine is set to:

   ```bash
   timedatectl               # Linux
   sudo timedatectl set-timezone America/New_York   # if it needs fixing
   ```

3. Edit [cron/igmimz.cron](cron/igmimz.cron), replacing
   `/home/youruser/igmimz` with the real absolute path to this project on
   your server, then install it:

   ```bash
   crontab -e
   # paste in the line from cron/igmimz.cron
   ```

   or non-interactively:

   ```bash
   crontab -l 2>/dev/null | { cat; echo "0 8 * * * /absolute/path/to/igmimz/run.sh"; } | crontab -
   ```

4. Confirm it's installed:

   ```bash
   crontab -l
   ```

Output from each run is appended to `logs/run.log`.

## Deploying on your own server

Since this runs headless and unattended, an old PC repurposed as a
always-on Linux box works well:

1. **OS** — any recent Linux (Debian/Ubuntu is the path of least
   resistance for `apt install python3-venv git cron`).
2. **Keep it awake and online** — disable sleep/suspend
   (`sudo systemctl mask sleep.target suspend.target hibernate.target
   hybrid-sleep.target` on systemd distros), and make sure the machine
   reconnects to Wi-Fi/Ethernet automatically after a power blip.
3. **Get the code onto the machine**:

   ```bash
   git clone https://github.com/gcl140/igmimz.git
   cd igmimz
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env   # then edit it
   ```

4. Run `python newai.py` once interactively to create `session.json`
   (do this over SSH from the machine itself, or locally then copy
   `session.json` over — it's gitignored so it won't sync automatically).
5. Set the timezone and install the cron job as described above.
6. Confirm cron actually has permission to run: cron jobs run with a
   minimal environment, which is why `run.sh` explicitly activates the
   venv and `cd`s into the project directory rather than relying on
   whatever's in your interactive shell's `PATH`.
7. Watch the first scheduled run: `tail -f logs/run.log` a few minutes
   after 8am.

### Optional: keep the machine reachable remotely

If the old PC isn't always physically accessible, set up SSH
(`sudo apt install openssh-server`) and either port-forward on your
router or use a tunnel service (Tailscale/Cloudflare Tunnel) so you can
check on `logs/run.log` or update `posts/`/`captions.csv` without being
in front of it.

## Security notes

- Never commit `.env` or `session.json` — both are already in
  `.gitignore`. Both contain (or gate) live account credentials.
- If a session file or password is ever accidentally committed, rotate
  the Instagram password and log out other sessions from Instagram's
  Settings → Security → Login Activity immediately — removing a secret
  from a later commit does not invalidate it if the repo was ever public.
