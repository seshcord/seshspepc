import json
import yaml
import sys

class CFormatter:
    def __init__( self ):
        self.nests = []
        pass

    def output( self, content ):
        print( " " * (len( self.nests ) * 4) + content )
        return self

    def blank( self ):
        return self.output( "" )

    def comment( self, text ):
        return self.output( f"/* {text} */" )

    def include( self, include ):
        return self.output( f"#include <{include}>" )

    def pragma( self, pragma ):
        return self.output( f"#pragma {pragma}" )

    def define( self, word, content=None ):
        result = f"#DEFINE {word}"
        if content != None:
            result += f" {content}"
        return self.output( result )

    def var( self, vtype, name, comment=None ):
        result = f"{vtype} {name};"
        if comment != None:
            result += f" /* {comment} */"
        return self.output( result )

    def typedef( self, old, new ):
        return self.output( f"typedef {old} {new};" )

    def nest( self, ntype ):
        """Open a nested structure"""

        self.nests.append( ntype )
        return self

    def struct( self, stype=None ):
        if( stype != None ):
            self.output( f"struct {stype}" )
        else:
            self.output( f"struct" )
        self.output( "{" )
        self.nest( 'struct' )
        return self

    def enum( self, etype=None, *values ):
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
        ntype = self.nests.pop()
        if ntype in ('struct', 'enum', 'array'):
            if option != None:
                return self.output( f"{'}'} {option};" )
            else:
                return self.output( "};" )
        else:
            return self.output( "}" )

    def arrayliteral( self, atype, name, *items ):
        self.output( f"{atype} {name}[] = " + "{" )
        self.nest( 'array' )
        for item in items:
            self.output( f"{item}," )
        self.close()
        return self

    def funcprototype( self, ret, name, *args ):
        self.output( f"{ret} {name}( {', '.join( args )} );" )


def main():
    fmt = CFormatter()

    ( fmt.include( 'stdint.h' )
     .pragma( 'pack(1)' )
     .blank()
     .typedef( 'uint64_t', 'timestamp' )
     .typedef( 'uint8_t', 'uuid[16]' )
     .blank()
     )

    with open( 'spec.yaml' ) as fh:
        spec = yaml.load( fh )

    types = spec['packet_types']
    ptypes = []
    for pkttype in types:
        ptypes.append( f"PKT_ITEM_{pkttype.upper()}" )
    ptypes.append( "PKT_ITEM_END" )
    fmt.enum( "packet_items", *ptypes )

    for packet, info in spec['packets']['client'].items():
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


main()
