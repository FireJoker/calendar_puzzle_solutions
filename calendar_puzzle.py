import pygame
import random
import sys
import calendar
import datetime
import collections


# Board Configuration
BOARD_ROWS = 8
BOARD_COLS = 7
TILE_SIZE = 70
MARGIN = 5
INFO_HEIGHT = 100

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
    (160, 180, 200),    # Soft blue
    (180, 200, 160),    # Soft green
    (200, 180, 160),    # Soft orange
    (180, 160, 200),    # Soft purple
    (160, 200, 180),    # Soft teal
    (200, 160, 180),    # Soft pink
    (180, 180, 160),    # Soft yellow
    (160, 160, 200),    # Soft indigo
    (200, 160, 160),    # Soft red
    (160, 200, 200)     # Soft cyan
]

SCREEN_BACKGROUND_COLOR = (173, 216, 230)  # Light blue
TILE_COLOR = (255, 255, 255)  # White
EMPTY_TILE_COLOR = (150, 200, 220)  # Blue
PLACEHOLDER_TILE_COLOR = (211, 211, 211)  # Gray
TEXT_COLOR = (0, 0, 0)  # Black
INFO_AREA_BACKGROUND_COLOR = (200, 200, 200)  # Gray
INFO_AREA_TEXT_COLOR = (0, 0, 0)  # Black
LABEL_TEXT_COLOR = (50, 50, 50)  # Dark gray

