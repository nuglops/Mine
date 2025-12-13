import tkinter as tk
from tkinter import messagebox
import random
from collections import deque

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
        self.region_colors = []
        
        # Hint Timer State
        self.time_left = 30
        self.timer_running = False
        
        # Config
        self.cell_size = 50
        self.colors = [
            "#ffadad", "#ffd6a5", "#fdffb6", "#caffbf", 
            "#9bf6ff", "#a0c4ff", "#bdb2ff", "#ffc6ff",
            "#e5e5e5", "#ff99c8"
        ]
        
        # UI Setup
        self.setup_ui()
        self.start_new_game()

    def setup_ui(self):
        # Top Bar
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(top_frame, text="New Game", command=self.start_new_game).pack(side=tk.LEFT)
        tk.Button(top_frame, text="Check", command=self.check_win).pack(side=tk.LEFT, padx=5)
        
        self.timer_label = tk.Label(top_frame, text="Hint in: 30s", font=("Arial", 12, "bold"), fg="red")
        self.timer_label.pack(side=tk.RIGHT)
        
        # Canvas for the grid
        self.canvas = tk.Canvas(self.root, width=self.size*self.cell_size, height=self.size*self.cell_size)
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.handle_click) # Left click
        self.canvas.bind("<Button-3>", self.handle_right_click) # Right click

    def start_new_game(self):
        self.user_queens.clear()
        self.user_crosses.clear()
        self.time_left = 30
        self.generate_board()
        self.draw_board()
        self.start_timer()

    def start_timer(self):
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if not self.timer_running:
            return
            
        if self.time_left > 0:
            self.timer_label.config(text=f"Hint in: {self.time_left}s")
            self.time_left -= 1
            self.root.after(1000, self.update_timer)
        else:
            self.give_hint()
            self.time_left = 30 # Reset timer
            self.update_timer()

    def give_hint(self):
        """
        Hint Logic:
        1. If user placed a WRONG queen, mark it red (remove it).
        2. If user is missing a queen from a solved row, place it or mark X.
        """
        # 1. Check for errors
        for (r, c) in list(self.user_queens):
            if (r, c) not in self.solution_queens:
                self.flash_message(f"Error fixed at ({r+1}, {c+1})")
                self.user_queens.remove((r, c))
                self.draw_board()
                return

        # 2. Reveal a correct queen
        remaining = list(self.solution_queens - self.user_queens)
        if remaining:
            r, c = random.choice(remaining)
            self.user_queens.add((r, c))
            self.flash_message(f"Hint: Queen revealed at ({r+1}, {c+1})")
            self.draw_board()
        else:
            self.flash_message("Board is correct!")
            self.timer_running = False

    def flash_message(self, msg):
        self.timer_label.config(text=msg, fg="blue")
        # Reset color after 2 seconds
        self.root.after(2000, lambda: self.timer_label.config(fg="red"))

    def generate_board(self):
        # Step 1: Place Queens legally (Backtracking)
        self.solution_queens = set()
        rows = list(range(self.size))
        
        def is_safe(queens, r, c):
            for qr, qc in queens:
                if r == qr or c == qc: return False # Row/Col check
                if abs(r - qr) <= 1 and abs(c - qc) <= 1: return False # Touch check (King's move)
            return True

        def solve(col):
            if col >= self.size:
                return True
            
            # Randomize row attempts for procedural generation
            possible_rows = list(range(self.size))
            random.shuffle(possible_rows)
            
            for r in possible_rows:
                if is_safe(self.solution_queens, r, col):
                    self.solution_queens.add((r, col))
                    if solve(col + 1):
                        return True
                    self.solution_queens.remove((r, col))
            return False

        # Retry generation if it gets stuck (simple safeguard)
        while True:
            self.solution_queens.clear()
            if solve(0):
                break
        
        # Step 2: Grow Regions (Voronoi / BFS style)
        self.regions = {}
        queue = deque()
        
        # Seed the queue with queen positions
        # Each queen is the 'seed' for region ID = index
        sorted_queens = list(self.solution_queens)
        for i, (r, c) in enumerate(sorted_queens):
            self.regions[(r, c)] = i
            queue.append((r, c))
            
        # Grow regions
        while queue:
            r, c = queue.popleft()
            current_region = self.regions[(r, c)]
            
            neighbors = [(r+1,c), (r-1,c), (r,c+1), (r,c-1)]
            random.shuffle(neighbors) # Randomize growth shape
            
            for nr, nc in neighbors:
                if 0 <= nr < self.size and 0 <= nc < self.size:
                    if (nr, nc) not in self.regions:
                        self.regions[(nr, nc)] = current_region
                        queue.append((nr, nc))
        
        # Assign colors to region IDs
        random.shuffle(self.colors)
        self.region_map = {i: self.colors[i % len(self.colors)] for i in range(self.size)}

    def draw_board(self):
        self.canvas.delete("all")
        for r in range(self.size):
            for c in range(self.size):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Background Color (Region)
                region_id = self.regions.get((r, c), 0)
                color = self.region_map.get(region_id, "white")
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
                
                # Draw Icons
                if (r, c) in self.user_queens:
                    self.canvas.create_text(x1+25, y1+25, text="♛", font=("Arial", 30), fill="black")
                elif (r, c) in self.user_crosses:
                    self.canvas.create_text(x1+25, y1+25, text="x", font=("Arial", 20), fill="gray")
        
        # Draw Region Borders (Thick lines)
        self.draw_borders()

    def draw_borders(self):
        # Draw thicker lines between different regions
        for r in range(self.size):
            for c in range(self.size):
                reg = self.regions[(r,c)]
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Check right neighbor
                if c < self.size - 1 and self.regions[(r, c+1)] != reg:
                    self.canvas.create_line(x2, y1, x2, y2, width=3)
                # Check bottom neighbor
                if r < self.size - 1 and self.regions[(r+1, c)] != reg:
                    self.canvas.create_line(x1, y2, x2, y2, width=3)

    def handle_click(self, event):
        self.toggle_cell(event, mode="queen")

    def handle_right_click(self, event):
        self.toggle_cell(event, mode="cross")

    def toggle_cell(self, event, mode):
        c = event.x // self.cell_size
        r = event.y // self.cell_size
        
        if not (0 <= r < self.size and 0 <= c < self.size):
            return

        # Logic: Empty -> Queen -> X -> Empty
        # But split between left/right click for better UX
        if mode == "queen":
            if (r, c) in self.user_queens:
                self.user_queens.remove((r, c))
            else:
                self.user_queens.add((r, c))
                if (r, c) in self.user_crosses: self.user_crosses.remove((r, c))
        
        elif mode == "cross":
            if (r, c) in self.user_crosses:
                self.user_crosses.remove((r, c))
            else:
                self.user_crosses.add((r, c))
                if (r, c) in self.user_queens: self.user_queens.remove((r, c))
                
        self.draw_board()
        
        # Auto-check win
        if len(self.user_queens) == self.size:
            if self.user_queens == self.solution_queens:
                self.timer_running = False
                messagebox.showinfo("Winner!", "You found all the Queens!")

    def check_win(self):
        if self.user_queens == self.solution_queens:
            messagebox.showinfo("Result", "Correct!")
        else:
            errors = len(self.user_queens - self.solution_queens)
            messagebox.showwarning("Result", f"Incorrect. {errors} misplaced queens.")

if __name__ == "__main__":
    root = tk.Tk()
    game = QueensGame(root)
    root.mainloop()
