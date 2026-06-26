import json
import yaml
import sys

class CFormatter:
    """A basic C code emitter.

    This emits C code structures in a relatively structured way. It only
    includes a small subset of C structures; just enough to render the elements
    we need for the Seshcord header files.

    Each method called will output the relevant structure to stdout (keeping
    track of indents as needed.
    """

    def __init__( self ):
        """Initialize a new formatter."""

        # The current set of nested structures
        self.nests = []

    def output( self, content ):
        """Output a line, with indents as necessary"""
        print( " " * (len( self.nests ) * 4) + content )
        return self

    def blank( self ):
        """Output a blank line"""
        return self.output( "" )

    def comment( self, *comments ):
        """Output a comment.

        If one argument is provided, output a single-line comment. Else, output
        a multiline comment.
        """
        if len( comments ) == 1:
            return self.output( f"/* {comments[0]} */" )
        self.output( "/*" )
        for comment in comments:
            self.output( " * " + comment )
        self.output( " */" )
        return self

    def include( self, include ):
        """Output an #include directice"""
        return self.output( f"#include <{include}>" )

    def pragma( self, pragma ):
        """Output a #pragma directive"""
        return self.output( f"#pragma {pragma}" )

    def define( self, word, content=None ):
        """Output a #define directive.

        word -- The keyword to define
        content -- What to replace the keyword with. If None, will simply
        #definethe keyword into existence.
        """
        result = f"#define {word}"
        if content != None:
            result += f" {content}"
        return self.output( result )

    def var( self, vtype, name, comment=None ):
        """Output a variable definition.

        vtype -- The type of the variable
        name -- The name of the variable
        comment -- An optional comment to include after the definition
        """

        result = f"{vtype} {name};"
        if comment != None:
            result += f" /* {comment} */"
        return self.output( result )

    def typedef( self, new, existing ):
        """Output a typedef.

        new -- The name of the type to create
        existing -- The type to declare `new` equivalent to
        """
        return self.output( f"typedef {new} {existing};" )

    def nest( self, ntype ):
        """Open a nested structure.

        This pushes a new nested structure (struct, enum, etc) to the list, but
        does not output anything. Further outputs will be indented to match,
        until a close() is called.

        This is not meant to be called directly, but used by other
        structure-specific methods.

        ntype -- The type of nested structure. close() will reference this to
        determine the appropriate output to close the structure.
        """

        self.nests.append( ntype )
        return self

    def struct( self, stype=None ):
        """Open a structure.

        stype -- The name of the structure type to define. If None, defines an
        anonymous structure.
        """
        if( stype != None ):
            self.output( f"struct {stype}" )
        else:
            self.output( f"struct" )
        self.output( "{" )
        self.nest( 'struct' )
        return self

    def enum( self, etype=None, *values ):
        """Define an enum.

        etype -- The name of the enum type to define. If None, defines an
        anonymous enum.
        values -- The list of valid values for the enum.
        """

        if( etype != None ):
            self.output( f"enum {etype}" )
        else:
            self.output( f"enum" )
        self.output( "{" )
        self.nest( 'enum' )
        for value in values:
            self.output( f"{value}," )
        self.close()
        return self

    def close( self, option=None ):
        """Close a nested structure.

        Unlike nest(), this *is* intended to be called directly, to mark the
        end of the open structure.

        option -- Additional code to add to the closed structure. Its function
        defines on the type of structure: For a struct, enum, or array, it adds
        a variable name to the end, defining an instance of the defined
        structure.
        """

        ntype = self.nests.pop()
        if ntype in ('struct', 'enum', 'array'):
            if option != None:
                return self.output( f"{'}'} {option};" )
            else:
                return self.output( "};" )
        else:
            return self.output( "}" )

    def arrayliteral( self, atype, name, *items ):
        """Define an array literal.

        This creates an array of the given type, and includes a provided
        initializer list.

        atype -- The base data type of the array
        name -- The name of the variable to create
        items -- The initializer list
        """

        self.output( f"{atype} {name}[] = " + "{" )
        self.nest( 'array' )
        for item in items:
            self.output( f"{item}," )
        self.close()
        return self

    def funcprototype( self, ret, name, *args ):
        """Define a function prototype.

        ret -- Return value
        name -- Function name
        args -- Argument list
        """

        self.output( f"{ret} {name}( {', '.join( args )} );" )


