import { existsSync, readFileSync, renameSync, writeFileSync } from "node:fs";

export type Lunch = { name: string; items: string[]; prep: string; prepMinutes: number; generatedAt: string };
export type Tip = { emoji: string; text: string };
export type Task = { id: string; kidId: string; title: string; emoji: string };
export type Reward = { redeemedOn: string; reward: string };

export type State = {
  checks: Record<string, Record<string, Record<string, boolean>>>; // date -> kid -> itemId -> done
  tasks: Record<string, Task[]>; // date -> one-off tasks
  lunches: Record<string, Record<string, Lunch>>; // date -> kid -> lunch
  briefings: Record<string, { hash: string; tips: Tip[] }>; // date -> tips
  perfectDays: Record<string, string[]>; // kid -> dates every item was done (one gold star each)
  rewards: Record<string, Reward[]>; // kid -> rewards handed out, one per 7 gold stars
};

export class Store {
  readonly state: State;

  constructor(private readonly path: string) {
    this.state = existsSync(path)
      ? (JSON.parse(readFileSync(path, "utf8")) as State)
      : { checks: {}, tasks: {}, lunches: {}, briefings: {}, perfectDays: {}, rewards: {} };
  }

  save(): void {
    const tmp = `${this.path}.tmp`;
    writeFileSync(tmp, JSON.stringify(this.state, null, 2));
    renameSync(tmp, this.path);
  }
}
