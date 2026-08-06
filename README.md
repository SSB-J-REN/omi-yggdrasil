# Omi → Yggdrasil Vault

Sends Omi memories to a local Obsidian vault via webhook.

## Setup
No setup needed. Memories are automatically routed to the vault inbox and processed by a local Hermes LLM.

## Webhook
`POST https://interactions-suggestions-rebecca-iii.trycloudflare.com/omi/webhook`

> **Note:** This is a Cloudflare *quick tunnel* (`trycloudflare.com`). Quick tunnels are
> ephemeral — they get a new random hostname each time the tunnel restarts and stop working
> when the tunnel process is down. Whenever the hostname changes, update **both** this README
> and the `webhook_url` in `app.json` so they stay in sync. For a stable endpoint, use a named
> Cloudflare tunnel or a reserved ngrok domain instead.
