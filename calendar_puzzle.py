import pygame
import random
import sys
import calendar
import datetime
import collections

# --- Pygame 设置 ---
# 颜色 (可自定义)
SCREEN_BACKGROUND_COLOR = (173, 216, 230)  # 浅蓝色
TILE_COLOR = (255, 255, 255)  # 白色
EMPTY_TILE_COLOR = (150, 200, 220) # 稍深的浅蓝色，用于空块
PLACEHOLDER_TILE_COLOR = (211, 211, 211) # 浅灰色，用于非本月日期
TEXT_COLOR = (0, 0, 0)  # 黑色
INFO_AREA_BACKGROUND_COLOR = (200, 200, 200)  # 灰色
INFO_AREA_TEXT_COLOR = (0, 0, 0) # 黑色
PUZZLE_PIECES = [
    [(0,0), (0,1), (0,2), (0,3), (0,4), (1,1)], # Piece 1
    [(0,0), (0,1), (1,1), (1,0), (2,0)],       # Piece 2
    [(0,0), (1,0), (2,0), (2,1), (2,2),(2,3)],       # Piece 3
    [(0,0), (0,1), (1,1), (2,0), (2,1), (2,2)], # Piece 4
    [(0,1), (1,1), (2,0), (2,1), (2,2), (3,2)], # Piece 5
    [(0,0), (0,1), (0,2), (0,3), (1,0)], # Piece 6
    [(0,0), (1,0), (2,0), (3,0), (2,1), (2,2)], # Piece 7
    [(0,0), (1,0), (2,0), (2,1), (3,1)],       # Piece 8
    [(0,0), (1,0), (2,0), (3,0), (4,0), (4,1)]        # Piece 9
]
# Generate distinct colors for puzzle pieces
BASE_PIECE_COLORS = [
    (255, 105, 180), (255, 165, 0), (255, 255, 0), (0, 128, 0), 
    (0, 0, 255), (75, 0, 130), (238, 130, 238), (165, 42, 42), (0, 255, 255)
]
PIECE_COLORS = [BASE_PIECE_COLORS[i % len(BASE_PIECE_COLORS)] for i in range(len(PUZZLE_PIECES))]
TARGET_CELL_COLOR = (255, 0, 0)  # Red for target cells
SELECTED_PIECE_BORDER_COLOR = (0,255,0) # Green for selected piece highlight (if needed)
# Screen dimensions and tile size
TILE_SIZE = 70
MARGIN = 5
INFO_HEIGHT = 100 # Height for the top info area, increased for multi-line messages
# DEFAULT_ROWS and DEFAULT_COLS are removed as they are now user-defined

