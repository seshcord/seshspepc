import json
import sys

def main():
    print( "#include <stdint.h>" )
    print( "#pragma pack(1)" )
    print( "" )
    print( "typedef uint64_t timestamp;" )
    print( "typedef uint8_t uuid[16];" )
    print( "" )
    data = json.load( sys.stdin )
    for side in data.values():
        for packet in side.values():
            convertPacket( packet )

def convertPacket( packet ):
    print( f"/* {packet['desc']} */" );
    print( f"#define {packet['name']} {packet['num']}" )
    if len( packet['elements'] ) != 0:
        print( f"struct {packet['name'].lower()}" )
        print( "{" )
        dumpElements( packet['elements'] )
        print( "};" )
        print( f'#define {packet["name"]}_SCHEMA "{getSchema( packet["elements"] )}"' )
    else:
        print( "/* No payload */" )
    print( "" )

def dumpElements( elements, indent=1 ):
    xlat = {
            'str': 'char *',
            'binary': 'char *',
            'int8': 'int8_t',
            'uint8': 'uint8_t',
            'int16': 'int16_t',
            'uint16': 'uint16_t',
            'int32': 'int32_t',
            'uint32': 'uint32_t',
            'int64': 'int64_t',
            'uint64': 'uint64_t',
            'time': 'timestamp'
            }


    for e in elements:
        etype = e['type'] 
        if etype in xlat:
            etype = xlat[etype]
        desc = e['desc']
        name = e['name']
        spaces = "  " * indent
        if etype == 'struct' or etype == 'list':
            ptr = ''
            if etype == 'list': ptr = '*'
            print( f"{spaces}struct" )
            print( f"{spaces}" + "{" )
            dumpElements( e['children'], 2 )
            print( f"{spaces}" + "}" + f" {ptr}{name};" )
        else:
            print( f"{spaces}{etype} {name}; /* {desc} */" )


def getSchema( elements ):
    xlat = {
            'str': '*',
            'binary': '+',
            'int8': 'c',
            'uint8': 'C',
            'int16': 's',
            'uint16': 'S',
            'int32': 'i',
            'uint32': 'I',
            'int64': 'l',
            'uint64': 'L',
            'time': 'L',
            'uuid': 'U',
            'struct': '',
            'list': '[]'
            }
    schema = ''
    for e in elements:
        etype = e['type']
        x = xlat[etype]
        if 'children' in e:
            if x != '':
                schema += x[0]
            schema += getSchema( e['children'] )
            if x != '':
                schema += x[1]
        else:
            schema += x
    return schema

       



main()
