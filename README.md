# Network-based Tic-Tac-Toe Game (Python TCP)

A classic Tic-Tac-Toe game which works over a local network using TCP sockets.  
Two players (or a player vs server) can play across different machines, either via terminal or GUI.  

## Features

- Console version for LAN play between two machines
- GUI version using Flet for a smooth interactive experience
- TCP-based communication ensures reliable and ordered data transfer
- Robust error handling (timeouts, dropped connections, invalid input)
- Custom text-based protocol with simple string instructions

## Tech Stack

* Python 3
* `socket`, `threading`
* Flet (for GUI)
* LAN | TCP/IP

## Versions
### Version 1: Console-based Tic-Tac-Toe
Play over LAN in two terminals using basic input/output.

- Player inputs move (1–9) on 3x3 grid
- Board is printed after each move
- Game ends in win or draw

**How to run:**
```bash
# On Machine A (server)
python server.py

# On Machine B (client)
python client.py
````

> Can be run on same machine using `localhost`

### Version 2: GUI-based Tic-Tac-Toe (Flet)

A clean graphical interface using the [Flet](https://flet.dev) framework.

* Clickable 3x3 board
* Server responds with a move automatically
* Game restarts with a "Try again" button

**How to run:**

```bash
# On Server
python server_gui.py

# On Client (Flet must be installed)
python client_gui.py
```

## Screenshots
### Console version
Server’s side (client won the game):

![Image](https://github.com/user-attachments/assets/355eaa7b-3aa1-4a09-8691-aebe51dda3b8)

Client’s side (client won the game):

![Image](https://github.com/user-attachments/assets/c9c7488a-581e-4328-84ed-f11b8ca1c811)

### GUI version
Client’s side:

![Image](https://github.com/user-attachments/assets/3b5d1d3d-cf54-4e59-9050-d4908f75344b)
![Image](https://github.com/user-attachments/assets/789db76a-0340-4fa2-ad57-034f54f1a07b)

Server’s side:

![Image](https://github.com/user-attachments/assets/73876a8c-918f-406c-b1f3-6d5c85f119a0)
