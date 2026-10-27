"""Build complete, offline PDF + EPUB from prepared Markdown data.
Dependencies: reportlab, fonttools, pypdf (see requirements-books.txt).
Set BOOK_FONT and BOOK_FONT_BOLD to Unicode TrueType fonts for other platforms.
"""
from pathlib import Path
import html, json, os, re, zipfile, hashlib
from xml.etree import ElementTree as ET
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether, Image
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A5
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'data/content.json').read_text(encoding='utf-8'))
AUTHOR=json.loads((ROOT/'content/author.json').read_text(encoding='utf-8'))
AUTHOR_IMAGE=ROOT/'public'/AUTHOR['image'].lstrip('/')
AUTHOR_PARAGRAPHS=AUTHOR['bio'].split('\n\n')
ARTICLES=DATA['articles']; CATEGORIES=DATA['categories']; TERMS=DATA['terms']
DEST=ROOT/'public/downloads'; DEST.mkdir(parents=True,exist_ok=True)
TMP=ROOT/'tmp/pdfs';TMP.mkdir(parents=True,exist_ok=True)
EDITION=DATA['collection']['edition']; DATE=DATA['collection']['updated']
esc=lambda s:html.escape(str(s),quote=True)

def inline(s):
    s=esc(s)
    s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'`([^`]+)`',r'\1',s)
    return s

def blocks(md):
    lines=md.strip().splitlines();i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('|'):
            table=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                row=[c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?',c) for c in row):table.append(row)
                i+=1
            yield 'table',table;continue
        if line.startswith('- '):yield 'bullet',line[2:];i+=1;continue
        if line.startswith('#'):yield 'heading',line.lstrip('# ');i+=1;continue
        paragraph=[line];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('|','- ','#')):
            paragraph.append(lines[i].strip());i+=1
        yield 'paragraph',' '.join(paragraph)

def xhtml_blocks(md):
    out=[]
    for kind,value in blocks(md):
        if kind=='table':
            head='<thead><tr>'+''.join('<th scope="col">'+inline(c)+'</th>' for c in value[0])+'</tr></thead>'
            body='<tbody>'+''.join('<tr>'+''.join('<td>'+inline(c)+'</td>' for c in row)+'</tr>' for row in value[1:])+'</tbody>'
            out.append('<table>'+head+body+'</table>')
        elif kind=='bullet':out.append('<ul><li>'+inline(value)+'</li></ul>')
        else:out.append(('<h3>' if kind=='heading' else '<p>')+inline(value)+('</h3>' if kind=='heading' else '</p>'))
    return ''.join(out)

def document(title,body):
    return '<?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh-CN" lang="zh-CN"><head><title>'+esc(title)+'</title><link rel="stylesheet" type="text/css" href="book.css"/></head><body>'+body+'</body></html>'

