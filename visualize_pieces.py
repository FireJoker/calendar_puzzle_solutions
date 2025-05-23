import pygame
import sys

# 尝试从 calendar_puzzle.py 导入拼图定义和颜色
# 如果 calendar_puzzle.py 有复杂的初始化或执行逻辑，这可能需要调整
# 例如，将 PUZZLE_PIECES 和 PIECE_COLORS 移到共享的配置文件中
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

# --- Pygame 设置 ---
SCREEN_BACKGROUND_COLOR = (200, 200, 200)  # 浅灰色背景
TILE_COLOR = (255, 255, 255)  # 默认瓦片颜色 (未使用，因为我们用 PIECE_COLORS)
TEXT_COLOR = (0, 0, 0)  # 黑色文本

TILE_SIZE = 30  # 可视化时每个小方块的大小
MARGIN = 5      # 小方块之间的边距
PIECE_PADDING = 20 # 各个拼图块之间的额外间距

INFO_FONT_SIZE = 20

def get_piece_bounding_box(piece_coords):
    """计算单个拼图块的边界框 (min_r, min_c, max_r, max_c)"""
    if not piece_coords:
        return 0, 0, 0, 0
    min_r = min(p[0] for p in piece_coords)
    max_r = max(p[0] for p in piece_coords)
    min_c = min(p[1] for p in piece_coords)
    max_c = max(p[1] for p in piece_coords)
    return min_r, min_c, max_r, max_c

def draw_single_piece(screen, piece_coords, piece_color, top_left_x, top_left_y, piece_idx):
    """在指定位置绘制单个拼图块，确保坐标正确。"""
    if not piece_coords:
        return 0, 0 # Return width and height of 0 if no coords

    # 1. 标准化拼图块坐标 (所有坐标相对于其自身的左上角)
    min_r_orig = min(p[0] for p in piece_coords)
    min_c_orig = min(p[1] for p in piece_coords)
    # normalized_coords 是相对于 (0,0) 的坐标
    normalized_coords = sorted([(r - min_r_orig, c - min_c_orig) for r, c in piece_coords])

    # 2. 计算此标准化拼图块的边界，以确定其渲染尺寸
    if not normalized_coords: # Should not happen if piece_coords was not empty
        return 0, 0
    max_r_norm = max(p[0] for p in normalized_coords)
    max_c_norm = max(p[1] for p in normalized_coords)
    
    piece_width_tiles = max_c_norm + 1
    piece_height_tiles = max_r_norm + 1

    # 3. 绘制每个小方块
    for r_norm, c_norm in normalized_coords:
        # r_norm, c_norm 是相对于标准化拼图块左上角的瓦片索引
        rect_x = top_left_x + c_norm * (TILE_SIZE + MARGIN)
        # 为了实现Y轴向上的笛卡尔坐标系效果（在块内部），我们反转r_norm
        # piece_height_tiles 是块的总高度（以瓦片为单位）
        # 标准化的r_norm范围从0到piece_height_tiles-1
        # 转换后的r_norm用于绘图，使得原始定义中的r=0的行绘制在块的底部
        cartesian_r_norm = (piece_height_tiles - 1) - r_norm
        rect_y = top_left_y + cartesian_r_norm * (TILE_SIZE + MARGIN)
        tile_rect = pygame.Rect(rect_x, rect_y, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, piece_color, tile_rect)
        pygame.draw.rect(screen, TEXT_COLOR, tile_rect, 1) # 边框

    # 4. 绘制拼图块索引号
    font = pygame.font.Font(None, INFO_FONT_SIZE)
    text_surface = font.render(f"P{piece_idx + 1}", True, TEXT_COLOR)
    # 放在拼图块的左上角上方
    screen.blit(text_surface, (top_left_x, top_left_y - INFO_FONT_SIZE - 2))
    
    # 返回此拼图块渲染后的实际像素宽度和高度 (包括最后一个 MARGIN)
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

    # --- 动态计算屏幕尺寸和布局 ---
    # 目标：将所有拼图块合理地排列在屏幕上
    # 我们将尝试按行排列，如果一行太宽，则换行

    # 预计算所有拼图块的渲染尺寸，以便更好地规划布局
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

    # 布局变量
    max_screen_width_allowed = 1200 # 最大屏幕宽度，防止窗口过大
    current_x = PIECE_PADDING
    current_y = PIECE_PADDING + INFO_FONT_SIZE # 为标签留出顶部空间
    row_max_height_px = 0 # 当前行中最高拼图块的高度 (渲染高度 + 标签空间)
    total_width_needed = PIECE_PADDING # 至少需要的宽度
    max_row_width_so_far = 0 # 用于确定最终屏幕宽度

    # 第一次遍历：计算布局，确定屏幕尺寸
    positions = [] # (piece_idx, x, y, render_w, render_h_with_label)
    temp_current_y = current_y

    for i, (p_render_w, p_render_h) in enumerate(piece_render_sizes):
        if p_render_w == 0 and p_render_h == 0: # Skip empty pieces
            positions.append((i, 0, 0, 0, 0)) # Placeholder for empty
            continue

        piece_total_height_with_label = p_render_h + INFO_FONT_SIZE + PIECE_PADDING

        if current_x + p_render_w > max_screen_width_allowed - PIECE_PADDING: # 如果当前行放不下
            # 换行
            max_row_width_so_far = max(max_row_width_so_far, current_x) # 更新此行结束前的宽度
            current_x = PIECE_PADDING
            temp_current_y += row_max_height_px # 移动到下一行的起始Y
            row_max_height_px = 0 # 重置当前行最大高度
        
        positions.append((i, current_x, temp_current_y, p_render_w, piece_total_height_with_label))
        
        current_x += p_render_w + PIECE_PADDING
        row_max_height_px = max(row_max_height_px, piece_total_height_with_label)
    
    max_row_width_so_far = max(max_row_width_so_far, current_x) # 最后一行/单个很宽的拼图块
    final_screen_width = max(max_row_width_so_far, 400) # 确保最小宽度
    final_screen_height = max(temp_current_y + row_max_height_px, 300) # 确保最小高度

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
            
            # 调用 draw_single_piece, 它现在会处理标准化并返回渲染尺寸
            # 我们在布局阶段已经计算了这些尺寸，这里主要是为了绘制
            draw_single_piece(screen, piece_coords_orig, piece_color, pos_x, pos_y, i)
            
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()