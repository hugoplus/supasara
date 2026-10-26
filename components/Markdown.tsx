import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
export default function Markdown({ children }: {children:string}) {
 return <div className="markdown"><ReactMarkdown remarkPlugins={[remarkGfm]} components={{table:({children})=><div className="table-scroll" tabIndex={0} role="region" aria-label="可横向滚动的双语表格"><table>{children}</table></div>}}>{children}</ReactMarkdown></div>;
}
