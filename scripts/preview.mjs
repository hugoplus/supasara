import {createServer} from 'node:http';
import {createReadStream,existsSync} from 'node:fs';
import {stat} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root=fileURLToPath(new URL('../out/',import.meta.url));
if(!existsSync(path.join(root,'index.html')))throw Error('Run yarn build before previewing the static website.');
const port=Number(process.env.PORT||3177);
const types={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.txt':'text/plain; charset=utf-8','.svg':'image/svg+xml','.pdf':'application/pdf','.epub':'application/epub+zip','.woff2':'font/woff2','.png':'image/png','.ico':'image/x-icon'};
createServer(async(req,res)=>{
 try{
  if(!['GET','HEAD'].includes(req.method)){res.writeHead(405,{Allow:'GET, HEAD'}).end();return;}
  const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
  let file=path.resolve(root,'.'+pathname);
  const relative=path.relative(root,file);
  if(relative.startsWith('..')||path.isAbsolute(relative)){res.writeHead(403).end();return;}
  if((await stat(file)).isDirectory())file=path.join(file,'index.html');
  const info=await stat(file);
  res.writeHead(200,{'Content-Type':types[path.extname(file)]||'application/octet-stream','Content-Length':info.size});
  if(req.method==='HEAD'){res.end();return;}
  createReadStream(file).on('error',()=>res.destroy()).pipe(res);
 }catch{
  res.writeHead(404,{'Content-Type':'text/plain; charset=utf-8'}).end('Not found');
 }
}).listen(port,'127.0.0.1',()=>console.log(`supasara preview: http://127.0.0.1:${port}`));
