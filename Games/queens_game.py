import tkinter as tk
from tkinter import messagebox
import random
from collections import deque
import itertools

class QueensGame:
    def __init__(self, root, size=8):
        self.root = root
        self.size = size
        self.root.title(f"Queens Logic Game ({size}x{size})")
        
        # Game State
        self.solution_queens = set() # Set of (r, c) tuples
        self.regions = {} # Map (r, c) -> region_id
        self.user_queens = set()
        self.user_crosses = set()
        
        # Config
        self.cell_size = 60
        self.colors = [
            "#ffadad", "#ffd6a5", "#fdffb6", "#caffbf", 
            "#9bf6ff", "#a0c4ff", "#bdb2ff", "#ffc6ff",
            "#e5e5e5", "#ff99c8"
        ]
        
        # UI Setup
        self.setup_ui()
        self.start_new_game()

    def setup_ui(self):
        # Top Control Bar
        top_frame = tk.Frame(self.root, bg="#f0f0f0")
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        btn_style = {"font": ("Arial", 10), "padx": 10, "pady": 2}
        
        tk.Button(top_frame, text="New Game", command=self.start_new_game, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(top_frame, text="Check Win", command=self.check_win, **btn_style).pack(side=tk.LEFT, padx=2)
        
        # The Hint Button
        self.hint_btn = tk.Button(top_frame, text="Get Hint 💡", command=self.give_smart_hint, bg="#b3e0ff", **btn_style)
        self.hint_btn.pack(side=tk.LEFT, padx=10)
        
        # Status Label for "Why" messages
        self.status_label = tk.Label(top_frame, text="Welcome! Right-click to mark X.", font=("Arial", 11, "bold"), fg="#0056b3", bg="#f0f0f0", wraplength=500)
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Canvas
        self.canvas = tk.Canvas(self.root, width=self.size*self.cell_size, height=self.size*self.cell_size, highlightthickness=0)
        self.canvas.pack(padx=20, pady=20)
        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<Button-3>", self.handle_right_click)

    def start_new_game(self):
        self.user_queens.clear()
        self.user_crosses.clear()
        self.status_label.config(text="New game started.", fg="#0056b3")
        self.generate_board()
        self.draw_board()

    # --- HINT LOGIC STARTS HERE ---
    
    def get_region_cells(self, region_id):
        return [(r, c) for (r, c), rid in self.regions.items() if rid == region_id]

    def give_smart_hint(self):
        
        # --- Priority 1: Catch User Errors ---
        for (r, c) in list(self.user_queens):
            if (r, c) not in self.solution_queens:
                
                # Check ALL rule violations to give the most useful feedback
                
                # Rule 1: No more than one queen per Row/Column/Region
                sol_q_r = any((r, qc) in self.solution_queens for qc in range(self.size))
                sol_q_c = any((qr, c) in self.solution_queens for qr in range(self.size))
                sol_q_reg = any(self.regions[(qr, qc)] == self.regions[(r,c)] for (qr, qc) in self.solution_queens if (qr, qc) != (r, c))
                
                # Rule 2: No touching (King's move)
                sol_q_touch = any(
                    (r == qr or c == qc) and (abs(r-qr) <= 1 and abs(c-qc) <= 1) 
                    for (qr, qc) in self.solution_queens if (qr, qc) != (r,c)
                )

                self.user_queens.remove((r, c))
                
                if sol_q_r:
                    reason = f"This Queen must be removed: Row {r+1} already contains the actual Queen."
                elif sol_q_c:
                    reason = f"This Queen must be removed: Column {c+1} already contains the actual Queen."
                elif sol_q_reg:
                    region_id = self.regions[(r, c)]
                    reason = f"This Queen must be removed: Region {region_id+1} already contains the actual Queen."
                elif sol_q_touch:
                    reason = "This Queen must be removed: It touches the actual Queen (King's move constraint)."
                else:
                    reason = "This Queen must be removed: It simply does not match the solution."

                self.status_label.config(text=f"Error corrected at ({r+1}, {c+1}): {reason}", fg="red")
                self.draw_board()
                return

        # --- Priority 2: Forced Placement (If only one choice remains) ---
        empty_cells = set(itertools.product(range(self.size), repeat=2)) - self.user_queens - self.user_crosses

        # Check all Rows, Columns, and Regions for the last available spot
        
        for i in range(self.size):
            # Check Row i
            row_cells = [(i, c) for c in range(self.size)]
            queens_in_row = len([(r, c) for r, c in self.user_queens if r == i])
            empty_in_row = [(r, c) for r, c in empty_cells if r == i]
            
            if queens_in_row == 0 and len(empty_in_row) == 1:
                r, c = empty_in_row[0]
                self.user_queens.add((r, c))
                self.status_label.config(text=f"Forced Placement: Queen placed at ({r+1}, {c+1}). It is the only empty spot left in Row {r+1}.", fg="green")
                self.draw_board()
                return

            # Check Column i
            col_cells = [(r, i) for r in range(self.size)]
            queens_in_col = len([(r, c) for r, c in self.user_queens if c == i])
            empty_in_col = [(r, c) for r, c in empty_cells if c == i]

            if queens_in_col == 0 and len(empty_in_col) == 1:
                r, c = empty_in_col[0]
                self.user_queens.add((r, c))
                self.status_label.config(text=f"Forced Placement: Queen placed at ({r+1}, {c+1}). It is the only empty spot left in Column {c+1}.", fg="green")
                self.draw_board()
                return

            # Check Region i
            region_cells = self.get_region_cells(i)
            queens_in_region = len([pos for pos in self.user_queens if self.regions.get(pos) == i])
            empty_in_region = [pos for pos in empty_cells if self.regions.get(pos) == i]

            if queens_in_region == 0 and len(empty_in_region) == 1:
                r, c = empty_in_region[0]
                self.user_queens.add((r, c))
                self.status_label.config(text=f"Forced Placement: Queen placed at ({r+1}, {c+1}). It is the only empty spot left in Region {i+1}.", fg="green")
                self.draw_board()
                return


        # --- Priority 3: Forced Elimination (Mark X) ---
        
        # Find all empty spots that are NOT the solution Queen
        valid_eliminations = [(r, c) for r, c in empty_cells if (r, c) not in self.solution_queens]
        
        if not valid_eliminations:
            self.status_label.config(text="No guaranteed logical eliminations left (board may be complete/correct).", fg="#0056b3")
            return

        # Pick a random spot to eliminate and provide the logical reason
        r, c = random.choice(valid_eliminations)
        self.user_crosses.add((r, c))
        
        # Determine the logical reason for elimination based on the SOLUTION
        region_id = self.regions[(r, c)]
        
        sol_q_r = next(((qr, qc) for qr, qc in self.solution_queens if qr == r), None)
        sol_q_c = next(((qr, qc) for qr, qc in self.solution_queens if qc == c), None)
        sol_q_reg = next(((qr, qc) for qr, qc in self.solution_queens if self.regions[(qr,qc)] == region_id and (qr, qc) != (r,c)), None)
        
        
        if sol_q_r:
            reason = f"Eliminated: Row {r+1} already contains the actual Queen at Column {sol_q_r[1]+1}."
        elif sol_q_c:
            reason = f"Eliminated: Column {c+1} already contains the actual Queen at Row {sol_q_c[0]+1}."
        elif sol_q_reg:
            reason = f"Eliminated: Region {region_id+1} already contains the actual Queen at ({sol_q_reg[0]+1}, {sol_q_reg[1]+1})."
        else:
            # This should only happen if the cell is eliminated due to a touching constraint from a Queen *not* in the same row/col/region, which is less obvious logic.
            reason = "Eliminated: This cell conflicts with the actual solution placement due to the 'No Touching' rule."
            
        self.status_label.config(text=f"Marked X at ({r+1}, {c+1}): {reason}", fg="blue")
        self.draw_board()

    # --- HINT LOGIC ENDS HERE ---

    # --- BOARD GENERATION (Unchanged from previous version) ---

    def generate_board(self):
        # Step 1: Place Queens legally (Backtracking)
        self.solution_queens = set()
        
        def is_safe(queens, r, c):
            for qr, qc in queens:
                if r == qr or c == qc: return False
                if abs(r - qr) <= 1 and abs(c - qc) <= 1: return False
            return True

        def solve(col):
            if col >= self.size: return True
            possible_rows = list(range(self.size))
            random.shuffle(possible_rows)
            for r in possible_rows:
                if is_safe(self.solution_queens, r, col):
                    self.solution_queens.add((r, col))
                    if solve(col + 1): return True
                    self.solution_queens.remove((r, col))
            return False

        while True:
            self.solution_queens.clear()
            if solve(0): break
        
        # Step 2: Grow Regions (BFS)
        self.regions = {}
        queue = deque()
        sorted_queens = list(self.solution_queens)
        
        for i, (r, c) in enumerate(sorted_queens):
            self.regions[(r, c)] = i
            queue.append((r, c))
            
        while queue:
            r, c = queue.popleft()
            current_region = self.regions[(r, c)]
            neighbors = [(r+1,c), (r-1,c), (r,c+1), (r,c-1)]
            random.shuffle(neighbors)
            for nr, nc in neighbors:
                if 0 <= nr < self.size and 0 <= nc < self.size:
                    if (nr, nc) not in self.regions:
                        self.regions[(nr, nc)] = current_region
                        queue.append((nr, nc))
        
        random.shuffle(self.colors)
        self.region_map = {i: self.colors[i % len(self.colors)] for i in range(self.size)}

    # --- DRAWING AND INTERACTION (Minor changes for better display) ---

    def draw_board(self):
        self.canvas.delete("all")
        for r in range(self.size):
            for c in range(self.size):
                x1, y1 = c * self.cell_size, r * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                
                # Region Color
                region_id = self.regions.get((r, c), 0)
                color = self.region_map.get(region_id, "white")
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#d0d0d0")
                
                # Icons
                if (r, c) in self.user_queens:
                    self.canvas.create_text(x1+30, y1+30, text="♛", font=("Arial", 32), fill="black")
                elif (r, c) in self.user_crosses:
                    self.canvas.create_text(x1+30, y1+30, text="✕", font=("Arial", 20), fill="#777")
        
        self.draw_borders()

    def draw_borders(self):
        for r in range(self.size):
            for c in range(self.size):
                reg = self.regions.get((r,c))
                x1, y1 = c * self.cell_size, r * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                
                # Thick lines between regions
                if c < self.size - 1 and self.regions.get((r, c+1)) != reg:
                    self.canvas.create_line(x2, y1, x2, y2, width=3)
                if r < self.size - 1 and self.regions.get((r+1, c)) != reg:
                    self.canvas.create_line(x1, y2, x2, y2, width=3)
        
        # Draw outer boundary
        self.canvas.create_rectangle(0, 0, self.size*self.cell_size, self.size*self.cell_size, outline="black", width=2)


    def handle_click(self, event):
        self.toggle_cell(event, mode="queen")

    def handle_right_click(self, event):
        self.toggle_cell(event, mode="cross")

    def toggle_cell(self, event, mode):
        c, r = event.x // self.cell_size, event.y // self.cell_size
        if not (0 <= r < self.size and 0 <= c < self.size): return

        target_set = self.user_queens if mode == "queen" else self.user_crosses
        opp_set = self.user_crosses if mode == "queen" else self.user_queens
        
        if (r, c) in target_set:
            target_set.remove((r, c))
        else:
            target_set.add((r, c))
            if (r, c) in opp_set: opp_set.remove((r, c))

        self.draw_board()
        
        if len(self.user_queens) == self.size and self.user_queens == self.solution_queens:
            messagebox.showinfo("Winner!", "You found all the Queens!")

    def check_win(self):
        if self.user_queens == self.solution_queens:
            messagebox.showinfo("Result", "Correct! All constraints satisfied.")
        else:
            messagebox.showwarning("Result", f"Incorrect. Check your Row/Column/Region/Touching rules.")

if __name__ == "__main__":
    root = tk.Tk()
    game = QueensGame(root)
    root.mainloop()
