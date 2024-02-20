/**
 * @author Algirdas Noreika, Indeform Ltd
 * @copyright Copyright 2019, Indeform Ltd
 * @version 20240214
 * @description Data table.
 */


import * as Osom from "osom";

// Table type class should extend OsomTable class. TODO think how OsomList nad OsomTable may be different.
export default class ProjectsTable extends Osom.Component {
    constructor() {
        super( // HTML Element. Possible values: HTML Template, Element ID, or Element as DOM object.
            `
                <table class="table">
                <tr><td><b>Title</b></td><td>&nbsp;</td></tr>
                <tbody>
                    <tr osom-repeat="projects">
                    <td>{title}</td><td><button osom-event="removeProject" data-id="{id}" xxx="{id}">Remove</button></td>
                    </tr>
                </tbody>
                </table>
            `,

            // Data binding. Initial values.
            { projects: [] },

            // Events filter
            ['click'],      
        );

        this.update();
  }
  
 

    async update() {
        super.update();

        /*
        let resp = await Osom.Net.getJSON('http://127.0.0.1:8000/crud/testprojects');

        if (resp) {
            this.setData('projects', resp);
            console.log('Setting data', resp);
        } else {
            console.log("NODATA-ERROR", resp);
        }
        */
    }


    
    async on_removeProject(d, e) {
        /*
        let resp = await Osom.Net.postJSON('http://127.0.0.1:8000/crud/testprojects/remove', { remove: e.target.dataset['id'] });

        if (resp) {
            this.update();
        } else {
            console.log("Removal-ERROR", resp);
        }
        */
    }
}


