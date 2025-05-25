import pygame
import random
import sys
import calendar
import datetime
import collections

# Pygame Settings
SCREEN_BACKGROUND_COLOR = (173, 216, 230)  # Light blue
TILE_COLOR = (255, 255, 255)  # White
EMPTY_TILE_COLOR = (150, 200, 220)  # Blue
PLACEHOLDER_TILE_COLOR = (211, 211, 211)  # Gray
TEXT_COLOR = (0, 0, 0)  # Black
INFO_AREA_BACKGROUND_COLOR = (200, 200, 200)  # Gray
INFO_AREA_TEXT_COLOR = (0, 0, 0)  # Black
LABEL_TEXT_COLOR = (50, 50, 50)  # Dark gray

# Board Configuration
BOARD_ROWS = 8
BOARD_COLS = 7

# Restricted Areas
RESTRICTED_CELLS = [
    (0, 6), (1, 6),  # First and second rows, last column
    (7, 0), (7, 1), (7, 2), (7, 3)  # Last row, first four columns
]

# Cell Labels
CELL_LABELS = {
    # First row: Months
    (0, 0): "Jan", (0, 1): "Feb", (0, 2): "Mar", (0, 3): "Apr", (0, 4): "May", (0, 5): "Jun", (0, 6): "",
    # Second row: Months
    (1, 0): "Jul", (1, 1): "Aug", (1, 2): "Sep", (1, 3): "Oct", (1, 4): "Nov", (1, 5): "Dec", (1, 6): "",
    # Third row: Dates
    (2, 0): "1", (2, 1): "2", (2, 2): "3", (2, 3): "4", (2, 4): "5", (2, 5): "6", (2, 6): "7",
    # Fourth row: Dates
    (3, 0): "8", (3, 1): "9", (3, 2): "10", (3, 3): "11", (3, 4): "12", (3, 5): "13", (3, 6): "14",
    # Fifth row: Dates
    (4, 0): "15", (4, 1): "16", (4, 2): "17", (4, 3): "18", (4, 4): "19", (4, 5): "20", (4, 6): "21",
    # Sixth row: Dates
    (5, 0): "22", (5, 1): "23", (5, 2): "24", (5, 3): "25", (5, 4): "26", (5, 5): "27", (5, 6): "28",
    # Seventh row: Dates and Weekdays
    (6, 0): "29", (6, 1): "30", (6, 2): "31", (6, 3): "Sun", (6, 4): "Mon", (6, 5): "Tues", (6, 6): "Wed",
    # Eighth row: Weekdays
    (7, 0): "", (7, 1): "", (7, 2): "", (7, 3): "", (7, 4): "Thur", (7, 5): "Fri", (7, 6): "Sat",
}

# Puzzle Pieces
PUZZLE_PIECES = [
    [(0,0), (0,1), (0,2), (1,2), (2,2)], # L-shape
    [(0,0), (0,1), (0,2), (1,1), (2,1)], # T-shape
    [(0,0), (0,1), (1,1), (2,1), (2,2)], # Z-shape
    [(0,0), (0,1), (0,2), (1,0), (1,2)], # U-shape
    [(0,0), (0,1), (0,2), (1,0), (1,1)], # L-shape
    [(0,0), (0,1), (0,2), (1,2), (1,3)], # Long L-shape
    [(0,0), (0,1), (0,2), (0,3), (1,0)], # Long bar
    [(0,0), (1,0), (2,0), (3,0)], # Vertical bar
    [(0,0), (1,0), (2,0), (2,1)], # Small L-shape
    [(0,0), (1,0), (1,1), (2,1)] # Z-shape
]

# Colors
BASE_PIECE_COLORS = [
    (255, 99, 71),    # Tomato Red
    (50, 205, 50),    # Lime Green
    (30, 144, 255),   # Dodger Blue
    (255, 215, 0),    # Gold
    (147, 112, 219),  # Medium Purple
    (255, 140, 0),    # Dark Orange
    (0, 191, 255),    # Deep Sky Blue
    (255, 20, 147),   # Deep Pink
    (60, 179, 113),   # Medium Sea Green
    (106, 90, 205)    # Slate Blue
]

