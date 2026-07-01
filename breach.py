import random
import os
import sys

# Поддержка raw-ввода для Linux/Unix
try:
    import tty
    import termios
    def get_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':  # Обработка escape-последовательностей (стрелочки)
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
    # Фоллбек для Windows на всякий случай
    import msvcrt
    def get_key():
        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'):
            ch2 = msvcrt.getch()
            if ch2 == b'H': return 'up'
            if ch2 == b'P': return 'down'
            if ch2 == b'M': return 'right'
            if ch2 == b'K': return 'left'
        ch = ch.decode('utf-8', errors='ignore')
        if ch in ('\r', '\n'): return 'enter'
        return ch

# Настройки игры
HEX_CODES = ['1C', '55', 'BD', 'E9', '7A', 'FF']
GRID_SIZE = 5
BUFFER_SIZE = 6

# Кроваво-красная палитра (Cyberpunk / Arasaka NetSec)
C_RESET = '\033[0m'
C_RED = '\033[91m'       # Яркий красный (активные элементы)
C_DARK_RED = '\033[31m'  # Темно-красный (фон матрицы)
C_CURSOR = '\033[41m\033[97m\033[1m'  # Белый текст на красном фоне (курсор)
C_USED = '\033[90m'      # Серый (взломанные ячейки)
C_WHITE = '\033[97m'     # Чистый белый

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def generate_targets():
    return {
        "ДАТАМАЙН V1": [random.choice(HEX_CODES) for _ in range(2)],
        "ДАТАМАЙН V2": [random.choice(HEX_CODES) for _ in range(3)],
        "БЕКДОР СЕТИ": [random.choice(HEX_CODES) for _ in range(4)]
    }

def print_board(matrix, used, mode, active_idx, cursor_pos, buffer, targets, message=""):
    clear_screen()
    print(f"{C_RED}╔════════════════════════════════════════════════════════╗{C_RESET}")
    print(f"{C_RED}║  КРИТИЧЕСКИЙ СБОЙ СИСТЕМЫ: ОБНАРУЖЕН ПРОТОКОЛ ВЗЛОМА   ║{C_RESET}")
    print(f"{C_RED}╚════════════════════════════════════════════════════════╝{C_RESET}\n")

    print(f"{C_WHITE}ДЕМОНЫ В СЕТИ:{C_RESET}")
    for name, seq in targets.items():
        print(f"  {name:<15} ->  {C_RED}{' '.join(seq)}{C_RESET}")
    print()

    # Рендеринг буфера
    buf_display = []
    for i in range(BUFFER_SIZE):
        if i < len(buffer):
            buf_display.append(f"{C_WHITE}{buffer[i]}{C_RESET}")
        else:
            buf_display.append(f"{C_DARK_RED}[..]{C_RESET}")
    print(f"{C_WHITE}БУФЕР ХЭКЕРА:{C_RESET} " + " ".join(buf_display) + f" ({len(buffer)}/{BUFFER_SIZE})\n")

    print(f"{C_WHITE}МАТРИЦА ДАННЫХ:{C_RESET}")
    
    for r in range(GRID_SIZE):
        row_str = []
        for c in range(GRID_SIZE):
            cell = matrix[r][c]
            is_used = (r, c) in used
            
            # Логика наведения курсора
            is_cursor = (mode == 'row' and r == active_idx and c == cursor_pos) or \
                        (mode == 'col' and c == active_idx and r == cursor_pos)
            
            # Принадлежность к текущей рабочей линии
            is_active_line = (mode == 'row' and r == active_idx) or (mode == 'col' and c == active_idx)

            if is_cursor:
                row_str.append(f"{C_CURSOR}{cell}{C_RESET}")
            elif is_used:
                row_str.append(f"{C_USED}──{C_RESET}")
            elif is_active_line:
                row_str.append(f"{C_RED}{cell}{C_RESET}")
            else:
                row_str.append(f"{C_DARK_RED}{cell}{C_RESET}")

        # Небольшой указатель текущей активной строки
        prefix = f"{C_RED}» {C_RESET}" if mode == 'row' and r == active_idx else "  "
        print(prefix + "  ".join(row_str))
        
    print(f"\n{C_DARK_RED}{message}{C_RESET}")
    print(f"{C_USED}[Стрелочки / HJKL] - Перемещение | [Space / Enter] - Выбор | [Q] - Выход{C_RESET}")

def check_targets(buffer, targets):
    completed = []
    buf_str = " ".join(buffer)
    for name, seq in targets.items():
        if " ".join(seq) in buf_str:
            completed.append(name)
    return completed

def main():
    matrix = [[random.choice(HEX_CODES) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    targets = generate_targets()
    used = set()
    buffer = []

    mode = 'row'       # Начинаем традиционно с выбора в строке
    active_idx = 0     # Первая строка активна
    cursor_pos = 0     # Позиция курсора на активной линии (сейчас это колонка 0)
    msg = "СОЕДИНЕНИЕ УСТАНОВЛЕНО. Выберите стартовый код в верхней строке."

    while True:
        print_board(matrix, used, mode, active_idx, cursor_pos, buffer, targets, msg)
        msg = ""

        # Проверка условий победы/луза
        completed = check_targets(buffer, targets)
        if len(completed) == len(targets):
            print_board(matrix, used, mode, active_idx, cursor_pos, buffer, targets)
            print(f"\n{C_RED}[ СЕТЬ ВЗЛОМАНА ] Все демоны успешно внедрены!{C_RESET}")
            break

        if len(buffer) >= BUFFER_SIZE:
            print_board(matrix, used, mode, active_idx, cursor_pos, buffer, targets)
            if completed:
                print(f"\n{C_RED}[ ЧАСТИЧНЫЙ УСПЕХ ] Загружены: {', '.join(completed)}{C_RESET}")
            else:
                print(f"\n{C_RED}[ СИСТЕМА ЗАБЛОКИРОВАНА ] Превышен размер буфера.{C_RESET}")
            break

        key = get_key()

        if key in ('q', 'Q', '\x03'):  # Выход по Q или Ctrl+C
            print("\nАварийное отключение...")
            break

        # Управление перемещением
        if mode == 'row':
            # В режиме строки двигаемся горизонтально (влево/вправо)
            if key in ('left', 'h'):
                cursor_pos = (cursor_pos - 1) % GRID_SIZE
            elif key in ('right', 'l'):
                cursor_pos = (cursor_pos + 1) % GRID_SIZE
        else:
            # В режиме колонки двигаемся вертикально (вверх/вниз)
            if key in ('up', 'k'):
                cursor_pos = (cursor_pos - 1) % GRID_SIZE
            elif key in ('down', 'j'):
                cursor_pos = (cursor_pos + 1) % GRID_SIZE

        # Выбор ячейки
        if key in (' ', '\r', '\n', 'enter', 'space'):
            r = active_idx if mode == 'row' else cursor_pos
            c = cursor_pos if mode == 'row' else active_idx

            if (r, c) in used:
                msg = "ОШИБКА: Точка матрицы уже использована!"
                continue

            # Фиксируем выбор
            buffer.append(matrix[r][c])
            used.add((r, c))

            # Переключаем режим и прокидываем индекс новой оси
            if mode == 'row':
                mode = 'col'
                active_idx = c       # Теперь активна колонка с индексом выбранного столбца
                cursor_pos = r       # Курсор встает на текущую строку
            else:
                mode = 'row'
                active_idx = r       # Теперь активна строка с индексом выбранной строки
                cursor_pos = c       # Курсор встает на текущий столбец

if __name__ == "__main__":
    main()
