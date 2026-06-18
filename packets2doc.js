/*
 * Read the packet spec in YAML format from stdin and render markdown on
 * stdout
 */

import fs from 'fs';
import YAML from 'yaml';
import { tsMarkdown } from 'ts-markdown';

// The tree of markdown elements to render
const entries = [
    { h1: 'Seshcord Packet Types' },
];

// stdin as a filehandle
const fh = fs.readFileSync( 0, 'utf8' )
// The decoded YAML tree
const yaml = YAML.parse( fh )

// Read each side: Server->Client and Client->Server
for( const [side, packets] of Object.entries( yaml ))
{
    // The "human-readable" side name
    var sidename;
    if( side == 'server' )
    {
        sidename = "Server-to-Client packets";
    }
    else if( side == 'client' )
    {
        sidename = "Client-to-Server packets";
    }
    else
    {
        console.error( "Unknown packet side: ", side );
        process.exit( 1 );
    }

    entries.push( {h2: sidename} );

    // The packets on this side
    var list = []

    //console.log( side );
    for( const [name, def] of Object.entries( packets ))
    {
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

}

// Render the actual markdown to stdout
console.log( tsMarkdown( entries ));

