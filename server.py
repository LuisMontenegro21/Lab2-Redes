import socket, os, csv, time
from receiver_hamming import verify_hamming   # usa tu Parte 1

LOG_PATH = "results.csv"

def ensure_log():
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["ts","len_bits","outcome","ascii_text"])

def write_log(len_bits, outcome, ascii_text):
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([int(time.time()), len_bits, outcome, ascii_text])

def bin_to_ascii(bits):
    if len(bits) % 8 != 0: return ""
    try:
        return ''.join(chr(int(bits[i:i+8],2)) for i in range(0,len(bits),8))
    except: return ""

def handle_line_ham(bits: str):
    # Rechaza lo que no sea binario
    if not bits or any(c not in "01" for c in bits):
        return {"resp":"[HAM] Trama inválida", "len_bits":len(bits), "outcome":"bad_bits", "ascii":""}

    status, data_bits = verify_hamming(bits)  # tu lógica de Parte 1
    if status == "ok":
        text = bin_to_ascii(data_bits)
        return {"resp":f"[HAM] OK\nDatos: {data_bits}\nASCII: {text or '(no ASCII)'}",
                "len_bits":len(bits), "outcome":"ok", "ascii":text}
    if status == "corrigio":
        text = bin_to_ascii(data_bits)
        return {"resp":f"[HAM] Corrigió 1 bit\nDatos: {data_bits}\nASCII: {text or '(no ASCII)'}",
                "len_bits":len(bits), "outcome":"corrected", "ascii":text}
    return {"resp":"[HAM] Error no corregible", "len_bits":len(bits), "outcome":"uncorrectable", "ascii":""}

def main():
    HOST, PORT = "127.0.0.1", 5050
    ensure_log()
    print(f"Servidor Hamming en {HOST}:{PORT}")
    print(f"Log CSV: {os.path.abspath(LOG_PATH)}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(64)

        while True:
            conn, addr = s.accept()
            # lee por LÍNEAS, robusto para \n y \r\n; procesa muchas líneas por socket
            with conn, conn.makefile('r', encoding='utf-8', newline='\n') as f:
                print("Conectado:", addr)
                for raw in f:
                    had_nl = raw.endswith('\n')
                    line = raw.rstrip('\r\n')
                    if line == "":
                        # Ignora cada salto de línea “puro”
                        # (debug: muestra si llegó con NL)
                        print("· Línea vacía ignorada (had_nl=", had_nl, ")")
                        continue

                    # Procesar SOLO Hamming
                    out = handle_line_ham(line)
                    print(out["resp"])
                    write_log(out["len_bits"], out["outcome"], out["ascii"])

                    # respuesta opcional al cliente (eco)
                    try:
                        conn.sendall((out["resp"] + "\n").encode())
                    except Exception:
                        break

if __name__ == "__main__":
    main()
