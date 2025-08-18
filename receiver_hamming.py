def is_power_of_two(x): return x and (x & (x-1)) == 0

def hamming_syndrome(code):
    n = len(code)
    # calcular r (número de bits de paridad) por 2^r >= n+1
    r = 0
    while (1 << r) < (n + 1):
        r += 1
    syndrome = 0
    for i in range(r):
        p = 1 << i
        s = 0
        for k in range(1, n+1):
            if k & p:
                s ^= int(code[k-1])
        if s: syndrome |= p
    return syndrome  # 0 => sin error; !=0 => posición a corregir (1-indexed)

def strip_parity(code):
    data_bits = []
    for i, bit in enumerate(code, start=1):
        if not is_power_of_two(i):
            data_bits.append(bit)
    return ''.join(data_bits)

if __name__ == "__main__":
    rx = input("Ingrese palabra de Hamming (bits 0/1): ").strip()
    if not rx or any(c not in "01" for c in rx):
        print("Entrada inválida."); raise SystemExit(1)

    code = list(rx)
    syn = hamming_syndrome(code)
    if syn == 0:
        print("OK: sin errores.")
        print("Mensaje:", strip_parity(code))
    else:
        pos = syn
        if 1 <= pos <= len(code):
            # corregir 1 bit
            code[pos-1] = '1' if code[pos-1] == '0' else '0'
            print(f"Se detectó y corrigió 1 error en la posición {pos}.")
            print("Mensaje corregido:", strip_parity(code))
        else:
            print("Syndrome inválido; descartar (pos fuera de rango).")
