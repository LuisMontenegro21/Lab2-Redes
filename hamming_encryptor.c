#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>
#include "includes.h"
#include "net_client.h"

bool power_of_two(int n){
    if(n<=0)
        return false;
    return (n & (n-1)) == 0;
}


char* hamming_code(const char *message, int size, int r){
    int total = size + r;
    //char code_parity[total];
    char* code_parity = (char *)malloc((size+r)*sizeof(char));
    if (code_parity == NULL){
        fprintf(stderr, "Error allocating memory");
        return NULL;
    }
    int j = 0;

    // fill positions 
    for (int i=1;i<=total; i++){
        if (power_of_two(i)){
            code_parity[i-1] = '0';
        } else {
            code_parity[i-1] = message[j++];
        }
    }

    for (int i = 0; i < r; i++){
        int parity_pos = 1 << i; // move to the least significant bit to the most to check for parity
        int parity = 0;

        for (int k = 1; k<=total; k++){
            if ((k & parity_pos) && k != parity_pos){ // check k AND parity_pos : 1 AND 1 = 1 i.e. true and skip parity positions : 1,2,4,8...
                parity += (code_parity[k-1] - '0'); // add values of the non-parity values that add up to the result
                // parity ^= (code_parity[k-1] - '0'); // perform XOR on the left positions
            }
        }
        parity %= 2;
        code_parity[parity_pos - 1] = parity + '0';
    }
    code_parity[total] = '\0';
    return code_parity;  
}

/*
    Check if parity is correct for message
*/
int check_parity(int m) {
    int r = 0;
    while (pow(2, r) < m + r + 1) 
        r++;
    
    return r;
}




int main(void){
    printf("###Hamming code encryption###\n");
   
    char* message = request_message();
    if (message == NULL){
        perror("Message is NULL");
        return 1;
    }
    int real_length = strlen(message); // get real size

    int r = check_parity(real_length); // check optimal parity size
    char* hamming_message = hamming_code(message, real_length, r);
    printf("Hamming encoding: %s\t", hamming_message);
    add_noise(hamming_message);
    printf("Hamming with errors: %s\t");

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

    // close
    net_client_send_line(&cli, hamming_message);
    net_client_close(&cli);
    net_client_cleanup();


    free(message); // free message memory
    free(hamming_message); // free hamming_code memory

    return 0;
}