def main():
    fmt = CFormatter()

    # Output the heading
    ( fmt.comment( "This is an automatically generated file. Do not edit.",
                  '',
                  "To regenerate this file, edit spec.yaml and call",
                  "spec2packetsh.py" )

     .include( 'stdint.h' )
     .pragma( 'pack(1)' )
     .blank()
     .typedef( 'uint64_t', 'timestamp' )
     .typedef( 'uint8_t', 'uuid[16]' )
     .blank()
     .output( f"typedef void (*packet_callback)( void * );" )
     .blank()
     )

    # Load the YAML
    with open( 'spec.yaml' ) as fh:
        spec = yaml.load( fh )

    # The list of types used by the spec
    types = spec['packet_types']

    # Create the packet_items enum
    ptypes = []
    for pkttype in types:
        ptypes.append( f"PKT_ITEM_{pkttype.upper()}" )
    ptypes.append( "PKT_ITEM_END" )
    fmt.comment( "The types of data that may be included in a packet.",
                "See the specification for what these types mean.",
                "PKT_ITEM_END marks the end of a list or struct." )
    fmt.enum( "packet_items", *ptypes )

    fmt.struct( "packet_info" )
    fmt.var( 'enum packet_items *', 'schema', comment='Packet schema' )
    fmt.var( 'int', 'len', comment='Packet schema length' )
    fmt.var( 'packet_callback', 'callback', comment='Handler function' )
    fmt.close()
    fmt.blank()

    side = 'client'
    for packet, info in spec['packets'][side].items():
        fmt.comment( info['desc'] )
        fmt.define( packet, info['id'] )
        if 'fields' in info:
            schema = []
            fmt.struct( packet.lower() )
            for field in info['fields']:
                schema.append( f"PKT_ITEM_{field['type'].upper()}" )
                if 'children' in field:
                    fmt.struct()
                    for child in field['children']:
                        fmt.var( types[child['type']]['c'], child['name'], child['desc'] )
                        schema.append( f"PKT_ITEM_{child['type'].upper()}" )
                    if field['type'] == 'list':
                        fmt.close( f"*{field['name']}" )
                    if field['type'] == 'struct':
                        fmt.close( field['name'] )
                    schema.append( "PKT_ITEM_END" )


                if 'c' in types[field['type']]:
                    fmt.var( types[field['type']]['c'], field['name'],
                            field['desc'] )

            fmt.close()
            fmt.arrayliteral( 'enum packet_items',
                             f"{packet.upper()}_SCHEMA",
                             *schema )
            fmt.define( f"{packet.upper()}_SCHEMA_LEN {len( schema )}" )
        if 'fields' in info:
            cbarg = f"struct {packet.lower()}"
        else:
            cbarg = 'void *'

        fmt.funcprototype( 'void', f"callback_{packet.lower()}", cbarg )
        fmt.blank()

    # Map packet types by number and sort them
    packetmap = {v['id']: k for k, v in spec['packets'][side].items()}
    packetnums = list( packetmap.keys() )
    packetnums.sort()

    fmt.define( f"PACKET_{side.upper()}_MIN", packetnums[0] )
    fmt.define( f"PACKET_{side.upper()}_MAX", packetnums[-1] )

    infos = []
    for i in range( packetnums[0], packetnums[-1] + 1 ):
        if i in packetmap:
            packet = packetmap[i]
            infos.append( "{ " + f"{packet}_SCHEMA, {packet}_SCHEMA_LEN, callback_{packet.lower()}" + " }" )
    fmt.arrayliteral( 'packet_info', f"{side}_packet_dispatcher", *infos )





if __name__ == '__main__':
    main()
