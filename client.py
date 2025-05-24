import socket
import sys

HOST = '172.16.187.3' # change to server's ip address
PORT = 65432

def safe_recv_line(s_file):
    try:
        line = s_file.readline()
        if not line:
            raise ConnectionResetError("Connection closed by server.")
        return line.strip()
    except Exception as e:
        print(f"Error receiving data: {e}")
        raise

def safe_send(sock, msg):
    try:
        sock.sendall((msg + '\n').encode())
    except Exception as e:
        print(f"Error sending data: {e}")
        raise

def handle_server_disconnect():
    print("\nServer disconnected. Game ended.")
    sys.exit(1)

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(60.0)
            s.connect((HOST, PORT))
        except socket.timeout:
            print("Connection timeout. Server might be down.")
            sys.exit(1)
        except ConnectionRefusedError:
            print("Could not connect to server. Make sure the server is running.")
            sys.exit(1)
        except Exception as e:
            print(f"Connection error: {e}")
            sys.exit(1)
        finally:
            s.settimeout(None)

        s_file = s.makefile('r')
        print("Connected to server")

        print("Initial board:")
        try:
            for _ in range(3):
                print(safe_recv_line(s_file))
        except ConnectionResetError:
            handle_server_disconnect()

        while True:
            try:
                prompt = safe_recv_line(s_file)
                print(prompt)

                if prompt in ["You win!", "Server wins!", "Draw!"]:
                    break

                move = input().strip()
                safe_send(s, move)

                response = safe_recv_line(s_file)
                if response == "Invalid move!":
                    print("Invalid move! Try again.")
                    continue

                if response == "MOVE_ACCEPTED":
                    print("Your move applied:")
                    try:
                        for _ in range(3):  
                            print(safe_recv_line(s_file))

                        msg = safe_recv_line(s_file)
                        if msg == "Server's turn":
                            print(msg)
                            for _ in range(3):  
                                print(safe_recv_line(s_file))
                            result = safe_recv_line(s_file)
                        else:
                            result = msg 

                        if result in ["You win!", "Server wins!", "Draw!"]:
                            print(result)
                            break
                    except ConnectionResetError:
                        handle_server_disconnect()
                else:
                    print("Unexpected response from server:", response)
                    break

            except ConnectionResetError:
                handle_server_disconnect()
            except KeyboardInterrupt:
                print("\nClient closed manually.")
                sys.exit(0)
            except Exception as e:
                print(f"Unexpected error: {e}")
                sys.exit(1)

except Exception as e:
    print(f"Unexpected error in client: {e}")
    sys.exit(1)