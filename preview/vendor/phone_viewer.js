import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {GLTFExporter} from 'three/addons/exporters/GLTFExporter.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';

const data=JSON.parse(document.querySelector('#model-data').textContent);
const host=document.querySelector('#stage');
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,preserveDrawingBuffer:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2)); renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping; renderer.toneMappingExposure=1.22;
renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFSoftShadowMap; host.appendChild(renderer.domElement);
const scene=new THREE.Scene();
const pmrem=new THREE.PMREMGenerator(renderer); const env=new RoomEnvironment(); scene.environment=pmrem.fromScene(env,.045).texture; env.dispose(); pmrem.dispose();
scene.add(new THREE.HemisphereLight(0xfff6ef,0x382530,1.8));
for(const [position,intensity,size] of [[[.25,.55,.52],3.6,.25],[[-.55,.15,.2],2.0,.22],[[.05,-.45,-.25],1.4,.15]]){
 const light=new THREE.DirectionalLight(0xffffff,intensity);light.position.set(...position);light.castShadow=true;light.shadow.mapSize.set(1024,1024);light.shadow.camera.left=-.2;light.shadow.camera.right=.2;light.shadow.camera.top=.2;light.shadow.camera.bottom=-.2;scene.add(light);
}
const camera=new THREE.PerspectiveCamera(33,1,.001,10); const controls=new OrbitControls(camera,renderer.domElement); controls.enableDamping=true;controls.minDistance=.12;controls.maxDistance=.8;
const raw=Uint8Array.from(atob(data.base64),c=>c.charCodeAt(0)); const gltf=await new GLTFLoader().parseAsync(raw.buffer,''); const model=gltf.scene;scene.add(model);
const screen=model.getObjectByName('Screen_Placeholder'); if(!screen)throw Error('Screen placeholder missing');
const originalMaterial=screen.material;let imageURL=null;let replacement=null; let spinning=false;
const canvas=document.createElement('canvas');canvas.width=1489;canvas.height=3202;const context=canvas.getContext('2d');
const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;texture.flipY=false;
const screenMaterial=new THREE.MeshStandardMaterial({map:texture,roughness:.68,metalness:0});screenMaterial.name='Matte_Gray_Screen';
function clearScreen(){context.fillStyle='#808486';context.fillRect(0,0,canvas.width,canvas.height);texture.needsUpdate=true;}
clearScreen();
function drawImage(image){clearScreen();const scale=Math.min(canvas.width/image.width,canvas.height/image.height);const w=image.width*scale,h=image.height*scale;context.drawImage(image,(canvas.width-w)/2,(canvas.height-h)/2,w,h);texture.needsUpdate=true;}
document.querySelector('#upload').onchange=async event=>{
 const file=event.target.files[0];if(!file)return; if(imageURL)URL.revokeObjectURL(imageURL);imageURL=URL.createObjectURL(file);const image=new Image();image.src=imageURL;
 try{await image.decode();drawImage(image);screen.material=screenMaterial;replacement=file.name;document.querySelector('#status').textContent='Showing '+file.name;}catch{document.querySelector('#status').textContent='Choose a PNG, JPG or WebP image.';}
};
document.querySelector('#reset').onclick=()=>{screen.material=originalMaterial;replacement=null;document.querySelector('#status').textContent='Neutral matte-gray placeholder';};
window.setView=mode=>{
 spinning=false;document.querySelector('#spin').textContent='Auto rotate'; model.rotation.set(0,0,0);
 let target=[-.006,.010,-.018],position=[.185,.205,-.315];
 if(mode==='front')position=[0,0,.41];
 if(mode==='back')position=[0,.02,-.42];
 if(mode==='screen'){target=[0,0,.0043];position=[0,0,.19];}
 camera.position.set(...position);controls.target.set(...target);controls.update();
 document.querySelectorAll('[data-view]').forEach(button=>button.classList.toggle('active',button.dataset.view===mode));
};
document.querySelectorAll('[data-view]').forEach(button=>button.onclick=()=>window.setView(button.dataset.view));
document.querySelector('#spin').onclick=event=>{spinning=!spinning;event.target.textContent=spinning?'Pause rotation':'Auto rotate';};
function download(blob,name){const url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(url),2000);}
document.querySelector('#download').onclick=()=>download(new Blob([raw],{type:'model/gltf-binary'}),'Burgundy_Flagship_Phone.glb');
document.querySelector('#save').onclick=async()=>{
 if(!replacement){document.querySelector('#status').textContent='Choose an image first; the original model already contains the gray placeholder.';return;}
 const button=document.querySelector('#save');button.disabled=true;button.textContent='Saving…';
 try{const rotation=model.rotation.clone();model.rotation.set(0,0,0);model.updateMatrixWorld(true);let array;try{array=await new GLTFExporter().parseAsync(model,{binary:true,maxTextureSize:2048});}finally{model.rotation.copy(rotation);}download(new Blob([array],{type:'model/gltf-binary'}),'Burgundy_Flagship_Phone_Custom_Screen.glb');document.querySelector('#status').textContent='Saved GLB with '+replacement;}catch(error){document.querySelector('#status').textContent='Could not save this screen image.';}finally{button.disabled=false;button.textContent='Save GLB with screen image';}
};
new ResizeObserver(()=>{const width=host.clientWidth,height=host.clientHeight;renderer.setSize(width,height,false);camera.aspect=width/height;camera.updateProjectionMatrix();}).observe(host);
window.setView('angle');const clock=new THREE.Clock();renderer.setAnimationLoop(()=>{const delta=Math.min(clock.getDelta(),.05);if(spinning)model.rotation.y+=delta*.45;controls.update();renderer.render(scene,camera);});
window.phoneViewer={model,screen,renderer,camera,controls};window.modelsReady=true;
