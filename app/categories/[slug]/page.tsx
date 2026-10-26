import Link from 'next/link';
import {notFound} from 'next/navigation';
import {articles,categories,descriptions} from '@/lib/content';
export function generateStaticParams(){return categories.map(c=>({slug:c.slug}))}
export async function generateMetadata({params}:{params:Promise<{slug:string}>}){const {slug}=await params;return {title:categories.find(c=>c.slug===slug)?.title_zh}}
export default async function Page({params}:{params:Promise<{slug:string}>}){const {slug}=await params;const c=categories.find(c=>c.slug===slug);if(!c)notFound();const list=articles.filter(a=>a.category_id===c.id);return <div className="wrap page"><Link href="/categories/" className="eyebrow">← 全部分类</Link><h1>{c.title_zh}</h1><p className="lead">{descriptions[c.order-1]} <span className="muted">共 {list.length} 篇</span></p><div className="reading-list">{list.map(a=><Link href={`/articles/${a.slug}/`} key={a.id}><span className="eyebrow">{a.id}</span><div><h2>{a.title}</h2><p>{a.subtitle}</p></div><span>↗</span></Link>)}</div></div>}
