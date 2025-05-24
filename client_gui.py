import flet as ft
import socket
import threading
import time

HOST = '172.16.187.3' # change to server's ip address
PORT = 65432

class TicTacToeClient:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Tic-Tac-Toe Client"
        self.page.window_resizable = False
        self.page.window_width = 260
        self.page.window_height = 320
        self.page.padding = 30
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.board_controls = []
        self.socket = None
        self.s_file = None
        self.my_turn = True
        self.last_game_status = None
        self.client_score = 0
        self.server_score = 0
        self.move_timer = None
        self.move_time_limit = 60
        self.timer_thread = None
        self.timer_running = False

        self.status_text = ft.Text("Connecting to server...", 
                                 size=20, 
                                 weight=ft.FontWeight.BOLD,
                                 text_align=ft.TextAlign.CENTER)
        
        self.score_text = ft.Text(
            self.get_score_text(),
            size=16,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )

        self.timer_text = ft.Text(
            "",
            size=16,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )

        self.board_grid = ft.Column(
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.restart_button = ft.ElevatedButton(
            content=ft.Text("Try again", size=22, weight=ft.FontWeight.BOLD),
            width=180,
            height=55,
            visible=False,
            on_click=self.restart_game,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=10,
            ),
        )

        self.page.add(self.score_text)
        self.page.add(self.status_text)
        self.page.add(self.timer_text)
        self.build_board()
        self.page.add(self.board_grid)
        self.page.add(
            ft.Row(
                [
                    ft.Container(
                        self.restart_button,
                        margin=ft.margin.only(top=30)
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER
            )
        )

        threading.Thread(target=self.connect_to_server, daemon=True).start()
        self.page.on_window_event = self.on_window_close

    def handle_button_click(self, e, idx):
        if self.my_turn:
            self.send_move(idx + 1)

    def build_board(self):
        self.board_grid.controls = []
        self.board_controls.clear()
        for i in range(3):
            row = []
            for j in range(3):
                idx = i * 3 + j
                btn = ft.ElevatedButton(
                    content=ft.Text(" ", size=38, weight=ft.FontWeight.BOLD),
                    width=100,
                    height=100,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5),
                        padding=20,
                    ),
                    data=idx,
                    on_click=lambda e, idx=idx: self.handle_button_click(e, idx)
                )
                self.board_controls.append(btn)
                row.append(btn)
            self.board_grid.controls.append(
                ft.Row(controls=row, alignment=ft.MainAxisAlignment.CENTER)
            )
        self.page.update()

    def connect_to_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((HOST, PORT))
            self.s_file = self.socket.makefile('r')
            self.status_text.value = "Connected to server. Waiting for your move."
            self.page.update()
            self.update_board_from_server()
            self.listen_to_server()
        except Exception as e:
            self.page.update()
            ft.dialog.alert(self.page, f"Connection error: {e}")

    def safe_recv_line(self):
        line = self.s_file.readline()
        if not line:
            raise ConnectionResetError("Server disconnected.")
        return line.strip()

    def send_move(self, move):
        if not self.my_turn:
            return
        self.my_turn = False
        self.cancel_move_timer()
        try:
            self.socket.sendall(f"{move}\n".encode())
        except Exception as e:
            ft.dialog.alert(self.page, f"Send failed: {e}")
            self.page.window_destroy()

    def update_board(self, board_lines):
        for i, line in enumerate(board_lines):
            cells = line.split('|')
            for j, cell in enumerate(cells):
                idx = i * 3 + j
                self.board_controls[idx].content.value = cell.strip() if cell.strip() else " "
        self.page.update()

    def disable_all_buttons(self):
        for btn in self.board_controls:
            btn.disabled = True
        self.restart_button.visible = True
        self.page.update()

    def update_board_from_server(self):
        board_lines = [self.safe_recv_line() for _ in range(3)]
        self.update_board(board_lines)

    def restart_game(self, e):
        self.cancel_move_timer()
        try:
            if self.socket:
                self.socket.close()
        except Exception as ex:
            print(f"[restart_game] Socket close error: {ex}")
        self.board_controls.clear()
        self.socket = None
        self.s_file = None
        self.my_turn = True
        self.last_game_status = None
        self.status_text.value = "Connecting to server..."
        self.restart_button.visible = False
        self.build_board()
        self.page.update()
        threading.Thread(target=self.connect_to_server, daemon=True).start()

    def listen_to_server(self):
        try:
            while True:
                msg = self.safe_recv_line()

                if msg == "Your move (1-9):":
                    self.my_turn = True
                    self.status_text.value = "Your turn!"
                    self.start_move_timer()

                elif msg == "Invalid move!":
                    self.status_text.value = "Invalid move! Try again."
                    self.my_turn = True

                elif msg == "MOVE_ACCEPTED":
                    self.status_text.value = "Server is thinking..."
                    self.update_board_from_server()

                elif msg == "Server's turn":
                    self.status_text.value = "Server is thinking..."
                    self.update_board_from_server()

                elif msg in ["You win!", "Server wins!", "Draw!"]:
                    self.cancel_move_timer()
                    self.last_game_status = msg
                    self.status_text.value = msg
                    self.update_score(msg)
                    self.disable_all_buttons()
                    ft.dialog.alert(self.page, msg)
                    self.page.update()
                    return

                elif msg == "CONTINUE":
                    pass

                else:
                    print("Unknown message:", msg)

                self.page.update()

        except ConnectionResetError:
            if self.last_game_status in ["You win!", "Server wins!", "Draw!"]:
                return
            ft.dialog.alert(self.page, "Server disconnected.")
            self.status_text.value = "Connection failed."
            self.page.update()
            self.page.window_destroy()

    def on_window_close(self, e):
        self.cancel_move_timer()
        try:
            if self.socket:
                self.socket.close()
        except Exception as ex:
            print(f"[on_window_close] Socket close error: {ex}")

    def get_score_text(self):
        return f"Client: {self.client_score}   Server: {self.server_score}"

    def update_score(self, result):
        if result == "You win!":
            self.client_score += 1
        elif result == "Server wins!":
            self.server_score += 1
        elif result == "Draw!":
            self.client_score += 1
            self.server_score += 1
        self.score_text.value = self.get_score_text()
        self.page.update()

    def start_move_timer(self):
        self.cancel_move_timer()
        self.time_left = self.move_time_limit
        self.timer_running = True

        def timer_logic():
            start = time.monotonic()
            while self.timer_running and self.time_left > 0 and self.my_turn:
                elapsed = int(time.monotonic() - start)
                left = max(self.move_time_limit - elapsed, 0)
                if left != self.time_left:
                    self.time_left = left
                    self.timer_text.value = f"Time left: {self.time_left} s"
                    self.page.update()
                time.sleep(0.1)
            if self.timer_running and self.time_left <= 0 and self.my_turn:
                self.on_move_timeout()

        self.timer_thread = threading.Thread(target=timer_logic, daemon=True)
        self.timer_thread.start()

    def cancel_move_timer(self):
        self.timer_running = False
        self.timer_text.value = ""
        self.page.update()

    def on_move_timeout(self):
        self.status_text.value = "Time is up! You lost this game."
        self.page.update()
        ft.dialog.alert(self.page, "Time is up! You lost this game.")
        try:
            if self.socket:
                self.socket.close()
        except Exception:
            pass
        self.page.window_destroy()

def main(page: ft.Page):
    TicTacToeClient(page)

ft.app(target=main)