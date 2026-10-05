import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
const data=JSON.parse(document.getElementById('model-data').textContent);
const host=document.querySelector('#stage');
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,preserveDrawingBuffer:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.NoToneMapping;
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
host.appendChild(renderer.domElement);
const scene=new THREE.Scene();
const camera=new THREE.PerspectiveCamera(35,1,.01,100);
const controls=new OrbitControls(camera,renderer.domElement);
controls.enableDamping=true;controls.enablePan=false;
scene.add(new THREE.AmbientLight(0xffffff,1.35));
for(const [pos,power,shadow] of [[[-3,5,8],2.1,true],[[3,4,-8],2.1,false],[[6,-1,3],.35,false]]){
 const l=new THREE.DirectionalLight(0xffffff,power);l.position.set(...pos);scene.add(l);
 if(shadow){l.castShadow=true;l.shadow.mapSize.set(2048,2048);Object.assign(l.shadow.camera,{left:-5,right:5,top:5,bottom:-5,near:.1,far:25});l.shadow.bias=-.0001;l.shadow.normalBias=.005;}
}
const models=[];let active=0,spinning=false;
const loader=new GLTFLoader();
for(const item of data){
 const raw=Uint8Array.from(atob(item.base64),c=>c.charCodeAt(0));
 const gltf=await loader.parseAsync(raw.buffer,'');
 gltf.scene.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;}});
 scene.add(gltf.scene);models.push(gltf.scene);
}
function resetCamera(){
 const distance=active===0?11.7:3.8;
 camera.position.set(0,0,distance);controls.target.set(0,0,0);
 controls.minDistance=active===0?5:1.8;controls.maxDistance=active===0?20:8;
 controls.update();
}
window.setView=mode=>{
 spinning=false;document.querySelector('#spin').textContent='Auto rotate';
 resetCamera();models[active].rotation.set(mode==='angle'?.10:0,mode==='back'?Math.PI:mode==='side'?Math.PI/2:mode==='angle'?-.25:0,mode==='angle'?-.04:0);
 document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===mode));
};
window.selectModel=i=>{
 active=i;models.forEach((m,j)=>m.visible=j===i);
 document.querySelectorAll('[data-model]').forEach(b=>b.classList.toggle('selected',Number(b.dataset.model)===i));
 document.querySelector('#object-name').textContent=i===0?'The sealed envelope':'The Sembang wax seal';
 window.setView('angle');
};
document.querySelectorAll('[data-model]').forEach(b=>b.onclick=()=>window.selectModel(Number(b.dataset.model)));
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>window.setView(b.dataset.view));
document.querySelector('#spin').onclick=e=>{spinning=!spinning;e.target.textContent=spinning?'Pause rotation':'Auto rotate';};
document.querySelectorAll('[data-download]').forEach(b=>b.onclick=()=>{
 const item=data[Number(b.dataset.download)];const a=document.createElement('a');a.download=item.name+'.glb';a.href='data:model/gltf-binary;base64,'+item.base64;a.click();
});
new ResizeObserver(()=>{
 const w=host.clientWidth,h=host.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();
}).observe(host);
window.selectModel(0);
const clock=new THREE.Clock();
renderer.setAnimationLoop(()=>{const dt=Math.min(clock.getDelta(),.05);if(spinning)models[active].rotation.y+=dt*.45;controls.update();renderer.render(scene,camera);});
window.envelopeViewer={models,renderer,camera,controls};window.modelsReady=true;
