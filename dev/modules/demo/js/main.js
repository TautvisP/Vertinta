

import * as Osom from "osom"
import CreateProjectForm from "./frm-create-project";
import ProjectsTable from "./projects-table";


class Main extends Osom.Component {
    constructor() {
        super( // HTML Element. Possible values: HTML Template, Element ID, or Element as DOM object.
            'main-container',

            // Data binding. Initial values.
            { projects: [] },

            // Events filter
            ['click'],      
        );


        this.pt = this.append(ProjectsTable, 'data-table-container');
        this.cpf = this.append(CreateProjectForm, document.body, { list:this.pt });

        console.log(this);
    }
  

    on_createProject(d, e) {
        this.cpf.clear();
        this.cpf.show();
    };
}


new Main();