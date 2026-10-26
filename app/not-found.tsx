import Link from 'next/link';
export default function NotFound(){return <div className="wrap page"><p className="eyebrow">404</p><h1>这个页面还没入库。</h1><p className="lead">试试词汇搜索，或从分类目录重新开始。</p><Link href="/vocabulary/" className="button">打开词汇索引 ↗</Link></div>}
