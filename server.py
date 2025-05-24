import socket
import sys

def init_board():
    return [[str(j * 3 + i + 1) for i in range(3)] for j in range(3)]

def board_to_string(board):
    return '\n'.join([' | '.join(row) for row in board])

def display_board(board):
    print(board_to_string(board))
    print()

def check_victory(board, sign):
    for row in board:
        if all(cell == sign for cell in row): return True
    for col in range(3):
        if all(board[row][col] == sign for row in range(3)): return True
    if all(board[i][i] == sign for i in range(3)): return True
    if all(board[i][2 - i] == sign for i in range(3)): return True
    return False

def is_draw(board):
    return all(cell in ['X', 'O'] for row in board for cell in row)

def apply_move(board, move, sign):
    try:
        move = int(move)
        row, col = divmod(move - 1, 3)
        if 0 <= row < 3 and 0 <= col < 3 and board[row][col] not in ['X', 'O']:
            board[row][col] = sign
            return True
        return False
    except (ValueError, TypeError):
        return False

def send(conn, msg):
    try:
        conn.sendall((msg + '\n').encode())
    except (BrokenPipeError, ConnectionResetError):
        print("Connection lost while sending.")
        raise
    except Exception as e:
        print(f"Error sending data: {e}")
        raise

def safe_recv(conn):
    try:
        conn.settimeout(60.0)  # 60 second timeout
        data = conn.recv(1024)
        if not data:
            raise ConnectionResetError("Client disconnected.")
        return data.decode().strip()
    except socket.timeout:
        print("Timeout while waiting for client response")
        raise
    except Exception as e:
        print(f"Error receiving data: {e}")
        raise
    finally:
        conn.settimeout(None)

def send_board(conn, board):
    for row in board:
        send(conn, ' | '.join(row))

HOST = '0.0.0.0'
PORT = 65432

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print("Waiting for a player...")
        conn, addr = s.accept()

        with conn:
            print(f"Connected to {addr}")
            board = init_board()
            send_board(conn, board)

            while True:
                send(conn, "Your move (1-9):")
                try:
                    move = safe_recv(conn)
                except (ConnectionResetError, socket.timeout):
                    print("Client disconnected or timed out")
                    break

                if not apply_move(board, move, 'O'):
                    send(conn, "Invalid move!")
                    continue

                if check_victory(board, 'O'):
                    send(conn, "MOVE_ACCEPTED")
                    send_board(conn, board)
                    send(conn, "You win!")
                    display_board(board)
                    print("Client wins!")
                    break

                if is_draw(board):
                    send(conn, "MOVE_ACCEPTED")
                    send_board(conn, board)
                    send(conn, "Draw!")
                    display_board(board)
                    print("Draw!")
                    break

                send(conn, "MOVE_ACCEPTED")
                send_board(conn, board)

                send(conn, "Server's turn")
                display_board(board)

                while True:
                    try:
                        move = input("Your move (1-9): ").strip()
                    except KeyboardInterrupt:
                        print("\nServer interrupted.")
                        sys.exit(0)
                    if apply_move(board, move, 'X'):
                        break
                    print("Invalid move. Try again.")

                send_board(conn, board)

                if check_victory(board, 'X'):
                    send(conn, "Server wins!")
                    display_board(board)
                    print("You win!")
                    break
                elif is_draw(board):
                    send(conn, "Draw!")
                    print("Draw!")
                    break
                else:
                    send(conn, "CONTINUE")

except KeyboardInterrupt:
    print("\nServer shut down manually.")
except Exception as e:
    print(f"Unexpected error: {e}")