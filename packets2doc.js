/*
 * Read the packet spec in YAML format from stdin and render markdown on
 * stdout
 */

import fs from 'fs';
import YAML from 'yaml';
import { tsMarkdown } from 'ts-markdown';

// The tree of markdown elements to render
const entries = [
    "<!-- This is an automatically generated file, and should",
    "not be edited manually. Edit the packets.yaml file and",
    "run make to regenerate this file. -->",
    ""
];

// stdin as a filehandle
const fh = fs.readFileSync( 0, 'utf8' )
// The decoded YAML tree
const yaml = YAML.parse( fh )

var list = [];
for( const [section, data] of Object.entries( yaml ))
{
    if( section == 'types' )
    {
        // Packet data types, WIP
        var list = [];
        for( const [type, info] of Object.entries( data ))
        {
            list.push( {text: [{code: type}, 
                ": ", info['desc']]} );
        }
        entries.push( {ul: list} );
    }
    else if( section == 'packets' )
    {
        // Read each side: Server->Client and Client->Server
        for( const [side, packets] of Object.entries( data ))
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
    }
    else if( Array.isArray( data ))
    {
        entries.push( ...data );
    }
    else
    {
        entries.push( {p: "Non-array spec data"} );
    }
}

// Render the actual markdown to stdout
console.log( tsMarkdown( entries ));

