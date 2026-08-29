import { Client } from '/Users/spectrasynq/SpectraSynq-EDA/EasyEDA-MCP/node_modules/@modelcontextprotocol/sdk/dist/esm/client/index.js';
import { StreamableHTTPClientTransport } from '/Users/spectrasynq/SpectraSynq-EDA/EasyEDA-MCP/node_modules/@modelcontextprotocol/sdk/dist/esm/client/streamableHttp.js';

const url = new URL(process.env.EASYEDA_MCP_HTTP_URL || 'http://127.0.0.1:19733/mcp');

export async function withMcp(fn) {
	const transport = new StreamableHTTPClientTransport(url);
	const client = new Client({ name: 'dec-usb-hub', version: '1.0.0' }, { capabilities: {} });
	await client.connect(transport);
	try {
		return await fn(client);
	} finally {
		await client.close().catch(() => {});
	}
}

export async function callTool(client, name, args = {}, timeout = 300000) {
	const res = await client.callTool({ name, arguments: args }, undefined, { timeout });
	const text = (res?.content || []).filter(c => c.type === 'text').map(c => c.text).join('\n');
	if (res?.isError) throw new Error(`${name} error: ${text || JSON.stringify(res)}`);
	if (!text) return res;
	try { return JSON.parse(text); } catch { return text; }
}

export function unwrap(result) {
	if (result && typeof result === 'object' && result.result && typeof result.result === 'object') {
		return result.result;
	}
	return result;
}
