import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { normalize } from '../lib/search.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const collection=read('content/collection.json'), categories=read('content/categories.json'), vocabulary=read('content/vocabulary.json');
const ids=collection.reading_order;
assert.equal(new Set(ids).size,ids.length);
const files=fs.readdirSync(path.join(root,'content/articles')).filter(f=>f.endsWith('.md'));
assert.equal(files.length,ids.length);
const headings=['核心术语','概念与使用场景','一个工作案例','工作中怎么说','常见混淆与使用边界','要点回顾'];
const articles=ids.map((id,i)=>{
 const raw=fs.readFileSync(path.join(root,'content/articles',id.toLowerCase()+'.md'),'utf8');
 const [,front,body]=raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/)||[];
 assert.ok(front,`Missing frontmatter: ${id}`);
 const meta=Object.fromEntries(front.split(/\r?\n/).map(l=>{const p=l.indexOf(': ');return [l.slice(0,p),JSON.parse(l.slice(p+2))]}));
 assert.equal(meta.id,id);assert.equal(meta.slug,id.toLowerCase());assert.equal(meta.order,i+1);
 assert.ok(categories.some(c=>c.id===meta.category_id));
 assert.ok(meta.related_article_ids.every(r=>ids.includes(r)&&r!==id));
 const matches=[...body.matchAll(/^## ([1-6])\. (.+)$/gm)];
 assert.deepEqual(matches.map(m=>m[2].trim()),headings);
 const sections=matches.map((m,j)=>({id:collection.section_ids[j],anchor:`${meta.slug}-${collection.section_ids[j]}`,title:m[2],markdown:body.slice(m.index+m[0].length,matches[j+1]?.index??body.length).trim()}));
 const paragraphs=sections[0].markdown.split(/\n\s*\n/).filter(p=>!p.startsWith('|'));
 const description=paragraphs.find(p=>/[\u4e00-\u9fff]/.test(p))||meta.subtitle;
 delete meta.legacy_path;
 return {...meta,description,sections,body};
});
const byId=Object.fromEntries(articles.map(a=>[a.id,a]));
const coverage=new Set();
const terms=vocabulary.map(t=>{
 assert.ok(t.occurrences.some(o=>o.article_id===t.preferred_article_id));
 for(const o of t.occurrences){const a=byId[o.article_id];assert.ok(a);const rows=a.sections[0].markdown.split('\n').filter(r=>r.startsWith('|')).slice(2);assert.equal(rows[o.table_row-1]?.split('|')[1].trim(),o.source_label);coverage.add(`${a.id}:${o.table_row}`);}
 const articleIds=[...new Set(t.occurrences.map(o=>o.article_id))];
 return {...t,articleIds,categoryIds:[...new Set(articleIds.map(id=>byId[id].category_id))],href:`/articles/${t.preferred_article_id.toLowerCase()}/#${t.preferred_article_id.toLowerCase()}-terms`};
});
for(const a of articles){const n=a.sections[0].markdown.split('\n').filter(r=>r.startsWith('|')).length-2;for(let i=1;i<=n;i++)assert.ok(coverage.has(`${a.id}:${i}`),`Missing vocabulary ${a.id}:${i}`);}
const records=[...terms.map(t=>{const labels=[t.english,...t.full_forms,...t.chinese,...t.aliases];return {id:t.id,kind:'term',title:t.english,description:t.chinese.join(' / '),note:t.usage_note,status:t.status,articleIds:t.articleIds,categoryIds:t.categoryIds,href:t.href,keys:[...new Set(labels.map(normalize))],normalized:normalize(labels.join(' '))};}),...articles.map(a=>{const labels=[a.title,a.subtitle,...a.search_aliases];return {id:a.id,kind:'article',title:a.title,description:a.subtitle,note:'',status:'standard',articleIds:[a.id],categoryIds:[a.category_id],href:`/articles/${a.slug}/`,keys:labels.map(normalize),normalized:normalize(labels.join(' ')),body:normalize(a.body)};})];
fs.mkdirSync(path.join(root,'data'),{recursive:true});fs.mkdirSync(path.join(root,'public/data'),{recursive:true});
fs.writeFileSync(path.join(root,'data/content.json'),JSON.stringify({collection,categories,articles,terms}));
fs.writeFileSync(path.join(root,'public/data/search.json'),JSON.stringify(records));
console.log(`Prepared ${articles.length} articles, ${terms.length} terms and ${coverage.size} vocabulary rows.`);
