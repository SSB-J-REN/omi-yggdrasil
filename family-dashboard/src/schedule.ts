import type { CalEvent } from "./calendar.js";
import type { Kid } from "./config.js";
import { weekday } from "./dates.js";

function titleHas(events: CalEvent[], keyword: string): boolean {
  const k = keyword.toLowerCase();
  return events.some((e) => e.title.toLowerCase().includes(k));
}

// Does this kid need a packed lunch on `day`? `dayEvents` are the calendar events touching that day.
export function needsLunch(kid: Kid, day: string, dayEvents: CalEvent[]): boolean {
  const rule = kid.lunch;
  if (rule.mode === "calendar") return titleHas(dayEvents, rule.keyword);
  return rule.weekdays.includes(weekday(day)) && !rule.skipKeywords.some((k) => titleHas(dayEvents, k));
}
