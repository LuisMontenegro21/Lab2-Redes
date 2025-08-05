#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

/*
 Runs the hamming code to check for errors in a message
*/
bool hamming_code(const char *message, int size){
    for (int i = 0; i!=size; i++){
        // printf("i: %d\n", i);
        int val = message[i] - '0'; // turns ascii value into 1 and 0
        printf("Index: %d Value: %d\n", i+1, val);
    }
    return true;
}

/*
 Checks that all symbols are 0 and 1
*/
bool check_symbols(const char *message, int size){
    for (int i = 0; i!=size; i++){
        if (message[i] - '0' != 0 || message[i] - '0' != 1) return false;
    }
    return true;
}



int main(int argc, char *argv[]){
    printf("###Hamming code encryption###\n");

    char *message = NULL;
    size_t initial_size = 100;

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
    char *temp_string = (char *)realloc(message, (real_length + 1) * sizeof(char));
    if (temp_string == NULL){
        perror("Failed to realocate memory");
        free(message); 
        return 1;
    }
    message = temp_string;
    int size = (int)real_length;
    if(!check_symbols(message, size)){
        printf("Unknown symbol found on message: only 0 and 1 accepted");
        return 1;
    }
    if(hamming_code(message, size)){
        printf("Message has no errors");
    } // perform hamming code

    free(message);
    return 0;
}