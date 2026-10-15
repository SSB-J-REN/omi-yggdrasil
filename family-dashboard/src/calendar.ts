import ical, { type VEvent } from "node-ical";
import type { CalendarSource } from "./config.js";
import { addDays, dateKey, parseKey } from "./dates.js";

export type CalEvent = {
  title: string;
  start: string;
  end: string;
  allDay: boolean;
  time: string; // formatted in the server's TZ so the tablet's clock setting can't skew it
  calendar: string;
  color: string;
  days: string[];
};

const CACHE_MS = 10 * 60 * 1000;
const cache = new Map<string, { fetchedAt: number; text: string }>();

async function fetchIcs(url: string): Promise<string> {
  const hit = cache.get(url);
  if (hit && Date.now() - hit.fetchedAt < CACHE_MS) return hit.text;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Calendar fetch failed: HTTP ${res.status}`);
  const text = await res.text();
  cache.set(url, { fetchedAt: Date.now(), text });
  return text;
}

function summaryText(summary: unknown): string {
  if (typeof summary === "string") return summary;
  if (summary && typeof summary === "object" && "val" in summary) return String(summary.val);
  return "(untitled)";
}

// Local date keys the instance touches. All-day ends are exclusive; a timed event ending at midnight doesn't spill over.
function coveredDays(start: Date, end: Date): string[] {
  const first = dateKey(start);
  const last = dateKey(end > start ? new Date(end.getTime() - 1) : start);
  const days: string[] = [];
  for (let k = first; k <= last; k = addDays(k, 1)) days.push(k);
  return days;
}

export async function loadEvents(sources: CalendarSource[], fromKey: string, days: number): Promise<CalEvent[]> {
  const from = parseKey(fromKey);
  const to = parseKey(addDays(fromKey, days));
  const events: CalEvent[] = [];
  const seen = new Set<string>(); // the same event shows up on both parents' calendars when both are invited

  for (const source of sources) {
    const parsed = ical.sync.parseICS(await fetchIcs(source.url));
    for (const component of Object.values(parsed)) {
      if (!component || component.type !== "VEVENT") continue;
      const vevent = component as VEvent;
      if (vevent.status === "CANCELLED") continue;
      const instances = ical.expandRecurringEvent(vevent, { from, to, expandOngoing: true });
      for (const inst of instances) {
        if (inst.event.status === "CANCELLED") continue;
        if (inst.end <= from || inst.start >= to) continue;
        const id = `${inst.event.uid}|${inst.start.toISOString()}`;
        if (seen.has(id)) continue;
        seen.add(id);
        events.push({
          title: summaryText(inst.summary),
          start: inst.start.toISOString(),
          end: inst.end.toISOString(),
          allDay: inst.isFullDay,
          time: inst.isFullDay ? "All day" : inst.start.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" }),
          calendar: source.name,
          color: source.color,
          days: coveredDays(inst.start, inst.end),
        });
      }
    }
  }

  return events.sort((a, b) => Number(b.allDay) - Number(a.allDay) || a.start.localeCompare(b.start));
}