PIECE_COLORS = [BASE_PIECE_COLORS[i % len(BASE_PIECE_COLORS)] for i in range(len(PUZZLE_PIECES))]
TARGET_CELL_COLOR = (128, 128, 128)  # Gray
SELECTED_PIECE_BORDER_COLOR = (0, 255, 0)  # Green
RESTRICTED_CELL_COLOR = SCREEN_BACKGROUND_COLOR  # Same as background color

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

    # Maximum number of solutions to find
    MAX_SOLUTIONS = 10

    def __init__(self):
        """
        Initialize the puzzle board and game state.
        """
        self.rows = BOARD_ROWS
        self.cols = BOARD_COLS
        self.board = [[self.EMPTY_CELL for _ in range(self.cols)] for _ in range(self.rows)]
        self._initialize_restricted_areas()
        self.target_cells_coords = []
        self.target_cells_types = []
        self.max_target_cells = 3
        self.puzzle_pieces_definitions = PUZZLE_PIECES
        self.placed_pieces_info = {}
        self.is_solved_state = False
        self.current_status_message = "Select: month, day, weekday"
        self.min_piece_size = self._calculate_min_piece_size()
        self.solutions = []
        self.current_solution_index = -1

    def _initialize_restricted_areas(self):
        """Initialize restricted areas on the board."""
        for r, c in RESTRICTED_CELLS:
            self.board[r][c] = self.RESTRICTED_CELL

    def _calculate_min_piece_size(self):
        """
        Calculate the minimum size among all puzzle pieces.
        """
        if not self.puzzle_pieces_definitions:
            return float('inf')
        return min(len(piece) for piece in self.puzzle_pieces_definitions if piece)

    def _get_cell_type(self, r, c):
        """
        Determine the type of cell at the given coordinates.
        """
        if r < 2:  # First two rows are months
            return self.CELL_TYPE_MONTH
        elif r < 6:  # Rows 2-5 are days
            return self.CELL_TYPE_DAY
        elif r == 6:  # Row 6 contains both days and weekdays
            return self.CELL_TYPE_DAY if c < 3 else self.CELL_TYPE_WEEKDAY
        else:  # Row 7 contains weekdays
            return self.CELL_TYPE_WEEKDAY if c >= 4 else None

    def toggle_target_cell(self, r, c):
        """
        Select a target cell.
        Returns True if the operation was successful.
        """
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return False
        if self.board[r][c] == self.RESTRICTED_CELL:
            return False
            
        coord = (r, c)
        cell_type = self._get_cell_type(r, c)
                   
        # Check if we already have this type of cell selected
        if cell_type in self.target_cells_types:
            # Replace existing cell of same type
            idx = self.target_cells_types.index(cell_type)
            old_coord = self.target_cells_coords[idx]
            self.board[old_coord[0]][old_coord[1]] = self.EMPTY_CELL
            self.target_cells_coords.pop(idx)
            self.target_cells_types.pop(idx)
            
        if len(self.target_cells_coords) >= self.max_target_cells:
            self.current_status_message = "Press 'S' to solve"
            return False
            
        if self.board[r][c] != self.EMPTY_CELL:
            return False
            
        # Select the cell
        self.target_cells_coords.append(coord)
        self.target_cells_types.append(cell_type)
        self.board[r][c] = self.TARGET_CELL
        
        if len(self.target_cells_coords) == self.max_target_cells:
            self.current_status_message = "Press 'S' to solve"
        else:
            # Get remaining types to select
            remaining_types = set(range(3)) - set(self.target_cells_types)
            type_names = ['month' if self.CELL_TYPE_MONTH in remaining_types else '',
                         'day' if self.CELL_TYPE_DAY in remaining_types else '',
                         'weekday' if self.CELL_TYPE_WEEKDAY in remaining_types else '']
            type_names = [t for t in type_names if t]  # Remove empty strings
            
            self.current_status_message = f"Select: {', '.join(type_names)}"
        return True

    def get_piece_variations(self, piece_coords):
        """
        Generate all unique variations of a puzzle piece.
        """
        variations = []
        current_piece_normalized = list(piece_coords)

        for _ in range(2):  # Original and flipped versions
            if not current_piece_normalized:
                if [] not in variations:
                    variations.append([])
                continue

            # Normalize the current shape
            min_r = min(p[0] for p in current_piece_normalized)
            min_c = min(p[1] for p in current_piece_normalized)
            current_piece_normalized = sorted([(r - min_r, c - min_c) for r, c in current_piece_normalized])

            # Generate rotations
            for _ in range(4):
                if current_piece_normalized not in variations:
                    variations.append(current_piece_normalized)

                if not current_piece_normalized:
                    break

                max_r = max(p[0] for p in current_piece_normalized)
                rotated_piece = [(c, max_r - r) for r, c in current_piece_normalized]
                min_r = min(p[0] for p in rotated_piece)
                min_c = min(p[1] for p in rotated_piece)
                current_piece_normalized = sorted([(r - min_r, c - min_c) for r, c in rotated_piece])

            # Prepare for flip
            if not piece_coords:
                continue
            max_c = max(p[1] for p in piece_coords)
            current_piece_normalized = [(r, max_c - c) for r, c in piece_coords]

        return variations

    def can_place_piece(self, piece_variation_coords, r_offset, c_offset):
        """Check if a piece can be placed at the given position."""
        for pr, pc in piece_variation_coords:
            board_r, board_c = r_offset + pr, c_offset + pc
            if not (0 <= board_r < self.rows and 0 <= board_c < self.cols):
                return False
            if self.board[board_r][board_c] != self.EMPTY_CELL:
                return False
        return True

    def _place_or_remove_piece_on_board(self, piece_idx, piece_variation_coords, r_offset, c_offset, place=True):
        """
        Place or remove a piece on the board.
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

    def _is_valid_pruning_candidate(self):
        """Check if the current board state is valid for pruning."""
        if self.min_piece_size == 0:
            return True

        visited = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        for r_start in range(self.rows):
            for c_start in range(self.cols):
                if self.board[r_start][c_start] == self.EMPTY_CELL and not visited[r_start][c_start]:
                    island_size = 0
                    q = collections.deque([(r_start, c_start)])
                    visited[r_start][c_start] = True
                    island_size += 1

                    while q:
                        r, c = q.popleft()
                        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                            nr, nc = r + dr, c + dc
                            if (0 <= nr < self.rows and 0 <= nc < self.cols and
                                self.board[nr][nc] == self.EMPTY_CELL and not visited[nr][nc]):
                                visited[nr][nc] = True
                                island_size += 1
                                q.append((nr, nc))

                    if island_size < self.min_piece_size:
                        return False
        return True

    def _solve_recursive(self, piece_idx_to_place):
        """Recursive backtracking solver."""
        if piece_idx_to_place == len(self.puzzle_pieces_definitions):
            self.solutions.append(self.placed_pieces_info.copy())
            return len(self.solutions) >= self.MAX_SOLUTIONS

        original_piece_coords = self.puzzle_pieces_definitions[piece_idx_to_place]
        if not original_piece_coords:
            return self._solve_recursive(piece_idx_to_place + 1)

        piece_variations = self.get_piece_variations(original_piece_coords)
        found_solution = False

        for r_offset in range(self.rows):
            for c_offset in range(self.cols):
                for variation_coords in piece_variations:
                    if self.can_place_piece(variation_coords, r_offset, c_offset):
                        self._place_or_remove_piece_on_board(piece_idx_to_place, variation_coords, r_offset, c_offset, True)
                        
                        if self._is_valid_pruning_candidate():
                            if self._solve_recursive(piece_idx_to_place + 1):
                                found_solution = True
                                if len(self.solutions) >= self.MAX_SOLUTIONS:
                                    return True
                        
                        self._place_or_remove_piece_on_board(piece_idx_to_place, variation_coords, r_offset, c_offset, False)

        return found_solution

    def solve(self):
        """
        Attempt to solve the puzzle.
        """
        if len(self.target_cells_coords) != self.max_target_cells:
            self.current_status_message = "Select: month, day, weekday"
            return False

        # Reset board while keeping restricted and target cells
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) not in self.target_cells_coords and (r, c) not in RESTRICTED_CELLS:
                    self.board[r][c] = self.EMPTY_CELL

        self.placed_pieces_info = {}
        self.is_solved_state = False
        self.solutions = []
        self.current_solution_index = -1

        self.current_status_message = "Attempting to solve... (this may take a moment)"
        pygame.event.pump()

        if self._solve_recursive(0):
            self.is_solved_state = True
            if self.solutions:
                self.current_solution_index = 0
                self._apply_solution(self.solutions[0])
                self.current_status_message = f"Solution 1/{len(self.solutions)}. \nPress 'N' for next solution, \n'P' for previous solution, \n'R' to restart."
            else:
                self.current_status_message = "No solution found. \nTry different target cells or press 'R' to restart."
        else:
            self.is_solved_state = False
            self.current_status_message = "No solution found. \nTry different target cells or press 'R' to restart."
            self._reset_board()

        return self.is_solved_state

    def _reset_board(self):
        """Reset the board while keeping restricted and target cells."""
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) in self.target_cells_coords:
                    self.board[r][c] = self.TARGET_CELL
                elif (r, c) in RESTRICTED_CELLS:
                    self.board[r][c] = self.RESTRICTED_CELL
                else:
                    self.board[r][c] = self.EMPTY_CELL
        self.placed_pieces_info = {}

    def _apply_solution(self, solution):
        """
        Apply a solution to the board.
        """
        self._reset_board()
        self.placed_pieces_info = solution.copy()
        for piece_idx, piece_info in solution.items():
            for r, c in piece_info['coords_on_board']:
                self.board[r][c] = piece_info['id_on_board']

    def show_next_solution(self):
        """
        Show the next solution
        """
        if not self.solutions:
            return False
        
        self.current_solution_index = (self.current_solution_index + 1) % len(self.solutions)
        self._apply_solution(self.solutions[self.current_solution_index])
        self.current_status_message = f"Solution {self.current_solution_index + 1}/{len(self.solutions)}. \nPress 'N' for next solution, \n'P' for previous solution, \n'R' to restart."
        return True

    def show_previous_solution(self):
        """
        Show the previous solution
        """
        if not self.solutions:
            return False
        
        self.current_solution_index = (self.current_solution_index - 1) % len(self.solutions)
        self._apply_solution(self.solutions[self.current_solution_index])
        self.current_status_message = f"Solution {self.current_solution_index + 1}/{len(self.solutions)}. \nPress 'N' for next solution, \n'P' for previous solution, \n'R' to restart."
        return True

    def reset_game(self):
        """
        Reset the game to initial state.
        """
        # Reset board state
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) in RESTRICTED_CELLS:
                    self.board[r][c] = self.RESTRICTED_CELL
                else:
                    self.board[r][c] = self.EMPTY_CELL
        
        # Clear all selections and game state
        self.target_cells_coords = []
        self.target_cells_types = []
        self.placed_pieces_info = {}
        self.is_solved_state = False
        self.solutions = []
        self.current_solution_index = -1
        self.current_status_message = "Select: month, day, weekday"

def draw_board(screen, puzzle, font, label_font):
    """
    Render the puzzle board and status messages.
    """
    screen.fill(SCREEN_BACKGROUND_COLOR)
    
    # Draw info area
    info_rect = pygame.Rect(0, 0, screen.get_width(), INFO_HEIGHT)
    pygame.draw.rect(screen, INFO_AREA_BACKGROUND_COLOR, info_rect)

    # Draw status message
    max_text_width = screen.get_width() - 20
    status_lines = []
    
    paragraphs = puzzle.current_status_message.split('\n')
    for paragraph in paragraphs:
        words = paragraph.split(' ')
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
        if current_line.strip():
            status_lines.append(current_line.strip())

    line_height = font.get_linesize()
    total_text_height = len(status_lines) * line_height
    start_y = (INFO_HEIGHT - total_text_height) // 2 + 5
    if start_y < 5:
        start_y = 5

    for i, line_text in enumerate(status_lines):
        if not line_text:
            continue
        line_surface = font.render(line_text, True, INFO_AREA_TEXT_COLOR)
        line_rect = line_surface.get_rect(left=10, top=start_y + i * line_height)
        screen.blit(line_surface, line_rect)

    # Draw board
    for r in range(puzzle.rows):
        for c in range(puzzle.cols):
            cell_value = puzzle.board[r][c]
            rect_x = c * (TILE_SIZE + MARGIN) + MARGIN
            rect_y = r * (TILE_SIZE + MARGIN) + MARGIN + INFO_HEIGHT
            tile_rect = pygame.Rect(rect_x, rect_y, TILE_SIZE, TILE_SIZE)

            # Determine cell color
            if cell_value == puzzle.TARGET_CELL:
                current_tile_color = TARGET_CELL_COLOR
            elif cell_value == puzzle.RESTRICTED_CELL:
                current_tile_color = RESTRICTED_CELL_COLOR
            elif cell_value > 0:  # Piece
                piece_idx = cell_value - 1
                current_tile_color = PIECE_COLORS[piece_idx] if 0 <= piece_idx < len(PIECE_COLORS) else TILE_COLOR
            else:  # EMPTY_CELL
                current_tile_color = EMPTY_TILE_COLOR

            pygame.draw.rect(screen, current_tile_color, tile_rect)
            
            # Draw border for non-restricted cells
            if cell_value != puzzle.RESTRICTED_CELL:
                pygame.draw.rect(screen, TEXT_COLOR, tile_rect, 1)

            # Draw label
            if (r, c) in CELL_LABELS and CELL_LABELS[(r, c)]:
                label_text = CELL_LABELS[(r, c)]
                label_surface = label_font.render(label_text, True, LABEL_TEXT_COLOR)
                label_rect = label_surface.get_rect(center=tile_rect.center)
                screen.blit(label_surface, label_rect)

def get_game_config():
    """
    Get the current date configuration.
    """
    today = datetime.datetime.now()
    current_month = today.month
    current_day = today.day
    current_weekday = today.weekday()  # 0-6, where 0 is Monday
    
    # Convert weekday to our format (0-6, where 0 is Sunday)
    weekday_map = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 0}
    current_weekday = weekday_map[current_weekday]
    
    return current_month, current_day, current_weekday

def main():
    """
    Main entry point for the puzzle game.
    """
    current_month, current_day, current_weekday = get_game_config()

    pygame.init()
    pygame.font.init()

    try:
        puzzle = CalendarPuzzle()
        
        # Auto-select current date cells
        month_row = (current_month - 1) // 6
        month_col = (current_month - 1) % 6
        puzzle.toggle_target_cell(month_row, month_col)
        
        day_row = (current_day - 1) // 7 + 2
        day_col = (current_day - 1) % 7
        puzzle.toggle_target_cell(day_row, day_col)
        
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

    # Initialize display
    screen_width = puzzle.cols * (TILE_SIZE + MARGIN) + MARGIN
    screen_height = puzzle.rows * (TILE_SIZE + MARGIN) + MARGIN + INFO_HEIGHT
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Calendar Puzzle")

    # Set up fonts
    font_size = 24
    label_font_size = 28
    font = pygame.font.Font(None, font_size)
    label_font = pygame.font.Font(None, label_font_size)

    def handle_keyboard_events(event):
        """
        Handle keyboard input events.
        """
        if event.key == pygame.K_r:
            if puzzle.is_solved_state:
                print("\n--- Restart Game ---")
                puzzle.reset_game()
                
                # Re-select current date cells after reset
                month_row = (current_month - 1) // 6
                month_col = (current_month - 1) % 6
                puzzle.toggle_target_cell(month_row, month_col)
                
                day_row = (current_day - 1) // 7 + 2
                day_col = (current_day - 1) % 7
                puzzle.toggle_target_cell(day_row, day_col)
                
                if current_weekday <= 3:  # Sun, Mon, Tues, Wed
                    weekday_row = 6
                    weekday_col = current_weekday + 3
                else:  # Thur, Fri, Sat
                    weekday_row = 7
                    weekday_col = current_weekday
                
                puzzle.toggle_target_cell(weekday_row, weekday_col)
                print("Game reset. Current date selected.")

        elif event.key == pygame.K_s:
            if not puzzle.is_solved_state:
                if len(puzzle.target_cells_coords) == puzzle.max_target_cells:
                    print("Attempting to solve puzzle...")
                    puzzle.solve()
                else:
                    puzzle.current_status_message = "Select: month, day, weekday"
                    print(puzzle.current_status_message)
        
        elif event.key == pygame.K_n:  # Next solution
            if puzzle.is_solved_state:
                puzzle.show_next_solution()
        
        elif event.key == pygame.K_p:  # Previous solution
            if puzzle.is_solved_state:
                puzzle.show_previous_solution()

    def handle_mouse_click(pos):
        """
        Handle mouse click events.
        """
        mouse_x, mouse_y = pos
        # Adjust for info area height
        adjusted_y = mouse_y - INFO_HEIGHT
        
        if adjusted_y < 0:  # Clicked in info area
            return
            
        # Calculate grid position
        clicked_c = (mouse_x - MARGIN) // (TILE_SIZE + MARGIN)
        clicked_r = (adjusted_y - MARGIN) // (TILE_SIZE + MARGIN)
        
        # Validate grid position
        if not (0 <= clicked_r < puzzle.rows and 0 <= clicked_c < puzzle.cols):
            return
            
        if not puzzle.is_solved_state:
            puzzle.toggle_target_cell(clicked_r, clicked_c)
        else:
            puzzle.current_status_message = f"Solution {puzzle.current_solution_index + 1}/{len(puzzle.solutions)}. \nPress 'N' for next solution, \n'P' for previous solution, \n'R' to restart."

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            # Handle window close event
            if event.type == pygame.QUIT:
                running = False
            
            # Handle keyboard events
            if event.type == pygame.KEYDOWN:
                handle_keyboard_events(event)
            
            # Handle mouse click events
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_mouse_click(event.pos)

        draw_board(screen, puzzle, font, label_font)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()