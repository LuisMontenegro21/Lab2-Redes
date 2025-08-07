#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>




void reverse(char *bin, int left, int right) {
    while (left < right) {
        char temp = bin[left];
        bin[left] = bin[right];
        bin[right] = temp;
        left++;
        right--;
    }
}

void to_binary(int n, char* bin) {
    int index = 0;
    if (n == 0){
        bin[index++] = '0';
    }

    while (n > 0) {
        int bit = n % 2;
        bin[index++] = '0' + bit;
        n /= 2;
    }
    bin[index] = '\0';

	reverse(bin, 0, index-1);
}

bool power_of_two(int n){
    if(n<=0)
        return false;
    return (n & (n-1)) == 0;
}


void hamming_code(const char *message, int size, int r){
    int total = size + r;
    char code_parity[total];
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
            if ((k & parity_pos) && k != parity_pos){ // check k AND parity_pos : 1 AND 1 = 1 i.e. true
                parity ^= (code_parity[k-1] - '0'); // perform XOR
            }
        }
        code_parity[parity_pos - 1] = parity + '0';
    }
    printf("Output message:\n");
    for (int i = 0; i<total; i++){
        printf("%c", code_parity[i]);
    }

    
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
    int r = check_parity(size);

    hamming_code(message, size, r);


    free(message);
    return 0;
}