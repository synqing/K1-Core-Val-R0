const targets = await (await fetch('http://127.0.0.1:9223/json/list', { signal: AbortSignal.timeout(3000) })).json();
for (const t of targets) {
	if (t.type === 'page') console.log(JSON.stringify({ title: t.title, url: t.url }));
}
