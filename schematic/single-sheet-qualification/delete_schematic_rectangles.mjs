#!/usr/bin/env node

// Remove an explicitly enumerated set of schematic rectangle primitives through
// the documented EasyEDA Pro API, then prove the deletion by API read-back.

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PAGE_UUID = '1991698f35bf4c09b8de4bcf78bd2b7b';
const primitiveIds = process.argv.slice(2);

if (primitiveIds.length === 0)
	throw new Error('At least one rectangle primitive ID is required');

const targets = await (await fetch(`${CDP_BASE}/json/list`, {
	signal: AbortSignal.timeout(3000),
})).json();
const page = targets.find(target => target.type === 'page' && String(target.url).includes('pro.easyeda.com'));
if (!page)
	throw new Error('No EasyEDA page target');

const socket = new WebSocket(page.webSocketDebuggerUrl);
let sequence = 0;
const pending = new Map();
const contexts = [];
socket.onmessage = event => {
	const message = JSON.parse(event.data);
	if (message.id && pending.has(message.id)) {
		pending.get(message.id)(message);
		pending.delete(message.id);
	}
	if (message.method === 'Runtime.executionContextCreated')
		contexts.push(message.params.context);
};
await new Promise(resolve => { socket.onopen = resolve; });
const send = (method, params = {}) => new Promise(resolve => {
	const id = ++sequence;
	pending.set(id, resolve);
	socket.send(JSON.stringify({ id, method, params }));
});

try {
	await send('Runtime.enable');
	const tree = await send('Page.getFrameTree');
	const frames = [];
	const visit = node => {
		if (node?.frame)
			frames.push(node.frame);
		for (const child of node.childFrames || [])
			visit(child);
	};
	visit(tree.result?.frameTree || tree.result);
	await new Promise(resolve => setTimeout(resolve, 300));
	const frame = frames.find(item => String(item.name).includes(PAGE_UUID));
	const context = contexts.find(item => item.auxData?.frameId === frame?.id);
	if (!context)
		throw new Error(`No execution context for schematic ${PAGE_UUID}`);

	const expression = `(async () => {
		const root = window._EXTAPI_ROOT_;
		if (!root?.sch_PrimitiveRectangle)
			throw new Error('sch_PrimitiveRectangle unavailable');
		const requested = ${JSON.stringify(primitiveIds)};
		const before = await root.sch_PrimitiveRectangle.getAllPrimitiveId();
		const missingBefore = requested.filter(id => !before.includes(id));
		if (missingBefore.length)
			throw new Error('Requested rectangle IDs absent before delete: ' + missingBefore.join(','));
		const deleted = await root.sch_PrimitiveRectangle.delete(requested);
		const after = await root.sch_PrimitiveRectangle.getAllPrimitiveId();
		const remaining = requested.filter(id => after.includes(id));
		if (remaining.length)
			throw new Error('Rectangle deletion did not persist: ' + remaining.join(','));
		await root.sch_Document.save();
		return { deleted, requested, before, after };
	})()`;
	const response = await send('Runtime.evaluate', {
		contextId: context.id,
		expression,
		returnByValue: true,
		awaitPromise: true,
		timeout: 30000,
	});
	if (response.result?.exceptionDetails) {
		const detail = response.result.exceptionDetails.exception?.description
			|| response.result.exceptionDetails.text;
		throw new Error(detail || 'Rectangle deletion failed');
	}
	console.log(JSON.stringify(response.result?.result?.value, null, 2));
}
finally {
	socket.close();
}