PIECE_COLORS = [BASE_PIECE_COLORS[i % len(BASE_PIECE_COLORS)] for i in range(len(PUZZLE_PIECES))]
TARGET_CELL_COLOR = (255, 0, 0)  # Red
SELECTED_PIECE_BORDER_COLOR = (0,255,0)  # Green
RESTRICTED_CELL_COLOR = (128, 128, 128)  # Gray

# UI Dimensions
TILE_SIZE = 70
MARGIN = 5
INFO_HEIGHT = 100

class CalendarPuzzle:
    """
    Main class for the calendar puzzle game.
    Handles board state, piece placement, target cell selection, and solving logic.
    """
    # Constants for board cell states
    EMPTY_CELL = 0
    TARGET_CELL = -1  # User-selected cell, not to be covered by pieces
    RESTRICTED_CELL = -2  # Restricted area, cannot place pieces
    # Piece IDs will be 1 through len(PUZZLE_PIECES)

    # Cell type constants
    CELL_TYPE_MONTH = 0
    CELL_TYPE_DAY = 1
    CELL_TYPE_WEEKDAY = 2

    def __init__(self):
        """
        Initialize the puzzle board, restricted areas, and game state.
        """
        self.rows = BOARD_ROWS
        self.cols = BOARD_COLS
        self.board = [[self.EMPTY_CELL for _ in range(self.cols)] for _ in range(self.rows)]
        # Initialize restricted areas
        for r, c in RESTRICTED_CELLS:
            self.board[r][c] = self.RESTRICTED_CELL
        self.target_cells_coords = []
        self.target_cells_types = []  # Track the type of each selected cell
        self.max_target_cells = 3
        self.puzzle_pieces_definitions = PUZZLE_PIECES
        self.placed_pieces_info = {}
        self.is_solved_state = False
        self.current_status_message = "Select 1 month, 1 day, and 1 weekday"
        self.min_piece_size = self._calculate_min_piece_size()

    def _calculate_min_piece_size(self):
        """
        Calculate the minimum size among all puzzle pieces.
        Used for pruning in the solver.
        """
        if not self.puzzle_pieces_definitions:
            return float('inf')  # Or handle as an error/default
        min_size = float('inf')
        for piece in self.puzzle_pieces_definitions:
            if piece:  # Ensure piece is not empty list
                min_size = min(min_size, len(piece))
        return min_size if min_size != float('inf') else 0  # Return 0 if all pieces were empty or no pieces

    def can_place_piece(self, piece_variation_coords, r_offset, c_offset):
        """
        Check if a piece (in a specific variation) can be placed at the given offset.
        Returns True if all cells are empty and not restricted.
        """
        for pr, pc in piece_variation_coords:
            board_r, board_c = r_offset + pr, c_offset + pc
            if not (0 <= board_r < self.rows and 0 <= board_c < self.cols):
                return False
            # Check if cell is restricted or already occupied
            if self.board[board_r][board_c] != self.EMPTY_CELL:
                return False
        return True

    def _get_cell_type(self, r, c):
        """
        Determine the type of cell at the given coordinates.
        Returns CELL_TYPE_MONTH, CELL_TYPE_DAY, or CELL_TYPE_WEEKDAY.
        """
        if r < 2:  # First two rows are months
            return self.CELL_TYPE_MONTH
        elif r < 6:  # Rows 2-5 are days
            return self.CELL_TYPE_DAY
        elif r == 6:  # Row 6 contains both days and weekdays
            if c < 3:  # First three columns are days
                return self.CELL_TYPE_DAY
            else:  # Last four columns are weekdays
                return self.CELL_TYPE_WEEKDAY
        else:  # Row 7 contains weekdays
            if c >= 4:  # Last three columns are weekdays
                return self.CELL_TYPE_WEEKDAY
            return None  # First four columns are restricted areas

    def toggle_target_cell(self, r, c):
        """
        Select or unselect a target cell. Target cells must not be restricted or already occupied.
        Must select one of each type (month, day, weekday).
        """
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            self.current_status_message = "Clicked out of bounds"
            return False
        if self.board[r][c] == self.RESTRICTED_CELL:
            self.current_status_message = "Cannot select restricted area as target"
            return False
            
        coord = (r, c)
        cell_type = self._get_cell_type(r, c)
        
        if coord in self.target_cells_coords:
            # Unselect the cell
            idx = self.target_cells_coords.index(coord)
            self.target_cells_coords.pop(idx)
            self.target_cells_types.pop(idx)
            self.board[r][c] = self.EMPTY_CELL
            
            remaining_types = set(self.target_cells_types)
            type_names = []
            if self.CELL_TYPE_MONTH not in remaining_types:
                type_names.append("month")
            if self.CELL_TYPE_DAY not in remaining_types:
                type_names.append("day")
            if self.CELL_TYPE_WEEKDAY not in remaining_types:
                type_names.append("weekday")
                
            self.current_status_message = f"Cell unselected. Need to select: {', '.join(type_names)}"
            return True
        else:
            # Check if we already have this type of cell selected
            if cell_type in self.target_cells_types:
                self.current_status_message = f"Cannot select another {['month', 'day', 'weekday'][cell_type]}"
                return False
                
            if len(self.target_cells_coords) < self.max_target_cells:
                if self.board[r][c] == self.EMPTY_CELL:
                    self.target_cells_coords.append(coord)
                    self.target_cells_types.append(cell_type)
                    self.board[r][c] = self.TARGET_CELL
                    
                    remaining_types = set(range(3)) - set(self.target_cells_types)
                    type_names = []
                    if self.CELL_TYPE_MONTH in remaining_types:
                        type_names.append("month")
                    if self.CELL_TYPE_DAY in remaining_types:
                        type_names.append("day")
                    if self.CELL_TYPE_WEEKDAY in remaining_types:
                        type_names.append("weekday")
                        
                    self.current_status_message = f"Selected {['month', 'day', 'weekday'][cell_type]}. Need to select: {', '.join(type_names)}"
                    if len(self.target_cells_coords) == self.max_target_cells:
                        self.current_status_message += ". Press 'S' to solve"
                    return True
                else:
                    self.current_status_message = "Cannot select an occupied cell as target"
                    return False
            else:
                self.current_status_message = f"Cannot select more than {self.max_target_cells} target cells. Press 'S' to solve or unselect one"
                return False

    def get_piece_variations(self, piece_coords):
        """
        Generate all unique variations (rotations and horizontal flips) of a puzzle piece.
        Returns a list of normalized coordinate lists.
        """
        variations = []
        current_piece_normalized = list(piece_coords)

        for _ in range(2):  # Outer loop: Pass 1 for original piece, Pass 2 for its flipped version
            if not current_piece_normalized: 
                if [] not in variations: variations.append([])  # Add empty list for empty piece definition, once
                continue 
            
            # Normalize the current shape
            min_r = min(p[0] for p in current_piece_normalized)
            min_c = min(p[1] for p in current_piece_normalized)
            current_piece_normalized = sorted([(r - min_r, c - min_c) for r, c in current_piece_normalized])

            # Generate 4 rotations of the normalized shape
            for i in range(4):  # 0, 90, 180, 270 degrees rotations
                if current_piece_normalized not in variations:
                    variations.append(current_piece_normalized)
                
                # Rotate current_piece_normalized 90 degrees clockwise
                if not current_piece_normalized: break
                
                max_r_val_for_rotation = 0
                if current_piece_normalized:
                    max_r_val_for_rotation = max(p[0] for p in current_piece_normalized)
                
                rotated_piece_temp = []
                for r_val, c_val in current_piece_normalized:
                    rotated_piece_temp.append((c_val, max_r_val_for_rotation - r_val))
                
                # Normalize the newly rotated piece
                if not rotated_piece_temp: 
                    current_piece_normalized = []
                    continue
                min_r_rot = min(p[0] for p in rotated_piece_temp)
                min_c_rot = min(p[1] for p in rotated_piece_temp)
                current_piece_normalized = sorted([(r - min_r_rot, c - min_c_rot) for r, c in rotated_piece_temp])
            
            # Prepare for the next pass of the outer loop
            if not piece_coords: continue
            
            max_c_val_for_flip = 0
            if piece_coords:
                 max_c_val_for_flip = max(p[1] for p in piece_coords)
            current_piece_normalized = [(r, max_c_val_for_flip - c) for r,c in piece_coords]

        return variations

    def _place_or_remove_piece_on_board(self, piece_idx, piece_variation_coords, r_offset, c_offset, place=True):
        """
        Place or remove a piece on the board at the specified offset.
        Updates the board state and placed pieces info.
        """
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
        """
        Attempt to solve the puzzle using recursive backtracking.
        Resets the board (except restricted and target cells) before solving.
        """
        if len(self.target_cells_coords) != self.max_target_cells:
            self.current_status_message = "Please select 3 target cells first."
            return False
        
        # Reset board while keeping restricted areas unchanged
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) not in self.target_cells_coords and (r, c) not in RESTRICTED_CELLS:
                    self.board[r][c] = self.EMPTY_CELL
        self.placed_pieces_info = {}
        self.is_solved_state = False
        
        self.current_status_message = "Attempting to solve... (this may take a moment)"
        print("\n[SOLVER] Starting solve process...")
        pygame.event.pump() 

        if self._solve_recursive(0):
            self.is_solved_state = True
            self.current_status_message = "Solved! Press 'R' to restart."
            print("[SOLVER] Solution found!")
        else:
            self.is_solved_state = False
            self.current_status_message = "Could not find a solution. Try different target cells or press 'R' to restart."
            print("[SOLVER] No solution found.")
            # Reset board while keeping restricted areas and target cells unchanged
            for r in range(self.rows):
                for c in range(self.cols):
                    if (r, c) in self.target_cells_coords:
                        self.board[r][c] = self.TARGET_CELL
                    elif (r, c) in RESTRICTED_CELLS:
                        self.board[r][c] = self.RESTRICTED_CELL
                    else:
                        self.board[r][c] = self.EMPTY_CELL
            self.placed_pieces_info = {}
        return self.is_solved_state

    def _is_valid_pruning_candidate(self):
        """
        Pruning function for the solver.
        Checks if any contiguous empty region is smaller than the smallest piece,
        which would make the current board state unsolvable.
        """
        if self.min_piece_size == 0:  # If min_piece_size is 0 (e.g. no pieces, or all pieces are empty)
            return True  # No basis for pruning, or trivially true

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
                        return False  # Prune this path
        return True  # All islands are large enough

    def _solve_recursive(self, piece_idx_to_place):
        """
        Recursive backtracking solver.
        Tries to place each piece in all possible positions and orientations.
        Returns True if a solution is found, otherwise False.
        """
        if piece_idx_to_place == len(self.puzzle_pieces_definitions):
            print("[RECURSIVE] All pieces placed successfully.")
            return True 

        original_piece_coords = self.puzzle_pieces_definitions[piece_idx_to_place]
        print(f"[RECURSIVE] Trying piece index {piece_idx_to_place} (Piece {piece_idx_to_place + 1})")
        if not original_piece_coords:  # Skip empty piece definitions
            print(f"[RECURSIVE] Piece index {piece_idx_to_place} is empty, skipping.")
            return self._solve_recursive(piece_idx_to_place + 1)

        piece_variations = self.get_piece_variations(original_piece_coords)

        for r_offset in range(self.rows):
            for c_offset in range(self.cols):
                for variation_idx, variation_coords in enumerate(piece_variations):
                    if self.can_place_piece(variation_coords, r_offset, c_offset):
                        self._place_or_remove_piece_on_board(piece_idx_to_place, variation_coords, r_offset, c_offset, place=True)
                        print(f"[RECURSIVE] Placed piece {piece_idx_to_place + 1} (variation {variation_idx + 1}) at ({r_offset},{c_offset}). Cells: {self.placed_pieces_info[piece_idx_to_place]['coords_on_board']}")
                        
                        if not self._is_valid_pruning_candidate():
                            self._place_or_remove_piece_on_board(piece_idx_to_place, variation_coords, r_offset, c_offset, place=False)
                            print(f"[RECURSIVE] Pruned & Backtracked: Removed piece {piece_idx_to_place + 1} (variation {variation_idx + 1}) from ({r_offset},{c_offset}) due to small island.")
                            continue

                        if self._solve_recursive(piece_idx_to_place + 1):
                            return True
                        self._place_or_remove_piece_on_board(piece_idx_to_place, variation_coords, r_offset, c_offset, place=False)
                        print(f"[RECURSIVE] Backtracked: Removed piece {piece_idx_to_place + 1} (variation {variation_idx + 1}) from ({r_offset},{c_offset})") 
        return False

    def reset_game(self):
        """
        Reset the game to the initial state, keeping restricted areas unchanged.
        """
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) in RESTRICTED_CELLS:
                    self.board[r][c] = self.RESTRICTED_CELL
                else:
                    self.board[r][c] = self.EMPTY_CELL
        self.target_cells_coords = []
        self.target_cells_types = []
        self.placed_pieces_info = {}
        self.is_solved_state = False
        self.current_status_message = "Select 1 month, 1 day, and 1 weekday"
        print("Game reset. Select 1 month, 1 day, and 1 weekday.")

    def is_solved(self):
        """
        Return whether the puzzle is currently solved.
        """
        return self.is_solved_state

