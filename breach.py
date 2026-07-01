import random
import os
import sys

# Cross-platform raw input handling (Linux/macOS vs Windows)
try:
    import tty
    import termios
    def get_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A': return 'up'
                    if ch3 == 'B': return 'down'
                    if ch3 == 'C': return 'right'
                    if ch3 == 'D': return 'left'
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
except ImportError:
    import msvcrt
    def get_key():
        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'):
            ch2 = msvcrt.getch()
            if ch2 == b'H': return 'up'
            if ch2 == b'P': return 'down'
            if ch2 == b'M': return 'right'
            if ch2 == b'K': return 'left'
        try:
            ch_str = ch.decode('utf-8')
        except:
            ch_str = ''
        if ch_str in ('\r', '\n'): return 'enter'
        if ch_str == ' ': return 'space'
        return ch_str.lower()

HEX_CODES = ['1C', '55', 'BD', 'E9', '7A', 'FF']
GRID_SIZE = 5
BUFFER_SIZE = 6

# Arasaka NetSec Palette (Aggressive Red & Clean UI)
C_RESET = '\033[0m'
C_RED = '\033[91m'       # Active systems / alert
C_DARK_RED = '\033[31m'  # Standard matrix elements
C_GREEN = '\033[92m'     # Uploaded daemons
C_WHITE = '\033[97m'     # Synchronized sequence steps
C_USED = '\033[90m'      # Burned/inactive nodes
C_CURSOR = '\033[41m\033[97m\033[1m' # High-contrast inverse cursor

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def generate_targets():
    return {
        "DATAMINE V1": [random.choice(HEX_CODES) for _ in range(2)],
        "DATAMINE V2": [random.choice(HEX_CODES) for _ in range(3)],
        "ICEPICK DAEMON": [random.choice(HEX_CODES) for _ in range(4)]
    }

def get_target_status(buffer, seq):
    buf_str = " ".join(buffer)
    seq_str = " ".join(seq)
    
    if seq_str in buf_str:
        return 'COMPLETED', len(seq)
        
    overlap = 0
    for k in range(len(seq), 0, -1):
        if len(buffer) >= k and buffer[-k:] == seq[:k]:
            overlap = k
            break
            
    remaining_space = BUFFER_SIZE - len(buffer)
    if (len(seq) - overlap > remaining_space) and (len(seq) > remaining_space):
        return 'FAILED', 0
        
    return 'IN_PROGRESS', overlap

def print_board(matrix, used, mode, active_idx, cursor_pos, buffer, targets, message=""):
    clear_screen()
    print(f"{C_RED}╔════════════════════════════════════════════════════════╗{C_RESET}")
    print(f"{C_RED}║  CRITICAL SYSTEM FAULT: BREACH PROTOCOL ENGAGED        ║{C_RESET}")
    print(f"{C_RED}╚════════════════════════════════════════════════════════╝{C_RESET}\n")

    print(f"{C_WHITE}BREACH TARGETS:{C_RESET}")
    for name, seq in targets.items():
        status, overlap = get_target_status(buffer, seq)
        
        rendered_seq = []
        for i, code in enumerate(seq):
            if status == 'COMPLETED':
                rendered_seq.append(f"{C_GREEN}{code}{C_RESET}")
            elif status == 'FAILED':
                rendered_seq.append(f"{C_USED}{code}{C_RESET}")
            else:
                if i < overlap:
                    rendered_seq.append(f"{C_WHITE}{code}{C_RESET}")
                else:
                    rendered_seq.append(f"{C_RED}{code}{C_RESET}")
                    
        if status == 'COMPLETED':
            status_tag = f" {C_GREEN}[ UPLOADED ]{C_RESET}"
        elif status == 'FAILED':
            status_tag = f" {C_USED}[ LINK FAULT ]{C_RESET}"
        elif overlap > 0:
            status_tag = f" {C_WHITE}[ SYNC {overlap}/{len(seq)} ]{C_RESET}"
        else:
            status_tag = ""

        print(f"  {name:<15} ->  {' '.join(rendered_seq)}{status_tag}")
    print()

    # Buffer render
    buf_display = []
    for i in range(BUFFER_SIZE):
        if i < len(buffer):
            buf_display.append(f"{C_WHITE}{buffer[i]}{C_RESET}")
        else:
            buf_display.append(f"{C_DARK_RED}[..]{C_RESET}")
    print(f"{C_WHITE}BUFFER:{C_RESET} " + " ".join(buf_display) + f" ({len(buffer)}/{BUFFER_SIZE})\n")

    print(f"{C_WHITE}CODE MATRIX:{C_RESET}")
    for r in range(GRID_SIZE):
        row_str = []
        for c in range(GRID_SIZE):
            cell = matrix[r][c]
            is_used = (r, c) in used
            is_cursor = (mode == 'row' and r == active_idx and c == cursor_pos) or \
                        (mode == 'col' and c == active_idx and r == cursor_pos)
            is_active_line = (mode == 'row' and r == active_idx) or (mode == 'col' and c == active_idx)

            if is_cursor:
                row_str.append(f"{C_CURSOR}{cell}{C_RESET}")
            elif is_used:
                row_str.append(f"{C_USED}──{C_RESET}")
            elif is_active_line:
                row_str.append(f"{C_RED}{cell}{C_RESET}")
            else:
                row_str.append(f"{C_DARK_RED}{cell}{C_RESET}")

        prefix = f"{C_RED}» {C_RESET}" if mode == 'row' and r == active_idx else "  "
        print(prefix + "  ".join(row_str))
        
    if message:
        print(f"\n{C_RED}{message}{C_RESET}")
    else:
        print("\n")
    print(f"{C_USED}[Arrows / HJKL] - Move | [Space / Enter] - Select Code | [Q] - Disconnect{C_RESET}")

