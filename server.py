# server.py
import socket
from receiver_crc32 import verify_crc
from receiver_hamming import verify_hamming

def bin_to_ascii(bits):
    if len(bits) % 8 != 0: return None
    try:
        return ''.join(chr(int(bits[i:i+8],2)) for i in range(0,len(bits),8))
    except: return None

def handle_line(line):
    if ':' not in line: return "Formato inválido"
    alg, payload = line.split(':',1)
    bits = payload.strip()
    if any(c not in "01" for c in bits): return "Trama inválida"

    if alg.upper()=="CRC":
        ok, msg_bits = verify_crc(bits)
        if ok:
            text = bin_to_ascii(msg_bits) or "(no ASCII válido)"
            return f"[CRC] OK\nBits: {msg_bits}\nASCII: {text}"
        else:
            return "[CRC] ERROR: trama descartada"
    elif alg.upper()=="HAM":
        status, data_bits = verify_hamming(bits)
        if status=="ok":
            text = bin_to_ascii(data_bits) or "(no ASCII válido)"
            return f"[HAM] OK\nBits: {data_bits}\nASCII: {text}"
        elif status=="corrigio":
            text = bin_to_ascii(data_bits) or "(no ASCII válido)"
            return f"[HAM] Corrigió 1 bit\nBits: {data_bits}\nASCII: {text}"
        else:
            return "[HAM] Error no corregible"
    else:
        return "Algoritmo desconocido"

def main():
    HOST, PORT = "127.0.0.1", 5050
    print(f"Servidor en {HOST}:{PORT}")
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        s.bind((HOST,PORT)); s.listen(1)
        while True:
            conn,addr = s.accept()
            with conn:
                data=b""
                while True:
                    chunk=conn.recv(4096)
                    if not chunk: break
                    data+=chunk
                    if b"\n" in data: break
                line=data.decode().strip()
                print(f"\n--- Recibido: {line[:100]}")
                resp=handle_line(line)
                print(resp)
                conn.sendall((resp+"\n").encode())

if __name__=="__main__":
    main()
