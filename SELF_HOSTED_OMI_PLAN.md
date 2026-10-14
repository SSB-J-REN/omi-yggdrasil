# Self-Hosted Omi Replacement — Project Brief

## Goal

Replace Omi's cloud with a fully self-hosted pipeline on this Ubuntu server:

```
Audio source (phone now, wearable later)
  → Tailscale
  → Transcription service (this server)
  → Hermes LLM (this server, already running)
  → Obsidian vault inbox (Yggdrasil, already exists)
```

No third-party cloud APIs. Audio, transcripts and notes never leave hardware we own.

## Current State

- Omi device + Omi app + Omi cloud produce memories.
- Omi cloud POSTs memories to `/omi/webhook` on this server via a public tunnel (ngrok / cloudflared).
- The webhook hands memories to a local Hermes LLM, which writes notes into the Yggdrasil Obsidian vault inbox.
- Repo with the Omi app manifest: `ssb-j-ren/omi-yggdrasil`.

**The existing webhook, tunnel and Hermes setup are working. Do not stop, restart, remove, or change ports on any of them without explicit confirmation from the user.** The new pipeline runs alongside the old one until it is proven.

## Rules for Working on This Server

1. Before any command that stops, removes, recreates, restarts, or re-ports something currently running (docker stop/rm, systemctl restart, port changes), warn in **bold** and wait for confirmation.
2. Decide the approach first, then give one linear plan. Ask if unsure.
3. Code blocks contain only runnable code. Explanations go outside them.
4. Simple over complex. One way to do things. No fallbacks, no backups. Fail fast with clear errors.
5. Surgical changes. Fix root causes. Minimal, targeted logging.

## Step 0 — Discovery (do this first, report back, change nothing)

Report:

- OS version, CPU, RAM, free disk.
- GPU model and VRAM (`nvidia-smi`), or confirm CPU-only.
- How Hermes runs (Docker, systemd, Ollama, llama.cpp, etc.), its port, and its API format.
- Where the `/omi/webhook` handler lives, what language it's written in, and how it writes to the vault.
- Absolute path to the Yggdrasil vault inbox.
- What's listening on which ports (`ss -tlnp`).
- Whether Tailscale is installed.

## Phase 1 — Transcription Service (phone as the mic)

Build one small service, `ygg-ingest`:

1. `POST /audio` accepts an audio file (m4a/wav/opus) from the phone.
2. Silero VAD strips out silence.
3. faster-whisper transcribes the audio (model size chosen to fit the GPU/CPU found in Step 0).
4. The transcript is sent to Hermes using the same prompt/format the existing webhook uses.
5. Hermes's output is written as a markdown note into the vault inbox, matching the existing note format.
6. Raw audio is deleted once the note is written.

Requirements:

- Run it on a new port that doesn't conflict with anything from Step 0.
- Run it as its own systemd service or Docker container (follow whatever Hermes already uses).
- Expose it only over Tailscale. No public tunnel.
- If Whisper, Hermes, or the vault write fails, return an error and log the reason. No silent retries.

Done when: a voice memo recorded on the phone and uploaded over Tailscale shows up as a correct note in the vault inbox.

## Phase 2 — Speaker Labels

Add pyannote diarization so transcripts are labeled by speaker before they go to Hermes.

Done when: a two-person conversation produces a note that attributes statements to separate speakers.

## Phase 3 — Wearable (later, not on this server)

- Hardware: Seeed XIAO nRF52840 Sense + LiPo battery.
- Firmware: stream Opus-compressed audio over Bluetooth.
- Android app: receive the Bluetooth audio, buffer it, upload chunks to `ygg-ingest` over Tailscale.
- Server change: accept Opus chunks on `/audio`.

## Phase 4 — Retire Omi

Only after Phases 1–3 have run reliably for 2+ weeks: with user confirmation, shut down the Omi webhook and its public tunnel.

## Compliance

Always-on recording runs into two-party consent laws in some US states and other countries. Recording must be started by a button press or show a visible indicator. Never record in the background by default.
