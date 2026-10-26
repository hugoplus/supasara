export function normalize(value) { return value.normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]/gu, ''); }
export function search(records, query, category = '') {
  const q = normalize(query);
  if (!q) return [];
  return records.filter(r => !category || r.categoryIds.includes(category)).map(r => ({...r,score:r.keys.includes(q)?100:r.keys.some(k=>k.startsWith(q))?70:r.normalized.includes(q)?40:r.body?.includes(q)?10:0})).filter(r=>r.score>0).sort((a,b)=>b.score-a.score || (a.kind==='term'?0:1)-(b.kind==='term'?0:1) || a.title.localeCompare(b.title));
}
