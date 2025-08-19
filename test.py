# Create a self-contained test runner script that can (A) compile the C clients and/or (B) send tests directly via Python sockets.
from pathlib import Path
from textwrap import dedent

test_py = dedent(r"""
#!/usr/bin/env python3
# test.py
#
# Runner para pruebas rápidas contra server_logged.py / server.py
# - Modo A: Compila clientes C (crc32.exe, hamming.exe) y los ejecuta varias veces
# - Modo B (default): Genera tramas en Python y las envía por sockets directamente
#
# Uso típico:
#   python test.py --host 127.0.0.1 --port 5050 --runs 50 --lens 4 8 --perr 0 0.01
#   python test.py --compile   (solo compila los .c con MinGW y sale)
#   python test.py --use-exe --runs 20 --lens 4     (intenta usar crc32.exe/hamming.exe, alimentando stdin)
#
import argparse
import os
import random
import socket
import subprocess
import time
from pathlib import Path

# ------------------ Presentación ------------------
def ascii_to_bits(s: str) -> str:
    return ''.join(f"{ord(ch):08b}" for ch in s)

def bits_to_ascii(bits: str) -> str:
    if len(bits) % 8 != 0:
        return None
    try:
        return ''.join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8))
    except Exception:
        return None

# ------------------ Ruido ------------------
def apply_noise(bits: str, p: float) -> str:
    if p <= 0:
        return bits
    out = []
    for b in bits:
        if random.random() < p:
            out.append('1' if b == '0' else '0')
        else:
            out.append(b)
    return ''.join(out)

# ------------------ CRC-32 (IEEE, polinomio normal) ------------------
POLY = "100000100110000010001110110110111"  # 0x04C11DB7 (33 bits)

def crc32_frame(msg_bits: str) -> str:
    """Devuelve msg_bits + remainder(32) (división binaria)"""
    m = len(POLY)
    pad = m - 1
    dividend = list(msg_bits + '0'*pad)
    n = len(dividend)
    for i in range(n - m + 1):
        if dividend[i] == '1':
            for j in range(m):
                dividend[i+j] = str(int(dividend[i+j]) ^ int(POLY[j]))
    remainder = ''.join(dividend[-pad:])
    return msg_bits + remainder

# ------------------ Hamming (SEC, paridad par) ------------------
def is_power_of_two(x: int) -> bool:
    return x > 0 and (x & (x-1)) == 0

def calc_r(k: int) -> int:
    r = 0
    while (1 << r) < (k + r + 1):
        r += 1
    return r

def hamming_encode(data_bits: str) -> str:
    k = len(data_bits)
    r = calc_r(k)
    n = k + r
    code = ['0'] * n
    # coloca datos
    j = 0
    for i in range(1, n+1):
        if not is_power_of_two(i):
            code[i-1] = data_bits[j]; j += 1
    # paridades (paridad par)
    for i in range(r):
        p = 1 << i
        s = 0
        for pos in range(1, n+1):
            if pos & p:
                s ^= int(code[pos-1])
        if s % 2 != 0:
            code[p-1] = '1' if code[p-1]=='0' else '0'
    return ''.join(code)

# ------------------ Networking ------------------
def send_line(host: str, port: int, line: str, timeout: float=3.0) -> str:
    with socket.create_connection((host, port), timeout=timeout) as s:
        s.sendall(line.encode('utf-8') + b"\n")
        s.settimeout(timeout)
        data = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
            if b"\n" in data:
                break
        return data.decode('utf-8', errors='ignore').strip()

# ------------------ Exec helpers ------------------
def run_exe(exe_path: Path, input_str: str, timeout: float=5.0) -> tuple[int,str,str]:
    """Ejecuta un .exe y le pasa input_str por stdin. Retorna (rc, stdout, stderr)."""
    p = subprocess.Popen(
        [str(exe_path)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True
    )
    try:
        out, err = p.communicate(input=input_str, timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        out, err = p.communicate()
    return p.returncode, out, err

def try_compile():
    # Compila los binarios con MinGW (gcc). Requiere net_client.c, includes.c, etc.
    cmds = [
        ["gcc", "-o", "crc32.exe", "crc32.c", "net_client.c", "includes.c", "-lws2_32"],
        ["gcc", "-o", "hamming.exe", "hamming_encryptor.c", "net_client.c", "includes.c", "-lws_2_32"]  # typo común: "-lws_2_32"
    ]
    # corregimos el segundo comando (biblioteca correcta)
    cmds[1] = ["gcc", "-o", "hamming.exe", "hamming_encryptor.c", "net_client.c", "includes.c", "-lws2_32"]
    ok_all = True
    for cmd in cmds:
        print("[compile] ", " ".join(cmd))
        rc = subprocess.call(cmd)
        if rc != 0:
            print("  -> ERROR de compilación (rc=", rc, ")")
            ok_all = False
    return ok_all

# ------------------ Experimentos ------------------
def random_ascii(nchars: int) -> str:
    return ''.join(chr(random.randint(32, 126)) for _ in range(nchars))

def run_python_sender(host, port, runs, lens, perrs, do_crc: bool, do_ham: bool):
    print(f"[PY-SENDER] host={host} port={port} runs={runs} lens={lens} perrs={perrs} algos={['CRC' if do_crc else '', 'HAM' if do_ham else '']}")
    for nchars in lens:
        for perr in perrs:
            for _ in range(runs):
                text = random_ascii(nchars)
                msg_bits = ascii_to_bits(text)
                if do_crc:
                    frame = crc32_frame(msg_bits)
                    noisy = apply_noise(frame, perr)
                    resp = send_line(host, port, f"CRC:{noisy}")
                    print(resp)
                if do_ham:
                    code = hamming_encode(msg_bits)
                    noisy = apply_noise(code, perr)
                    resp = send_line(host, port, f"HAM:{noisy}")
                    print(resp)

def run_with_executables(host, port, runs, lens):
    """
    Lanza los .exe varias veces y les pasa entrada por stdin.
    NOTA: Esto asume que tus .exe leen **binario** por stdin y ellos mismos envían por sockets.
    Si no integraste el envío en C, usa run_python_sender en su lugar.
    """
    crc_exe = Path("crc32.exe")
    ham_exe = Path("hamming.exe")
    if not crc_exe.exists() and not ham_exe.exists():
        print("No hay ejecutables .exe disponibles. Ejecuta con --compile o usa el modo Python sender.")
        return
    for nchars in lens:
        for _ in range(runs):
            text = random_ascii(nchars)
            bits = ascii_to_bits(text)
            if crc_exe.exists():
                # Si tu CRC C espera binario del mensaje (no ASCII), pásale bits (sin CRC).
                rc, out, err = run_exe(crc_exe, bits+"\n")
                print("[crc32.exe]", rc, out.strip()[:120], err.strip()[:120])
            if ham_exe.exists():
                rc, out, err = run_exe(ham_exe, bits+"\n")
                print("[hamming.exe]", rc, out.strip()[:120], err.strip()[:120])

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5050)
    ap.add_argument("--runs", type=int, default=10)
    ap.add_argument("--lens", nargs="+", type=int, default=[4,8])
    ap.add_argument("--perr", dest="perrs", nargs="+", type=float, default=[0.0, 0.01])
    ap.add_argument("--compile", action="store_true", help="solo compilar crc32.exe y hamming.exe")
    ap.add_argument("--use-exe", action="store_true", help="usar ejecutables en lugar de sender Python")
    ap.add_argument("--algos", nargs="+", default=["CRC","HAM"])
    return ap.parse_args()

def main():
    args = parse_args()
    random.seed(123)
    if args.compile:
        ok = try_compile()
        print("Compilación", "OK" if ok else "con errores")
        return

    do_crc = any(a.upper()=="CRC" for a in args.algos)
    do_ham = any(a.upper()=="HAM" for a in args.algos)

    if args.use_exe:
        run_with_executables(args.host, args.port, args.runs, args.lens)
    else:
        run_python_sender(args.host, args.port, args.runs, args.lens, args.perrs, do_crc, do_ham)

if __name__ == "__main__":
    main()
""")

Path("/mnt/data/test.py").write_text(test_py, encoding="utf-8")
print("Created: /mnt/data/test.py")
