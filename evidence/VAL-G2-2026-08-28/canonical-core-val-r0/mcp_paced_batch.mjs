#!/usr/bin/env node
import { readFileSync, writeFileSync } from 'node:fs';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';

const [, , jobsPath, outPath] = process.argv;
const delayMs = Number(process.env.PACE_MS || 200);
if (!jobsPath || !outPath) {
  console.error('usage: mcp_paced_batch.mjs <jobs.json> <results.json>');
  process.exit(2);
}
const jobs = JSON.parse(readFileSync(jobsPath, 'utf8'));
const url = new URL(process.env.EASYEDA_MCP_HTTP_URL || 'http://127.0.0.1:19733/mcp');
const transport = new StreamableHTTPClientTransport(url);
const client = new Client({ name: 'paced-batch', version: '1.0.0' }, { capabilities: {} });
const results = [];
let ok = 0, failed = 0;
const sleep = ms => new Promise(r => setTimeout(r, ms));
await client.connect(transport);
try {
  for (let i = 0; i < jobs.length; i++) {
    const job = jobs[i];
    try {
      const res = await client.callTool({ name: job.tool, arguments: job.args ?? {} }, undefined, { timeout: 120000 });
      let payload = res.structuredContent;
      if (payload === undefined) {
        const text = (res.content ?? []).find((c) => c.type === 'text')?.text;
        try { payload = text ? JSON.parse(text) : null; } catch { payload = text ?? null; }
      }
      if (res.isError) {
        results.push({ tag: job.tag ?? i, ok: false, error: String(payload).slice(0, 400) });
        failed++;
      } else {
        results.push({ tag: job.tag ?? i, ok: true, result: payload });
        ok++;
      }
    } catch (err) {
      results.push({ tag: job.tag ?? i, ok: false, error: String(err?.message ?? err).slice(0, 400) });
      failed++;
    }
    if (i < jobs.length - 1) await sleep(delayMs);
  }
} finally {
  try { await client.close(); } catch {}
}
writeFileSync(outPath, JSON.stringify(results, null, 1));
console.error(`paced batch: ${ok} ok, ${failed} failed`);
process.exit(failed ? 1 : 0);
