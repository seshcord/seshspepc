import { render } from './yaml2md.js';

const formatter = {
    'types': function( data ) {
        var list = [];
        for( const [type, info] of Object.entries( data ))
        {
            list.push( {text: [{code: type}, 
                ": ", info['desc']]} );
        }
        return [{ul: list}];
    },
    packets: function( data ) {
        // Formatted content to be returned
        var result = []

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

            result.push( {h2: sidename} );

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
            result.push( {ul: list} );
        }

        return result;
    }
};

render( formatter );
