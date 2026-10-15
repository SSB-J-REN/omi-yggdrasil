# Family Hub — wall tablet dashboard

A kiosk page for an old Android tablet in the common room:

- **Coming up** — the next 7 days from both parents' Google Calendars, with 🥪 badges on days each kid needs a packed lunch.
- **Kids' checklists** — big tap-to-check morning/evening routines, weekly star counts, confetti when everything is done. Parents can add one-off tasks ("Feed the dog") for today.
- **Lunches** — Hermes (via Ollama) suggests today's lunch and the *next* lunch day's lunch (the one you prep tonight), with night-before prep steps.
- **Heads up** — Hermes reads today + tomorrow on the calendar and gives 3–5 practical prep tips.

## How lunch days are decided

| Kid | Rule (in `config/family.json`) |
|---|---|
| Addy | Mon–Fri, **unless** a calendar event title contains `No School`, `School Closed` or `Teacher Workday` |
| Logan | Only days with a calendar event whose title contains `Daycare` |

## Allergy safety

Hermes is told: no peanuts, no finned fish. Every suggestion is then checked against `bannedIngredients` in `config/family.json` (peanut, tuna, salmon, anchovy, Caesar, Worcestershire, imitation crab, …). A hit is rejected and Hermes is asked again (3 tries); if all fail the card shows the error instead of a lunch. Rejections are logged as `[lunch] rejected ...`.

This is a word filter, not a label reader. Always check packaging for "may contain peanuts" warnings.

## Setup (home server)

1. Copy this folder to the server, then create your env file:

   ```bash
   cp .env.example .env
   ```

2. Fill in `.env`:
   - `TZ` — your timezone.
   - `CAL_JAREN_ICS` / `CAL_MOM_ICS` — in Google Calendar on a computer: **Settings → (your calendar) → Integrate calendar → Secret address in iCal format**. Do this for both calendars. Treat these links like passwords.
   - `DASHBOARD_PORT` — any free port (default 8088).

3. Edit `config/family.json`: check the kids' **birthdays** (ages are computed from them and shape the lunch ideas), rename the `"Mom"` calendar, and adjust chores.

4. Check that the container will be able to reach Ollama. Native Ollama on Linux listens only on `127.0.0.1` by default, which Docker containers cannot reach. Check with:

   ```bash
   ss -ltn | grep 11434
   ```

   If it shows `127.0.0.1:11434`, Ollama has to listen on `0.0.0.0` (set `OLLAMA_HOST=0.0.0.0` in its systemd unit). **That requires restarting Ollama, which briefly interrupts anything else using it (including the Yggdrasil/Hermes pipeline).** If Ollama runs in Docker instead, put both containers on the same Docker network and set `OLLAMA_URL=http://<ollama-container-name>:11434`.

5. Set `OLLAMA_MODEL` to the exact model name from `ollama list`.

6. Build and start:

   ```bash
   docker compose up -d --build
   ```

7. Open `http://<server-ip>:<DASHBOARD_PORT>` from your phone to confirm.

## Tablet (Android)

1. Install **Fully Kiosk Browser** from the Play Store.
2. Start URL: `http://<server-ip>:<DASHBOARD_PORT>`.
3. Recommended settings: *Keep screen on*, *Screen off/on timer* (e.g. off 9 PM, on 6 AM), *Kiosk mode* (PIN-locked so the kids can't leave the app), *Auto reload on network reconnect*.
4. Give the server a fixed IP (DHCP reservation in your router) so the URL never changes.

## Changing things

- Chores, kids, banned ingredients, lunch rules: edit `config/family.json`, then `docker compose restart family-dashboard` (the dashboard is down for a few seconds).
- Data (checkmarks, stars, tasks, cached lunches/tips) lives in `data/state.json`.
