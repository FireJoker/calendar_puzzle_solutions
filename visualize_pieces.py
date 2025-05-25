import pygame
import sys

# Try to import puzzle definitions and colors from calendar_puzzle.py
# If calendar_puzzle.py has complex initialization or execution logic, this may need adjustment
# For example, move PUZZLE_PIECES and PIECE_COLORS to a shared configuration file
try:
    from calendar_puzzle import PUZZLE_PIECES, PIECE_COLORS
except ImportError as e:
    print(f"Error importing from calendar_puzzle: {e}")
    print("Please ensure calendar_puzzle.py is in the same directory or Python path,")
    print("and that PUZZLE_PIECES and PIECE_COLORS are defined at the top level.")
    # Fallback definitions if import fails, so the script can partially run for structure check
    PUZZLE_PIECES = [[(0,0), (0,1), (1,0)]] # Example piece
    PIECE_COLORS = [(255,0,0)] # Example color
    # sys.exit()

# --- Pygame Settings ---
SCREEN_BACKGROUND_COLOR = (200, 200, 200)  # Light gray background
TILE_COLOR = (255, 255, 255)  # Default tile color (unused, as we use PIECE_COLORS)
TEXT_COLOR = (0, 0, 0)  # Black text

TILE_SIZE = 30  # Size of each small square in visualization
MARGIN = 5      # Margin between small squares
PIECE_PADDING = 20  # Additional spacing between puzzle pieces

INFO_FONT_SIZE = 20

def get_piece_bounding_box(piece_coords):
    """Calculate the bounding box of a single puzzle piece (min_r, min_c, max_r, max_c)"""
    if not piece_coords:
        return 0, 0, 0, 0
    min_r = min(p[0] for p in piece_coords)
    max_r = max(p[0] for p in piece_coords)
    min_c = min(p[1] for p in piece_coords)
    max_c = max(p[1] for p in piece_coords)
    return min_r, min_c, max_r, max_c

def draw_single_piece(screen, piece_coords, piece_color, top_left_x, top_left_y, piece_idx):
    """Draw a single puzzle piece at the specified location, ensuring correct coordinates."""
    if not piece_coords:
        return 0, 0 # Return width and height of 0 if no coords

    # 1. Normalize puzzle piece coordinates (all coordinates relative to its top-left corner)
    min_r_orig = min(p[0] for p in piece_coords)
    min_c_orig = min(p[1] for p in piece_coords)
    # normalized_coords are coordinates relative to (0,0)
    normalized_coords = sorted([(r - min_r_orig, c - min_c_orig) for r, c in piece_coords])

    # 2. Calculate the bounding box of this normalized puzzle piece to determine its rendering size
    if not normalized_coords: # Should not happen if piece_coords was not empty
        return 0, 0
    max_r_norm = max(p[0] for p in normalized_coords)
    max_c_norm = max(p[1] for p in normalized_coords)
    
    piece_width_tiles = max_c_norm + 1
    piece_height_tiles = max_r_norm + 1

    # 3. Draw each small square
    for r_norm, c_norm in normalized_coords:
        # r_norm, c_norm are tile indices relative to the top-left corner of the normalized puzzle piece
        rect_x = top_left_x + c_norm * (TILE_SIZE + MARGIN)
        # To achieve a Y-axis upward Cartesian coordinate system effect (inside the block), we reverse r_norm
        # piece_height_tiles is the total height of the block (in tiles)
        # Standardized r_norm range is 0 to piece_height_tiles-1
        # Converted r_norm for drawing, so that the row with r=0 in the original definition is drawn at the bottom of the block
        cartesian_r_norm = (piece_height_tiles - 1) - r_norm
        rect_y = top_left_y + cartesian_r_norm * (TILE_SIZE + MARGIN)
        tile_rect = pygame.Rect(rect_x, rect_y, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, piece_color, tile_rect)
        pygame.draw.rect(screen, TEXT_COLOR, tile_rect, 1) # Border

    # 4. Draw puzzle piece index number
    font = pygame.font.Font(None, INFO_FONT_SIZE)
    text_surface = font.render(f"P{piece_idx + 1}", True, TEXT_COLOR)
    # Place above top-left corner of puzzle piece
    screen.blit(text_surface, (top_left_x, top_left_y - INFO_FONT_SIZE - 2))
    
    # Return actual pixel width and height of this puzzle piece after rendering (including last MARGIN)
    render_width_px = piece_width_tiles * TILE_SIZE + (piece_width_tiles -1) * MARGIN if piece_width_tiles > 0 else 0
    render_height_px = piece_height_tiles * TILE_SIZE + (piece_height_tiles-1) * MARGIN if piece_height_tiles > 0 else 0
    return render_width_px, render_height_px

