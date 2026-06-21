/*
 * Read the database spec in YAML format from stdin and render markdown
 * on stdout
 */

import fs from 'fs';
import YAML from 'yaml';
import { tsMarkdown } from 'ts-markdown';

// The tree of markdown elements to render
const entries = [
    "<!-- This is an automatically generated file, and should",
    "not be edited manually. Edit the database.yaml file and",
    "run make to regenerate this file. -->",
    "",

    { h1: 'Seshcord Database Types' },
    { p: [
        "The following is the set of tables used for the ",
        "Discord server."
    ] }
];

// stdin as a filehandle
const fh = fs.readFileSync( 0, 'utf8' )
// The decoded YAML tree
const yaml = YAML.parse( fh )

// console.log( yaml ); process.exit( 1 );

// Read each database table
for( const [name, data] of Object.entries( yaml['tables'] ))
{
    entries.push( {h2: name} );
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

    /*
        //
        // Packet name, id, and description
        list.push( [
            {text: [
                def['id'], ' ', 
                {code: name}, ': ',
                def['desc']
            ]}
        ] );

        // Packet data, if any
        if( 'fields' in def )
        {
            // The list of fields to be rendered as markdown
            var fields = [];

            for( const field of def['fields'] )
            {
                // Name, type and description of field, to
                // be rendered as markdown
                const info = {text: [
                    {code: field['name']},
                    ' (', field['type'], '): ',
                    field['desc']
                ]};

                // For structs or lists: The child fields
                if( 'children' in field )
                {
                    // The list of children, to be rendered
                    // as markdown
                    var children = []

                    for( var child of field['children'] )
                    {
                        children.push( {text: [
                            {code: child['name']},
                            ' (', child['type'], '): ',
                            child['desc']
                        ]} );
                    }
                    fields.push( [info, {ul: children}] );
                }
                else
                {
                    fields.push( info );
                }
            }
            list.at( -1 ).push( {ul: fields} );
        }
        //console.log( name, def );
    }
    entries.push( {ul: list} );
    */

}

// Render the actual markdown to stdout
console.log( tsMarkdown( entries ));

