def xor_at(buf, pos, poly):
    b = list(buf)
    for j in range(len(poly)):
        b[pos + j] = str(int(b[pos + j]) ^ int(poly[j]))
    return ''.join(b)

def crc_check(received, poly):
    n = len(received)
    m = len(poly)
    # Dividir toda la cadena recibida (mensaje+CRC)
    dividend = list(received)
    for i in range(n - m + 1):
        if dividend[i] == '1':
            for j in range(m):
                dividend[i + j] = str(int(dividend[i + j]) ^ int(poly[j]))
    remainder = ''.join(dividend[-(m-1):])
    return remainder  # '0'*(m-1) si no hay error

def verify_crc(bits: str) -> tuple[bool, str]:
    """Verifica la trama con CRC.
       Retorna (ok, mensaje_original)"""
    POLY = "100000100110000010001110110110111"
    n, m = len(bits), len(POLY)
    dividend = list(bits)
    for i in range(n - m + 1):
        if dividend[i] == '1':
            for j in range(m):
                dividend[i + j] = str(int(dividend[i + j]) ^ int(POLY[j]))
    remainder = ''.join(dividend[-(m-1):])
    if set(remainder) == {'0'}:
        msg = bits[:-(m-1)]
        return True, msg
    else:
        return False, ""

if __name__ == "__main__":
    POLY = "100000100110000010001110110110111"  # CRC-32 IEEE (binario)
    rx = input("Ingrese trama+CRC en binario: ").strip()
    if not rx or any(c not in "01" for c in rx):
        print("Entrada inválida.")
        raise SystemExit(1)
    r = crc_check(rx, POLY)
    if set(r) == {'0'}:
        # quitar el CRC (m-1 bits al final) para mostrar mensaje original
        msg = rx[:-(len(POLY)-1)]
        print("OK: sin errores. Mensaje original:", msg)
    else:
        print("ERROR: CRC no coincide. Mensaje descartado.")
