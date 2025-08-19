import socket

HOST, PORT = "127.0.0.1", 5050
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT)); s.listen(1)
    conn, addr = s.accept()
    with conn, conn.makefile('r', encoding='utf-8', newline='\n') as f:
        print("connected:", addr)
        for line in f:                        # reads until '\n'
            bitstring = line.rstrip('\n')
            print("got", len(bitstring), "bits")
            print(f"Bitstring: {bitstring}")
