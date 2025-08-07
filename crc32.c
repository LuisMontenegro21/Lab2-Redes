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


int main(){

    return 0;
}