def draw_board(screen, puzzle, font, label_font):
    """
    Render the puzzle board, including tiles, labels, and status messages.
    """
    screen.fill(SCREEN_BACKGROUND_COLOR)
    # Information Area
    info_rect = pygame.Rect(0, 0, screen.get_width(), INFO_HEIGHT)
    pygame.draw.rect(screen, INFO_AREA_BACKGROUND_COLOR, info_rect)

    # Display status message
    max_text_width = screen.get_width() - 20
    status_lines = []
    words = puzzle.current_status_message.split(' ')
    current_line = ""
    if not words:
        words = [""]

    for word in words:
        test_line = current_line + word + " "
        test_surface = font.render(test_line, True, INFO_AREA_TEXT_COLOR)
        if test_surface.get_width() < max_text_width:
            current_line = test_line
        else:
            status_lines.append(current_line.strip())
            current_line = word + " "
    status_lines.append(current_line.strip())

    line_height = font.get_linesize()
    total_text_height = len(status_lines) * line_height
    start_y = (INFO_HEIGHT - total_text_height) // 2 + 5
    if start_y < 5: start_y = 5

    for i, line_text in enumerate(status_lines):
        if not line_text: continue
        line_surface = font.render(line_text, True, INFO_AREA_TEXT_COLOR)
        line_rect = line_surface.get_rect(left=10, top=start_y + i * line_height)
        screen.blit(line_surface, line_rect)

    # Board rendering
    board_render_offset_y = 0

    for r in range(puzzle.rows):
        for c in range(puzzle.cols):
            cell_value = puzzle.board[r][c]
            rect_x = c * (TILE_SIZE + MARGIN) + MARGIN
            rect_y = r * (TILE_SIZE + MARGIN) + MARGIN + INFO_HEIGHT + board_render_offset_y
            tile_rect = pygame.Rect(rect_x, rect_y, TILE_SIZE, TILE_SIZE)

            # Determine cell color
            current_tile_color = None
            if cell_value == puzzle.TARGET_CELL:
                current_tile_color = TARGET_CELL_COLOR
            elif cell_value == puzzle.RESTRICTED_CELL:
                current_tile_color = RESTRICTED_CELL_COLOR
            elif cell_value > 0: # Piece
                piece_idx = cell_value - 1
                current_tile_color = PIECE_COLORS[piece_idx] if 0 <= piece_idx < len(PIECE_COLORS) else TILE_COLOR
            else: # EMPTY_CELL
                current_tile_color = EMPTY_TILE_COLOR
            
            pygame.draw.rect(screen, current_tile_color, tile_rect)
            pygame.draw.rect(screen, TEXT_COLOR, tile_rect, 1) # Border for each cell

            # Add custom text if available
            if (r, c) in CELL_LABELS and CELL_LABELS[(r, c)]:  # Only display non-empty text
                label_text = CELL_LABELS[(r, c)]
                label_surface = label_font.render(label_text, True, LABEL_TEXT_COLOR)
                label_rect = label_surface.get_rect(center=tile_rect.center)
                screen.blit(label_surface, label_rect)

