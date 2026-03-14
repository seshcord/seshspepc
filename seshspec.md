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

## Packet Types ##

The following packet types are recognized:

### Client-to-Server Packets ###
  
* 0 `SESHCORD_CL_HANDSHAKE_INIT`: client wants to initialize a connection to the server
  * `clientName` (str): Client name
  * `clientVer` (str): Client version
  * `hostInfo` (struct): Host system info (non-identifiable)
    * `cpuArch` (str): CPU architecture
    * `os` (str): Operating system name and approximate version (e.g. Windows 10)
    * `deviceModel` (str): Device model name

* 1 `SESHCORD_CL_AUTH_REGISTER`: client wants to create a new account
  * `username` (str): Username
  * `email` (str): EMail
  * `password` (str): Password (hashed)
  * `antiSpam` (str): anti-spam check value if applicable (captcha?)

* 2 `SESHCORD_CL_AUTH_LOGIN`: client wants to log in to an existing account
  * `username` (str): username or email
  * `password` (str): Password (hashed)
  * `antiSpam` (str): as above

* 3 `SESHCORD_CL_SEND_MSG`: Message sent from client
  * `chat` (uuid): Chat to send message to
  * `content` (str): Message text
  * `attachCount` (uint8): Number of attachments
  * `attachments` (list): Attachments
    * `filename` (str): Filename
    * `size` (uint32): File size
    * `data` (binary): The attachment itself.

* 4 `SESHCORD_CL_GET_SERVERS`: client wants to get list of joined servers

* 5 `SESHCORD_CL_GET_DMS`: client wants to get list of DMs
  * `since` (time): How far back to retrieve DMs

* 6 `SESHCORD_CL_GET_FRIENDS`: client wants to get list of friends

* -1 `SESHCORD_CL_ERROR`: previous S->C packet had error
  * `sid` (uint16): sequence ID of faulted packet

### Server-to-Client Packets ###

* 0 `SESHCORD_SV_MSG`: message sent or editted
  * `id` (uuid): message ID of this message (if it's an existing message, the
    client treats it as an edit)
  * `chat` (uuid): uuid of chat
  * `sender` (uuid): user ID who sent the message
  * `content` (str): message content
  * `attachCount` (uint8): Number of attachments
  * `attachments` (list): Attachments
    * `filename` (str): Filename
    * `size` (uint32): File size
    * `path` (str): CDN file path; client constructs web link based on secure
      connection status (if non-secure, http, else https), server domain name,
      etc

* 1 `SESHCORD_SV_MSG_DEL`: message was deleted
  * `id` (uuid): Message ID
  * `by` (uuid): Deletor (may be original user, or mod)

* 2 `SESHCORD_SV_FRIEND_REQ`: client got a friend request
  * `id` (uuid): Requestor

* -1 `SESHCORD_SV_ERR`: previous C->S packet had error
  * `id` (uint16): sequence ID of faulted packet

## Database schema ##

The following is the database setup:

* `users`: User accounts
    * uuid `id`: Unique ID
    * str `name`: Usernae
    * time `registered`: Time of account registration
    * str `password`: Password (hashed)

* `chats`: Text chats of any variety
    * uuid `id`: The ID of the chat
    * uuid `server`: The server the chat lives on, if any
    * str `name`: The name of the chat, if appropriate
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










