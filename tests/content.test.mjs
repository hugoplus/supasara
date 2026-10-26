import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {search,normalize} from '../lib/search.mjs';
const content=JSON.parse(fs.readFileSync(new URL('../data/content.json',import.meta.url),'utf8'));
const index=JSON.parse(fs.readFileSync(new URL('../public/data/search.json',import.meta.url),'utf8'));
test('all 177 articles have six sections and valid related links',()=>{
 assert.equal(content.articles.length,177);assert.equal(content.terms.length,469);
 const ids=new Set(content.articles.map(a=>a.id));assert.equal(ids.size,177);
 for(const a of content.articles){assert.equal(a.sections.length,6);for(const id of a.related_article_ids)assert.ok(ids.has(id));}
});
test('Chinese, full name, abbreviation and punctuation lead to the same concept',()=>{
 for(const q of ['ATP','可承诺量','Available to Promise','ＡＴＰ'])assert.ok(search(index,q)[0].articleIds.includes('S104'));
 assert.ok(search(index,'B/L')[0].articleIds.includes('S075'));
 assert.ok(search(index,'ASRS')[0].articleIds.includes('S123'));
 assert.equal(normalize('ＡＴＰ'),'atp');assert.deepEqual(search(index,''),[]);
});
test('ambiguous meanings stay separate and context is visible',()=>{
 for(const q of ['ABC','JIT','Variance'])assert.equal(search(index,q).filter(r=>r.kind==='term'&&r.score===100).length,2);
 assert.equal(search(index,'CEC')[0].status,'unresolved');assert.notEqual(search(index,'CEC')[0].id,search(index,'CFC')[0].id);
 assert.deepEqual(search(index,'ATP','C04'),[]);
});
test('every search target resolves to an existing article and section',()=>{
 for(const r of index){const slug=r.href.split('/')[2];const a=content.articles.find(a=>a.slug===slug);assert.ok(a);if(r.href.includes('#'))assert.ok(a.sections.some(s=>s.anchor===r.href.split('#')[1]));}
});
test('download manifest points to complete real files',()=>{
 const m=JSON.parse(fs.readFileSync(new URL('../public/downloads/manifest.json',import.meta.url),'utf8'));
 assert.equal(m.articleCount,177);assert.deepEqual(m.files.map(f=>f.format).sort(),['EPUB','PDF']);
 for(const f of m.files){const p=new URL('../public'+f.url,import.meta.url);assert.equal(fs.statSync(p).size,f.bytes);}
});
