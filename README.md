# Calendar Puzzle

## English

### Introduction
A Python-based puzzle game where the player needs to fit a set of predefined puzzle pieces onto a game board, leaving three user-selected "target" cells uncovered. The game board is typically a 9x6 grid, with cells labeled to represent months, days of the month, and days of the week, mimicking a perpetual calendar. The goal is to cover all cells except the three chosen target cells.

### How to Run
1.  **Main Puzzle Game (`calendar_puzzle.py`)**:
    *   Run the script: `python calendar_puzzle.py`
    *   The game will prompt you to enter the board dimensions (e.g., 9 rows, 6 columns for the standard calendar layout).
    *   You can optionally enter a year and month, but these are primarily for display and do not affect the core puzzle logic for this version.
    *   Click on three empty cells on the board to select them as target cells. These cells must remain uncovered.
    *   Press 'S' to attempt to solve the puzzle.
    *   Press 'R' to reset the game.
    *   ![image](https://github.com/user-attachments/assets/7b391b76-a545-4880-9ebf-9d4fa2ff4863)
    *   ![image](https://github.com/user-attachments/assets/e70ec987-9200-48f9-b7da-0603f87851eb)



2.  **Puzzle Piece Visualizer (`visualize_pieces.py`)**:
    *   This script displays all the defined puzzle pieces.
    *   Run the script: `python visualize_pieces.py`
    *   A window will open showing each piece with its index.
    *   ![image](https://github.com/user-attachments/assets/32633eef-9fcc-4e65-a21b-323e2296c5c6)



### Core Algorithm (in `calendar_puzzle.py`)
*   **Piece Representation**: Puzzle pieces are defined as a list of (row, column) coordinates relative to their own origin.
*   **Piece Variations**: The game generates all unique variations of each piece by considering rotations (0, 90, 180, 270 degrees) and flips (horizontal).
*   **Target Cell Selection**: The user selects three cells on the board that must not be covered by any puzzle piece.
*   **Backtracking Solver (`_solve_recursive`)**:
    *   The core solving mechanism uses a recursive backtracking algorithm.
    *   It tries to place each piece, one by one, in all its possible variations and at all possible positions on the board.
    *   **Placement Check (`can_place_piece`)**: Before placing a piece, it checks if the target cells are within the board boundaries and if they are currently empty (not occupied by another piece or a target cell).
    *   **Pruning (`_is_valid_pruning_candidate`)**: After a piece is tentatively placed, a pruning step checks if any remaining empty "islands" (contiguous empty cells) are smaller than the smallest puzzle piece. If so, this path is pruned as it's impossible to fill such small gaps. This significantly speeds up the search.
    *   If a piece can be placed and the pruning condition is met, the algorithm recursively tries to place the next piece.
    *   If the next piece cannot be placed, or if all subsequent placements lead to a dead end, the algorithm backtracks, removes the current piece, and tries a different variation or position for it.
    *   The solution is found when all pieces are successfully placed without covering the target cells.

### Main Features
*   Interactive puzzle board.
*   User-defined board size (though fixed labels are for 9x6).
*   Selection of three target cells that must remain uncovered.
*   Automatic puzzle solving using a backtracking algorithm with pruning.
*   Visualization of puzzle pieces.
*   Reset functionality.
*   Status messages to guide the user.

## 中文

### 项目简介
一个基于 Python 的益智游戏，玩家需要将一组预定义的拼图块放置在游戏板上，同时要空出用户选择的三个“目标”单元格。游戏板通常是一个 9x6 的网格，单元格上标有月份、日期和星期，模拟一个万年历。目标是覆盖除选定的三个目标单元格之外的所有单元格。

### 如何运行
1.  **主益智游戏 (`calendar_puzzle.py`)**:
    *   运行脚本: `python calendar_puzzle.py`
    *   游戏会提示您输入棋盘尺寸（例如，标准日历布局为 9 行 6 列）。
    *   您可以选择性地输入年份和月份，但这主要用于显示，不影响此版本核心的拼图逻辑。
    *   在棋盘上点击三个空格单元格，将它们选为目标单元格。这些单元格必须保持未被覆盖。
    *   按 'S' 键尝试解决谜题。
    *   按 'R' 键重置游戏。
    *   ![image](https://github.com/user-attachments/assets/7b391b76-a545-4880-9ebf-9d4fa2ff4863)
    *   ![image](https://github.com/user-attachments/assets/e70ec987-9200-48f9-b7da-0603f87851eb)

2.  **拼图块可视化工具 (`visualize_pieces.py`)**:
    *   此脚本会显示所有已定义的拼图块。
    *   运行脚本: `python visualize_pieces.py`
    *   将打开一个窗口，显示每个拼图块及其索引。
    *   ![image](https://github.com/user-attachments/assets/32633eef-9fcc-4e65-a21b-323e2296c5c6)


### 核心算法 (位于 `calendar_puzzle.py`)
*   **拼图块表示**: 拼图块被定义为其自身原点相关的 (行, 列) 坐标列表。
*   **拼图块变体**: 游戏通过考虑旋转 (0, 90, 180, 270 度) 和翻转 (水平) 来生成每个拼图块的所有唯一变体。
*   **目标单元格选择**: 用户在棋盘上选择三个不能被任何拼图块覆盖的单元格。
*   **回溯求解器 (`_solve_recursive`)**:
    *   核心求解机制使用递归回溯算法。
    *   它尝试逐个将每个拼图块以其所有可能的变体和在棋盘上的所有可能位置进行放置。
    *   **放置检查 (`can_place_piece`)**: 在放置拼图块之前，它会检查目标单元格是否在棋盘边界内，以及它们当前是否为空（未被其他拼图块或目标单元格占据）。
    *   **剪枝 (`_is_valid_pruning_candidate`)**: 在试探性地放置一个拼图块后，一个剪枝步骤会检查是否有任何剩余的空“岛屿”（连续的空格单元格）小于最小的拼图块。如果是，则剪掉此路径，因为不可能填充这么小的间隙。这显著加快了搜索速度。
    *   如果一个拼图块可以被放置并且满足剪枝条件，算法会递归地尝试放置下一个拼图块。
    *   如果下一个拼图块无法放置，或者所有后续放置都导致死胡同，算法会回溯，移除当前拼图块，并尝试其不同的变体或位置。
    *   当所有拼图块都成功放置并且没有覆盖目标单元格时，就找到了解决方案。

### 主要功能
*   交互式拼图板。
*   用户自定义棋盘大小（尽管固定标签是为 9x6 设计的）。
*   选择三个必须保持未被覆盖的目标单元格。
*   使用带剪枝的回溯算法自动解决谜题。
*   拼图块可视化。
*   重置功能。
*   状态消息引导用户。
