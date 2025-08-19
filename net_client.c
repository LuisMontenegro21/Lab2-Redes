#ifndef _WIN32_WINNT
#define _WIN32_WINNT 0x0600   
#endif
#define WIN32_LEAN_AND_MEAN
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

int net_client_init(void) {
    WSADATA wsa;
    int rc = WSAStartup(MAKEWORD(2,2), &wsa);
    if (rc != 0) {
        fprintf(stderr, "WSAStartup failed: %d\n", rc);
        return rc;
    }
    return 0;
}

void net_client_cleanup(void) {
    WSACleanup();
}


void net_client_make(net_client_t* c, const char* host, unsigned short port) {
    c->sock = INVALID_SOCKET;
    c->is_connected = 0;
    strncpy(c->host, host ? host : "127.0.0.1", sizeof(c->host)-1);
    c->host[sizeof(c->host)-1] = '\0';
    c->port = port;
}

int net_client_connect(net_client_t* c) {
    if (c->is_connected) return 0;

    SOCKET s = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (s == INVALID_SOCKET) {
        fprintf(stderr, "socket() failed: %d\n", WSAGetLastError());
        return WSAGetLastError();
    }

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof addr);
    addr.sin_family = AF_INET;
    addr.sin_port   = htons(c->port);

    // --- Use inet_addr for IPv4 ---
    addr.sin_addr.s_addr = inet_addr(c->host);
    if (addr.sin_addr.s_addr == INADDR_NONE) {
        fprintf(stderr, "Invalid IPv4 address: %s\n", c->host);
        closesocket(s);
        return WSAEINVAL;
    }

    if (connect(s, (struct sockaddr*)&addr, sizeof addr) == SOCKET_ERROR) {
        int err = WSAGetLastError();
        fprintf(stderr, "connect() failed: %d\n", err);
        closesocket(s);
        return err;
    }

    c->sock = s;
    c->is_connected = 1;
    return 0;
}

void net_client_close(net_client_t* c) {
    if (c->is_connected && c->sock != INVALID_SOCKET) {
        closesocket(c->sock);
    }
    c->sock = INVALID_SOCKET;
    c->is_connected = 0;
}

int send_all(SOCKET s, const char* buf, size_t len) {
    const char* p = buf;
    while (len > 0) {
        int n = send(s, p, (int)len, 0);
        if (n == SOCKET_ERROR) return WSAGetLastError();
        p   += n;
        len -= n;
    }
    return 0;
}


int net_client_send(net_client_t* c, const char* msg) {
    if (!c->is_connected) {
        int rc = net_client_connect(c);
        if (rc) return rc;
    }
    size_t len = strlen(msg);
    int rc = send_all(c->sock, msg, len);
    if (rc) {
        // try one reconnect
        net_client_close(c);
        if ((rc = net_client_connect(c)) != 0) return rc;
        rc = send_all(c->sock, msg, len);
    }
    return rc;
}


int net_client_send_line(net_client_t* c, const char* msg) {
    int rc = net_client_send(c, msg);
    if (rc) return rc;
    const char nl = '\n';
    return send_all(c->sock, &nl, 1);
}
