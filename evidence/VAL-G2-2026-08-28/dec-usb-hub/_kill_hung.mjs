import { execSync } from 'node:child_process';
const out = execSync('ps -ax -o pid=,command=', { encoding: 'utf8' });
const mine = out.split('\n').filter((line) =>
	/_t00_fp_cutout|_restore_sch|_t00_fp_rebuild|mcp_http_call|mcp_batch/.test(line)
);
console.log(mine.join('\n') || 'none');
for (const line of mine) {
	const pid = Number(line.trim().split(/\s+/)[0]);
	if (pid && pid !== process.pid) {
		try { process.kill(pid, 'SIGKILL'); console.log('killed', pid); } catch (e) { console.log('no', pid, e.message); }
	}
}
