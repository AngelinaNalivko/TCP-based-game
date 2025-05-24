import socket
import random
import time

def init_board():
    return [[" " for _ in range(3)] for _ in range(3)]

def board_to_string(board):
    return '\n'.join([' | '.join(row) for row in board])

def display_board(board):
    print(board_to_string(board))
    print()

def get_available_moves(board):
    return [i + 1 for i, cell in enumerate(sum(board, [])) if cell not in ['X', 'O']]

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
    except Exception as ex:
        print(f"[apply_move] Error: {ex}")
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
        conn.settimeout(60.0)
        data = conn.recv(1024)
        if not data:
            print("[safe_recv] Client disconnected.")
            return None
        return data.decode().strip()
    except socket.timeout:
        print("Timeout while waiting for client response")
        return None
    except Exception as e:
        print(f"Error receiving data: {e}")
        return None
    finally:
        conn.settimeout(None)

def send_board(conn, board):
    for row in board:
        send(conn, ' | '.join(row))

def find_best_move(board):
    moves = get_available_moves(board)
    if random.random() < 0.1:
        return random.choice(moves)
    for move in moves:
        temp = [row[:] for row in board]
        apply_move(temp, move, 'X')
        if check_victory(temp, 'X'):
            return move
    for move in moves:
        temp = [row[:] for row in board]
        apply_move(temp, move, 'O')
        if check_victory(temp, 'O'):
            return move
    if board[1][1] == ' ':
        return 5
    for move in [1, 3, 7, 9]:
        row, col = divmod(move - 1, 3)
        if board[row][col] == ' ':
            return move
    return random.choice(moves)

HOST = '0.0.0.0'
PORT = 65432

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print("Server started. Waiting for players...")

        while True:
            print("Waiting for a player...")
            s.settimeout(60.0)
            try:
                conn, addr = s.accept()
            except socket.timeout:
                print("No client connected for 60 seconds. Server shutting down.")
                break
            with conn:
                print(f"Connected to {addr}")
                board = init_board()
                send_board(conn, board)

                while True:
                    send(conn, "Your move (1-9):")
                    move = safe_recv(conn)
                    if move is None:
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
                    time.sleep(0.5)
                    move = find_best_move(board)
                    apply_move(board, move, 'X')
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