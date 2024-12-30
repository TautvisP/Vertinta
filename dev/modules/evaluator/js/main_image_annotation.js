import ImageAnnotation from './image_annotation.js';

class MainImageAnnotation {
    /**
    * Constructor
    * @returns {void}
    **/
    constructor() {
        new ImageAnnotation('annotation-container', {}, ['click']);
    }
}

new MainImageAnnotation();