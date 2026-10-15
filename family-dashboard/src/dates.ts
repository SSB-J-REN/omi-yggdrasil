// All date keys are local-time "YYYY-MM-DD" strings. The container's TZ env decides "local".

export function dateKey(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

export function parseKey(key: string): Date {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(key);
  if (!match) throw new Error(`Invalid date key: ${key}`);
  return new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
}

export function addDays(key: string, n: number): string {
  const d = parseKey(key);
  d.setDate(d.getDate() + n);
  return dateKey(d);
}

export function todayKey(): string {
  return dateKey(new Date());
}

// Monday of the week containing `key`.
export function weekStart(key: string): string {
  const offset = (parseKey(key).getDay() + 6) % 7;
  return addDays(key, -offset);
}

// Whole years old on `day`, so ages roll over on birthdays without a config change.
export function ageOn(birthday: string, day: string): number {
  const b = parseKey(birthday);
  const d = parseKey(day);
  const hadBirthday = d.getMonth() > b.getMonth() || (d.getMonth() === b.getMonth() && d.getDate() >= b.getDate());
  return d.getFullYear() - b.getFullYear() - (hadBirthday ? 0 : 1);
}

export function weekday(key: string): number {
  return parseKey(key).getDay();
}
