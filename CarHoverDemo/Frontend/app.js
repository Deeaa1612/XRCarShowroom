import * as THREE from 'https://unpkg.com/three@0.160.1/build/three.module.js';
import { OrbitControls } from 'https://unpkg.com/three@0.160.1/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'https://unpkg.com/three@0.160.1/examples/jsm/loaders/GLTFLoader.js';

let scene, camera, renderer, controls;
init3D();

document.getElementById('chatBtn').addEventListener('click', handleChat);

function init3D() {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x111111);

  camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.set(0, 2, 6);

  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);

  controls = new OrbitControls(camera, renderer.domElement);

  const ambientLight = new THREE.AmbientLight(0xffffff, 1);
  scene.add(ambientLight);

  animate();
}

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}

function handleChat() {
  const fileInput = document.getElementById('fileInput');
  const file = fileInput.files[0];

  if (!file) {
    alert('Please upload a PDF brochure first.');
    return;
  }

  const reader = new FileReader();
  reader.onload = async function () {
    const pdfData = new Uint8Array(reader.result);
    const base64PDF = btoa(String.fromCharCode(...pdfData));

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer YOUR_OPENAI_API_KEY',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: "gpt-4-1106-preview",
        messages: [
          {
            role: "system",
            content: "Extract the car model and list important features from the brochure PDF content provided."
          },
          {
            role: "user",
            content: `PDF content (base64): ${base64PDF}`
          }
        ]
      })
    });

    const result = await response.json();
    const reply = result.choices[0].message.content;

    displayFeatures(reply);
    loadCarModel(); // Load 3D model dynamically
  };

  reader.readAsArrayBuffer(file);
}

function displayFeatures(reply) {
  const modelName = reply.match(/(HYUNDAI|MARUTI|TATA|KIA|HONDA|BMW|MERCEDES)[^\n]*/i);
  document.getElementById('modelName').textContent = modelName ? modelName[0].toUpperCase() : "CAR MODEL";
  console.log("Extracted features:\n" + reply);
}

function loadCarModel() {
  const loader = new GLTFLoader();
  loader.load('model.glb', (gltf) => {
    gltf.scene.scale.set(1.5, 1.5, 1.5);
    gltf.scene.position.set(0, 0, 0);
    scene.add(gltf.scene);
  }, undefined, (error) => {
    console.error("Model load error:", error);
  });
}
