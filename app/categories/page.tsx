import Link from 'next/link';
import {articles,categories,descriptions} from '@/lib/content';
export const metadata={title:'分类阅读'};
export default function Page(){return <div className="wrap page"><p className="eyebrow">THE COLLECTION</p><h1>找到你正在做的事。</h1><p className="lead">从基础术语到数据分析，按业务主题阅读完整合集。</p><div className="category-grid section">{categories.map((c,i)=><Link className="category-card" href={`/categories/${c.slug}/`} key={c.id}><span className="category-number">0{i+1}</span><div><h2>{c.title_zh}</h2><p>{descriptions[i]}</p><small>{articles.filter(a=>a.category_id===c.id).length} 篇</small></div><span>↗</span></Link>)}</div></div>}
