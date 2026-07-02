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

# Arasaka NetSec Palette
C_RESET = '\033[0m'
C_RED = '\033[91m'       
C_DARK_RED = '\033[31m'  
C_GREEN = '\033[92m'     
C_WHITE = '\033[97m'     
C_USED = '\033[90m'      
C_CURSOR = '\033[41m\033[97m\033[1m'

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def select_difficulty():
    clear_screen()
    print(f"{C_RED}╔════════════════════════════════════════════════════════╗{C_RESET}")
    print(f"{C_RED}║               SELECT INTRUSION LEVEL                   ║{C_RESET}")
    print(f"{C_RED}╚════════════════════════════════════════════════════════╝{C_RESET}\n")
    print("  1. LAMER      (Easy)   [Matrix: 4x4, Buffer: 6,  Daemons: 2]")
    print("  2. IRC MEMBER (Medium) [Matrix: 6x6, Buffer: 10, Daemons: 3]")
    print("  3. HACKER     (Hard)   [Matrix: 8x8, Buffer: 14, Daemons: 4]\n")
    
    while True:
        choice = input(f"{C_WHITE}Choose level (1-3) or Q to quit: {C_RESET}").strip().lower()
        if choice in ('1', '2', '3'):
            return int(choice)
        if choice == 'q':
            sys.exit(0)

def generate_solvable_level(grid_size, buffer_size, daemon_lengths, daemon_names):
    """Guarantees 100% solvability with STRICT UNIQUE bytes within each daemon sequence,
       and guarantees that at least one daemon starts in the first row."""
    while True:
        matrix = [[random.choice(HEX_CODES) for _ in range(grid_size)] for _ in range(grid_size)]
        
        path = []
        c0 = random.randint(0, grid_size - 1)
        path.append((0, c0))
        current_search = 'row_for_col'
        failed = False
        
        for _ in range(buffer_size - 1):
            r_curr, c_curr = path[-1]
            if current_search == 'row_for_col':
                options = [r for r in range(grid_size) if (r, c_curr) not in path]
                if not options:
                    failed = True; break
                r_next = random.choice(options)
                path.append((r_next, c_curr))
                current_search = 'col_for_row'
            else:
                options = [c for c in range(grid_size) if (r_curr, c) not in path]
                if not options:
                    failed = True; break
                c_next = random.choice(options)
                path.append((r_curr, c_next))
                current_search = 'row_for_col'
                
        if not failed:
            sequence_pool = [matrix[r][c] for r, c in path]
            targets = {}
            invalid_sequence = False
            
            # Выбираем случайного деймона, который гарантированно начнется с первого шага (из нулевой строки)
            anchor_daemon_idx = random.randint(0, len(daemon_names) - 1)
            
            for i, (name, length) in enumerate(zip(daemon_names, daemon_lengths)):
                max_start = len(sequence_pool) - length
                
                if i == anchor_daemon_idx:
                    start_idx = 0  # Жестко привязываем к самому первому байту (0-я строка)
                else:
                    start_idx = random.randint(0, max_start)
                    
                seq = sequence_pool[start_idx : start_idx + length]
                
                if len(set(seq)) != len(seq):
                    invalid_sequence = True
                    break
                targets[name] = seq
                
            if not invalid_sequence:
                return matrix, targets

def get_target_status(buffer, seq, buffer_size):
    buf_str = " ".join(buffer)
    seq_str = " ".join(seq)
    
    if seq_str in buf_str:
        return 'COMPLETED', len(seq)
        
    overlap = 0
    for k in range(len(seq), 0, -1):
        if len(buffer) >= k and buffer[-k:] == seq[:k]:
            overlap = k
            break
            
    remaining_space = buffer_size - len(buffer)
    if (len(seq) - overlap > remaining_space) and (len(seq) > remaining_space):
        return 'FAILED', 0
        
    return 'IN_PROGRESS', overlap

def print_board(matrix, used, mode, active_idx, cursor_pos, buffer, targets, grid_size, buffer_size, reboots_left, message=""):
    clear_screen()
    print(f"{C_RED}╔════════════════════════════════════════════════════════╗{C_RESET}")
    print(f"{C_RED}║  CRITICAL SYSTEM FAULT: BREACH PROTOCOL ENGAGED        ║{C_RESET}")
    print(f"{C_RED}╚════════════════════════════════════════════════════════╝{C_RESET}\n")

    print(f"{C_WHITE}BREACH TARGETS:{C_RESET}")
    for name, seq in targets.items():
        status, overlap = get_target_status(buffer, seq, buffer_size)
        
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

        print(f"  {name:<18} ->  {' '.join(rendered_seq)}{status_tag}")
    print()

    buf_display = []
    for i in range(buffer_size):
        if i < len(buffer):
            buf_display.append(f"{C_WHITE}{buffer[i]}{C_RESET}")
        else:
            buf_display.append(f"{C_DARK_RED}[..]{C_RESET}")
    print(f"{C_WHITE}BUFFER:{C_RESET} " + " ".join(buf_display) + f" ({len(buffer)}/{buffer_size})  |  {C_RED}REBOOTS LEFT: {reboots_left}/3{C_RESET}\n")

    print(f"{C_WHITE}CODE MATRIX:{C_RESET}")
    for r in range(grid_size):
        row_str = []
        for c in range(grid_size):
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
    print(f"{C_USED}[Arrows / HJKL] - Move | [Space / Enter] - Select | [R] - Reset | [Q] - Disconnect{C_RESET}")