def make_epub():
    css='body{font-family:serif;line-height:1.8;margin:5%;color:#243b32}h1{font-size:1.8em;line-height:1.4}h2{font-size:1.25em;color:#18594c;margin-top:1.8em}h3{font-size:1.1em}p{orphans:2;widows:2}table{border-collapse:collapse;width:100%;font-size:.8em;table-layout:fixed}td,th{border:1px solid #ccd7cb;padding:.5em;vertical-align:top;overflow-wrap:anywhere;word-wrap:break-word}th{background:#e9efdf;text-align:left}a{color:#18594c}small{color:#657268}.cover{padding-top:20%;text-align:center}.cover h1{font-size:2.6em}.subtitle{color:#657268}.part{margin-top:2em}li{margin-bottom:.5em}'
    files={'book.css':css}
    files['cover.xhtml']=document('supasara · 供应链英语','<section class="cover"><p>SUPASARA / FIELD GUIDE</p><h1>供应链英语</h1><p>Supply Chain English</p><p>术语 · 场景 · 表达</p><p>177 篇文章 · 469 个词义条目</p><p>完整版本 '+esc(EDITION)+' · '+DATE+'</p></section>')
    files['intro.xhtml']=document('阅读说明','<h1>阅读说明</h1><p>本书面向中文母语的仓储、物流与供应链从业者，提供术语解释、原创教学案例和双语工作表达。</p><p>每个案例均为教学示例。专业用语的含义可能因系统、地区或合同变化，使用前请结合各篇边界说明。</p><p>本书完整收录七个分类的177篇文章，末尾词汇索引支持跳转。相同缩写的不同含义分别列出；CEC与CFC仍标记为待澄清。</p>')
    files['author.xhtml']=document('关于作者', '<h1>作者 · '+esc(AUTHOR['name'])+'</h1>'+''.join('<p>'+esc(p)+'</p>' for p in AUTHOR_PARAGRAPHS)+'<p>小红书：'+esc(AUTHOR['account'])+'</p><p>'+esc(AUTHOR['invitation'])+'</p><img src="images/yushu-rednote.png" alt="'+esc(AUTHOR['imageAlt'])+'" style="display:block;width:100%;max-width:24em;height:auto;margin:1em auto"/>')
    files['images/yushu-rednote.png']=AUTHOR_IMAGE.read_bytes()
    files['cover.xhtml']=files['cover.xhtml'].replace('</section>', '<p>作者 · '+esc(AUTHOR['name'])+'</p></section>')
    nav='<h1>目录</h1><nav epub:type="toc" id="toc"><ol><li><a href="intro.xhtml">阅读说明</a></li><li><a href="author.xhtml">关于作者</a></li>'
    for c in CATEGORIES:
        group=[a for a in ARTICLES if a['category_id']==c['id']]
        nav+='<li><a href="'+group[0]['slug']+'.xhtml">'+esc(c['title_zh'])+'</a><ol>'
        for a in group:
            nav+='<li><a href="'+a['slug']+'.xhtml">'+esc(a['id']+' · '+a['title'])+'</a></li>'
        nav+='</ol></li>'
    nav+='<li><a href="vocabulary.xhtml">双语词汇索引</a></li></ol></nav>'
    files['nav.xhtml']=document('目录',nav)
    byid={a['id']:a for a in ARTICLES}
    for a in ARTICLES:
        body='<article id="'+a['slug']+'"><p>'+esc(a['id'])+'</p><h1>'+esc(a['title'])+'</h1><p class="subtitle">'+esc(a['subtitle'])+'</p>'
        for s in a['sections']:body+='<section id="'+s['anchor']+'"><h2>'+esc(s['title'])+'</h2>'+xhtml_blocks(s['markdown'])+'</section>'
        body+='<h2>相关主题</h2><ul>'+''.join('<li><a href="'+byid[r]['slug']+'.xhtml">'+esc(byid[r]['title'])+'</a></li>' for r in a['related_article_ids'])+'</ul></article>'
        files[a['slug']+'.xhtml']=document(a['title'],body)
    vocab='<h1>双语词汇索引</h1><p>按英文排序；不同语境保留独立词义。</p>'
    for t in TERMS:
        aid=t['preferred_article_id'].lower()
        vocab+='<p><b>'+esc(t['english'])+'</b> — '+esc(' / '.join(t['chinese']))+' <a href="'+aid+'.xhtml#'+aid+'-terms">'+esc(t['preferred_article_id'])+'</a>'
        if t['usage_note']:vocab+='<br/><small>'+esc(t['usage_note'])+'</small>'
        vocab+='</p>'
    files['vocabulary.xhtml']=document('双语词汇索引',vocab)
    manifest='';spine=[]
    for i,(name,content) in enumerate(files.items()):
        typ='image/png' if name.endswith('.png') else 'text/css' if name.endswith('.css') else 'application/xhtml+xml'
        manifest+=f'<item id="i{i}" href="{name}" media-type="{typ}"'+(' properties="nav"' if name=='nav.xhtml' else '')+'/>'
        if name.endswith('.xhtml'):spine.append(f'<itemref idref="i{i}"/>')
    opf='<?xml version="1.0" encoding="utf-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id" xml:lang="zh-CN"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="book-id">urn:supasara:supply-chain-english:'+EDITION+'</dc:identifier><dc:title>supasara · 供应链英语</dc:title><dc:language>zh-CN</dc:language><meta property="dcterms:modified">'+DATE+'T00:00:00Z</meta></metadata><manifest>'+manifest+'</manifest><spine>'+''.join(spine)+'</spine></package>'
    target=DEST/'supasara-complete.epub'
    opf=opf.replace('<dc:language>', '<dc:creator>'+esc(AUTHOR['name'])+'</dc:creator><dc:language>')
    with zipfile.ZipFile(target,'w') as z:
        z.writestr('mimetype','application/epub+zip',compress_type=zipfile.ZIP_STORED)
        z.writestr('META-INF/container.xml','<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>',compress_type=zipfile.ZIP_DEFLATED)
        z.writestr('OEBPS/content.opf',opf,compress_type=zipfile.ZIP_DEFLATED)
        for name,content in files.items():z.writestr('OEBPS/'+name,content,compress_type=zipfile.ZIP_DEFLATED)
    # Parse every XML file and verify all chapter/anchor links in the actual archive.
    with zipfile.ZipFile(target) as z:
        assert z.infolist()[0].filename=='mimetype' and z.infolist()[0].compress_type==0
        ids={}
        for name in z.namelist():
            if name.endswith(('.xhtml','.opf','.xml')):
                tree=ET.fromstring(z.read(name));ids[name]={e.attrib['id'] for e in tree.iter() if 'id' in e.attrib}
        for name in [n for n in z.namelist() if n.endswith('.xhtml')]:
            for e in ET.fromstring(z.read(name)).iter():
                href=e.attrib.get('href','') or e.attrib.get('src','')
                if not href or '://' in href:continue
                file,_,anchor=href.partition('#');dest='OEBPS/'+file if file else name
                assert dest in z.namelist(),(name,href)
                if anchor:assert anchor in ids[dest],(name,href)
    return target

