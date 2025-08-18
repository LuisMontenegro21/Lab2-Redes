#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>
#include "includes.h"

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
    
    return code_parity;  
}

/*
    Check if parity is correct for message
*/
int check_parity(int m) {
    int r = 0;
    while (pow(2, r) < m + r + 1) {
        r++;
    }

    return r;
}




int main(int argc, char *argv[]){
    printf("###Hamming code encryption###\n");
    char *message = NULL;
    size_t initial_size = 100; // message size up to 100
    const int minimal_size = 4;

    message = (char *)malloc(initial_size * sizeof(char)); // allocate memory
    if (message == NULL){
        perror("Message is NULL");
        return 1;
    }
    if (scanf("%99s", message) != 1) {
        fprintf(stderr, "Error when reading input");
        return 1;
    }

    size_t real_length = strlen(message); // get real size
    // check minimal size allowed 
    if ((int)real_length < minimal_size){
        printf("Error: Minimal length for a code is 4: %d found\n", (int)real_length);
        return 1;
    }
    // reallocate memory to fit the size
    char *temp_string = (char *)realloc(message, (real_length + 1) * sizeof(char));
    if (temp_string == NULL){
        perror("Failed to realocate memory");
        free(message); 
        return 1;
    }

    message = temp_string;
    int size = (int)real_length;
    if (!check_symbols(message, size)){
        return 1;
    }

    int r = check_parity(size); // check optimal parity size
    char* hamming_message = hamming_code(message, size, r);
    printf("Hamming encoding: %s\t", hamming_message);

    free(message); // free message memory
    free(hamming_message); // free hamming_code memory

    return 0;
}