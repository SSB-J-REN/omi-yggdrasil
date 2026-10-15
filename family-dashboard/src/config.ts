import { readFileSync } from "node:fs";
import { ageOn, parseKey, todayKey } from "./dates.js";

export type ChecklistItem = { title: string; emoji: string };

export type LunchRule =
  | { mode: "weekdays"; weekdays: number[]; skipKeywords: string[]; place: string }
  | { mode: "calendar"; keyword: string; place: string };

export type Kid = {
  id: string;
  name: string;
  birthday: string; // YYYY-MM-DD
  emoji: string;
  color: string;
  lunch: LunchRule;
  routines: { morning: ChecklistItem[]; evening: ChecklistItem[] };
};

export type CalendarSource = { name: string; color: string; url: string };

export type Config = {
  kids: Kid[];
  calendars: CalendarSource[];
  bannedIngredients: string[];
  lunchNotes: string;
  ollamaUrl: string;
  ollamaModel: string;
};

type RawCalendar = { name: string; color: string; urlEnv: string };
type RawConfig = Omit<Config, "calendars" | "ollamaUrl" | "ollamaModel"> & { calendars: RawCalendar[] };

export function ageOf(kid: Kid): number {
  return ageOn(kid.birthday, todayKey());
}

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) throw new Error(`Missing required environment variable ${name}`);
  return value;
}

export function loadConfig(path: string): Config {
  const raw = JSON.parse(readFileSync(path, "utf8")) as RawConfig;
  if (raw.kids.length === 0) throw new Error("family.json must define at least one kid");
  if (raw.bannedIngredients.length === 0) throw new Error("family.json must list bannedIngredients");
  for (const kid of raw.kids) {
    parseKey(kid.birthday);
    if (kid.lunch.mode !== "weekdays" && kid.lunch.mode !== "calendar") {
      throw new Error(`Kid ${kid.id}: lunch.mode must be "weekdays" or "calendar"`);
    }
  }
  return {
    ...raw,
    calendars: raw.calendars.map((c) => ({ name: c.name, color: c.color, url: requireEnv(c.urlEnv) })),
    ollamaUrl: requireEnv("OLLAMA_URL"),
    ollamaModel: requireEnv("OLLAMA_MODEL"),
  };
}
