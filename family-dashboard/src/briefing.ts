import { createHash } from "node:crypto";
import type { CalEvent } from "./calendar.js";
import type { Config } from "./config.js";
import { chatJson } from "./ollama.js";
import type { Tip } from "./store.js";

export type DaySummary = { label: string; events: CalEvent[]; lunchFor: string[] };

const schema = {
  type: "object",
  properties: {
    tips: {
      type: "array",
      items: {
        type: "object",
        properties: { emoji: { type: "string" }, text: { type: "string" } },
        required: ["emoji", "text"],
      },
    },
  },
  required: ["tips"],
};

function describe(days: DaySummary[]): string {
  return days
    .map((d) => {
      const events = d.events.map((e) => `  - ${e.time}: ${e.title} (${e.calendar})`);
      const lunch = d.lunchFor.length ? `  - Packed lunch needed for: ${d.lunchFor.join(", ")}` : "  - No packed lunches";
      return [`${d.label}:`, ...(events.length ? events : ["  - No events"]), lunch].join("\n");
    })
    .join("\n");
}

export function briefingHash(days: DaySummary[]): string {
  return createHash("sha1").update(describe(days)).digest("hex");
}

export async function generateBriefing(config: Config, days: DaySummary[]): Promise<Tip[]> {
  const kids = config.kids.map((k) => `${k.name} (age ${k.age})`).join(" and ");
  const system =
    `You are a friendly family assistant for two parents with kids ${kids}. ` +
    `Given the family calendar, give 3 to 5 short, practical heads-ups: things to prep, pack, remember, or leave early for. ` +
    `Each tip is one sentence with one fitting emoji. Only reference events that are listed. Never invent events.`;
  const reply = (await chatJson(config.ollamaUrl, config.ollamaModel, system, describe(days), schema)) as { tips: Tip[] };
  if (!Array.isArray(reply.tips)) throw new Error(`Ollama returned malformed tips: ${JSON.stringify(reply)}`);
  return reply.tips;
}
