const {chromium}=require('playwright');const path=require('path');
const root=path.resolve(__dirname,'../..');
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--allow-file-access-from-files']});
 const page=await browser.newPage({viewport:{width:1500,height:880},deviceScaleFactor:1.5});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('file://'+root+'/Sembang Envelope Preview.html');await page.waitForFunction(()=>window.modelsReady);
 for(const mode of ['angle','front','back','side']){
  await page.evaluate(m=>window.setView(m),mode);await page.waitForTimeout(500);
  await page.screenshot({path:root+'/envelope/preview_'+mode+'.png',fullPage:true});
 }
 await page.click('[data-model="1"]');await page.waitForTimeout(500);await page.screenshot({path:root+'/envelope/preview_wax_seal.png',fullPage:true});
 await page.click('#spin');const before=await page.evaluate(()=>window.envelopeViewer.models[1].rotation.y);await page.waitForTimeout(600);const after=await page.evaluate(()=>window.envelopeViewer.models[1].rotation.y);if(after<=before)throw Error('Rotation failed');
 const pending=page.waitForEvent('download');await page.click('[data-download="0"]');const download=await pending;if(download.suggestedFilename()!=='Sembang_Cream_Envelope.glb')throw Error('Wrong download');
 await page.setViewportSize({width:390,height:844});await page.waitForTimeout(300);if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Mobile overflow');
 console.log(JSON.stringify({errors,models:2,viewButtons:true,rotation:true,download:true,mobileLayout:true}));if(errors.length)throw Error(errors.join('\n'));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
