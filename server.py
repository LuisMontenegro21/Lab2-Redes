import socket, os, csv, time
from receiver_crc32 import verify_crc          # Parte 1
from receiver_hamming import verify_hamming    # Parte 1

LOG_PATH = "results.csv"

def abs_log_path():
    return os.path.abspath(LOG_PATH)

def ensure_log():
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ts","alg","len_bits","outcome","ascii_text","meta_p","meta_r"])

def write_log(alg, len_bits, outcome, ascii_text="", meta_p="", meta_r=""):
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([int(time.time()), alg, len_bits, outcome, ascii_text, meta_p, meta_r])

def bin_to_ascii(bits):
    if len(bits) % 8 != 0: return ""
    try:
        return ''.join(chr(int(bits[i:i+8],2)) for i in range(0,len(bits),8))
    except: return ""

def parse_meta(alg_token):
    # Permite "CRC|p=0.01|r=5" o "HAM|p=0.02"
    parts = alg_token.split("|")
    alg = parts[0].upper().strip()
    p = r = ""
    for kv in parts[1:]:
        if "=" in kv:
            k,v = kv.split("=",1)
            k = k.strip().lower(); v = v.strip()
            if k == "p": p = v
            elif k == "r": r = v
    return alg, p, r

def handle_labeled(alg_token, bits):
    alg, meta_p, meta_r = parse_meta(alg_token)
    if not bits or any(c not in "01" for c in bits):
        return {"resp":"Trama inválida (solo 0/1).",
                "alg":alg, "len_bits":len(bits), "outcome":"bad_bits", "ascii":"", "p":meta_p, "r":meta_r}

    if alg == "CRC":
        ok, msg_bits = verify_crc(bits)
        if ok:
            text = bin_to_ascii(msg_bits)
            return {"resp":f"[CRC] OK\nBits: {msg_bits}\nASCII: {text or '(no ASCII válido)'}",
                    "alg":"CRC", "len_bits":len(bits), "outcome":"ok", "ascii":text, "p":meta_p, "r":meta_r}
        else:
            return {"resp":"[CRC] ERROR: trama descartada",
                    "alg":"CRC", "len_bits":len(bits), "outcome":"discard", "ascii":"", "p":meta_p, "r":meta_r}

    if alg == "HAM":
        status, data_bits = verify_hamming(bits)
        if status == "ok":
            text = bin_to_ascii(data_bits)
            return {"resp":f"[HAM] OK\nBits: {data_bits}\nASCII: {text or '(no ASCII válido)'}",
                    "alg":"HAM", "len_bits":len(bits), "outcome":"ok", "ascii":text, "p":meta_p, "r":meta_r}
        if status == "corrigio":
            text = bin_to_ascii(data_bits)
            return {"resp":f"[HAM] Corrigió 1 bit\nBits: {data_bits}\nASCII: {text or '(no ASCII válido)'}",
                    "alg":"HAM", "len_bits":len(bits), "outcome":"corrected", "ascii":text, "p":meta_p, "r":meta_r}
        return {"resp":"[HAM] Error no corregible",
                "alg":"HAM", "len_bits":len(bits), "outcome":"uncorrectable", "ascii":"", "p":meta_p, "r":meta_r}

    return {"resp":"Algoritmo desconocido",
            "alg":alg, "len_bits":len(bits), "outcome":"unknown_alg", "ascii":"", "p":meta_p, "r":meta_r}

def handle_line(line):
    line = line.strip()
    if not line:
        return {"resp":"Línea vacía","alg":"", "len_bits":0, "outcome":"empty", "ascii":"", "p":"", "r":""}

    # Caso A: viene con etiqueta (CRC:/HAM:)
    if ':' in line:
        alg_token, payload = line.split(':', 1)
        bits = payload.strip()
        return handle_labeled(alg_token, bits)

    # Caso B: viene SOLO bits -> intentar detectar:
    if all(c in "01" for c in line):
        bits = line

        # 1) Intentar CRC primero
        ok, msg_bits = verify_crc(bits)
        if ok:
            text = bin_to_ascii(msg_bits)
            return {"resp":f"[CRC*] OK (auto)\nBits: {msg_bits}\nASCII: {text or '(no ASCII válido)'}",
                    "alg":"CRC", "len_bits":len(bits), "outcome":"ok", "ascii":text, "p":"", "r":""}

        # 2) Intentar Hamming
        status, data_bits = verify_hamming(bits)
        if status == "ok":
            text = bin_to_ascii(data_bits)
            return {"resp":f"[HAM*] OK (auto)\nBits: {data_bits}\nASCII: {text or '(no ASCII válido)'}",
                    "alg":"HAM", "len_bits":len(bits), "outcome":"ok", "ascii":text, "p":"", "r":""}
        if status == "corrigio":
            text = bin_to_ascii(data_bits)
            return {"resp":f"[HAM*] Corrigió 1 bit (auto)\nBits: {data_bits}\nASCII: {text or '(no ASCII válido)'}",
                    "alg":"HAM", "len_bits":len(bits), "outcome":"corrected", "ascii":text, "p":"", "r":""}

        # Si nada aplicó:
        return {"resp":"No se reconoció formato (ni CRC ni Hamming válidos)",
                "alg":"", "len_bits":len(bits), "outcome":"unrecognized_bits", "ascii":"", "p":"", "r":""}

    # Caso C: cualquier otra cosa
    return {"resp":"Formato inválido","alg":"", "len_bits":0, "outcome":"bad_format", "ascii":"", "p":"", "r":""}

def main():
    HOST, PORT = "127.0.0.1", 5050
    ensure_log()
    print(f"Servidor en {HOST}:{PORT}")
    print(f"Log CSV: {abs_log_path()}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT)); s.listen(1)
        while True:
            conn, addr = s.accept()
            with conn, conn.makefile('r', encoding='utf-8', newline='\n') as f:
                print("Conectado:", addr)
                for line in f:  # lee hasta '\n' (robusto para \r\n también)
                    print(f"\nRAW: {repr(line)}")
                    line = line.rstrip('\r\n')
                    out = handle_line(line)
                    print(out["resp"])
                    write_log(out["alg"], out["len_bits"], out["outcome"], out["ascii"], out["p"], out["r"])
                    try:
                        conn.sendall((out["resp"] + "\n").encode())
                    except Exception:
                        break

if __name__ == "__main__":
    main()