def main():
    # Force ANSI escape codes support on Windows 10/11 native console
    if os.name == 'nt':
        os.system('')

    matrix = [[random.choice(HEX_CODES) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    targets = generate_targets()
    used = set()
    buffer = []

    mode = 'row'
    active_idx = 0
    cursor_pos = 0
    msg = "LINK STABLE. Select initialization code in the top row."

    while True:
        print_board(matrix, used, mode, active_idx, cursor_pos, buffer, targets, msg)
        msg = ""

        target_states = {name: get_target_status(buffer, seq)[0] for name, seq in targets.items()}
        completed = [n for n, s in target_states.items() if s == 'COMPLETED']
        failed = [n for n, s in target_states.items() if s == 'FAILED']

        if len(completed) == len(targets):
            print_board(matrix, used, mode, active_idx, cursor_pos, buffer, targets)
            print(f"\n{C_GREEN}[ FULL ACCESS GRANTED ] All daemons successfully uploaded.{C_RESET}")
            break

        if len(buffer) >= BUFFER_SIZE or (len(completed) + len(failed) == len(targets)):
            print_board(matrix, used, mode, active_idx, cursor_pos, buffer, targets)
            if completed:
                print(f"\n{C_RED}[ PARTIAL BREACH ] Extracted payloads: {', '.join(completed)}{C_RESET}")
            else:
                print(f"\n{C_RED}[ HARDWARE LOCKOUT ] Network isolated. Intrusion failed.{C_RESET}")
            break

        key = get_key()

        if key in ('q', 'Q', '\x03'):
            print("\nTerminal session terminated.")
            break

        if mode == 'row':
            if key in ('left', 'h'): cursor_pos = (cursor_pos - 1) % GRID_SIZE
            elif key in ('right', 'l'): cursor_pos = (cursor_pos + 1) % GRID_SIZE
        else:
            if key in ('up', 'k'): cursor_pos = (cursor_pos - 1) % GRID_SIZE
            elif key in ('down', 'j'): cursor_pos = (cursor_pos + 1) % GRID_SIZE

        if key in (' ', '\r', '\n', 'enter', 'space'):
            r = active_idx if mode == 'row' else cursor_pos
            c = cursor_pos if mode == 'row' else active_idx

            if (r, c) in used:
                msg = "WARNING: Node already burned! Select another coordinate."
                continue

            buffer.append(matrix[r][c])
            used.add((r, c))

            if mode == 'row':
                mode = 'col'
                active_idx = c
                cursor_pos = r
            else:
                mode = 'row'
                active_idx = r
                cursor_pos = c

if __name__ == "__main__":
    main()