class CalendarPuzzle:
    # Constants for board cell states
    EMPTY_CELL = 0
    TARGET_CELL = -1 # User-selected cell, not to be covered by pieces
    # Piece IDs will be 1 through len(PUZZLE_PIECES)

    def __init__(self, rows, cols, year=None, month=None): # Year/Month are optional for display
        self.rows = rows
        self.cols = cols
        self.year = year 
        self.month = month 
        self.board = [[self.EMPTY_CELL for _ in range(cols)] for _ in range(rows)]
        self.target_cells_coords = [] # List of (r, c) tuples for the 3 target cells
        self.max_target_cells = 3
        self.puzzle_pieces_definitions = PUZZLE_PIECES
        self.placed_pieces_info = {} # {piece_idx: {'coords_on_board': [], 'id_on_board': piece_id_on_board}}
        self.is_solved_state = False
        self.current_status_message = "Select 3 target cells."
        self.fixed_labels = {}
        self._initialize_fixed_labels()
        self.min_piece_size = self._calculate_min_piece_size()

    def _calculate_min_piece_size(self):
        if not self.puzzle_pieces_definitions:
            return float('inf') # Or handle as an error/default
        min_size = float('inf')
        for piece in self.puzzle_pieces_definitions:
            if piece: # Ensure piece is not empty list
                min_size = min(min_size, len(piece))
        return min_size if min_size != float('inf') else 0 # Return 0 if all pieces were empty or no pieces

    def toggle_target_cell(self, r, c):
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            self.current_status_message = "Clicked out of bounds."
            return False
        coord = (r, c)
        if coord in self.target_cells_coords:
            self.target_cells_coords.remove(coord)
            self.board[r][c] = self.EMPTY_CELL
            self.current_status_message = f"Target cell unselected. {len(self.target_cells_coords)}/{self.max_target_cells} selected."
            if len(self.target_cells_coords) < self.max_target_cells:
                 self.current_status_message += " Select more or press 'S' to solve."
            return True
        else:
            if len(self.target_cells_coords) < self.max_target_cells:
                if self.board[r][c] == self.EMPTY_CELL: # Can only select empty cells as targets
                    self.target_cells_coords.append(coord)
                    self.board[r][c] = self.TARGET_CELL
                    self.current_status_message = f"Target cell selected. {len(self.target_cells_coords)}/{self.max_target_cells} selected."
                    if len(self.target_cells_coords) == self.max_target_cells:
                        self.current_status_message += " Press 'S' to solve."
                    return True
                else:
                    self.current_status_message = "Cannot select an occupied cell as target."
                    return False
            else:
                self.current_status_message = f"Cannot select more than {self.max_target_cells} target cells. Press 'S' to solve or unselect one."
                return False

    def get_piece_variations(self, piece_coords): # piece_coords is the original, unmodified piece definition
        variations = []
        # current_piece_normalized is a working copy. It's initially a list copy of piece_coords.
        # In the first pass of the outer loop, it's processed as the original shape.
        # At the end of the first pass, it's reassigned to the raw flipped version of the *original* piece_coords.
        # In the second pass, this raw flipped shape is then processed.
        current_piece_normalized = list(piece_coords)

        for _ in range(2): # Outer loop: Pass 1 for original piece, Pass 2 for its flipped version.
            # --- Part 1: Normalize the current working piece --- 
            # For Pass 1, current_piece_normalized is list(piece_coords).
            # For Pass 2, current_piece_normalized is the raw (unnormalized) flipped version of piece_coords.
            if not current_piece_normalized: 
                if [] not in variations: variations.append([]) # Add empty list for empty piece definition, once.
                # This 'continue' skips Part 2 (rotations) if current_piece_normalized is empty.
                # The flip logic in Part 3 will still execute based on the original piece_coords.
                # If piece_coords itself is empty, Part 3's `if not piece_coords: continue` handles it.
                continue 
            
            # Normalize the current shape (either original or raw flipped).
            min_r = min(p[0] for p in current_piece_normalized)
            min_c = min(p[1] for p in current_piece_normalized)
            current_piece_normalized = sorted([(r - min_r, c - min_c) for r, c in current_piece_normalized])
            # Now, current_piece_normalized holds the standard normalized form of the shape for this pass.

            # --- Part 2: Generate 4 rotations of the normalized shape --- 
            for i in range(4): # 0, 90, 180, 270 degrees rotations.
                # current_piece_normalized is already normalized here (either from Part 1 or from a previous rotation).
                if current_piece_normalized not in variations:
                    variations.append(current_piece_normalized)
                
                # Rotate current_piece_normalized 90 degrees clockwise: (r, c) -> (c, max_r_of_bounding_box - r).
                if not current_piece_normalized: break # 如果初始检查通过，则不应发生。
                
                max_r_val_for_rotation = 0
                if current_piece_normalized: # Max r of the piece *being currently rotated*.
                    max_r_val_for_rotation = max(p[0] for p in current_piece_normalized)
                
                rotated_piece_temp = []
                for r_val, c_val in current_piece_normalized:
                    rotated_piece_temp.append((c_val, max_r_val_for_rotation - r_val))
                
                # Normalize the newly rotated piece and update current_piece_normalized for the next rotation.
                if not rotated_piece_temp: 
                    current_piece_normalized = []
                    continue # If rotation results in empty (unlikely for valid pieces).
                min_r_rot = min(p[0] for p in rotated_piece_temp)
                min_c_rot = min(p[1] for p in rotated_piece_temp)
                current_piece_normalized = sorted([(r - min_r_rot, c - min_c_rot) for r, c in rotated_piece_temp])
            
            # --- Part 3: Prepare for the next pass of the outer loop (if any) --- 
            # Reset current_piece_normalized to be the raw horizontal flip of the *original* piece_coords.
            # This raw flipped piece will be normalized in Part 1 of the next outer loop iteration (Pass 2).
            if not piece_coords: continue # If original piece_coords is empty, cannot calculate flip. Skips to end of outer loop.
            
            max_c_val_for_flip = 0
            # This check `if piece_coords:` is technically redundant due to `if not piece_coords: continue` above, but harmless.
            if piece_coords: # Recalculate max_c from the *original* piece_coords for accurate flipping.
                 max_c_val_for_flip = max(p[1] for p in piece_coords)
            current_piece_normalized = [(r, max_c_val_for_flip - c) for r,c in piece_coords] # Apply flip to original piece_coords.
            # The loop will then re-normalize this raw flipped version at the start of the next iteration (Pass 2).

        return variations

    def can_place_piece(self, piece_variation_coords, r_offset, c_offset):
        for pr, pc in piece_variation_coords:
            board_r, board_c = r_offset + pr, c_offset + pc
            if not (0 <= board_r < self.rows and 0 <= board_c < self.cols):
                return False
            if self.board[board_r][board_c] != self.EMPTY_CELL:
                return False
        return True

    def _place_or_remove_piece_on_board(self, piece_idx, piece_variation_coords, r_offset, c_offset, place=True):
        piece_id_on_board = (piece_idx + 1) if place else self.EMPTY_CELL
        affected_cells = []
        for pr, pc in piece_variation_coords:
            board_r, board_c = r_offset + pr, c_offset + pc
            self.board[board_r][board_c] = piece_id_on_board
            affected_cells.append((board_r, board_c))
        
        if place:
            self.placed_pieces_info[piece_idx] = {
                'coords_on_board': affected_cells, 
                'id_on_board': piece_id_on_board
            }
        elif piece_idx in self.placed_pieces_info:
            del self.placed_pieces_info[piece_idx]

    def solve(self):
        if len(self.target_cells_coords) != self.max_target_cells:
            self.current_status_message = "Please select 3 target cells first."
            return False
        
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != self.TARGET_CELL:
                    self.board[r][c] = self.EMPTY_CELL
        self.placed_pieces_info = {}
        self.is_solved_state = False
        
        self.current_status_message = "Attempting to solve... (this may take a moment)"
        print("\n[SOLVER] Starting solve process...") # Log start
        pygame.event.pump() 

        if self._solve_recursive(0):
            self.is_solved_state = True
            self.current_status_message = "Solved! Press 'R' to restart."
            print("[SOLVER] Solution found!") # Log success
        else:
            self.is_solved_state = False
            self.current_status_message = "Could not find a solution. Try different target cells or press 'R' to restart."
            print("[SOLVER] No solution found.") # Log failure
            for r_idx in range(self.rows):
                for c_idx in range(self.cols):
                    if (r_idx, c_idx) not in self.target_cells_coords:
                        self.board[r_idx][c_idx] = self.EMPTY_CELL
                    else:
                        self.board[r_idx][c_idx] = self.TARGET_CELL
            self.placed_pieces_info = {}
        return self.is_solved_state

    def _is_valid_pruning_candidate(self):
        if self.min_piece_size == 0: # If min_piece_size is 0 (e.g. no pieces, or all pieces are empty)
            return True # No basis for pruning, or trivially true

        visited = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        for r_start in range(self.rows):
            for c_start in range(self.cols):
                if self.board[r_start][c_start] == self.EMPTY_CELL and not visited[r_start][c_start]:
                    # Found an unvisited empty cell, start BFS for this island
                    island_size = 0
                    q = collections.deque([(r_start, c_start)])
                    visited[r_start][c_start] = True
                    island_size += 1

                    while q:
                        r, c = q.popleft()
                        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < self.rows and 0 <= nc < self.cols and \
                               self.board[nr][nc] == self.EMPTY_CELL and not visited[nr][nc]:
                                visited[nr][nc] = True
                                island_size += 1
                                q.append((nr, nc))
                    
                    # After BFS for one island, check its size
                    if island_size < self.min_piece_size:
                        # print(f"[PRUNING] Island at ({r_start},{c_start}) size {island_size} < min_piece_size {self.min_piece_size}")
                        return False # Prune this path
        return True # All islands are large enough

    def _solve_recursive(self, piece_idx_to_place):
        # print(f"[RECURSIVE] Attempting to place piece {piece_idx_to_place + 1}") # Log piece attempt
        if piece_idx_to_place == len(self.puzzle_pieces_definitions):
            print("[RECURSIVE] All pieces placed successfully.") # Log base case success
            return True 

        original_piece_coords = self.puzzle_pieces_definitions[piece_idx_to_place]
        print(f"[RECURSIVE] Trying piece index {piece_idx_to_place} (Piece {piece_idx_to_place + 1})")
        if not original_piece_coords: # Skip empty piece definitions
            print(f"[RECURSIVE] Piece index {piece_idx_to_place} is empty, skipping.")
            return self._solve_recursive(piece_idx_to_place + 1)

        piece_variations = self.get_piece_variations(original_piece_coords)

        for r_offset in range(self.rows):
            for c_offset in range(self.cols):
                for variation_idx, variation_coords in enumerate(piece_variations):
                    if self.can_place_piece(variation_coords, r_offset, c_offset):
                        # print(f"[RECURSIVE] Trying to place piece {piece_idx_to_place + 1}, variation {variation_idx + 1} at ({r_offset}, {c_offset})")
                        self._place_or_remove_piece_on_board(piece_idx_to_place, variation_coords, r_offset, c_offset, place=True)
                        print(f"[RECURSIVE] Placed piece {piece_idx_to_place + 1} (variation {variation_idx + 1}) at ({r_offset},{c_offset}). Cells: {self.placed_pieces_info[piece_idx_to_place]['coords_on_board']}")
                        # pygame.event.pump() # Optional: pump events during recursion for responsiveness
                        if not self._is_valid_pruning_candidate():
                            # print(f"[PRUNING TRIGGERED] After placing piece {piece_idx_to_place + 1}, an island is too small.")
                            self._place_or_remove_piece_on_board(piece_idx_to_place, variation_coords, r_offset, c_offset, place=False)
                            print(f"[RECURSIVE] Pruned & Backtracked: Removed piece {piece_idx_to_place + 1} (variation {variation_idx + 1}) from ({r_offset},{c_offset}) due to small island.")
                            continue # Try next variation or position for the current piece

                        if self._solve_recursive(piece_idx_to_place + 1):
                            return True
                        # print(f"[RECURSIVE] Backtracking: Removing piece {piece_idx_to_place + 1} (variation {variation_idx + 1}) from ({r_offset}, {c_offset})")
                        self._place_or_remove_piece_on_board(piece_idx_to_place, variation_coords, r_offset, c_offset, place=False)
                        print(f"[RECURSIVE] Backtracked: Removed piece {piece_idx_to_place + 1} (variation {variation_idx + 1}) from ({r_offset},{c_offset})") 
        return False

    def reset_game(self):
        self.board = [[self.EMPTY_CELL for _ in range(self.cols)] for _ in range(self.rows)]
        self.target_cells_coords = []
        self.placed_pieces_info = {}
        self.is_solved_state = False
        self.current_status_message = "Select 3 target cells."
        print("Game reset. Select 3 target cells.")

    def is_solved(self): # Redefined for the new puzzle type
        return self.is_solved_state

    def _is_valid_pruning_candidate(self):
        if self.min_piece_size == 0: # If min_piece_size is 0 (e.g. no pieces, or all pieces are empty)
            return True # No basis for pruning, or trivially true

        visited = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        for r_start in range(self.rows):
            for c_start in range(self.cols):
                if self.board[r_start][c_start] == self.EMPTY_CELL and not visited[r_start][c_start]:
                    # Found an unvisited empty cell, start BFS for this island
                    island_size = 0
                    q = collections.deque([(r_start, c_start)])
                    visited[r_start][c_start] = True
                    island_size += 1

                    while q:
                        r, c = q.popleft()
                        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < self.rows and 0 <= nc < self.cols and \
                               self.board[nr][nc] == self.EMPTY_CELL and not visited[nr][nc]:
                                visited[nr][nc] = True
                                island_size += 1
                                q.append((nr, nc))
                    
                    # After BFS for one island, check its size
                    if island_size < self.min_piece_size:
                        # print(f"[PRUNING] Island at ({r_start},{c_start}) size {island_size} < min_piece_size {self.min_piece_size}")
                        return False # Prune this path
        return True # All islands are large enough

    def _initialize_fixed_labels(self):
        # For 9x6 board
        if not (self.rows == 9 and self.cols == 6):
            # This fixed layout is designed for 9x6, do not apply to other sizes
            return

        MONTH_ABBRS = [""] + [calendar.month_abbr[i] for i in range(1, 13)]
        DAY_ABBRS = [calendar.day_abbr[i] for i in range(7)] # Mon to Sun

        # Months (Rows 0-1, 6 cols each)
        # Row 0: Jan - Jun
        for c_idx in range(6):
            self.fixed_labels[(0, c_idx)] = MONTH_ABBRS[c_idx + 1]
        # Row 1: Jul - Dec
        for c_idx in range(6):
            self.fixed_labels[(1, c_idx)] = MONTH_ABBRS[6 + c_idx + 1]

        # Days 1-31 (Rows 2-7)
        day_num = 1
        # Rows 2-6: Days 1-30 (6 days per row)
        for r_idx in range(2, 7): # Rows 2, 3, 4, 5, 6
            for c_idx in range(6):
                if day_num <= 30:
                    self.fixed_labels[(r_idx, c_idx)] = str(day_num)
                    day_num += 1
        
        # Row 7 (index 7): Day 31, then two empty, then Mon, Tue, Wed
        self.fixed_labels[(7, 0)] = str(day_num) # Day 31 (day_num will be 31)
        self.fixed_labels[(7, 1)] = ""           # Empty
        self.fixed_labels[(7, 2)] = ""           # Empty
        self.fixed_labels[(7, 3)] = DAY_ABBRS[0] # Mon
        self.fixed_labels[(7, 4)] = DAY_ABBRS[1] # Tue
        self.fixed_labels[(7, 5)] = DAY_ABBRS[2] # Wed

        # Row 8 (index 8): Two empty, then Thu, Fri, Sat, Sun
        self.fixed_labels[(8, 0)] = ""           # Empty
        self.fixed_labels[(8, 1)] = ""           # Empty
        self.fixed_labels[(8, 2)] = DAY_ABBRS[3] # Thu
        self.fixed_labels[(8, 3)] = DAY_ABBRS[4] # Fri
        self.fixed_labels[(8, 4)] = DAY_ABBRS[5] # Sat
        self.fixed_labels[(8, 5)] = DAY_ABBRS[6] # Sun

