import tkinter as tk
from queue import PriorityQueue
class Node:
    def __init__(self, state, parent=None, action=None, cost=0, heuristic=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.heuristic = heuristic

    def __lt__(self, other):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)
class Room:
    def __init__(self, name):
        self.name = name
        self.walls = set()
        self.cost = 0

class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze")

        self.rooms = {}
        self.create_rooms()
        self.create_gui()

    def create_rooms(self):
        room_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']

        for name in room_names:
            self.rooms[name] = Room(name)

    def create_gui(self):
        self.canvas = tk.Canvas (self.root, width=300, height=300, bg="white")  # background color
        self.canvas.pack ( )

        self.draw_grid ( )

        tk.Label (self.root, text="Source Room:").pack ( )
        self.source_entry = tk.Entry (self.root, relief=tk.GROOVE)
        self.source_entry.pack ( )

        tk.Label (self.root, text="Goal Room:").pack ( )
        self.goal_entry = tk.Entry (self.root, relief=tk.GROOVE)
        self.goal_entry.pack ( )

        tk.Label (self.root, text="Walls (e.g., AD GH BC EF):").pack ( )
        self.walls_entry = tk.Entry (self.root, relief=tk.GROOVE)
        self.walls_entry.pack ( )

        tk.Label (self.root, text="Search Strategy (UC or A*):").pack ( )
        self.strategy_entry = tk.Entry (self.root, relief=tk.GROOVE)
        self.strategy_entry.pack ( )

        tk.Button (self.root, text="Find", command=self.start_game).pack ( )

    def draw_grid(self):
        for row in range(3):
            for col in range(3):
                room_name = chr(65 + row * 3 + col)
                # Color
                self.canvas.create_rectangle(col * 100, row * 100, (col + 1) * 100, (row + 1) * 100, fill="lightblue")
                self.canvas.create_text((col + 0.5) * 100, (row + 0.5) * 100, text=room_name, fill="black")

    def start_game(self):
        source = self.source_entry.get().upper()
        goal = self.goal_entry.get().upper()
        walls = self.walls_entry.get().upper().split()
        strategy = self.strategy_entry.get().upper()

        self.set_walls(walls)

        path = self.search(source, goal, strategy)

        if path:
            self.highlight_path(path)
        else:
            print("No path found")

    def set_walls(self, walls):
        for wall in walls:
            room1, room2 = wall[0], wall[1]
            self.rooms[room1].walls.add(room2)
            self.rooms[room2].walls.add(room1)

        self.draw_walls()

    def draw_walls(self, unit_size=100):
        for room_name, room in self.rooms.items():
            room_row, room_col = divmod(ord(room_name) - ord('A'), 3)
            for neighbor_name in room.walls:
                neighbor_row, neighbor_col = divmod(ord(neighbor_name) - ord('A'), 3)

                if room_row == neighbor_row:
                    # Horizontal wall
                    min_col = min(room_col, neighbor_col)
                    # Change the  color
                    self.canvas.create_line((min_col + 1) * unit_size, room_row * unit_size,
                                            (min_col + 1) * unit_size, (room_row + 1) * unit_size,
                                            width=5, fill="blue")
                elif room_col == neighbor_col:
                    # Vertical wall
                    min_row = min(room_row, neighbor_row)
                    # Change the line color to blue
                    self.canvas.create_line(room_col * unit_size, (min_row + 1) * unit_size,
                                            (room_col + 1) * unit_size, (min_row + 1) * unit_size,
                                            width=5, fill="blue")
    def search(self, source, goal, strategy):
        start_room = self.rooms[source]
        goal_room = self.rooms[goal]

        if strategy == 'UC':
            return self.uniform_cost_search(start_room, goal_room)
        elif strategy == 'A*':
            return self.a_star_search(start_room, goal_room)
        else:
            print("Invalid search strategy.")
            return None

    def calculate_move_cost(self, curr, next_room):

        row1, col1 = divmod(ord(curr) - ord('A'), 3)
        row2, col2 = divmod(ord(next_room) - ord('A'), 3)

        # Right/left move
        if row1 == row2:
            return 2

        # Up/down move
        if col1 == col2:
            return 1


        raise ValueError("Invalid room movement")


    def uniform_cost_search(self, start, goal):

        visited = set ( )
        queue = PriorityQueue ( )
        queue.put ((0, start.name, [start.name]))
        expanded_nodes = 0

        while not queue.empty ( ) and expanded_nodes < 10:
            cost, current_name, path = queue.get ( )
            if current_name in visited:
                continue

            visited.add (current_name)
            expanded_nodes += 1
            print (f"Expanded Node {expanded_nodes}: {current_name} with path: {' -> '.join (path)}, cost: {cost}")

            if current_name == goal.name:
                return path


            neighbors = [(neighbor_name, self.calculate_move_cost (current_name, neighbor_name)) for neighbor_name in
                         self.get_neighbors (current_name)]


            neighbors.sort (key=lambda x: x[1])

            for neighbor_name, move_cost in neighbors:
                if neighbor_name not in visited:
                    new_cost = cost + move_cost
                    queue.put ((new_cost, neighbor_name, path + [neighbor_name]))

        return None

    def a_star_search(self, start, goal):

        visited = set()
        queue = PriorityQueue()
        queue.put((0, start.name, [start.name]))
        expanded_nodes = 0

        while not queue.empty() and expanded_nodes < 10:
            cost, current_name, path = queue.get()
            if current_name in visited:
                continue

            visited.add(current_name)
            expanded_nodes += 1
            print(f"Expanded Node {expanded_nodes}: {current_name} with path: {' -> '.join(path)}, cost: {cost}")

            if current_name == goal.name:
                return path

            for neighbor_name in self.get_neighbors(current_name):
                if neighbor_name not in visited:
                    move_cost = self.calculate_move_cost(current_name, neighbor_name)
                    heuristic = self.calculate_hamming_distance(neighbor_name, goal.name)
                    queue.put((cost + move_cost + heuristic, neighbor_name, path + [neighbor_name]))

        return None

    def get_neighbors(self, room_name):

        row, col = divmod(ord(room_name) - ord('A'), 3)
        potential_moves = [
            ('left', (row, col - 1)),
            ('right', (row, col + 1)),
            ('up', (row - 1, col)),
            ('down', (row + 1, col))
        ]
        neighbors = []
        for direction, (r, c) in potential_moves:
            if 0 <= r < 3 and 0 <= c < 3:
                neighbor_name = chr(ord('A') + r * 3 + c)
                if neighbor_name not in self.rooms[room_name].walls:
                    neighbors.append(neighbor_name)
        return neighbors


    def calculate_hamming_distance(self, room1, room2):

        row1, col1 = divmod(ord(room1) - ord('A'), 3)
        row2, col2 = divmod(ord(room2) - ord('A'), 3)
        return abs(row1 - row2) + abs(col1 - col2)

    def highlight_path(self, path):
        for i in range (len (path) - 1):
            room1 = path[i]
            room2 = path[i + 1]

            if room2 in self.rooms[room1].walls:
                continue

            row1, col1 = divmod (ord (room1) - ord ('A'), 3)
            row2, col2 = divmod (ord (room2) - ord ('A'), 3)


            self.canvas.create_line ((col1 + 0.5) * 100, (row1 + 0.5) * 100,
                                     (col2 + 0.5) * 100, (row2 + 0.5) * 100,
                                     width=3, fill="red",
                                     dash=(5, 5))
if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()