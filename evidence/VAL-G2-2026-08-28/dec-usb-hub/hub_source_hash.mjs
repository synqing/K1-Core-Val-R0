// FNV-1a revision used by EasyEDA MCP computeSourceRevision.
export function computeSourceRevision(source) {
	let hash = 2166136261;
	for (let i = 0; i < source.length; i += 1) {
		hash ^= source.charCodeAt(i);
		hash = Math.imul(hash, 16777619);
	}
	return `${source.length}:${(hash >>> 0).toString(16).padStart(8, '0')}`;
}
