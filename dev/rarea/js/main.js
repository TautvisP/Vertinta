/**
 * @author Indeform Ltd
 * @license MIT
 * @description Main Restricted Area class.
 *      Class is responsible for initialization of sub-components, tools and classes.
 **/

import DemoCad from "./cad"

/**
* RAreaMain class
* @class
**/
export default class RAreaMain {
    /**
    * Constructor
    * @returns {void}
    **/
    constructor() {
        new DemoCad();
    }
}

new RAreaMain();
