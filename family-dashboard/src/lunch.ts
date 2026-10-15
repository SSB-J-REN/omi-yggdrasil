import type { Config, Kid } from "./config.js";
import { chatJson } from "./ollama.js";
import type { Lunch } from "./store.js";

const MAX_ATTEMPTS = 3;

const schema = {
  type: "object",
  properties: {
    name: { type: "string" },
    items: { type: "array", items: { type: "string" } },
    prep: { type: "string" },
    prepMinutes: { type: "integer" },
  },
  required: ["name", "items", "prep", "prepMinutes"],
};

// Word-start match so "peanuts" and "sardines" are caught while "goldfish" crackers (no fish) are not.
export function findBanned(lunch: Pick<Lunch, "name" | "items" | "prep">, banned: string[]): string[] {
  const text = [lunch.name, ...lunch.items, lunch.prep].join(" ").toLowerCase();
  return banned.filter((term) => new RegExp(`\\b${term.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}`).test(text));
}

function isLunchShape(v: unknown): v is Omit<Lunch, "generatedAt"> {
  if (!v || typeof v !== "object") return false;
  const o = v as Record<string, unknown>;
  return (
    typeof o.name === "string" &&
    Array.isArray(o.items) &&
    o.items.every((i) => typeof i === "string") &&
    typeof o.prep === "string" &&
    typeof o.prepMinutes === "number"
  );
}

export async function generateLunch(config: Config, kid: Kid, recent: string[]): Promise<Lunch> {
  const system =
    `You plan quick, kid-friendly packed lunches for a ${kid.age}-year-old eating at ${kid.lunch.place}. ` +
    `STRICT ALLERGY RULES: never include peanuts or any peanut product, and never include finned fish of any kind ` +
    `(including tuna, salmon, anchovy, fish sauce, Caesar dressing, Worcestershire, or imitation crab). ` +
    `${config.lunchNotes} The lunch must be packable the night before and need no reheating. ` +
    `"prep" is short night-before instructions for a parent.`;
  const user =
    `Suggest one lunch for ${kid.name}. Avoid repeating these recent lunches: ${recent.join("; ") || "none yet"}.`;

  const rejected: string[] = [];
  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    const reply = await chatJson(config.ollamaUrl, config.ollamaModel, system, user, schema);
    if (!isLunchShape(reply)) throw new Error(`Ollama returned a malformed lunch: ${JSON.stringify(reply)}`);
    const hits = findBanned(reply, config.bannedIngredients);
    if (hits.length === 0) return { ...reply, generatedAt: new Date().toISOString() };
    console.warn(`[lunch] rejected "${reply.name}" for ${kid.name}: contains ${hits.join(", ")}`);
    rejected.push(`${reply.name} (${hits.join(", ")})`);
  }
  throw new Error(`Every lunch suggestion for ${kid.name} hit a banned ingredient: ${rejected.join("; ")}`);
}
