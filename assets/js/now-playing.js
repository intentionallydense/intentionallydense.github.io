// Now-playing line on the homepage, from Last.fm's public recent-tracks API.
// The key is a read-only Last.fm API key made for this widget; it is meant to
// be public (the shared secret is not used and never belongs here).
// Used by: index.html (#now-playing). Hides itself if Last.fm is unreachable.
(function () {
  const USER = "svylai";
  const API_KEY = "f183876382be7661c6cbec10c20d4df2";
  const URL =
    "https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks" +
    `&user=${USER}&api_key=${API_KEY}&limit=1&format=json`;
  const REFRESH_MS = 60 * 1000;

  const el = document.getElementById("now-playing");
  if (!el) return;

  function ago(unixSeconds) {
    const s = Math.max(0, Date.now() / 1000 - unixSeconds);
    if (s < 3600) return `${Math.max(1, Math.round(s / 60))}m ago`;
    if (s < 86400) return `${Math.round(s / 3600)}h ago`;
    return `${Math.round(s / 86400)}d ago`;
  }

  function render(track) {
    const playing = track["@attr"] && track["@attr"].nowplaying === "true";
    const art = (track.image || []).find((i) => i.size === "medium");

    el.replaceChildren();

    if (art && art["#text"]) {
      const img = document.createElement("img");
      img.src = art["#text"];
      img.alt = "";
      img.className = "now-playing-art";
      el.append(img);
    }

    const text = document.createElement("span");
    const label = document.createElement("span");
    label.className = "now-playing-label";
    label.textContent = playing ? "listening to" : "last played";

    const link = document.createElement("a");
    link.href = track.url;
    link.target = "_blank";
    link.rel = "noopener";
    link.textContent = `${track.name} — ${track.artist["#text"]}`;

    text.append(label, document.createElement("br"), link);
    if (!playing && track.date) {
      const when = document.createElement("span");
      when.className = "now-playing-label";
      when.textContent = ` · ${ago(Number(track.date.uts))}`;
      text.append(when);
    }
    el.append(text);

    el.classList.toggle("is-playing", playing);
    el.hidden = false;
  }

  async function refresh() {
    try {
      const res = await fetch(URL);
      if (!res.ok) throw new Error(res.status);
      const data = await res.json();
      const track = data.recenttracks && data.recenttracks.track && data.recenttracks.track[0];
      if (track) render(track);
    } catch (e) {
      // Leave whatever was last shown; stays hidden if it never loaded.
    }
  }

  refresh();
  setInterval(() => {
    if (!document.hidden) refresh();
  }, REFRESH_MS);
})();