def main():
    if os.name == 'nt':
        os.system('')

    while True:  # Global replay loop
        level = select_difficulty()
        
        if level == 1:
            grid_size, buffer_size = 4, 6
            daemon_lengths = [2, 3]
            daemon_names = ["DATAMINE V1", "DATAMINE V2"]
        elif level == 2:
            grid_size, buffer_size = 6, 10
            daemon_lengths = [2, 3, 4]
            daemon_names = ["DATAMINE V1", "DATAMINE V2", "ICEPICK DAEMON"]
        else:
            grid_size, buffer_size = 8, 14
            daemon_lengths = [2, 3, 4, 5]
            daemon_names = ["DATAMINE V1", "DATAMINE V2", "ICEPICK DAEMON", "BLACKWALL OVERRIDE"]

        matrix, targets = generate_solvable_level(grid_size, buffer_size, daemon_lengths, daemon_names)
        used = set()
        buffer = []

        mode = 'row'
        active_idx = 0
        cursor_pos = 0
        reboots_left = 3
        msg = "LINK STABLE. Select initialization code in the top row."

        session_active = True
        while session_active:
            print_board(matrix, used, mode, active_idx, cursor_pos, buffer, targets, grid_size, buffer_size, reboots_left, msg)
            msg = ""

            target_states = {name: get_target_status(buffer, seq, buffer_size)[0] for name, seq in targets.items()}
            completed = [n for n, s in target_states.items() if s == 'COMPLETED']
            failed = [n for n, s in target_states.items() if s == 'FAILED']

            if len(completed) == len(targets):
                print_board(matrix, used, mode, active_idx, cursor_pos, buffer, targets, grid_size, buffer_size, reboots_left)
                print(f"\n{C_GREEN}[ FULL ACCESS GRANTED ] All daemons successfully uploaded.{C_RESET}")
                session_active = False
                continue

            if len(buffer) >= buffer_size or (len(completed) + len(failed) == len(targets)):
                print_board(matrix, used, mode, active_idx, cursor_pos, buffer, targets, grid_size, buffer_size, reboots_left)
                if completed:
                    print(f"\n{C_RED}[ PARTIAL BREACH ] Extracted payloads: {', '.join(completed)}{C_RESET}")
                else:
                    print(f"\n{C_RED}[ HARDWARE LOCKOUT ] Network isolated. Intrusion failed.{C_RESET}")
                
                if reboots_left > 0:
                    print(f"{C_WHITE}Press [R] to Reboot Matrix ({reboots_left} left) or [Q] to Abort.{C_RESET}")
                    choice_made = False
                    while not choice_made:
                        k = get_key()
                        if k in ('r', 'R'):
                            reboots_left -= 1
                            buffer, used = [], set()
                            mode, active_idx, cursor_pos = 'row', 0, 0
                            msg = "SYSTEM REBOOTED. Matrix state restored."
                            choice_made = True
                        elif k in ('q', 'Q', '\x03'):
                            sys.exit(0)
                    if msg:
                        continue
                else:
                    session_active = False
                    continue

            key = get_key()

            if key in ('q', 'Q', '\x03'):
                print("\nTerminal session terminated.")
                sys.exit(0)

            if key in ('r', 'R'):
                if reboots_left > 0:
                    reboots_left -= 1
                    buffer, used = [], set()
                    mode, active_idx, cursor_pos = 'row', 0, 0
                    msg = f"SYSTEM REBOOTED. Options left: {reboots_left}"
                    continue
                else:
                    msg = "WARNING: No reboots left! Hardware lockout imminent."
                    continue

            if mode == 'row':
                if key in ('left', 'h'): cursor_pos = (cursor_pos - 1) % grid_size
                elif key in ('right', 'l'): cursor_pos = (cursor_pos + 1) % grid_size
            else:
                if key in ('up', 'k'): cursor_pos = (cursor_pos - 1) % grid_size
                elif key in ('down', 'j'): cursor_pos = (cursor_pos + 1) % grid_size

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

        # Post-game choice block
        print(f"\n{C_WHITE}──────────────────────────────────────────────────────────{C_RESET}")
        print(f"{C_WHITE}SESSION TERMINATED. INITIALIZE NEW BREACH PROTOCOL?{C_RESET}")
        print(f"{C_USED}[Space / Enter] - New Session | [Q] - Disconnect Terminal{C_RESET}")
        
        menu_choice = False
        while not menu_choice:
            k = get_key()
            if k in ('q', 'Q', '\x03'):
                clear_screen()
                print("Terminal disconnected successfully. Goodbye, netrunner.")
                sys.exit(0)
            if k in (' ', '\r', '\n', 'enter', 'space'):
                menu_choice = True

if __name__ == "__main__":
    main()
