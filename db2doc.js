/*
 * Read the database spec in YAML format from stdin and render markdown
 * on stdout
 */

import { render } from './yaml2md.js';

const formatter = {
    types: function( data ) {
        return [{p: "TBD"}];
    },
    tables: function( tables ) {
        // Rendered content to return
        var entries = [];
        // Read each database table
        for( const [name, data] of Object.entries( tables ))
        {
            entries.push( {h3: name} );
            entries.push( {p: data['desc']} );

            // List of fields, to be rendered
            var fields = []
            for( const field of data['fields'] )
            {
                fields.push( {text: [ 
                    {code: field['name']},
                    ' (', field['type'], '): ',
                    field['desc']
                ]});
            }

            entries.push( {'ul': fields} );
        }

        return entries;
    }
}

render( formatter );
