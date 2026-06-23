/*
 * Read the packet spec in YAML format from stdin and render markdown on
 * stdout
 */

import fs from 'fs';
import YAML from 'yaml';
import { tsMarkdown } from 'ts-markdown';

/* Section formatters
 *
 * Each function in this object will accept a section from the YAML
 * documentation, and will return a list of items to add to the markdown
 * entries list.
 */

export function render( formatter )
{
    // The tree of markdown elements to render
    const entries = [];

    // stdin as a filehandle
    const fh = fs.readFileSync( 0, 'utf8' )
    // The decoded YAML tree
    const yaml = YAML.parse( fh )

    for( const [section, data] of Object.entries( yaml ))
    {
        if( section in formatter )
        {
            entries.push( ...formatter[section]( data ));
        }
        else if( typeof data === "string" )
        {
            entries.push( data );
        }
        else if( Array.isArray( data ))
        {
            entries.push( ...data );
        }
        else
        {
            console.error( "Unrecognized section format:", section  );
            process.exit( 1 );
        }
    }

    // Render the actual markdown to stdout
    console.log( tsMarkdown( entries ));
}

if( import.meta.main )
{
    console.log( "This script should be imported as a module\n",
        "not called directly." );
}
