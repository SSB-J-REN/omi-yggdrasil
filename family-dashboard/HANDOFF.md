# Family Hub — Deployment Handoff

Written for the Claude session running on the home server (host PC). It covers what was built, what still needs doing, and the rules to follow while deploying it.

- **Repo:** `https://github.com/SSB-J-REN/omi-yggdrasil`
- **Branch:** `claude/family-dashboard-tablet-4tn948` (not merged to `master`)
- **Folder:** `family-dashboard/` (self-contained; it does not touch the existing Omi → Yggdrasil webhook files at the repo root)

---

## 1. Ground rules for the host session

1. **Do not stop, restart, remove or re-port any service that is currently running** (Ollama, the Hermes agent, the Yggdrasil/Omi webhook, ngrok/cloudflared tunnels, other containers) without first warning the owner in bold and getting explicit confirmation.
2. Make changes inside `family-dashboard/` only.
3. Fail fast. If a precondition isn't met (no Ollama, port in use, missing calendar URL), stop and report. Don't add workarounds or fallbacks.
4. Never commit `.env` (it holds the private calendar links). It is already in `.gitignore`.

---

## 2. What it is

A Docker-hosted web app shown full-screen on an old Android tablet mounted in the common room.

| Panel | What it does |
|---|---|
| **📅 Coming up** | Next 7 days from both parents' Google Calendars (read-only, via secret iCal links). A 🥪 badge marks days each kid needs a packed lunch. |
| **Kid cards (Addy, Logan)** | Big tap-to-check morning/evening routines plus parent-added one-off tasks. Pop + sparkle animation on every check. |
| **⭐ Gold stars** | Finishing every item on a kid's list for the day earns 1 gold star with a full-screen celebration. Stars add up (they don't have to be consecutive days). A star stays once earned. |
| **🎁 Rewards** | Every 7 stars earns a reward: a bigger 🎁→🏆 celebration, then a "Reward ready" button. A parent taps it, types the chosen reward, and the star row resets. |
| **🥪 Lunches** | Hermes model (via Ollama) suggests today's lunch and the next lunch day's lunch (prepped tonight), with night-before prep steps. "New idea" regenerates. |
| **💡 Heads up** | Hermes reads today + tomorrow on the calendar and gives 3–5 practical prep tips. |

### Family facts baked into `config/family.json`

| Kid | Birthday | Lunch rule |
|---|---|---|
| **Addy** | 2021-05-07 | Mon–Fri, **skipped** when any calendar event title contains `No School`, `School Closed` or `Teacher Workday` |
| **Logan** | 2023-04-13 | Only on days with a calendar event whose title contains `Daycare` |

Ages are computed from birthdays daily and passed to the model.

### Allergy safety (do not weaken)

- Banned: **peanut** and **finned fish** only (owner confirmed no other restrictions).
- The model is instructed to avoid them, **and** every suggestion is checked against `bannedIngredients` (peanut, tuna, salmon, anchovy, Caesar, Worcestershire, imitation crab, …). A hit is rejected and the model is asked again (3 tries). If all 3 fail, the card shows an error instead of a lunch. Rejections log as `[lunch] rejected ...`.
- The UI tells parents to still check labels for "may contain" warnings.

---

## 3. Architecture

```
Android tablet (Fully Kiosk Browser)
        │  http://<server-ip>:8088
        ▼
family-dashboard container (Node 22, Express, TypeScript)
   ├── Google Calendar secret .ics links  (HTTPS, cached 10 min)
   ├── Ollama /api/chat with JSON schema  (OLLAMA_URL)
   └── ./data/state.json                   (checks, stars, rewards, tasks, cached lunches/tips)
```

### Files

| Path | Purpose |
|---|---|
| `src/server.ts` | Express routes, checklist and star/reward logic |
| `src/calendar.ts` | Fetches and parses .ics, expands recurring events, de-duplicates events shared across both calendars, formats times in container `TZ` |
| `src/schedule.ts` | Which kid needs lunch on which day |
| `src/lunch.ts` | Lunch generation and banned-ingredient filter |
| `src/briefing.ts` | Daily "Heads up" tips (cached per day; regenerated when the calendar changes) |
| `src/ollama.ts` | Ollama native `/api/chat` call with `format: <json schema>` |
| `src/config.ts` | Loads `config/family.json` + env; throws on missing values |
| `src/store.ts` | JSON file persistence (atomic write) |
| `src/dates.ts` | Local-date helpers and age calculation |
| `public/` | Tablet UI (plain ES2017 JS, no build step, for older Android WebViews) |
| `config/family.json` | Kids, routines, lunch rules, calendar names/colors, banned ingredients |
| `.env.example` | Template for secrets and host settings |
| `Dockerfile`, `docker-compose.yml` | Two-stage build; container port 8080 → host `DASHBOARD_PORT` |

### API (for testing)

| Method | Path | Notes |
|---|---|---|
| GET | `/api/dashboard` | Calendar days, kids, checklist state, stars |
| GET | `/api/lunches` | Generates missing lunches (can take a while on first call) |
| POST | `/api/lunches/regenerate` | `{kidId, date}` |
| GET | `/api/briefing` | Daily tips |
| POST | `/api/check` | `{kidId, itemId, done}` → `{newStar, rewardEarned, stars, filled, rewardsReady}` |
| POST | `/api/tasks` / DELETE `/api/tasks/:id` | One-off tasks for today |
| POST | `/api/rewards` | `{kidId, reward}`, only when a reward is ready |

---

## 4. What has and hasn't been verified