def get_game_config():
    """
    Return the board configuration and current date information.
    """
    today = datetime.datetime.now()
    current_month = today.month
    current_day = today.day
    current_weekday = today.weekday()  # 0-6, where 0 is Monday
    
    # Convert weekday to our format (0-6, where 0 is Sunday)
    # Our board shows: Sun(0), Mon(1), Tues(2), Wed(3), Thur(4), Fri(5), Sat(6)
    weekday_map = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 0}  # Map Monday(0) to 1, etc.
    current_weekday = weekday_map[current_weekday]
    
    return BOARD_ROWS, BOARD_COLS, current_month, current_day, current_weekday


def main():
    """
    Main entry point for the puzzle game.
    Handles Pygame initialization, event loop, and rendering.
    """
    rows, cols, current_month, current_day, current_weekday = get_game_config()

    pygame.init()
    pygame.font.init()

    try:
        puzzle = CalendarPuzzle()
        
        # Auto-select current date cells
        # Month cell (0-based month index)
        month_row = (current_month - 1) // 6
        month_col = (current_month - 1) % 6
        puzzle.toggle_target_cell(month_row, month_col)
        
        # Day cell
        day_row = (current_day - 1) // 7 + 2  # Days start from row 2
        day_col = (current_day - 1) % 7
        puzzle.toggle_target_cell(day_row, day_col)
        
        # Weekday cell
        # Weekdays are in rows 6 and 7, with specific positions:
        # Row 6: Sun(3), Mon(4), Tues(5), Wed(6)
        # Row 7: Thur(4), Fri(5), Sat(6)
        if current_weekday <= 3:  # Sun, Mon, Tues, Wed
            weekday_row = 6
            weekday_col = current_weekday + 3
        else:  # Thur, Fri, Sat
            weekday_row = 7
            weekday_col = current_weekday
        
        puzzle.toggle_target_cell(weekday_row, weekday_col)
        
    except Exception as e:
        print(f"Error initializing puzzle: {e}")
        pygame.quit()
        sys.exit()

    screen_width = puzzle.cols * (TILE_SIZE + MARGIN) + MARGIN
    board_render_offset_y_calc = 0 
    screen_height = puzzle.rows * (TILE_SIZE + MARGIN) + MARGIN + INFO_HEIGHT + board_render_offset_y_calc
    screen = pygame.display.set_mode((screen_width, screen_height))
    
    caption = "Puzzle Game"
    pygame.display.set_caption(caption)

    # Set up fonts for main text and cell labels
    font_size = 24
    label_font_size = 28
    font = pygame.font.Font(None, font_size)
    label_font = pygame.font.Font(None, label_font_size)

    running = True
    while running:
        for event in pygame.event.get():
            # Handle window close event
            if event.type == pygame.QUIT:
                running = False
            
            # Handle keyboard events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    print("\n--- Restart Game ---")
                    puzzle.reset_game()
                    # Re-select current date cells after reset
                    month_row = (current_month - 1) // 6
                    month_col = (current_month - 1) % 6
                    puzzle.toggle_target_cell(month_row, month_col)
                    
                    day_row = (current_day - 1) // 7 + 2
                    day_col = (current_day - 1) % 7
                    puzzle.toggle_target_cell(day_row, day_col)
                    
                    # Weekday cell
                    if current_weekday <= 3:  # Sun, Mon, Tues, Wed
                        weekday_row = 6
                        weekday_col = current_weekday + 3
                    else:  # Thur, Fri, Sat
                        weekday_row = 7
                        weekday_col = current_weekday
                    
                    puzzle.toggle_target_cell(weekday_row, weekday_col)

                elif event.key == pygame.K_s:
                    if len(puzzle.target_cells_coords) == puzzle.max_target_cells:
                        print("Attempting to solve puzzle...")
                        puzzle.solve()
                    else:
                        puzzle.current_status_message = f"Please select {puzzle.max_target_cells} target cells"
                        print(puzzle.current_status_message)
            
            # Handle mouse click events
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    mouse_x, mouse_y = event.pos
                    board_area_start_y = INFO_HEIGHT
                    
                    if mouse_y > board_area_start_y:
                        clicked_c = (mouse_x - MARGIN) // (TILE_SIZE + MARGIN)
                        tile_area_y = mouse_y - board_area_start_y
                        if tile_area_y >= 0:
                            clicked_r = (tile_area_y - MARGIN) // (TILE_SIZE + MARGIN)
                            
                            if 0 <= clicked_r < puzzle.rows and 0 <= clicked_c < puzzle.cols:
                                if not puzzle.is_solved_state:
                                    puzzle.toggle_target_cell(clicked_r, clicked_c)
                                else:
                                    puzzle.current_status_message = "Puzzle solved. Press 'R' to restart"
                            else:
                                puzzle.current_status_message = "Clicked outside board area"
                        else:
                             puzzle.current_status_message = "Clicked above board tiles"
                    else:
                        puzzle.current_status_message = "Clicked in info area"

        draw_board(screen, puzzle, font, label_font)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()