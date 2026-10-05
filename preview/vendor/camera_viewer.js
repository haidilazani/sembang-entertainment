import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {GLTFExporter} from 'three/addons/exporters/GLTFExporter.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
const host=document.querySelector('#stage');
const data=JSON.parse(document.querySelector('#model-data').textContent);
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,preserveDrawingBuffer:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.25;
host.appendChild(renderer.domElement);
const scene=new THREE.Scene();
const pmrem=new THREE.PMREMGenerator(renderer);const room=new RoomEnvironment();
scene.environment=pmrem.fromScene(room,.04).texture;room.dispose();pmrem.dispose();
scene.add(new THREE.AmbientLight(0xffffff,.6));
for(const [p,power] of [[[-.2,.5,.5],2.3],[[.4,.1,-.3],1.8]]){const l=new THREE.DirectionalLight(0xffffff,power);l.position.set(...p);scene.add(l);}
const camera=new THREE.PerspectiveCamera(33,1,.001,10);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.minDistance=.09;controls.maxDistance=1.1;
const raw=Uint8Array.from(atob(data.base64),c=>c.charCodeAt(0));
const loaded=await new GLTFLoader().parseAsync(raw.buffer,'');const model=loaded.scene;scene.add(model);
const screen=model.getObjectByName('Screen_Placeholder');
if(!screen)throw Error('Editable screen is missing');
screen.material.toneMapped=false;
const original=screen.material;
const contentCanvas=document.createElement('canvas');contentCanvas.width=1600;contentCanvas.height=900;
const ctx=contentCanvas.getContext('2d');
const texture=new THREE.CanvasTexture(contentCanvas);texture.colorSpace=THREE.SRGBColorSpace;texture.flipY=false;
const editableMaterial=new THREE.MeshBasicMaterial({map:texture,toneMapped:false});editableMaterial.name='Screen_Content';
let spinning=false,media=null,stream=null,objectURL=null,currentMode='placeholder';
const status=document.querySelector('#media-status');
function stopMedia(){
 if(stream){stream.getTracks().forEach(t=>t.stop());stream=null;}
 if(media instanceof HTMLVideoElement){media.pause();media.srcObject=null;media.removeAttribute('src');media.load();}
 if(objectURL){URL.revokeObjectURL(objectURL);objectURL=null;}media=null;
 document.querySelector('#stop-live').hidden=true;
}
function drawMedia(){
 if(!media)return;
 const w=media.videoWidth||media.naturalWidth,h=media.videoHeight||media.naturalHeight;
 if(!w||!h)return;
 ctx.fillStyle='#101821';ctx.fillRect(0,0,1600,900);
 const scale=Math.min(1600/w,900/h)*(currentMode==='logo'?.77:1);
 ctx.drawImage(media,(1600-w*scale)/2,(900-h*scale)/2,w*scale,h*scale);texture.needsUpdate=true;
}
async function imageFromURL(url){const im=new Image();im.src=url;await im.decode();return im;}
document.querySelector('#upload').onchange=async e=>{
 const file=e.target.files[0];if(!file)return;
 stopMedia();objectURL=URL.createObjectURL(file);currentMode='upload';
 try{
  if(file.type.startsWith('video/')){const v=document.createElement('video');v.src=objectURL;v.muted=true;v.loop=true;v.playsInline=true;await v.play();media=v;}
  else media=await imageFromURL(objectURL);
  screen.material=editableMaterial;drawMedia();status.textContent='Showing '+file.name;
 }catch(err){status.textContent='Could not open this file. Try a PNG, JPG or MP4.';stopMedia();}
};
document.querySelector('#logo').onclick=async()=>{
 stopMedia();currentMode='logo';media=await imageFromURL('data:image/svg+xml;charset=utf-8,'+encodeURIComponent(data.logo));screen.material=editableMaterial;drawMedia();status.textContent='Sembang logo on screen';
};
document.querySelector('#reset').onclick=()=>{stopMedia();currentMode='placeholder';screen.material=original;status.textContent='Neutral 16:9 placeholder';};
document.querySelector('#live').onclick=async()=>{
 stopMedia();status.textContent='Waiting for browser camera permission…';
 try{
  if(!navigator.mediaDevices?.getUserMedia)throw Error('unavailable');
  stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:{ideal:'environment'}},audio:false});
  const v=document.createElement('video');v.srcObject=stream;v.muted=true;v.playsInline=true;await v.play();media=v;currentMode='live';screen.material=editableMaterial;
  document.querySelector('#stop-live').hidden=false;status.textContent='Live camera · stays on this device';
 }catch(err){stopMedia();status.textContent=err.name==='NotAllowedError'?'Camera permission declined. You can upload an image instead.':'Live camera unavailable here. Try localhost or upload an image.';}
};
document.querySelector('#stop-live').onclick=()=>document.querySelector('#reset').click();
window.addEventListener('pagehide',stopMedia);
window.setView=mode=>{
 spinning=false;document.querySelector('#spin').textContent='Auto rotate';model.rotation.set(0,0,0);
 let target=[-.035,0,.025],position=[-.205,.130,.295];
 if(mode==='front')position=[-.035,.008,.48];
 if(mode==='back')position=[-.04,.12,-.43];
 if(mode==='screen'){target=[-.1137,-.002,-.0256];position=[-.1137,-.002,.135];}
 camera.position.set(...position);controls.target.set(...target);controls.update();
 document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===mode));
};
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>window.setView(b.dataset.view));
document.querySelector('#spin').onclick=e=>{spinning=!spinning;e.target.textContent=spinning?'Pause rotation':'Auto rotate';};
function saveBlob(blob,name){const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),3000);}
document.querySelector('#download').onclick=()=>saveBlob(new Blob([raw],{type:'model/gltf-binary'}),'Cinema_Camera.glb');
document.querySelector('#save-custom').onclick=async()=>{
 const button=document.querySelector('#save-custom');button.disabled=true;button.textContent='Saving…';
 try{
  drawMedia();const rotation=model.rotation.clone();model.rotation.set(0,0,0);model.updateMatrixWorld(true);
  let buffer;try{buffer=await new GLTFExporter().parseAsync(model,{binary:true,maxTextureSize:1600});}finally{model.rotation.copy(rotation);}
  saveBlob(new Blob([buffer],{type:'model/gltf-binary'}),'Cinema_Camera_Custom_Screen.glb');status.textContent='Saved model with the current screen image';
 }catch(err){status.textContent='Could not export: '+err.message;}
 finally{button.disabled=false;button.textContent='Save model with current screen';}
};
new ResizeObserver(()=>{const w=host.clientWidth,h=host.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();}).observe(host);
window.setView('angle');const clock=new THREE.Clock();
renderer.setAnimationLoop(()=>{const dt=Math.min(clock.getDelta(),.05);if(spinning)model.rotation.y+=dt*.38;if(media instanceof HTMLVideoElement)drawMedia();controls.update();renderer.render(scene,camera);});
window.cameraViewer={model,screen,renderer,controls,camera};window.modelsReady=true;
