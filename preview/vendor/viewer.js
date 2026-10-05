import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const views=[];
let spinning=false;
const loader=new GLTFLoader();
const data=JSON.parse(document.getElementById('model-data').textContent);
window.modelViews=views;
window.modelsReady=false;
const promises=data.map(async (item,i)=>{
  const host=document.querySelectorAll('.viewport')[i];
  const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,preserveDrawingBuffer:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));
  renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.toneMapping=THREE.NoToneMapping;
  host.appendChild(renderer.domElement);
  const scene=new THREE.Scene();
  const camera=new THREE.PerspectiveCamera(34,1,.1,50);
  camera.position.set(0,0,6.6);
  const controls=new OrbitControls(camera,renderer.domElement);
  controls.enableDamping=true;
  controls.enablePan=false;
  controls.minDistance=4.4;
  controls.maxDistance=10;
  scene.add(new THREE.AmbientLight(0xffffff,2.2));
  const key=new THREE.DirectionalLight(0xffffff,1.0);
  key.position.set(-3,5,8); scene.add(key);
  const rear=new THREE.DirectionalLight(0xffffff,1.0);
  rear.position.set(3,4,-8); scene.add(rear);
  const side=new THREE.DirectionalLight(0xffffff,.8);
  side.position.set(7,-1,0); scene.add(side);
  const raw=Uint8Array.from(atob(item.base64),c=>c.charCodeAt(0));
  const gltf=await loader.parseAsync(raw.buffer,'');
  const model=gltf.scene;
  model.rotation.set(-.12,-.36,0);
  scene.add(model);
  const resize=()=>{
    const w=host.clientWidth,h=host.clientHeight;
    renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();
  };
  new ResizeObserver(resize).observe(host);resize();
  views.push({model,scene,camera,renderer,controls,id:i});
});
Promise.all(promises).then(()=>{window.modelsReady=true;document.querySelector('#status').textContent='4 models · ready to rotate';});
const clock=new THREE.Clock();
function frame(){
  requestAnimationFrame(frame);
  const dt=Math.min(clock.getDelta(),.05);
  for(const v of views){if(spinning)v.model.rotation.y+=dt*.5;v.controls.update();v.renderer.render(v.scene,v.camera);}
}frame();
window.setView=mode=>{
  spinning=false;document.querySelector('#spin').textContent='Auto rotate';
  for(const v of views){
    v.controls.reset();
    v.model.rotation.set(mode==='angle'?-.16:0,mode==='back'?Math.PI:mode==='side'?Math.PI/2:mode==='angle'?-.48:0,0);
  }
  document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===mode));
};
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>window.setView(b.dataset.view));
document.querySelector('#spin').onclick=e=>{spinning=!spinning;e.target.textContent=spinning?'Pause rotation':'Auto rotate';};
document.querySelector('#background').onchange=e=>document.body.dataset.background=e.target.value;
document.querySelectorAll('[data-download]').forEach(b=>b.onclick=()=>{
  const item=data[Number(b.dataset.download)];
  const a=document.createElement('a');a.href='data:model/gltf-binary;base64,'+item.base64;a.download=item.name+'.glb';a.click();
});
