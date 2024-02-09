/**
 * @author Indeform Ltd
 * @license MIT
 * @description Cad Demo
 **/


 import * as THREE from "three";

/**
* DemoCad class
* @class
**/
export default class DemoCad {
    cube = null;
    scene = null;
    camera = null;
    renderer = null;
    container = null;

   /**
    * Constructor
    * @returns {void}
    **/
    constructor() {
        this.init();
        this.createObjects();
        this.startAnimationLoop();
    }


    init() {
        window.addEventListener( 'resize', () => { this.onResize(); }, false );

        this.container = document.getElementById("view3d");
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera( 75, this.container.clientWidth / this.container.clientHeight, 0.1, 1000 );

        this.renderer = new THREE.WebGLRenderer();
        this.renderer.setSize( this.container.clientWidth, this.container.clientHeight );
        this.renderer.setClearColor( 0xaebdd0, 1 );

        this.container.appendChild( this.renderer.domElement );
        this.camera.position.z = 5;
    }


    onResize() {
        this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera.updateProjectionMatrix();

        this.renderer.setSize( this.container.clientWidth, this.container.clientHeight );
    }


    startAnimationLoop() {
        requestAnimationFrame( () => { this.startAnimationLoop(); } );
        this.update();
        this.renderer.render(this.scene, this.camera );
    }


    update() {
        this.cube.rotation.x += 0.01;
        this.cube.rotation.y += 0.01;
    }


    createObjects() {
        const geometry = new THREE.BoxGeometry();
        const material = new THREE.MeshBasicMaterial( { color:0xcdcdcd } );
        this.cube = new THREE.Mesh( geometry, material );
        this.scene.add( this.cube );
    }
}