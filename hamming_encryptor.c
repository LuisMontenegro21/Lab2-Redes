#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

static bool power_of_two(int n){
    if(n <= 0) return false;
    return (n & (n - 1)) == 0;
}

/* Calcula r tal que 2^r >= m + r + 1 */
static int calc_parity_bits(int m) {
    int r = 0;
    // usar shifts para evitar pow()
    while ((1 << r) < (m + r + 1)) {
        r++;
    }
    return r;
}

/* Verifica que todos los símbolos sean 0/1 */
static bool check_symbols(const char *message, int size){
    for (int i = 0; i < size; i++){
        if (message[i] != '0' && message[i] != '1'){
            fprintf(stderr, "Error: caracter invalido '%c' en posicion %d\n", message[i], i);
            return false;
        }
    }
    return true;
}

/* Genera la palabra Hamming con paridad par. Devuelve string heap-alloc (debes free()). */
static char* hamming_code(const char *message, int size, int r){
    int total = size + r;

    char *code_parity = (char *)malloc((size_t)total + 1);
    if (code_parity == NULL){
        fprintf(stderr, "Error: no se pudo asignar memoria\n");
        return NULL;
    }

    int j = 0;
    // Colocar datos en posiciones que NO son potencia de 2; paridades quedan en '0'
    for (int i = 1; i <= total; i++){
        if (power_of_two(i)) {
            code_parity[i - 1] = '0';
        } else {
            code_parity[i - 1] = message[j++];
        }
    }

    // Calcular bits de paridad (paridad par)
    for (int i = 0; i < r; i++){
        int parity_pos = 1 << i; // 1,2,4,8,...
        int parity = 0;

        for (int k = 1; k <= total; k++){
            if ((k & parity_pos) != 0){ // incluye su propia posicion
                parity ^= (code_parity[k - 1] - '0');
            }
        }
        // Ajustar bit de paridad para que la paridad sea PAR
        if (parity % 2 != 0){
            // Toggle en la posicion de paridad
            code_parity[parity_pos - 1] = (code_parity[parity_pos - 1] == '0') ? '1' : '0';
        }
    }

    code_parity[total] = '\0';
    return code_parity;
}

int main(void){
    printf("### Hamming code (emisor) ###\n");
    printf("Ingrese el mensaje en binario (solo 0/1):\n");

    char buffer[1024];
    if (!fgets(buffer, sizeof(buffer), stdin)) {
        fprintf(stderr, "Error al leer entrada\n");
        return 1;
    }

    // recortar \r\n
    size_t len = strcspn(buffer, "\r\n");
    buffer[len] = '\0';

    const int minimal_size = 4;
    if ((int)len < minimal_size){
        fprintf(stderr, "Error: longitud minima es %d, se recibio %zu\n", minimal_size, len);
        return 1;
    }

    if (!check_symbols(buffer, (int)len)){
        return 1;
    }

    int r = calc_parity_bits((int)len);
    char *hamming_msg = hamming_code(buffer, (int)len, r);
    if (!hamming_msg) {
        return 1;
    }

    printf("Palabra de Hamming: %s\n", hamming_msg);

    free(hamming_msg);
    return 0;
}
