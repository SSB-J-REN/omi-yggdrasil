# Omi → Yggdrasil Vault

Sends Omi memories to a local Obsidian vault via webhook.

## Setup
No setup needed. Memories are automatically routed to the vault inbox and processed by a local Hermes LLM.

## Webhook
`POST https://interactions-suggestions-rebecca-iii.trycloudflare.com/omi/webhook`

This is the single source of truth for the webhook endpoint. It **must** match
the `external_integration.webhook_url` field in `app.json` — if the two ever
disagree, the integration is misconfigured.

## Using a stable URL (recommended)

The current URL is a Cloudflare **quick tunnel**. Quick tunnels (and `ngrok-free`
URLs) are ephemeral: they get a new random address every time the local process
restarts. When the URL goes stale, Omi keeps firing a webhook on every memory
creation to a dead endpoint — repeated failing network calls that can wake the
phone's radio and drain the battery.

To make this stable, point the webhook at a domain you control that does **not**
rotate, for example:

- a reserved ngrok domain: `https://<your-subdomain>.ngrok.app/omi/webhook`
- a named Cloudflare Tunnel bound to your domain: `https://omi.<yourdomain>.com/omi/webhook`
- your own host/VPS: `https://api.<yourdomain>.com/omi/webhook`

When you have that URL, update it in **two places** and keep them identical:

1. `external_integration.webhook_url` in `app.json`
2. The `## Webhook` line above
