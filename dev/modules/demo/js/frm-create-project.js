/**
 * @author Algirdas Noreika, Indeform Ltd
 * @copyright Copyright 2019, Indeform Ltd
 * @version 20240214
 * @description Dialog for adding data.
 */


import * as Osom from "osom";


export default class CreateProjectForm extends Osom.Form {
  constructor({ list }) {
    super( // HTML Element. Possible values: HTML Template, Element ID, or Element as DOM object.
      `
        <div class="dialog hidden">
          <h1>Create Project<button osom-event="closeDialog">X</button></h1>
          <form method="post" onsubmit="return false;">
            <p><input type="text" name="title"/></p>
            <div class="footer"><button osom-event="submitData" class="close">Create</button></div>
          </form>
        </div>
      `,

      // Data binding. Initial values.
      {},

      // Events filter
      ['click'],   
    );

    //console.log("LIST", list);
    this.list = list;

  }


    on_closeDialog(d, e) {
        this.show(false);
    }


    async on_submitData(d, e) {
        
        let resp = await this.submit('http://127.0.0.1:8000/crud/testprojects/create');
        if (resp) {
            this.clear();
            this.list.update();
            this.show(false);
        }
    };
    
    
    show(val = true) {

        let elements = Object.values(this._elements);
        let first = elements[0]

        if (val) {
            first.classList.remove("hidden");
        } else {
            first.classList.add("hidden");
        }
    }
}


