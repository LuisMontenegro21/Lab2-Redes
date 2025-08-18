#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

static void xor_at(char *buf, size_t pos, const char *poly, size_t size_poly) {
    for (size_t j = 0; j < size_poly; ++j) 
        // performs bitwise XOR , yields 0 or 1 and then transform back to ascii by adding '0'
        buf[pos + j] = ((buf[pos+j] - '0') ^ (poly[j] - '0')) + '0';
}

char* crc32(const char *message, size_t message_len,const char *poly){
    const size_t size_poly = strlen(poly);
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
        if (dividend[i] == '1') xor_at(dividend, i, poly, size_poly);
    
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


int main(){
    printf("###CRC-32 encryption###\n");
    printf("Enter binary : read from left to right\n");
    printf("2^n 2^5 2^4 2^3 2^2 2^1 2^0\n");

    const char *characteristic_poly = "100000100110000010001110110110111";


    char *message = NULL;
    const int minimal_message_size = 4;
    size_t initial_size = 100; // message size up to 100


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
    if ((int)real_length < minimal_message_size){
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
    //  final message
    char *final_message = crc32(message, real_length, characteristic_poly);
    printf("Encoded: %s\n", final_message);
    
    free(message);
    free(final_message);

    return 0;
}