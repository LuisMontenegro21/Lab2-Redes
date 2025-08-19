def is_power_of_two(x): return x and (x & (x-1)) == 0

def hamming_syndrome(code):
    n, r = len(code), 0
    while (1 << r) < (n + 1): r += 1
    syndrome = 0
    for i in range(r):
        p = 1 << i; s = 0
        for k in range(1, n+1):
            if k & p: s ^= int(code[k-1])
        if s: syndrome |= p
    return syndrome

def strip_parity(code):
    return ''.join(bit for i, bit in enumerate(code,1) if not is_power_of_two(i))

def verify_hamming(bits: str) -> tuple[str, str]:
    """Verifica la trama Hamming.
       Retorna ('ok'|'corrigio'|'error', data_bits)"""
    code = list(bits)
    syn = hamming_syndrome(code)
    if syn == 0:
        return "ok", strip_parity(code)
    elif 1 <= syn <= len(code):
        # corregir 1 bit
        code[syn-1] = '1' if code[syn-1]=='0' else '0'
        return "corrigio", strip_parity(code)
    else:
        return "error", ""
