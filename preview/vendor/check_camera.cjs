const {chromium}=require('playwright');const path=require('path');
const root=path.resolve(__dirname,'../..');
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--allow-file-access-from-files','--use-fake-device-for-media-stream','--use-fake-ui-for-media-stream']});
 const page=await browser.newPage({viewport:{width:1540,height:960},deviceScaleFactor:1.5});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('file://'+root+'/Sembang Camera Preview.html');await page.waitForFunction(()=>window.modelsReady);
 for(const mode of ['angle','front','back','screen']){
  await page.evaluate(m=>window.setView(m),mode);await page.waitForTimeout(800);
  await page.screenshot({path:root+'/camera/preview_'+mode+'.png',fullPage:true});
 }
 await page.click('#logo');await page.waitForFunction(()=>document.querySelector('#media-status').textContent.includes('Sembang logo'));await page.waitForTimeout(500);
 await page.screenshot({path:root+'/camera/preview_logo.png',fullPage:true});
 const customPromise=page.waitForEvent('download');await page.click('#save-custom');const custom=await customPromise;await custom.saveAs(root+'/camera/Cinema_Camera_Sembang_Screen.glb');
 await page.setInputFiles('#upload',root+'/camera/screen_placeholder.png');await page.waitForFunction(()=>document.querySelector('#media-status').textContent.includes('screen_placeholder.png'));
 const clip=await page.evaluate(async()=>{
  const c=document.createElement('canvas');c.width=320;c.height=180;const ctx=c.getContext('2d');const stream=c.captureStream(10);const recorder=new MediaRecorder(stream,{mimeType:'video/webm'});const chunks=[];recorder.ondataavailable=e=>chunks.push(e.data);
  const done=new Promise(resolve=>recorder.onstop=async()=>resolve(Array.from(new Uint8Array(await new Blob(chunks,{type:'video/webm'}).arrayBuffer()))));
  recorder.start();let i=0;const timer=setInterval(()=>{ctx.fillStyle=i++%2?'#ef4c7a':'#fbfacf';ctx.fillRect(0,0,320,180);},80);await new Promise(r=>setTimeout(r,650));clearInterval(timer);recorder.stop();stream.getTracks().forEach(t=>t.stop());return await done;
 });
 await page.setInputFiles('#upload',{name:'screen-test.webm',mimeType:'video/webm',buffer:Buffer.from(clip)});await page.waitForFunction(()=>document.querySelector('#media-status').textContent.includes('screen-test.webm'));
 await page.click('#live');await page.waitForFunction(()=>document.querySelector('#media-status').textContent.startsWith('Live camera ·'),{timeout:15000});
 await page.waitForTimeout(800);await page.screenshot({path:root+'/camera/preview_live_test.png',fullPage:true});
 await page.click('#stop-live');await page.waitForFunction(()=>document.querySelector('#media-status').textContent==='Neutral 16:9 placeholder');
 await page.click('#spin');const before=await page.evaluate(()=>window.cameraViewer.model.rotation.y);await page.waitForTimeout(500);const after=await page.evaluate(()=>window.cameraViewer.model.rotation.y);if(after<=before)throw Error('Rotation failed');
 const originalPromise=page.waitForEvent('download');await page.click('#download');if((await originalPromise).suggestedFilename()!=='Cinema_Camera.glb')throw Error('Wrong model download');
 await page.setViewportSize({width:390,height:844});await page.waitForTimeout(400);if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Mobile overflow');
 console.log(JSON.stringify({errors,views:true,logo:true,imageUpload:true,videoUpload:true,customGLB:true,liveCameraWithSyntheticDevice:true,stopCamera:true,rotation:true,mobile:true}));
 if(errors.length)throw Error(errors.join('\n'));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
