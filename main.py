import tkinter as tk
from tkinter import messagebox
import random
import math
import heapq
import time

BG_COLOR = "#121212"
WALL_COLOR = "#333333"
EMPTY_COLOR = "#1E1E1E"
START_COLOR = "#00FFFF"
GOAL_COLOR = "#FF00FF"
FRONTIER_COLOR = "#FFFF00"
VISITED_COLOR = "#00008B"
PATH_COLOR = "#39FF14"

class Node:
    def __init__(self, r, c):
        self.r = r
        self.c = c
        self.is_wall = False
        self.g = float('inf')
        self.h = 0
        self.parent = None

    def f(self, is_a_star):
        return self.g + self.h if is_a_star else self.h

    def __lt__(self, other):
        return False

class PathfindingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic Pathfinding - Cyberpunk Edition")
        self.root.configure(bg=BG_COLOR)
        
        self.rows, self.cols = 20, 20
        self.cell_size = 25
        self.grid = []
        self.start_node = None
        self.goal_node = None
        self.is_running = False
        
        self.setup_ui()
        self.init_grid()

    def setup_ui(self):
        control_frame = tk.Frame(self.root, bg="#2C2C2C", padx=10, pady=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(control_frame, text="SETTINGS", fg=START_COLOR, bg="#2C2C2C", font=("Courier", 16, "bold")).pack(pady=10)

        self.algo_var = tk.StringVar(value="A*")
        tk.Radiobutton(control_frame, text="A* Search", variable=self.algo_var, value="A*", bg="#2C2C2C", fg="white", selectcolor=BG_COLOR).pack(anchor="w")
        tk.Radiobutton(control_frame, text="Greedy BFS", variable=self.algo_var, value="GBFS", bg="#2C2C2C", fg="white", selectcolor=BG_COLOR).pack(anchor="w")

        self.heur_var = tk.StringVar(value="Manhattan")
        tk.Radiobutton(control_frame, text="Manhattan", variable=self.heur_var, value="Manhattan", bg="#2C2C2C", fg="white", selectcolor=BG_COLOR).pack(anchor="w", pady=(10,0))
        tk.Radiobutton(control_frame, text="Euclidean", variable=self.heur_var, value="Euclidean", bg="#2C2C2C", fg="white", selectcolor=BG_COLOR).pack(anchor="w")

        self.dynamic_var = tk.BooleanVar(value=False)
        tk.Checkbutton(control_frame, text="Dynamic Obstacles", variable=self.dynamic_var, bg="#2C2C2C", fg=PATH_COLOR, selectcolor=BG_COLOR).pack(pady=10)

        tk.Button(control_frame, text="Generate Random Maze", command=self.random_maze, bg=WALL_COLOR, fg="white").pack(fill=tk.X, pady=5)
        tk.Button(control_frame, text="Clear Grid", command=self.init_grid, bg=WALL_COLOR, fg="white").pack(fill=tk.X, pady=5)
        tk.Button(control_frame, text="START SEARCH", command=self.start_search, bg=PATH_COLOR, fg="black", font=("Arial", 12, "bold")).pack(fill=tk.X, pady=20)

        tk.Label(control_frame, text="METRICS", fg=GOAL_COLOR, bg="#2C2C2C", font=("Courier", 14, "bold")).pack(pady=10)
        self.lbl_visited = tk.Label(control_frame, text="Nodes Visited: 0", bg="#2C2C2C", fg="white")
        self.lbl_visited.pack(anchor="w")
        self.lbl_cost = tk.Label(control_frame, text="Path Cost: 0", bg="#2C2C2C", fg="white")
        self.lbl_cost.pack(anchor="w")
        self.lbl_time = tk.Label(control_frame, text="Time: 0 ms", bg="#2C2C2C", fg="white")
        self.lbl_time.pack(anchor="w")

        self.canvas = tk.Canvas(self.root, width=self.cols*self.cell_size, height=self.rows*self.cell_size, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(side=tk.RIGHT, padx=20, pady=20)
        self.canvas.bind("<B1-Motion>", self.toggle_wall)
        self.canvas.bind("<Button-1>", self.toggle_wall)

    def init_grid(self):
        self.canvas.delete("all")
        self.grid = [[Node(r, c) for c in range(self.cols)] for r in range(self.rows)]
        self.start_node = self.grid[1][1]
        self.goal_node = self.grid[self.rows-2][self.cols-2]
        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        for r in range(self.rows):
            for c in range(self.cols):
                color = EMPTY_COLOR
                if self.grid[r][c].is_wall: color = WALL_COLOR
                elif self.grid[r][c] == self.start_node: color = START_COLOR
                elif self.grid[r][c] == self.goal_node: color = GOAL_COLOR
                
                x1, y1 = c * self.cell_size, r * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#222222")

    def toggle_wall(self, event):
        if self.is_running: return
        c, r = event.x // self.cell_size, event.y // self.cell_size
        if 0 <= r < self.rows and 0 <= c < self.cols:
            node = self.grid[r][c]
            if node != self.start_node and node != self.goal_node:
                node.is_wall = True
                self.draw_grid()

    def random_maze(self):
        self.init_grid()
        for r in range(self.rows):
            for c in range(self.cols):
                if random.random() < 0.3 and self.grid[r][c] not in (self.start_node, self.goal_node):
                    self.grid[r][c].is_wall = True
        self.draw_grid()

    def get_heuristic(self, nodeA, nodeB):
        if self.heur_var.get() == "Manhattan":
            return abs(nodeA.r - nodeB.r) + abs(nodeA.c - nodeB.c)
        else:
            return math.sqrt((nodeA.r - nodeB.r)**2 + (nodeA.c - nodeB.c)**2)

    def get_neighbors(self, node):
        neighbors = []
        dirs = [(-1,0), (1,0), (0,-1), (0,1)]
        for dr, dc in dirs:
            r, c = node.r + dr, node.c + dc
            if 0 <= r < self.rows and 0 <= c < self.cols and not self.grid[r][c].is_wall:
                neighbors.append(self.grid[r][c])
        return neighbors

    def start_search(self):
        if self.is_running: return
        self.is_running = True
        self.draw_grid()
        
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c].g = float('inf')
                self.grid[r][c].parent = None

        self.start_node.g = 0
        self.start_node.h = self.get_heuristic(self.start_node, self.goal_node)
        
        self.open_set = []
        heapq.heappush(self.open_set, (self.start_node.f(self.algo_var.get() == "A*"), self.start_node))
        self.closed_set = set()
        
        self.nodes_visited = 0
        self.start_time = time.time()
        self.step_search()

    def step_search(self):
        if not self.open_set:
            messagebox.showinfo("Result", "No path found!")
            self.is_running = False
            return

        current = heapq.heappop(self.open_set)[1]
        self.closed_set.add(current)
        self.nodes_visited += 1

        if self.dynamic_var.get() and random.random() < 0.05:
            rr, rc = random.randint(0, self.rows-1), random.randint(0, self.cols-1)
            rand_node = self.grid[rr][rc]
            if rand_node not in (self.start_node, self.goal_node) and not rand_node.is_wall:
                rand_node.is_wall = True
                self.draw_node(rand_node, WALL_COLOR)

        if current == self.goal_node:
            self.reconstruct_path()
            return

        is_a_star = self.algo_var.get() == "A*"

        for neighbor in self.get_neighbors(current):
            if neighbor in self.closed_set: continue

            tentative_g = current.g + 1

            if tentative_g < neighbor.g:
                neighbor.parent = current
                neighbor.g = tentative_g
                neighbor.h = self.get_heuristic(neighbor, self.goal_node)
                
                if not any(neighbor == item[1] for item in self.open_set):
                    heapq.heappush(self.open_set, (neighbor.f(is_a_star), neighbor))
                    if neighbor != self.goal_node:
                        self.draw_node(neighbor, FRONTIER_COLOR)

        if current != self.start_node:
            self.draw_node(current, VISITED_COLOR)

        elapsed = int((time.time() - self.start_time) * 1000)
        self.lbl_visited.config(text=f"Nodes Visited: {self.nodes_visited}")
        self.lbl_time.config(text=f"Time: {elapsed} ms")

        self.root.after(20, self.step_search)

    def reconstruct_path(self):
        current = self.goal_node
        path_cost = 0
        while current.parent:
            if current != self.goal_node:
                self.draw_node(current, PATH_COLOR)
            current = current.parent
            path_cost += 1
            self.root.update()
            time.sleep(0.02)
        
        self.lbl_cost.config(text=f"Path Cost: {path_cost}")
        self.is_running = False

    def draw_node(self, node, color):
        x1, y1 = node.c * self.cell_size, node.r * self.cell_size
        x2, y2 = x1 + self.cell_size, y1 + self.cell_size
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#222222")

if __name__ == "__main__":
    root = tk.Tk()
    app = PathfindingGUI(root)
    root.mainloop()
