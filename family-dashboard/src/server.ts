import { randomUUID } from "node:crypto";
import express, { type NextFunction, type Request, type Response } from "express";
import { briefingHash, generateBriefing, type DaySummary } from "./briefing.js";
import { loadEvents, type CalEvent } from "./calendar.js";
import { loadConfig, type ChecklistItem, type Kid } from "./config.js";
import { addDays, parseKey, todayKey, weekStart } from "./dates.js";
import { generateLunch } from "./lunch.js";
import { needsLunch } from "./schedule.js";
import { Store, type Lunch } from "./store.js";

const DAYS_AHEAD = 7;
const config = loadConfig(process.env.CONFIG_PATH ?? "/app/config/family.json");
const store = new Store(process.env.STATE_PATH ?? "/app/data/state.json");
const app = express();
app.use(express.json());
app.use(express.static("public"));

function slug(s: string): string {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}

function dayLabel(day: string, today: string): string {
  if (day === today) return "Today";
  if (day === addDays(today, 1)) return "Tomorrow";
  return parseKey(day).toLocaleDateString("en-US", { weekday: "long", month: "short", day: "numeric" });
}

function findKid(id: unknown): Kid {
  const kid = config.kids.find((k) => k.id === id);
  if (!kid) throw new Error(`Unknown kid: ${String(id)}`);
  return kid;
}

async function upcomingDays(today: string): Promise<(DaySummary & { date: string })[]> {
  const events = await loadEvents(config.calendars, today, DAYS_AHEAD);
  return Array.from({ length: DAYS_AHEAD }, (_, i) => {
    const date = addDays(today, i);
    const dayEvents = events.filter((e: CalEvent) => e.days.includes(date));
    return {
      date,
      label: dayLabel(date, today),
      events: dayEvents,
      lunchFor: config.kids.filter((k) => needsLunch(k, date, dayEvents)).map((k) => k.name),
    };
  });
}

function checklist(kid: Kid, today: string) {
  const done = store.state.checks[today]?.[kid.id] ?? {};
  const routine = (section: "morning" | "evening", items: ChecklistItem[]) =>
    items.map((item) => ({ id: `${section}:${slug(item.title)}`, section, ...item }));
  const tasks = (store.state.tasks[today] ?? [])
    .filter((t) => t.kidId === kid.id)
    .map((t) => ({ id: `task:${t.id}`, section: "task", title: t.title, emoji: t.emoji, taskId: t.id }));
  return [...routine("morning", kid.routines.morning), ...routine("evening", kid.routines.evening), ...tasks].map((item) => ({
    ...item,
    done: done[item.id] === true,
  }));
}

function weekStars(kid: Kid, today: string): number {
  let stars = 0;
  for (let d = weekStart(today); d <= today; d = addDays(d, 1)) {
    stars += Object.values(store.state.checks[d]?.[kid.id] ?? {}).filter(Boolean).length;
  }
  return stars;
}

// One generation per (date, kid) at a time, so the tablet and a phone refreshing together don't double-call Ollama.
const inFlight = new Map<string, Promise<Lunch>>();

function recentLunches(kid: Kid, before: string): string[] {
  return Object.keys(store.state.lunches)
    .filter((d) => d < before && d >= addDays(before, -14))
    .flatMap((d) => store.state.lunches[d]?.[kid.id]?.name ?? []);
}

function lunchFor(kid: Kid, date: string): Promise<Lunch> {
  const cached = store.state.lunches[date]?.[kid.id];
  if (cached) return Promise.resolve(cached);
  const key = `${date}:${kid.id}`;
  const pending = inFlight.get(key);
  if (pending) return pending;
  const job = generateLunch(config, kid, recentLunches(kid, date))
    .then((lunch) => {
      store.state.lunches[date] = { ...store.state.lunches[date], [kid.id]: lunch };
      store.save();
      return lunch;
    })
    .finally(() => inFlight.delete(key));
  inFlight.set(key, job);
  return job;
}

