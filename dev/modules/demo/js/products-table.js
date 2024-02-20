/**
 * @author Algirdas Noreika, Indeform Ltd
 * @copyright Copyright 2019, Indeform Ltd
 * @version 20240214
 * @description Data table.
 */


import * as Osom from "osom";

// Table type class should extend OsomTable class. TODO think how OsomList nad OsomTable may be different.
export default class ProductsTable extends Osom.Component {
    constructor() {
        super( // HTML Element. Possible values: HTML Template, Element ID, or Element as DOM object.
            `           
            <table class="tspace">
            <caption>Products</caption>
            <thead>
                <tr>
                    <th>Code</th>
                    <th>Title</th>
                    <th>Stock</th>
                </tr>
            </thead>
            <tbody>
                <tr osom-repeat="products">
                    <td>{code}</td>
                    <td>{title}</td>
                    <td>{stock}</td>
                    <td><button osom-event="removeProduct" data-id="{id}" xxx="{id}">Remove</button></td>
                </tr>
            </tbody>
            </table>
            `,

            // Data binding. Initial values.
            { products: [] },

            // Events filter
            ['click'],      
        );

        this.update();
  }
  
 

    async update() {
        super.update();

        let resp = await Osom.Net.getJSON('http://127.0.0.1:8000/demo/osom/api/list');

        if (resp) {
            this.setData('products', resp);
        } else {
            console.log("NODATA-ERROR", resp);
        }
    }


    
    async on_removeProduct(d, e) {
        let resp = await Osom.Net.postJSON('http://127.0.0.1:8000/demo/osom/api/remove', { remove: e.target.dataset['id'] });

        if (resp) {
            this.update();
        } else {
            console.log("Removal-ERROR", resp);
        }
    }
}


