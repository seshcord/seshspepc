## Basic Data Types ##

The following definitions shall be used to denote basic physical data formats:

* int8: Signed, two's complement 8-bit integer
* uint8: As above, but unsigned
* int16: Signed, two's complement, big-endian 16-bit integer
* uint16: As above, but unsigned
* int32: As above, but 32-bit
* uint32: As above, but unsigned
* int64: As above, but 64-bit
* uint64: As above, but unsigned
* int128: As above, but 128-bit
* uint128: As above, but unsigned
* str: Null-terminated UTF-8 encoded string
* time: A uint64 Unix timestamp
* uuid: A uint128 UUID
* binary: Arbitrary binary data. The element immediately preceeding this element
  must be an integer, representing the size in bytes.
* list: A series of elements that may appear zero or more times. The element
  immediately preceeding this element must be an integer, representing the
  number of elements.

## Wire Protocol ##

Seshcord runs over TCP, optionally over SSL.

Seshcord data will be sent between client and server as a stream of packets.
Each packet describes exatly one C->S or S->C event.

The packets have the following format:

* 4 ASCII characters 'SPKT' (clean 4 bytes)
* Payload size (uint32)
* Packet type (int16)
* Sequence id (uint16)
* Payload, if payload size non-zero. The format of the payload depends on the
  packet type.

[Packet types](packets.md)


## Database schema ##

The following is the database setup:

* `users`: User accounts
    * uuid `id`: Unique ID
    * str `name`: Username, should be (more or less) fixed, and suitable for a login name
    * str `display_name`: User's visible name, freely changeable (within reason)
    * time `registered`: Time of account registration
    * str `password`: Password (hashed)

* `servers`: Servers/guilds
    * uuid `id`: Unique ID
    * str `name`: Server name
    * time `created`: Time of creation

* `roles`: Roles available on a server
    * uuid `role`: Unique ID
    * uuid `server`: The server this role belongs to
    * str `name`: Name of the role
    * int `level`: Role permission level (higher levels can perform mod actions on users with lower levels)
    * bool `mod_role`: Can add/configure/delete a role equal or lesser to their own
    * bool `kick`: Can kick/ban/timeout users with lesser (or no) roles
    * bool `mod_channels`: Can add/configure/delete channels
    * bool `invite`: Can invite users/create invite links
    * (etc)

* `role_assignments`: Roles assigned to users
    * uuid `id`: Unique ID
    * uuid `user`: A user with a role
    * uuid `role`: A role assigned to the user

* `chats`: Text chats of any variety
    * uuid `id`: The ID of the chat
    * uuid `server`: The server the chat lives on, if any
    * str `name`: The name of the chat, if appropriate
    * uuid `role`: For server chats, the role required to access chat
    * (enum?) `type`: The type of chat. Server chat room, DM, DM group, etc.

* `chat_participants`: Users involved in a chat
    * uuid `chat`: The ID of the chat
    * uuid `participant`: A participant in the chat. 

* `messages`: Messages making up a chat room
    * uuid `id`: ID of the message
    * uuid `chat`: The chat the message was sent in/to
    * uuid `sender`: The user that sent the message
    * time `time`: The time the message was sent
    * str `text`: The message text

* `attachments`: Attachments on messages
    * uuid `id`: ID of the attachment
    * uuid `message`: ID of the message
    * str `url`: Link to attachment on CDN

* `friends`: Friend pairings (both active and pending)
    * uuid `id`: ID of this pairing
    * uuid `requestor`: ID of requestor
    * uuid `requestee`: ID of requestee
    * bool `accepted`: Whether request was accepted

* `notifications`: Any change in status a client should be notified of
    * uuid `id`: ID of this notification
    * uuid `target`: The user the notification is sent to
    * (enum?) `type`: The type of notification. Could be a message, edit, friend request, etc.
    * time `when`: The time of the change
    * uuid `ref`: ID of the target activity. Should match the appropriate table. Ex. For a message this should point to the relevant row in the messages table