app.get("/api/dashboard", async (_req, res) => {
  const today = todayKey();
  const days = await upcomingDays(today);
  res.json({
    today,
    days,
    kids: config.kids.map((kid) => ({
      id: kid.id,
      name: kid.name,
      emoji: kid.emoji,
      color: kid.color,
      weekStars: weekStars(kid, today),
      items: checklist(kid, today),
    })),
  });
});

app.get("/api/lunches", async (_req, res) => {
  const today = todayKey();
  const days = await upcomingDays(today);
  // Per kid: today's lunch (if any) and the next lunch day, which is what gets prepped tonight.
  const slots = config.kids.flatMap((kid) => {
    const lunchDays = days.filter((d) => d.lunchFor.includes(kid.name));
    const picks = lunchDays.filter((d, i) => d.date === today || i === lunchDays.findIndex((x) => x.date > today));
    return picks.map((d) => ({ kid, date: d.date, label: d.label }));
  });
  const results = await Promise.allSettled(slots.map((s) => lunchFor(s.kid, s.date)));
  res.json(
    slots.map((s, i) => {
      const r = results[i]!;
      return {
        kidId: s.kid.id,
        kidName: s.kid.name,
        emoji: s.kid.emoji,
        color: s.kid.color,
        place: s.kid.lunch.place,
        date: s.date,
        label: s.label,
        lunch: r.status === "fulfilled" ? r.value : null,
        error: r.status === "rejected" ? String(r.reason instanceof Error ? r.reason.message : r.reason) : null,
      };
    }),
  );
});

app.post("/api/lunches/regenerate", async (req, res) => {
  const kid = findKid(req.body.kidId);
  const date = String(req.body.date);
  parseKey(date);
  delete store.state.lunches[date]?.[kid.id];
  store.save();
  res.json(await lunchFor(kid, date));
});

app.get("/api/briefing", async (_req, res) => {
  const today = todayKey();
  const days = (await upcomingDays(today)).slice(0, 2);
  const hash = briefingHash(days);
  const cached = store.state.briefings[today];
  if (cached && cached.hash === hash) {
    res.json(cached.tips);
    return;
  }
  const tips = await generateBriefing(config, days);
  store.state.briefings[today] = { hash, tips };
  store.save();
  res.json(tips);
});

app.post("/api/check", (req, res) => {
  const kid = findKid(req.body.kidId);
  const itemId = String(req.body.itemId);
  const today = todayKey();
  if (!checklist(kid, today).some((i) => i.id === itemId)) throw new Error(`Unknown checklist item: ${itemId}`);
  const day = (store.state.checks[today] ??= {});
  (day[kid.id] ??= {})[itemId] = req.body.done === true;
  store.save();
  res.json({ ok: true });
});

app.post("/api/tasks", (req, res) => {
  const kid = findKid(req.body.kidId);
  const title = String(req.body.title ?? "").trim();
  if (!title) throw new Error("Task title is required");
  const emoji = String(req.body.emoji ?? "").trim() || "⭐";
  const task = { id: randomUUID(), kidId: kid.id, title, emoji };
  (store.state.tasks[todayKey()] ??= []).push(task);
  store.save();
  res.json(task);
});

app.delete("/api/tasks/:id", (req, res) => {
  const today = todayKey();
  const tasks = store.state.tasks[today] ?? [];
  const index = tasks.findIndex((t) => t.id === req.params.id);
  if (index === -1) throw new Error(`Unknown task: ${req.params.id}`);
  tasks.splice(index, 1);
  store.save();
  res.json({ ok: true });
});

app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  console.error(err);
  res.status(500).json({ error: err.message });
});

const port = Number(process.env.PORT ?? 8080);
app.listen(port, () => console.log(`Family dashboard on :${port} (TZ=${process.env.TZ ?? "system"})`));
