#include <stdint.h>
#pragma pack(1)

typedef uint64_t timestamp;
typedef uint8_t uuid[16];

/* previous C->S packet had error */
#define SESHCORD_SV_ERR -1
struct seshcord_sv_err
{
  uint16_t id; /* sequence ID of faulted packet */
};
#define SESHCORD_SV_ERR_SCHEMA "S"

/* message was deleted */
#define SESHCORD_SV_MSG_DEL 1
struct seshcord_sv_msg_del
{
  uuid id; /* Message ID */
  uuid by; /* Deletor (may be original user, or mod) */
};
#define SESHCORD_SV_MSG_DEL_SCHEMA "UU"

/* message sent or editted */
#define SESHCORD_SV_MSG 0
struct seshcord_sv_msg
{
  uuid id; /* message ID of this message (if it's an existing message, the client treats it as an edit) */
  uuid chat; /* uuid of chat, or user in case of dm */
  uuid sender; /* user ID who sent the message */
  char * content; /* message content */
  uint8_t attachCount; /* Number of attachments */
  struct
  {
    char * filename; /* Filename */
    uint32_t size; /* File size */
    char * path; /* CDN file path; client constructs web link based on secure */
  } *attachments;
};
#define SESHCORD_SV_MSG_SCHEMA "UUU*C[*I*]"

/* client got a friend request */
#define SESHCORD_SV_FRIEND_REQ 2
struct seshcord_sv_friend_req
{
  uuid id; /* Requestor */
};
#define SESHCORD_SV_FRIEND_REQ_SCHEMA "U"

/* client wants to log in to an existing account */
#define SESHCORD_CL_AUTH_LOGIN 2
struct seshcord_cl_auth_login
{
  char * username; /* username or email */
  char * password; /* Password (hashed) */
  char * antiSpam; /* as above */
};
#define SESHCORD_CL_AUTH_LOGIN_SCHEMA "***"

/* client wants to get list of DMs */
#define SESHCORD_CL_GET_DMS 5
struct seshcord_cl_get_dms
{
  timestamp since; /* How far back to retrieve DMs */
};
#define SESHCORD_CL_GET_DMS_SCHEMA "L"

/* Message sent from client */
#define SESHCORD_CL_SEND_MSG 3
struct seshcord_cl_send_msg
{
  uuid chat; /* Chat or user to send message to */
  char * content; /* Message text */
  uint8_t attachCount; /* Number of attachments */
  struct
  {
    char * filename; /* Filename */
    uint32_t size; /* File size */
    char * data; /* The attachment itself. */
  } *attachments;
};
#define SESHCORD_CL_SEND_MSG_SCHEMA "U*C[*I+]"

/* client wants to initialize a connection to the server */
#define SESHCORD_CL_HANDSHAKE_INIT 0
struct seshcord_cl_handshake_init
{
  char * clientName; /* Client name */
  char * clientVer; /* Client version */
  struct
  {
    char * cpuArch; /* CPU architecture */
    char * os; /* Operating system name and approximate version (e.g. Windows 10) */
    char * deviceModel; /* Device model name */
  } hostInfo;
};
#define SESHCORD_CL_HANDSHAKE_INIT_SCHEMA "*****"

/* client wants to get list of friends */
#define SESHCORD_CL_GET_FRIENDS 6
/* No payload */

/* client wants to get list of joined servers */
#define SESHCORD_CL_GET_SERVERS 4
/* No payload */

/* previous S->C packet had error */
#define SESHCORD_CL_ERROR -1
struct seshcord_cl_error
{
  uint16_t sid; /* sequence ID of faulted packet */
};
#define SESHCORD_CL_ERROR_SCHEMA "S"

/* client wants to create a new account */
#define SESHCORD_CL_AUTH_REGISTER 1
struct seshcord_cl_auth_register
{
  char * username; /* Username */
  char * email; /* EMail */
  char * password; /* Password (hashed) */
  char * antiSpam; /* anti-spam check value if applicable (captcha?) */
};
#define SESHCORD_CL_AUTH_REGISTER_SCHEMA "****"

