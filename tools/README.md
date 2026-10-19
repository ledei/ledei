# Updating the profile

All the text lives in `../profile.json`. The README and the card images in `../assets/` are generated from it, so don't edit them by hand.

1. Edit `profile.json`
2. Run `python3 tools/build.py` from the repo root
3. Commit `README.md`, `assets/` and `profile.json`

Common edits:

- **New job:** change `job` (company, url, since, period, title, text) and add a row at the top of `quest_log` with `"current": true`. Remove `"current"` from the old row.
- **Between jobs:** set `"job": null`. The Current quest card goes away, Guild shows "Open to new quests" and the intro drops "at …".
- **Make a quest row clickable:** give it a `"url"`. It gets a "Visit" hint.
- **Small label on a row:** add `"tag"`, like `"New game"` on KYH.
- **Stack:** edit `stack`. Each key becomes a line in the terminal's `cat stack.txt`.

Needs Python 3 and Google Chrome (used to measure each card). If Chrome lives somewhere else, run `CHROME=/path/to/chrome python3 tools/build.py`.

`tools/.out/` holds previews and the Claude canvas artboard. It isn't committed.
