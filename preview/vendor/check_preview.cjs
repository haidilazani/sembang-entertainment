const {chromium}=require('playwright');
const path=require('path');
const fs=require('fs');
const root=path.resolve(__dirname,'../..');
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--allow-file-access-from-files']});
 const page=await browser.newPage({viewport:{width:1600,height:830},deviceScaleFactor:1.5});
 const errors=[];
 page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('file://'+root+'/Sembang 3D Preview.html');
 await page.waitForFunction(()=>window.modelsReady,{timeout:60000});
 for(const mode of ['front','angle','back','side']){
  await page.evaluate(m=>window.setView(m),mode);
  await page.waitForTimeout(600);
  await page.screenshot({path:root+'/preview/'+mode+'.png',fullPage:true});
 }
 await page.selectOption('#background','dark');
 await page.evaluate(()=>window.setView('angle'));
 await page.waitForTimeout(400);
 await page.screenshot({path:root+'/preview/dark.png',fullPage:true});
 await page.selectOption('#background','light');
 await page.click('#spin');
 const before=await page.evaluate(()=>window.modelViews[0].model.rotation.y);
 await page.waitForTimeout(700);
 const after=await page.evaluate(()=>window.modelViews[0].model.rotation.y);
 if(after<=before)throw new Error('Auto rotation failed');
 await page.click('#spin');
 const downloadEvent=page.waitForEvent('download');
 await page.locator('[data-download="0"]').click();
 const download=await downloadEvent;
 if(download.suggestedFilename()!=='01_raspberry_cream.glb')throw new Error('Incorrect download');
 const report=await page.evaluate(()=>window.modelViews.map(v=>({id:v.id,meshes:v.model.children.length,triangles:v.renderer.info.render.triangles})));
 await page.setViewportSize({width:390,height:844});
 await page.waitForTimeout(500);
 if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw new Error('Mobile overflow');
 console.log(JSON.stringify({errors,models:report,rotationPassed:true,downloadPassed:true,mobileLayoutPassed:true},null,2));
 if(errors.length)throw new Error(errors.join('\n'));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