def make_pdf():
    regular=os.environ.get('BOOK_FONT','C:/Windows/Fonts/msyh.ttc')
    bold=os.environ.get('BOOK_FONT_BOLD','C:/Windows/Fonts/msyhbd.ttc')
    if not Path(regular).exists():raise RuntimeError('Set BOOK_FONT to a Chinese-capable TrueType font.')
    pdfmetrics.registerFont(TTFont('Book',regular,subfontIndex=0))
    pdfmetrics.registerFont(TTFont('BookBold',bold if Path(bold).exists() else regular,subfontIndex=0))
    pdfmetrics.registerFontFamily('Book',normal='Book',bold='BookBold',italic='Book',boldItalic='BookBold')
    width,height=A5; margin=34; usable=width-2*margin
    base=ParagraphStyle('body',fontName='Book',fontSize=9.2,leading=16.2,wordWrap='CJK',spaceAfter=9,textColor=colors.HexColor('#283e35'))
    styles={
      'body':base,'small':ParagraphStyle('small',parent=base,fontSize=7.6,leading=12),
      'title':ParagraphStyle('title',parent=base,fontName='BookBold',fontSize=23,leading=33,spaceAfter=15),
      'subtitle':ParagraphStyle('subtitle',parent=base,fontSize=11,leading=19,textColor=colors.HexColor('#637768'),spaceAfter=18),
      'h2':ParagraphStyle('h2',parent=base,fontName='BookBold',fontSize=12,leading=19,spaceBefore=17,spaceAfter=9,keepWithNext=True),
      'cell':ParagraphStyle('cell',parent=base,fontSize=7.7,leading=12,spaceAfter=0),
      'bullet':ParagraphStyle('bullet',parent=base,leftIndent=10,firstLineIndent=-7),
    }
    anchors={};chapter_pages={}
    class Book(BaseDocTemplate):
        def afterFlowable(self,f):
            if hasattr(f,'anchor'):
                self.canv.bookmarkPage(f.anchor);anchors[f.anchor]=self.page
            if hasattr(f,'toc_title'):
                self.notify('TOCEntry',(f.level,f.toc_title,self.page,f.anchor))
                self.canv.addOutlineEntry(f.toc_title,f.anchor,level=f.level,closed=True)
                if f.level==1:chapter_pages[f.anchor]=self.page
    def page(canvas,doc):
        canvas.saveState();canvas.setFont('Book',7);canvas.setFillColor(colors.HexColor('#748174'))
        if doc.page>1:
            canvas.drawString(margin,20,'supasara · 供应链英语');canvas.drawRightString(width-margin,20,str(doc.page))
            canvas.setStrokeColor(colors.HexColor('#dfe4d7'));canvas.line(margin,32,width-margin,32)
        canvas.restoreState()
    target=DEST/'supasara-complete.pdf'
    doc=Book(str(target),pagesize=A5,leftMargin=margin,rightMargin=margin,topMargin=35,bottomMargin=43,title='supasara · 供应链英语',author=AUTHOR['name'])
    doc.addPageTemplates(PageTemplate('book',frames=[Frame(margin,43,usable,height-78,id='normal',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=page))
    story=[Spacer(1,75),Paragraph('SUPASARA / FIELD GUIDE',styles['small']),Spacer(1,35),Paragraph('供应链英语',styles['title']),Paragraph('Supply Chain English',styles['subtitle']),Spacer(1,20),Paragraph('术语 · 场景 · 表达',base),Spacer(1,45),Paragraph('完整收录177篇文章<br/>7个主题 · 469个词义条目',base),Paragraph('版本 '+EDITION+' · '+DATE,styles['small']),PageBreak()]
    story.insert(-1,Paragraph('作者 · '+esc(AUTHOR['name']),base))
    author_heading=Paragraph('作者 · '+esc(AUTHOR['name']),styles['title'])
    author_heading.anchor='author';author_heading.toc_title='关于作者';author_heading.level=0
    image_width,image_height=ImageReader(str(AUTHOR_IMAGE)).getSize()
    card=Image(str(AUTHOR_IMAGE),width=250,height=250*image_height/image_width);card.hAlign='CENTER'
    story += [author_heading]+[Paragraph(esc(p),base) for p in AUTHOR_PARAGRAPHS]+[Paragraph('小红书：'+esc(AUTHOR['account']),base),PageBreak(),Paragraph('关注雨叔',styles['title']),Paragraph(esc(AUTHOR['invitation']),base),card,PageBreak()]
    story += [Paragraph('阅读说明',styles['title']),Paragraph('本书面向中文母语的仓储、物流与供应链从业者。每篇包括核心术语、使用场景、原创教学案例、双语表达、常见混淆和要点回顾。',base),Paragraph('所有案例均为教学示例。术语含义可能随地区、系统或合同而变化，请结合各篇说明。词汇索引保留不同语境；CEC与CFC仍标记为待澄清。',base),Paragraph('通过目录、PDF书签和文内链接跳转。电子阅读器用户也可选择同内容的EPUB版本。',base),PageBreak(),Paragraph('目录',styles['title'])]
    toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc0',parent=base,fontName='BookBold',fontSize=10,leading=16,spaceBefore=9),ParagraphStyle('toc1',parent=base,fontSize=8,leading=13,leftIndent=10,firstLineIndent=0,spaceAfter=3)]
    story.extend([toc,PageBreak()])
    def heading(text,anchor,level):
        p=Paragraph(esc(text),styles['title']);p.anchor=anchor;p.toc_title=text;p.level=level;return p
    for c in CATEGORIES:
        story.append(heading(c['title_zh'],c['id'],0));story.append(Paragraph(c['title_en'],styles['subtitle']));story.append(PageBreak())
        for a in [a for a in ARTICLES if a['category_id']==c['id']]:
            story.append(Paragraph(a['id'],styles['small']));story.append(heading(a['title'],a['slug'],1));story.append(Paragraph(esc(a['subtitle']),styles['subtitle']))
            for sec in a['sections']:
                p=Paragraph(esc(sec['title']),styles['h2']);p.anchor=sec['anchor'];story.append(p)
                for kind,value in blocks(sec['markdown']):
                    if kind=='table':
                        count=len(value[0]);ratios=[1/count]*count
                        if count==3:ratios=[.27,.40,.33]
                        if count==4:ratios=[.20,.27,.27,.26]
                        cells=[[Paragraph(inline(c),styles['cell']) for c in row] for row in value]
                        table=Table(cells,colWidths=[usable*r for r in ratios],repeatRows=1,hAlign='LEFT')
                        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e5ecdd')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#cfd9c9')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
                        story.extend([table,Spacer(1,10)])
                    else:story.append(Paragraph(('• ' if kind=='bullet' else '')+inline(value),styles['bullet' if kind=='bullet' else 'h2' if kind=='heading' else 'body']))
            story.append(Paragraph('相关主题',styles['h2']))
            byid={a['id']:a for a in ARTICLES}
            for rid in a['related_article_ids']:
                r=byid[rid];story.append(Paragraph('<link href="#'+r['slug']+'" color="#18594c">'+esc(rid+' · '+r['title'])+'</link>',styles['small']))
            story.append(PageBreak())
    story.append(heading('双语词汇索引','vocabulary',0))
    for t in TERMS:
        text='<b>'+esc(t['english'])+'</b> — '+esc(' / '.join(t['chinese']))+' <link href="#'+t['preferred_article_id'].lower()+'" color="#18594c">'+t['preferred_article_id']+'</link>'
        if t['usage_note']:text+='<br/>'+esc(t['usage_note'])
        story.append(Paragraph(text,styles['small']))
    doc.multiBuild(story)
    reader=PdfReader(target)
    assert len(chapter_pages)==177,len(chapter_pages)
    alltext=''.join(p.extract_text() or '' for p in reader.pages)
    assert all(a['title'] in alltext for a in ARTICLES),'A chapter title is missing from PDF text'
    assert '核心术语' in alltext and '双语词汇索引' in alltext
    assert AUTHOR['name']==reader.metadata.author and AUTHOR['account'] in alltext
    (TMP/'pdf-report.json').write_text(json.dumps({'pages':len(reader.pages),'chapters':len(chapter_pages),'chapter_pages':chapter_pages,'anchors':anchors},ensure_ascii=False,indent=2),encoding='utf-8')
    return target

if __name__=='__main__':
    epub=make_epub();pdf=make_pdf()
    files=[dict(format=f.suffix[1:].upper(),url='/downloads/'+f.name,bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in [pdf,epub]]
    (DEST/'manifest.json').write_text(json.dumps(dict(edition=EDITION,updated=DATE,articleCount=len(ARTICLES),termCount=len(TERMS),files=files),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'files':files,'articles':len(ARTICLES)},ensure_ascii=False))