def main():
    pygame.init()
    pygame.font.init()

    if 'PUZZLE_PIECES' not in globals() or 'PIECE_COLORS' not in globals():
        print("PUZZLE_PIECES or PIECE_COLORS not loaded. Exiting.")
        pygame.quit()
        sys.exit()

    num_pieces = len(PUZZLE_PIECES)
    if num_pieces == 0:
        print("No puzzle pieces to display.")
        pygame.quit()
        sys.exit()

    # --- Dynamic calculation of screen size and layout ---
    # Goal: Arrange all puzzle pieces reasonably on the screen
    # We will try to arrange them in rows, if a row is too wide, we will switch to a new row

    # Pre-calculate rendering sizes of all puzzle pieces to better plan layout
    piece_render_sizes = [] # List of (width_px, height_px) for each piece
    for i, piece_coords in enumerate(PUZZLE_PIECES):
        if not piece_coords:
            piece_render_sizes.append((0,0))
            continue
        min_r_orig = min(p[0] for p in piece_coords)
        min_c_orig = min(p[1] for p in piece_coords)
        normalized_coords = [(r - min_r_orig, c - min_c_orig) for r, c in piece_coords]
        if not normalized_coords:
            piece_render_sizes.append((0,0))
            continue
        max_r_norm = max(p[0] for p in normalized_coords)
        max_c_norm = max(p[1] for p in normalized_coords)
        p_width_tiles = max_c_norm + 1
        p_height_tiles = max_r_norm + 1
        
        render_w = p_width_tiles * TILE_SIZE + (p_width_tiles - 1) * MARGIN if p_width_tiles > 0 else 0
        render_h = p_height_tiles * TILE_SIZE + (p_height_tiles - 1) * MARGIN if p_height_tiles > 0 else 0
        piece_render_sizes.append((render_w, render_h))

    # Layout variables
    max_screen_width_allowed = 1200 # Maximum screen width to prevent window from being too large
    current_x = PIECE_PADDING
    current_y = PIECE_PADDING + INFO_FONT_SIZE # Space for label at top
    row_max_height_px = 0 # Current row's highest puzzle piece height (including label space)
    total_width_needed = PIECE_PADDING # Minimum width needed
    max_row_width_so_far = 0 # Used to determine final screen width

    # First pass: Calculate layout, determine screen size
    positions = [] # (piece_idx, x, y, render_w, render_h_with_label)
    temp_current_y = current_y

    for i, (p_render_w, p_render_h) in enumerate(piece_render_sizes):
        if p_render_w == 0 and p_render_h == 0: # Skip empty pieces
            positions.append((i, 0, 0, 0, 0)) # Placeholder for empty
            continue

        piece_total_height_with_label = p_render_h + INFO_FONT_SIZE + PIECE_PADDING

        if current_x + p_render_w > max_screen_width_allowed - PIECE_PADDING: # If current row can't fit
            # Switch to new row
            max_row_width_so_far = max(max_row_width_so_far, current_x) # Update width before this row ends
            current_x = PIECE_PADDING
            temp_current_y += row_max_height_px # Move to start of next row
            row_max_height_px = 0 # Reset current row max height
        
        positions.append((i, current_x, temp_current_y, p_render_w, piece_total_height_with_label))
        
        current_x += p_render_w + PIECE_PADDING
        row_max_height_px = max(row_max_height_px, piece_total_height_with_label)
    
    max_row_width_so_far = max(max_row_width_so_far, current_x) # Last row/single very wide puzzle piece
    final_screen_width = max(max_row_width_so_far, 400) # Ensure minimum width
    final_screen_height = max(temp_current_y + row_max_height_px, 300) # Ensure minimum height

    screen = pygame.display.set_mode((final_screen_width, final_screen_height))
    pygame.display.set_caption("Puzzle Pieces Visualization - Corrected")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(SCREEN_BACKGROUND_COLOR)

        for i, piece_coords_orig in enumerate(PUZZLE_PIECES):
            if not piece_coords_orig: continue

            piece_color = PIECE_COLORS[i % len(PIECE_COLORS)]
            pos_idx, pos_x, pos_y, _, _ = positions[i]
            
            # Call draw_single_piece, it now handles normalization and returns rendering size
            # We've already calculated these sizes in the layout phase, this is mainly for drawing
            draw_single_piece(screen, piece_coords_orig, piece_color, pos_x, pos_y, i)
            
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()