**Verified (in a cloud sandbox with a mock calendar and mock Ollama):**
- TypeScript compiles; the Dockerfile's build steps succeed in a clean directory.
- Recurring events, EXDATEs, all-day "No School" skip, Daycare detection, cross-calendar de-duplication.
- Banned-ingredient filter rejected a tuna lunch and regenerated.
- Checks, tasks, gold star on a completed day, 7th-star reward celebration, reward redemption, and refusal of a second redemption.
- Layout at 1280×800.

**Not yet verified (host session must do these):**
- `docker compose build` on a real Docker daemon.
- Real Google Calendar feeds.
- Real Hermes model output quality and speed through Ollama.
- Running on the actual tablet.

---

## 5. Deployment steps for the host session

### Step 1 — Get the code

```bash
git fetch origin claude/family-dashboard-tablet-4tn948
git checkout claude/family-dashboard-tablet-4tn948
cd family-dashboard
```

### Step 2 — Confirm the model backend (read-only checks)

The dashboard talks to **Ollama directly**, not to the Hermes agent. The Hermes agent can keep using the same Ollama model alongside it.

```bash
ss -ltnp | grep 11434
```

```bash
ollama list
```

```bash
docker ps --format '{{.Names}}\t{{.Image}}\t{{.Ports}}'
```

Decide from the output:

- **Ollama listens on `0.0.0.0:11434` or `*:11434`** → use `OLLAMA_URL=http://host.docker.internal:11434`. No changes to Ollama needed.
- **Ollama listens only on `127.0.0.1:11434`** → the container can't reach it. Fixing this means setting `OLLAMA_HOST=0.0.0.0` on the Ollama service and restarting it. **That restart briefly interrupts the Hermes agent and the Yggdrasil pipeline. Stop and get the owner's explicit confirmation before doing it.**
- **Ollama runs as a Docker container** → attach `family-dashboard` to that container's Docker network and set `OLLAMA_URL=http://<ollama-container-name>:11434`.
- **No Ollama at all** (the Hermes agent uses OpenRouter or another server) → stop and report to the owner. `src/ollama.ts` would need to target that provider; don't improvise.

Set `OLLAMA_MODEL` to the exact name from `ollama list` (the Hermes model).

### Step 3 — Pick a free port (read-only check)

```bash
ss -ltn | grep ':8088 '
```

No output means 8088 is free. Otherwise choose another free port for `DASHBOARD_PORT`. Don't move any existing service.

### Step 4 — Create `.env`

```bash
cp .env.example .env
```

Fill in:

| Key | Value / where it comes from |
|---|---|
| `DASHBOARD_PORT` | Free port from Step 3 |
| `TZ` | **Ask the owner.** The template says `America/Chicago`, which is only a placeholder. |
| `CAL_JAREN_ICS` | **Owner must provide.** Google Calendar on a computer → Settings → their own calendar → *Integrate calendar* → **Secret address in iCal format** |
| `CAL_MOM_ICS` | Same, for the wife's calendar |
| `OLLAMA_URL` | From Step 2 |
| `OLLAMA_MODEL` | From Step 2 |

### Step 5 — Owner-specific edits to `config/family.json`

- Rename calendar `"Mom"` to the wife's name (and the env var name too if desired; keep `urlEnv` and `.env` in sync).
- Optionally adjust routines, emojis, colors, or the `No School` keywords to match how the school's days off appear on their calendar.

### Step 6 — Build and start (new container only)

```bash
docker compose up -d --build
```

```bash
docker logs family-dashboard --tail 30
```

Expect `Family dashboard on :8080 (TZ=...)`. Startup throws immediately if an env var is missing.

### Step 7 — Smoke tests

```bash
curl -s localhost:${DASHBOARD_PORT:-8088}/api/dashboard | head -c 600
```

```bash
docker exec family-dashboard wget -qO- http://host.docker.internal:11434/api/tags
```

(Skip the second one if Ollama is on a Docker network; use the container name instead.)

```bash
time curl -s localhost:${DASHBOARD_PORT:-8088}/api/lunches
```

Check:
- Real calendar events appear for the next 7 days, with correct times.
- Addy has 🥪 on weekdays, and Logan only on days with a "Daycare" event.
- Lunches come back with no peanut or fish, and the response time is acceptable. Note how long the first call took and report it.
- `docker logs family-dashboard` shows no errors; report any `[lunch] rejected` lines.

### Step 8 — Tablet (owner does this; pass these instructions on)

1. Give the server a fixed LAN IP (DHCP reservation in the router).
2. Install **Fully Kiosk Browser** on the Android tablet.
3. Start URL: `http://<server-ip>:<DASHBOARD_PORT>`.
4. Settings: Keep screen on, screen off/on schedule (e.g. off 9 PM, on 6 AM), kiosk mode with PIN, auto-reload on network reconnect.

---

## 6. What the host session needs from the owner

1. The two Google Calendar **secret iCal links**.
2. Timezone.
3. Wife's name for the calendar label.
4. Confirmation before any change to Ollama's service or any running service (only if Step 2 requires it).

## 7. Report back to the owner when done

- Port and URL for the tablet.
- Ollama URL and model used, and whether Ollama needed any change.
- Smoke test results, including how long lunch generation took.
- Anything that failed, with the log lines.

## 8. Operating notes

- Config change → `docker compose restart family-dashboard` (dashboard down a few seconds; nothing else affected).
- Code change → `docker compose up -d --build`.
- All family data lives in `family-dashboard/data/state.json`. Back it up with the rest of the server if desired.
- Not built (possible later work): parent PIN on the reward button, reward history on screen, a different routine for weekends.
