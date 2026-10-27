import author from '@/content/author.json';
import type {Metadata} from 'next';
import Link from 'next/link';
import {description} from '@/lib/content';
import './globals.css';
export const metadata:Metadata={title:{default:'supasara · 供应链英语',template:'%s | supasara'},description,authors:[{name:author.name}],applicationName:'supasara',icons:{icon:'/icon.svg'}};
const navigation=[['/categories/','分类阅读'],['/vocabulary/','词汇索引'],['/downloads/','下载电子书'],['/about/','关于']];
export default function Layout({children}:{children:React.ReactNode}){return <html lang="zh-CN"><body><a className="skip" href="#main">跳到正文</a><header className="site-header"><Link href="/" className="brand"><span className="brand-mark" aria-hidden="true">s.</span><span>supasara<small>SUPPLY CHAIN ENGLISH</small></span></Link><nav className="desktop-nav" aria-label="主导航">{navigation.map(([url,label])=><Link key={url} href={url}>{label}</Link>)}</nav><details className="mobile-nav"><summary>导航 ☰</summary><nav aria-label="移动端导航">{navigation.map(([url,label])=><Link href={url} key={url}>{label}</Link>)}</nav></details></header><main id="main">{children}</main><footer className="site-footer"><div><Link href="/" className="footer-brand">supasara.</Link><p>把专业术语，变成工作的共同语言。</p><p><Link href="/about/">作者 · {author.name}</Link></p></div><div><Link href="/downloads/">离线阅读 ↗</Link><p>177 篇文章 · 7 个主题 · 中英对照</p></div></footer></body></html>}
