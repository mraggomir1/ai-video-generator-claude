const {chromium}=require('playwright'); const fs=require('fs');
(async()=>{
  const [mode]=process.argv.slice(2); const data=JSON.parse(fs.readFileSync('scenes.json'));
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:540,height:960},deviceScaleFactor:2});
  p.on('pageerror',e=>console.error('ERR',e.message));
  await p.goto('file://'+__dirname+'/page.html'); await p.evaluate(d=>build(d),data);
  if(mode==='preview'){
    const ts=process.argv.slice(3).map(Number);
    for(const t of ts){await p.evaluate(t=>render(t),t);await p.screenshot({path:`prev_${t}.png`});}
  } else {
    fs.mkdirSync('frames',{recursive:true}); const fps=30, N=Math.ceil(data.duration*fps);
    for(let i=0;i<N;i++){await p.evaluate(t=>render(t),i/fps);await p.screenshot({path:`frames/f${String(i).padStart(5,'0')}.jpg`,type:'jpeg',quality:92}); if(i%150==0)console.log(i,'/',N)}
  }
  await b.close();
})();
