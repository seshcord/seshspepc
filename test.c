#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "packets.h"

int encode_from_schema( void *, enum packet_items *, int, char *, int, int );
union ptype
{
    int8_t int8;
    uint8_t uint8;
    int16_t int16;
    uint16_t uint16;
    int32_t int32;
    uint32_t uint32;
    int64_t int64;
    uint64_t uint64;
    char *str;
    uint64_t time;
    uint8_t uuid[16];
    char *binary;
    void *ptr;
};

int main( void )
{
    struct seshcord_sv_msg test = {
        { 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 }, /* id */
        { 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0  }, /* chat */
        { 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0  }, /* sender */
        "This is a message", /* message content */
        1, /* attachment count */
        NULL
    };
    test.attachments = malloc( sizeof( *test.attachments ));
    test.attachments[0].filename = "test.txt";
    test.attachments[0].size = 42;
    test.attachments[0].path = "http://test.example.org/test.txt";

    char buffer[256];
    int res = encode_from_schema( &test,

            SESHCORD_SV_MSG_SCHEMA,
            SESHCORD_SV_MSG_SCHEMA_LEN,
            buffer, sizeof( buffer ), 1 );
    fprintf( stderr, "size: %i\n", res );
    fwrite( buffer, res, 1, stdout );
    return 0;
}

/* Helper macro for the following */
#define copybuffrom( from,s ) \
    fprintf( stderr, "Copying %i bytes\n", s ); \
    size += s; \
    remain -= s; \
    if( remain >= 0 ) { \
        memcpy( buffer, from, s ); \
        buffer += s; \
    } 

#define copybuf( s ) \
    copybuffrom( input, s ) \
    input += s;

#define copybuft( t ) \
    copybuf( sizeof( u-> t ));

#define copybufsave( t ) \
    copybuft( t ); \
    lastint = u-> t ; \
    fprintf( stderr, "Decoded an int %i\n", lastint )

/*
 * Encode a packet (payload) for transmission or calculate its size.
 *
 * packet_data: A structure containing decoded packet data
 * schema: The packet schema
 * len: Number of elements in the schema
 * buffer: The buffer to encode the raw binary data to
 * max: The length of the buffer.
 *
 * return: The size of the encoded packet.
 *
 * If the encoded packet is larger than `max`, the buffer is filled out to that
 * length and the rest is discarded. The return value will reflect the actual
 * size required to encode the packet, whether it is fully encoded or not.
 *
 * Thus, specifying NULL for `buffer` and 0 for `max` will calculate the size
 * of the packet without encoding it. This can be useful to determine the
 * amount of memory to allocate a buffer.
 */
int encode_from_schema( void *packet_data, 
        enum packet_items * schema, int len,
        char *buffer, int max, int count )
{
    int i; /* Index into schema */
    void *input = packet_data; /* Pointer to current data item */
    int remain = max; /* Remaining space in the buffer */
    long lastint = 0; /* The previously encoded integer */
    int size = 0; /* Size of the encoded packet */
    int tmp; /* Temporary integer storate */
    int lsize;
    union ptype *u;
    int j;
    for( j = 0; j < count; j++ )
    {
        for( i = 0; i < len; i++ )
        {
            u = input;
            fprintf( stderr, "Schema item type %i\n", schema[i] );

            switch( schema[i] )
            {
                case PKT_ITEM_UUID: /* 128-bit */
                    copybuft( uuid );
                    break;
                case PKT_ITEM_INT64:
                    copybufsave( int64 );
                    break;
                case PKT_ITEM_UINT64:
                case PKT_ITEM_TIME:
                    copybufsave( uint64 );
                    break;
                case PKT_ITEM_INT32:
                    copybufsave( int32 );
                    break;
                case PKT_ITEM_UINT32:
                    copybufsave( uint32 );
                    break;
                case PKT_ITEM_INT16:
                    copybufsave( int16 );
                    break;
                case PKT_ITEM_UINT16:
                    copybufsave( uint16 );
                    break;
                case PKT_ITEM_INT8:
                    copybufsave( int8 );
                    break;
                case PKT_ITEM_UINT8:
                    copybufsave( uint8 );
                    break;
                case PKT_ITEM_STR:
                    tmp = strlen( u->str ) + 1;
                    fprintf( stderr, "Copying a string of size %i\n", tmp );
                    copybuffrom( u->str, tmp );
                    input += sizeof( u->str );
                    break;
                case PKT_ITEM_BINARY:
                    copybuffrom( u->binary, lastint );
                    input += sizeof( u->binary );
                    break;
                case PKT_ITEM_LIST:
                    lsize = 0; /* list schema size */
                    i++;
                    while( schema[i + lsize] != PKT_ITEM_END ) lsize++;
                    fprintf( stderr, "Processing list of size %i of %i elements\n", lsize,lastint );
                    tmp = encode_from_schema( u->ptr, &schema[i], lsize, buffer, remain, lastint );
                    size += tmp;
                    remain -= tmp;
                    if( remain >= 0 ) buffer += tmp;
                    input += sizeof( u->ptr );
                    i += lsize;
                    break;


                case PKT_ITEM_STRUCT:
                case PKT_ITEM_END:
            } 
        }
    }
    return size;
}

/* Dummy callbacks to shut up the linker */
void callback_seshcord_cl_error( struct seshcord_cl_error data ) {}
void callback_seshcord_cl_handshake_init( struct seshcord_cl_handshake_init data ) {}
void callback_seshcord_cl_auth_register( struct seshcord_cl_auth_register data ) {}
void callback_seshcord_cl_auth_login( struct seshcord_cl_auth_login data ) {}
void callback_seshcord_cl_send_msg( struct seshcord_cl_send_msg data ) {}
void callback_seshcord_cl_get_servers( void * data ) {}
void callback_seshcord_cl_get_dms( struct seshcord_cl_get_dms data ) {}
void callback_seshcord_cl_get_friends( void * data ) {}

void callback_seshcord_sv_err( struct seshcord_sv_err data ) {}
void callback_seshcord_sv_msg( struct seshcord_sv_msg data ) {}
void callback_seshcord_sv_msg_del( struct seshcord_sv_msg_del data ) {}
void callback_seshcord_sv_friend_req( struct seshcord_sv_friend_req data) {}
