import json
import yaml
import sys
from pathlib import Path
from argparse import ArgumentParser

class CFormatter:
    """A basic C code emitter.

    This emits C code structures in a relatively structured way. It only
    includes a small subset of C structures; just enough to render the elements
    we need for the Seshcord header files.

    Each method called will output the relevant structure to stdout (keeping
    track of indents as needed.
    """

    def __init__( self, fh=None ):
        """Initialize a new formatter.

        fh -- The filehandle to write to, default stdout
        """

        # The current set of nested structures
        self.nests = []
        if fh == None:
            fh = sys.stdout
        self.fh = fh

    def output( self, content ):
        """Output a line, with indents as necessary"""
        print( " " * (len( self.nests ) * 4) + content, file=self.fh )
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

    def include( self, include, local=False ):
        """Output an #include directice

        local -- If the include is "local" (enclosed in quotes
            rather than brackets
        """
        if local:
            l = '"'
            r = '"'
        else:
            l = '<'
            r = '>'

        return self.output( f"#include {l}{include}{r}" )

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
    parser = ArgumentParser(
            description='Generate packet schema C files from the spec' )
    parser.add_argument(
            'spec', nargs='?', type=Path,
            help="Spec YAML file (default stdin)" )
    parser.add_argument(
            'output', nargs='?', type=Path,
            help="Output file (default stdout)" )
    parser.add_argument(
            '--code', '-c', action='store_true',
            help="Generate the code file. (Default is generate the " +
            "header, unless the output filename ends in .c)" )
    parser.add_argument(
            '--include', '-i', default='packets.h',
            help="The file to include in the .c output. (Default " +
            '"packets.h")' )

    args = parser.parse_args()

    if args.output == None:
        ofh = sys.stdout
    else:
        ofh = open( args.output, 'wt' )
        if args.output.suffix == '.c':
            args.code = True

    if args.spec == None:
        ifh = sys.stdin
    else:
        ifh = open( args.spec, 'rt' )

    with ifh:
        with ofh:
            if args.code:
                make_packets_c( ifh, ofh, args.include )
            else:
                make_packets_h( ifh, ofh )

# Make the packets.h file
def make_packets_h( ifh, ofh ):
    fmt = CFormatter( ofh )

    # Output the heading
    ( fmt.comment( "This is an automatically generated file. Do not edit.",
                  '',
                  "To regenerate this file, edit spec.yaml and call",
                  "spec2packetsh.py" )

     .include( 'stdint.h' )
     .include( 'stdlib.h' )
     .pragma( 'pack(1)' )
     .blank()
     .typedef( 'uint64_t', 'timestamp' )
     .typedef( 'uint8_t', 'uuid[16]' )
     .blank()
     .comment( "Handler function type for received packets" )
     # typedef() doesn't know how to do function pointers
     .output( f"typedef void (*packet_callback)( void * );" )
     .blank()
     )

    # Load the YAML
    spec = yaml.load( ifh )

    # The list of types used by the spec
    types = spec['packet_types']

    # Create the packet_items enum
    ptypes = []
    for pkttype in types:
        ptypes.append( f"PKT_ITEM_{pkttype.upper()}" )
    ptypes.append( "PKT_ITEM_END" )
    (fmt.comment( "The types of data that may be included in a packet.",
                 "See the specification for what these types mean.",
                 "PKT_ITEM_END marks the end of a list or struct." )
     .enum( "packet_items", *ptypes )
     .blank()
     )

    # Create the packet_info structure
    (fmt
     .comment( "Information for handling a particular packet. This includes",
              "schema (which descrives the physical packet structure), and",
              "a callback function to handle it." )
     .struct( "packet_info" )
     .var( 'enum packet_items *', 'schema', comment='Packet schema' )
     .var( 'int', 'len', comment='Packet schema length' )
     .var( 'packet_callback', 'callback', comment='Handler function' )
     .close()
     .blank()
     )

    for side in spec['packets']:
        fmt.comment( f"{side}-side packets." ).blank()
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
                            schema.append( f"PKT_ITEM_{child['type'].upper()}" )
                            fmt.var( types[child['type']]['c'], child['name'], child['desc'] )
                        if field['type'] == 'list':
                            fmt.close( f"*{field['name']}" )
                        if field['type'] == 'struct':
                            fmt.close( field['name'] )
                        schema.append( "PKT_ITEM_END" )

                    if 'c' in types[field['type']]:
                        fmt.var( types[field['type']]['c'], field['name'],
                                field['desc'] )

                fmt.close()
                # Extern the schema, it lives in packets.c
                fmt.output( f"extern enum packet_items {packet.upper()}_SCHEMA[];" )
                fmt.define( f"{packet.upper()}_SCHEMA_LEN", len( schema ))

            if 'fields' in info:
                cbarg = f"struct {packet.lower()}"
            else:
                cbarg = 'void *'

            fmt.funcprototype( 'void', f"callback_{packet.lower()}", cbarg )
            fmt.blank()


def make_packets_c( ifh, ofh, include ):
    fmt = CFormatter( ofh )

    # Output the heading
    ( fmt.comment( "This is an automatically generated file. Do not edit.",
                  '',
                  "To regenerate this file, edit spec.yaml and call",
                  "spec2packetsh.py" )

     .include( include, True )
     .blank()
     )

    # Load the YAML
    spec = yaml.load( ifh )

    for side in spec['packets']:
        fmt.comment( f"{side}-side packets." ).blank()
        for packet, info in spec['packets'][side].items():
            if 'fields' in info:
                fmt.comment( info['desc'] )
                schema = []
                for field in info['fields']:
                    schema.append( f"PKT_ITEM_{field['type'].upper()}" )
                    if 'children' in field:
                        for child in field['children']:
                            schema.append( f"PKT_ITEM_{child['type'].upper()}" )
                        schema.append( "PKT_ITEM_END" )

                fmt.arrayliteral( 'enum packet_items',
                                 f"{packet.upper()}_SCHEMA",
                                 *schema )
            fmt.blank()

        # Map packet types by number and sort them
        packetmap = {v['id']: k for k, v in spec['packets'][side].items()}
        packetnums = list( packetmap.keys() )
        packetnums.sort()

        (fmt.comment( 'Minimum and maximum pacet numbers' )
         .define( f"PACKET_{side.upper()}_MIN", packetnums[0] )
         .define( f"PACKET_{side.upper()}_MAX", packetnums[-1] )
         .blank()
         )

        fmt.comment( "List of packet type information" )
        infos = []
        for i in range( packetnums[0], packetnums[-1] + 1 ):
            if i in packetmap:
                packet = packetmap[i]
                if 'fields' in spec['packets'][side][packet]:
                    infos.append( "{ " + f"{packet}_SCHEMA, {packet}_SCHEMA_LEN, (packet_callback) callback_{packet.lower()}" + " }" )
                else:
                    infos.append( "{ " + f"NULL, 0, (packet_callback) callback_{packet.lower()}" + " }" )
        fmt.arrayliteral( 'struct packet_info', f"{side}_packet_dispatcher", *infos )





if __name__ == '__main__':
    main()
