/**
 * @author Algirdas Noreika, Indeform Ltd
 * @copyright Copyright 2019, Indeform Ltd
 * @version 20240214
 * @description Dialog for adding data.
 */


import * as Osom from "osom";


export default class CreateProductForm extends Osom.Form {
  constructor({ list }) {
    super( // HTML Element. Possible values: HTML Template, Element ID, or Element as DOM object.
      `
        <div class="dialog hidden">
          <h1>Create Product<button osom-event="closeDialog">X</button></h1>

          <form class="col1" method="post" onsubmit="return false;">
                <p>
                    <label for="code_field">Code:</label>
                    <input id="code_field" type="text" name="code"/>
                </p>
                <p>
                    <label for="title_field">Title:</label>
                    <input id="title_field" type="text" name="title"/>
                </p>
                <p>
                    <label for="stock_field">Stock:</label>
                    <input id="stock_field" type="text" name="stock"/>
                </p>
                <p class="tright">
                    <button osom-event="submitData" class="close">Create</button>
                </p>
            </form>
        </div>
      `,

      // Data binding. Initial values.
      {},

      // Events filter
      ['click'],   
    );

    this.list = list;

  }


    on_closeDialog(d, e) {
        this.show(false);
    }


    async on_submitData(d, e) {
        
        let resp = await this.submit('http://127.0.0.1:8000/demo/osom/api/create');
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


