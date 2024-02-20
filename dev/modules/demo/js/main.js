

import * as Osom from "osom"
import CreateProductForm from "./frm-create-product";
import ProductsTable from "./products-table";


class Main extends Osom.Component {
    constructor() {
        super( // HTML Element. Possible values: HTML Template, Element ID, or Element as DOM object.
            'main-container',

            // Data binding. Initial values.
            { products: [] },

            // Events filter
            ['click'],      
        );


        this.pt = this.append(ProductsTable, 'data-table-container');
        this.cpf = this.append(CreateProductForm, document.body, { list:this.pt });
    }
  

    on_createProduct(d, e) {
        this.cpf.clear();
        this.cpf.show();
    };
}


new Main();