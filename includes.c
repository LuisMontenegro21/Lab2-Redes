
#include "includes.h"
#include <stdbool.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <stdio.h>




char* request_message(){
    char *message = NULL;
    size_t initial_size = 100; // message size up to 100

    message = (char *)malloc(initial_size * sizeof(char)); // allocate memory
    if (message == NULL){
        perror("Message is NULL");
        return NULL;
    }
    if (scanf("%99s", message) != 1) {
        fprintf(stderr, "Error when reading input");    
        return NULL;
    }
    size_t real_length = strlen(message); // get real size
    char *temp_string = (char *)realloc(message, (real_length + 1) * sizeof(char));
    if (temp_string == NULL){
        perror("Failed to realocate memory");
        free(message); 
        return NULL;
    }

    message = temp_string;

    // char buf[256];
    // if (!fgets(buf, sizeof buf, stdin)) return NULL;

    // // strip trailing newline if present
    // size_t n = strcspn(buf, "\r\n");
    // buf[n] = '\0';

    // char *message = malloc(n + 1);
    // if (!message) return NULL;
    // memcpy(message, buf, n + 1);
    return string_to_binary(message);
}

char* string_to_binary(const char* message){
    size_t length = strlen(message);
    char* bin_message = (char*)malloc((length*8)+1);
    if (!bin_message)return NULL;

    char* p = bin_message;
    for (int i = 0; message[i] != '\0'; ++i){
        unsigned char ch = (unsigned char)message[i];
        for (int j = 7; j>=0; --j){
            *p++ = ((ch>>j)&1) ? '1' : '0';
        }
    }
    *p = '\0';
    return bin_message;
}


void add_noise(char* message){
    srand(time(NULL));
    int msg_len = strlen(message);
    int random_index = (rand() % msg_len);
    if ((rand() % 10) == 0)
        message[random_index] = message[random_index] == '0' ? '1' : '0';
}  
    