const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const LIVE = '64325d0e55e0435abd018defb0089a9b';
const HUB = '41c8e6523576456582ea35958b3684ed';
const ORACLE = 'dcd7e3cab2a24b9aa6e531d2b62e1b6f';
const SCAR = '54d2a25bce4b44c3af878e8b91af3554';
const HUSK = 'f0f6cd233d69411ea478de1037da28fc';
const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const pages = targets.filter((t) => t.type === 'page');
const out = pages.map((t) => ({
  title: (t.title || '').slice(0, 90),
  url: (t.url || '').slice(0, 200),
  live: String(t.url).includes(LIVE),
  hub: String(t.url).includes(HUB),
  oracle: String(t.url).includes(ORACLE),
  scar: String(t.url).includes(SCAR),
  husk: String(t.url).includes(HUSK),
}));
console.log(JSON.stringify({ count: out.length, pages: out }, null, 2));
if (out.length && out.every((p) => p.live)) process.exit(2);
