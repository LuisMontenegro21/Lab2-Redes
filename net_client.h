#ifndef NET_CLIENT_H
#define NET_CLIENT_H

#ifdef __cplusplus
extern "C" {
#endif


#include <winsock2.h>
#include <ws2tcpip.h>
#include <stdio.h>
#include <string.h>

#pragma comment(lib, "Ws2_32.lib")  

typedef struct {
    SOCKET sock;
    char   host[64];
    unsigned short port;
    int    is_connected;
} net_client_t;


int  net_client_init(void);
void net_client_cleanup(void);


void net_client_make(net_client_t* c, const char* host, unsigned short port);
int  net_client_connect(net_client_t* c);
void net_client_close(net_client_t* c);


int  send_all(SOCKET s, const char* buf, size_t len);
int  net_client_send(net_client_t* c, const char* msg);
int  net_client_send_line(net_client_t* c, const char* msg);

#ifdef __cplusplus
} 
#endif

#endif 
