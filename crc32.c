#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include "includes.h"
#include "net_client.h"

inline static void xor_at(char *buf, size_t pos, const char *poly, size_t size_poly) {
    for (size_t j = 0; j < size_poly; ++j) 
        // performs bitwise XOR , yields 0 or 1 and then transform back to ascii by adding '0'
        buf[pos + j] = ((buf[pos+j] - '0') ^ (poly[j] - '0')) + '0';
}

char* crc32(const char *message, size_t message_len){
    const char *characteristic_poly = "100000100110000010001110110110111";
    const size_t size_poly = strlen(characteristic_poly);
    const size_t pad = size_poly - 1;
    const size_t size_dividend = message_len + pad;

    char* dividend = (char*)malloc(size_dividend + 1);
    if (!dividend) return NULL;

    // fill dividend
    for(size_t k = 0; k<message_len; ++k)
        dividend[k] = message[k];

    memset(dividend + message_len, '0', pad);
    dividend[size_dividend] = '\0'; // set end
    
    for (size_t i = 0; i + size_poly <= size_dividend; ++i) 
        if (dividend[i] == '1') xor_at(dividend, i, characteristic_poly, size_poly);
    
    char *rem = (char*)malloc(pad+1);
    if (!rem) {free(dividend);return NULL;}
    memcpy(rem, dividend+message_len, pad);
    rem[pad] = '\0';
    free(dividend);

    // concatenate original message plus remainder
    size_t rem_len = strlen(rem);
    char* output = (char*)malloc(message_len + rem_len + 1);
    if (!output) {free(rem); return NULL;}
    // copy into output the message
    memcpy(output, message, message_len); 
    // copy aftwerards the remainder 
    memcpy(output + message_len, rem, rem_len);
    output[message_len + rem_len] = '\0';
    free(rem);
    return output;
}


int main(void){
    printf("###CRC-32 encryption###\n");
    // char *message = request_message();
    // size_t real_length = strlen(message); // get real size
    // char *final_message = crc32(message, real_length);
    // printf("CRC32 encoded: %s\t", final_message);
    // add_noise(final_message);
    // printf("CRC32 with errors: %s\t", final_message);

    if (net_client_init() != 0) {
        fprintf(stderr, "Failed to init Winsock\n");
        return 1;
    }


    net_client_t cli;
    net_client_make(&cli, "127.0.0.1", 5050);


    if (net_client_connect(&cli) != 0) {
        fprintf(stderr, "Failed to connect\n");
        net_client_cleanup();
        return 1;
    }
    char buf[32];
    int N = 1000;
    for (int i = 1; i<=N; ++i){
        snprintf(buf, sizeof buf, "%d", i);
        char* binary = string_to_binary(buf);
        size_t real_length = strlen(binary);
        char *final_message = crc32(binary, real_length);
        add_noise(final_message);
        net_client_send_line(&cli, final_message);
        free(final_message);
    }


    net_client_close(&cli);
    net_client_cleanup();

    
    // free(message);
    // free(final_message);

    return 0;
}