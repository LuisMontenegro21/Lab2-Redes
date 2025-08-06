#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
//#include <math.h>


// check powers
enum Powers {
    p1 = 1,
    p2 = 2,
    p3 = 4,
    p4 = 8,
    p5 = 16,
    p6 = 32,
    p7 = 64,
    p8 = 128,
    p9 = 256,
    p10 = 512,
    p11 = 1024,
    p12 = 2048
};

/*
Auxiliary functions
*/
void reverse(char *bin, int left, int right) {
    while (left < right) {
        char temp = bin[left];
        bin[left] = bin[right];
        bin[right] = temp;
        left++;
        right--;
    }
}

char* to_binary(int n) {
    int index = 0;
	char* bin = (char*) malloc(32 * sizeof(char));

    while (n > 0) {
        int bit = n % 2;
        bin[index++] = '0' + bit;
        n /= 2;
    }
    bin[index] = '\0';

	reverse(bin, 0, index-1);
  	return bin;
}

bool hamming_code(const char *message, int size){

    for (int index = 0; index!=size; index++){
        char* bin = to_binary(index); // returns a list of binary
        int index_value = message[index] - '0'; // turns ascii value into 1 and 0 
        printf("Index value: %d | Binary index: %s\n", index_value, bin);
    }
    return true;
}


/*
 Checks that all symbols are 0 and 1
*/
bool check_symbols(const char *message, int size){
    for (int i = 0; i!=size; i++){
        int val = message[i] - '0';
        if (val != 0 || val != 1){
            printf("Message error: %d\n", val);
            return false;
        }
    }
    return true;
}



int main(int argc, char *argv[]){
    printf("###Hamming code encryption###\n");

    char *message = NULL;
    size_t initial_size = 100;
    int minimal_size = 4;

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
    // check data integrity
    // if(check_symbols(message, size) == false){
    //     printf("Unknown symbol found on message: only 0 and 1 accepted");
    //     return 1;
    // }
    // perform hamming code
    if(hamming_code(message, size)){
        printf("Message has no errors");
    } 

    free(message);
    return 0;
}