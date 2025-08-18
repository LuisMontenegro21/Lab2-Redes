#include "includes.h"
#include <stdbool.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <stdio.h>


char* request_message(){
    return NULL;
}

void add_noise(char* message){
    srand(time(NULL));
    int msg_len = strlen(message);
    int random_index = (rand() % msg_len);
    char x = message[random_index];
    message[random_index] = ((x-'0')^1) + '0';
}  

/*
 Checks that all symbols are 0 and 1
*/
bool check_symbols(const char *message, int size){
    for (int i = 0; i!=size; i++){
        int val = message[i] - '0';
        if (val != 0 && val != 1){
            printf("Error on message: unknown character '%c' at position %d\n", message[i], i);
            return false;
        }
    }
    return true;
}