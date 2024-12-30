import ObjectGallery from './object_gallery.js';

class MainObjectGallery {
    /**
    * Constructor
    * @returns {void}
    **/
    constructor() {
        new ObjectGallery('gallery-container', {}, ['click']);
    }
}

new MainObjectGallery();