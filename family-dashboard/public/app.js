// Plain ES2017 so older Android WebViews can run it: no optional chaining, no build step.
"use strict";

var state = { dashboard: null, taskKid: null };

function $(id) { return document.getElementById(id); }

function esc(s) {
  return String(s).replace(/[&<>"']/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
  });
}

async function api(method, path, body) {
  var res = await fetch(path, {
    method: method,
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  var data = await res.json();
  if (!res.ok) throw new Error(data.error || "HTTP " + res.status);
  return data;
}

function showError(err) {
  var box = $("error");
  if (err) { box.textContent = "⚠️ " + err.message; box.hidden = false; } else { box.hidden = true; }
}

function tickClock() {
  var now = new Date();
  $("clock").textContent = now.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" });
  $("date").textContent = now.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" });
}

// ---- Calendar ----
function renderCalendar(days, kids) {
  var kidColor = {};
  kids.forEach(function (k) { kidColor[k.name] = k.color; });
  $("calendar").innerHTML = days.map(function (day) {
    var badges = day.lunchFor.map(function (name) {
      return '<span class="badge" style="background:' + kidColor[name] + '">🥪 ' + esc(name) + "</span>";
    }).join("");
    var events = day.events.map(function (e) {
      return '<div class="event" style="border-color:' + e.color + '"><span class="event-time">' + esc(e.time) +
        '</span><span class="event-title">' + esc(e.title) + "</span></div>";
    }).join("");
    return '<div class="day"><div class="day-label">' + esc(day.label) + "</div>" +
      (badges ? '<div class="day-badges">' + badges + "</div>" : "") +
      (events || '<div class="muted">Nothing planned</div>') + "</div>";
  }).join("");
}

// ---- Kids' checklists ----
var SECTIONS = [
  { key: "morning", title: "☀️ Morning" },
  { key: "evening", title: "🌙 Evening" },
  { key: "task", title: "⭐ Extra tasks" },
];

function renderKids(kids) {
  var afternoon = new Date().getHours() >= 14;
  var order = afternoon ? [SECTIONS[1], SECTIONS[2], SECTIONS[0]] : SECTIONS;
  $("kids").innerHTML = kids.map(function (kid) {
    var done = kid.items.filter(function (i) { return i.done; }).length;
    var pct = kid.items.length ? Math.round((done / kid.items.length) * 100) : 0;
    var sections = order.map(function (sec) {
      var items = kid.items.filter(function (i) { return i.section === sec.key; });
      if (!items.length) return "";
      return '<div class="section-title">' + sec.title + "</div>" + items.map(function (item) {
        return '<button class="item' + (item.done ? " done" : "") + '" data-kid="' + kid.id + '" data-item="' + esc(item.id) + '">' +
          '<span class="item-emoji">' + esc(item.emoji) + '</span><span class="item-title">' + esc(item.title) + "</span>" +
          '<span class="item-check">' + (item.done ? "✓" : "") + "</span>" +
          (item.taskId ? '<span class="item-delete" data-task="' + item.taskId + '">✕</span>' : "") + "</button>";
      }).join("");
    }).join("");
    return '<div class="kid" style="--kid:' + kid.color + '"><div class="kid-head"><span class="kid-name">' + esc(kid.emoji) + " " + esc(kid.name) +
      '</span><span class="stars">⭐ ' + kid.weekStars + " this week</span></div>" +
      '<div class="progress"><div style="width:' + pct + '%"></div></div>' +
      (pct === 100 ? '<div class="all-done">🎉 All done! Amazing job! 🎉</div>' : "") + sections + "</div>";
  }).join("");
}

function celebrate(emoji) {
  var party = $("party");
  var pieces = [emoji, "🎉", "⭐", "🌈", "✨"];
  for (var i = 0; i < 30; i++) {
    var p = document.createElement("div");
    p.className = "confetti";
    p.textContent = pieces[i % pieces.length];
    p.style.left = Math.random() * 100 + "vw";
    p.style.animationDelay = Math.random() * 0.8 + "s";
    party.appendChild(p);
  }
  setTimeout(function () { party.innerHTML = ""; }, 3600);
}

$("kids").addEventListener("click", async function (ev) {
  var del = ev.target.closest(".item-delete");
  var btn = ev.target.closest(".item");
  if (!btn) return;
  try {
    if (del) {
      await api("DELETE", "/api/tasks/" + del.getAttribute("data-task"));
    } else {
      var kid = state.dashboard.kids.filter(function (k) { return k.id === btn.getAttribute("data-kid"); })[0];
      var item = kid.items.filter(function (i) { return i.id === btn.getAttribute("data-item"); })[0];
      item.done = !item.done;
      kid.weekStars += item.done ? 1 : -1;
      renderKids(state.dashboard.kids);
      if (item.done && kid.items.every(function (i) { return i.done; })) celebrate(kid.emoji);
      await api("POST", "/api/check", { kidId: kid.id, itemId: item.id, done: item.done });
    }
    await loadDashboard();
  } catch (err) { showError(err); }
});

// ---- Lunches & tips ----
function renderLunches(slots) {
  if (!slots.length) { $("lunches").innerHTML = '<p class="muted">No packed lunches coming up this week.</p>'; return; }
  $("lunches").innerHTML = slots.map(function (s) {
    var body = s.lunch
      ? '<div class="lunch-name">' + esc(s.lunch.name) + "</div><ul>" +
        s.lunch.items.map(function (i) { return "<li>" + esc(i) + "</li>"; }).join("") + "</ul>" +
        '<div class="lunch-prep">🕗 Prep (~' + s.lunch.prepMinutes + " min): " + esc(s.lunch.prep) + "</div>"
      : '<div class="lunch-error">Couldn\'t make a lunch idea: ' + esc(s.error) + "</div>";
    return '<div class="lunch" style="--kid:' + s.color + '"><div class="lunch-for">' + esc(s.emoji) + " " + esc(s.kidName) +
      " · " + esc(s.label) + " at " + esc(s.place) + "</div>" + body +
      '<button class="pill small ghost" data-regen="' + s.kidId + '" data-date="' + s.date + '">🔄 New idea</button></div>';
  }).join("") + '<p class="disclaimer">AI suggestions, screened for peanut and fish words. Still check labels for "may contain" warnings.</p>';
}

$("lunches").addEventListener("click", async function (ev) {
  var btn = ev.target.closest("[data-regen]");
  if (!btn) return;
  btn.textContent = "Thinking…";
  btn.disabled = true;
  try {
    await api("POST", "/api/lunches/regenerate", { kidId: btn.getAttribute("data-regen"), date: btn.getAttribute("data-date") });
    await loadLunches();
  } catch (err) { showError(err); btn.textContent = "🔄 New idea"; btn.disabled = false; }
});

function renderTips(tips) {
  $("tips").innerHTML = tips.map(function (t) {
    return "<li><span>" + esc(t.emoji) + "</span><span>" + esc(t.text) + "</span></li>";
  }).join("") || '<li class="muted">Nothing special today.</li>';
}

// ---- Add-task dialog ----
$("addTaskBtn").addEventListener("click", function () {
  var kids = state.dashboard.kids;
  state.taskKid = kids[0].id;
  $("kidPicker").innerHTML = kids.map(function (k) {
    return '<button type="button" data-kid="' + k.id + '" style="--kid:' + k.color + '">' + esc(k.emoji) + " " + esc(k.name) + "</button>";
  }).join("");
  pickKid(state.taskKid);
  $("taskTitle").value = "";
  $("taskEmoji").value = "";
  $("dialog").hidden = false;
  $("taskTitle").focus();
});

function pickKid(id) {
  state.taskKid = id;
  Array.prototype.forEach.call($("kidPicker").children, function (b) {
    b.className = b.getAttribute("data-kid") === id ? "selected" : "";
  });
}

$("kidPicker").addEventListener("click", function (ev) {
  var b = ev.target.closest("[data-kid]");
  if (b) pickKid(b.getAttribute("data-kid"));
});
$("cancelTask").addEventListener("click", function () { $("dialog").hidden = true; });
$("taskForm").addEventListener("submit", async function (ev) {
  ev.preventDefault();
  try {
    await api("POST", "/api/tasks", { kidId: state.taskKid, title: $("taskTitle").value, emoji: $("taskEmoji").value });
    $("dialog").hidden = true;
    await loadDashboard();
  } catch (err) { showError(err); }
});

// ---- Loading ----
async function loadDashboard() {
  state.dashboard = await api("GET", "/api/dashboard");
  renderCalendar(state.dashboard.days, state.dashboard.kids);
  renderKids(state.dashboard.kids);
  showError(null);
}
async function loadLunches() { renderLunches(await api("GET", "/api/lunches")); }
async function loadTips() { renderTips(await api("GET", "/api/briefing")); }

function every(fn, ms) {
  function run() { fn().catch(showError); }
  run();
  setInterval(run, ms);
}

tickClock();
setInterval(tickClock, 10000);
every(loadDashboard, 60 * 1000);
every(loadLunches, 15 * 60 * 1000);
every(loadTips, 15 * 60 * 1000);