def draw_board(screen, puzzle, font, day_font): # day_font might not be needed or can be merged with font
    screen.fill(SCREEN_BACKGROUND_COLOR)
    # Information Area
    info_rect = pygame.Rect(0, 0, screen.get_width(), INFO_HEIGHT)
    pygame.draw.rect(screen, INFO_AREA_BACKGROUND_COLOR, info_rect)

    # Display Year/Month if available (optional feature)
    if puzzle.year is not None and puzzle.month is not None:
        month_names_en = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        month_year_str = f"{month_names_en[puzzle.month]} {puzzle.year}"
        month_year_surface = font.render(month_year_str, True, INFO_AREA_TEXT_COLOR)
        month_year_rect = month_year_surface.get_rect(right=screen.get_width() - 10, centery=INFO_HEIGHT // 2) # Changed to right-align
        screen.blit(month_year_surface, month_year_rect)
    else:
        title_surface = font.render("", True, INFO_AREA_TEXT_COLOR)
        title_rect = title_surface.get_rect(right=screen.get_width() - 10, centery=INFO_HEIGHT // 2) # Changed to right-align
        screen.blit(title_surface, title_rect)

    # Display current status message from puzzle object (multi-line capable)
    max_text_width = screen.get_width() - 20 # Max width for status text area
    status_lines = []
    words = puzzle.current_status_message.split(' ')
    current_line = ""
    if not words: # Handle empty message
        words = [""]

    for word in words:
        test_line = current_line + word + " "
        test_surface = font.render(test_line, True, INFO_AREA_TEXT_COLOR)
        if test_surface.get_width() < max_text_width:
            current_line = test_line
        else:
            status_lines.append(current_line.strip())
            current_line = word + " "
    status_lines.append(current_line.strip()) # Add the last line

    line_height = font.get_linesize()
    total_text_height = len(status_lines) * line_height
    # Start y position for the first line of text, vertically centered if possible
    start_y = (INFO_HEIGHT - total_text_height) // 2 + 5 # +5 for a bit of top padding
    if start_y < 5: start_y = 5 # Ensure it's not too high

    for i, line_text in enumerate(status_lines):
        if not line_text: continue # Skip empty lines that might result from splitting
        line_surface = font.render(line_text, True, INFO_AREA_TEXT_COLOR)
        # Position each line; left-aligned
        line_rect = line_surface.get_rect(left=10, top=start_y + i * line_height)
        screen.blit(line_surface, line_rect)

    # Board rendering starts below the info area
    board_render_offset_y = 0 # No column headers for this puzzle type

    for r in range(puzzle.rows):
        for c in range(puzzle.cols):
            cell_value = puzzle.board[r][c]
            rect_x = c * (TILE_SIZE + MARGIN) + MARGIN
            rect_y = r * (TILE_SIZE + MARGIN) + MARGIN + INFO_HEIGHT + board_render_offset_y
            tile_rect = pygame.Rect(rect_x, rect_y, TILE_SIZE, TILE_SIZE)
            label_text_str = puzzle.fixed_labels.get((r, c), "")

            # 1. Determine base color of the tile
            current_tile_color = None
            if cell_value == puzzle.TARGET_CELL:
                current_tile_color = TARGET_CELL_COLOR
            elif cell_value > 0: # Piece
                piece_idx = cell_value - 1
                current_tile_color = PIECE_COLORS[piece_idx] if 0 <= piece_idx < len(PIECE_COLORS) else TILE_COLOR
            else: # EMPTY_CELL or any other default
                current_tile_color = EMPTY_TILE_COLOR
            
            pygame.draw.rect(screen, current_tile_color, tile_rect)

            # 2. Draw the label text if it exists
            if label_text_str:
                # Using day_font for labels, ensure it's initialized
                # Text color is TEXT_COLOR (black by default)
                label_surface = day_font.render(label_text_str, True, TEXT_COLOR) 
                label_rect = label_surface.get_rect(center=tile_rect.center)
                screen.blit(label_surface, label_rect)
            
            # 3. Draw grid lines
            pygame.draw.rect(screen, TEXT_COLOR, tile_rect, 1) # Border for each cell

def get_game_config():
    # Define board dimensions for the new puzzle
    # 这些尺寸应该适合放置定义的拼图块
    # 7x7 或 8x8 的棋盘可能是一个好的开始，具体取决于拼图块的大小。
    # 让我们试试 7x7 的棋盘，它有49个单元格。3个目标单元格剩下46个单元格。
    # PUZZLE_PIECES 中的单元格总数 (如前一步所定义):
    # P1:6, P2:5, P3:5, P4:8, P5:7, P6:6, P7:10, P8:5, P9:5. 总计 = 57 单元格。
    # 这对于 7x7 的棋盘来说太大了 (46个可用单元格)。
    # 让我们调整棋盘大小，或者假设并非所有拼图块都被使用/拼图块更小。
    # 对于当前的 PUZZLE_PIECES，我们需要一个可以容纳它们的棋盘。
    # 让我们使用一个 9行 x 7列 的棋盘 = 63个单元格。63 - 3个目标 = 60个可用单元格。
    # 这应该足够容纳拼图块的57个单元格了。
    rows = 9 # 固定为日历布局的行数
    cols = 6 # 固定为日历布局的列数
    print(f"Setting up a board of {rows} rows and {cols} columns for the piece puzzle.")

    # 对于此拼图类型，年/月显示不用于棋盘本身。
    # 设置为 None, None，以便信息栏显示通用标题。
    display_year, display_month = None, None 

    print("固定日历布局已禁用年/月显示。")
    return rows, cols, display_year, display_month

def main():
    rows, cols, display_year, display_month = get_game_config()

    pygame.init()
    pygame.font.init()

    try:
        # Initialize for the new puzzle type
        puzzle = CalendarPuzzle(rows, cols, display_year, display_month)
    except Exception as e: # Catch generic exception for broader safety
        print(f"Error initializing puzzle: {e}")
        pygame.quit()
        sys.exit()

    screen_width = puzzle.cols * (TILE_SIZE + MARGIN) + MARGIN
    # board_render_offset_y is 0 in the updated draw_board for this puzzle type
    board_render_offset_y_calc = 0 
    screen_height = puzzle.rows * (TILE_SIZE + MARGIN) + MARGIN + INFO_HEIGHT + board_render_offset_y_calc
    screen = pygame.display.set_mode((screen_width, screen_height))
    
    caption = "Puzzle Game - Fill the Board"
    if display_year and display_month:
        # Optional: include date in caption if desired, though not central to this puzzle type
        # caption = f"Puzzle - {display_month}/{display_year}"
        pass
    pygame.display.set_caption(caption)

    font_size = max(15, TILE_SIZE // 3)
    # day_font is less critical now, but draw_board still accepts it. Can be same as font.
    day_font_size = max(15, TILE_SIZE // 2 - 5) 
    try:
        font = pygame.font.Font(None, font_size)
        day_font = pygame.font.Font(None, day_font_size) # Used for piece IDs if enabled in draw_board
    except pygame.error as e:
        print(f"Font loading error: {e}. Using default fallback.")
        font = pygame.font.Font(None, font_size) # Pygame's default font
        day_font = pygame.font.Font(None, day_font_size)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    print("\n--- Restarting Game ---")
                    # Re-fetch config if it can change, or just reset the existing puzzle instance
                    # rows, cols, display_year, display_month = get_game_config() # If config can change
                    # puzzle = CalendarPuzzle(rows, cols, display_year, display_month) # Re-create
                    puzzle.reset_game() # Use reset_game method

                elif event.key == pygame.K_s:
                    if len(puzzle.target_cells_coords) == puzzle.max_target_cells:
                        print("Attempting to solve puzzle...")
                        puzzle.solve() # This will update puzzle.current_status_message
                    else:
                        puzzle.current_status_message = f"Select {puzzle.max_target_cells} target cells before solving."
                        print(puzzle.current_status_message)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    mouse_x, mouse_y = event.pos
                    # Calculate clicked cell based on board rendering in draw_board
                    # board_area_start_y = INFO_HEIGHT + board_render_offset_y_calc (which is 0)
                    board_area_start_y = INFO_HEIGHT
                    
                    if mouse_y > board_area_start_y: # Click is below info area
                        # Adjust for the board_render_offset_y (0) when calculating clicked_r
                        clicked_c = (mouse_x - MARGIN) // (TILE_SIZE + MARGIN)
                        tile_area_y = mouse_y - board_area_start_y
                        if tile_area_y >= 0:
                            clicked_r = (tile_area_y - MARGIN) // (TILE_SIZE + MARGIN)
                            
                            if 0 <= clicked_r < puzzle.rows and 0 <= clicked_c < puzzle.cols:
                                if not puzzle.is_solved_state: # Allow interaction only if not solved
                                    puzzle.toggle_target_cell(clicked_r, clicked_c)
                                else:
                                    puzzle.current_status_message = "Puzzle solved. Press 'R' to restart."
                            else:
                                puzzle.current_status_message = "Clicked outside board area."
                        else:
                             puzzle.current_status_message = "Clicked above board tiles."
                    else:
                        puzzle.current_status_message = "Clicked in info area."

        draw_board(screen, puzzle, font, day_font)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__": # 主程序入口
    main()