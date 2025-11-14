#!/usr/bin/env python3
"""
mini_tbs.py — Mini Turn-Based Strategy prototype using Pygame
- Single-file prototype
- Click to select units
- Click a reachable tile to move; click an enemy in range to attack
- Press SPACE to end player turn
- Simple enemy AI moves toward nearest player and attacks if possible

Author: ChatGPT (tailored for you)
Run: python mini_tbs.py
"""

import pygame
import sys
import math
import random
from collections import deque

# -----------------------------
# CONFIG
# -----------------------------
TILE_SIZE = 64
MAP_W, MAP_H = 10, 8
SCREEN_W, SCREEN_H = TILE_SIZE * MAP_W, TILE_SIZE * MAP_H + 100  # extra for HUD
FPS = 60

# Colors
WHITE = (245, 245, 245)
BLACK = (12, 12, 12)
GRAY = (180, 180, 180)
LIGHT_GRAY = (210, 210, 210)
RED = (200, 50, 50)
GREEN = (60, 160, 60)
BLUE = (60, 120, 200)
YELLOW = (220, 200, 60)
DARK = (30, 30, 30)
TILE_HIGHLIGHT = (120, 220, 180, 120)

# -----------------------------
# Simple Data Classes
# -----------------------------
class Unit:
    def __init__(self, x, y, team, name="Soldier", hp=10, atk=4, mov=3, range_=1):
        self.x = x
        self.y = y
        self.team = team  # "player" or "enemy"
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.mov = mov
        self.range = range_
        self.has_moved = False
        self.has_acted = False

    def pos(self):
        return (self.x, self.y)

    def alive(self):
        return self.hp > 0

class Tile:
    def __init__(self, x, y, passable=True, cost=1):
        self.x = x
        self.y = y
        self.passable = passable
        self.cost = cost

# -----------------------------
# Utility functions
# -----------------------------
def in_bounds(x, y):
    return 0 <= x < MAP_W and 0 <= y < MAP_H

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# BFS to compute reachable tiles (simple movement range)
def compute_reachable(start, game_map, units, mov):
    sx, sy = start
    visited = {}
    q = deque()
    visited[(sx, sy)] = 0
    q.append((sx, sy))
    occupied = {u.pos() for u in units if u.alive()}

    while q:
        x, y = q.popleft()
        cost = visited[(x, y)]
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x+dx, y+dy
            if not in_bounds(nx, ny): 
                continue
            tile = game_map[ny][nx]
            if not tile.passable:
                continue
            new_cost = cost + tile.cost
            if new_cost > mov:
                continue
            # Treat occupied tiles as non-passable except the start tile
            if (nx, ny) in occupied and (nx, ny) != start:
                continue
            if (nx, ny) not in visited or new_cost < visited[(nx, ny)]:
                visited[(nx, ny)] = new_cost
                q.append((nx, ny))
    return set(visited.keys())

# Simple path finder (BFS) returns path as list of coords from start->target inclusive
def find_path(start, target, game_map, units):
    sx, sy = start
    tx, ty = target
    occupied = {u.pos() for u in units if u.alive() and u.pos() != start}
    q = deque()
    q.append((sx, sy))
    came_from = { (sx, sy): None }
    while q:
        x, y = q.popleft()
        if (x, y) == (tx, ty):
            break
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x+dx, y+dy
            if not in_bounds(nx, ny): continue
            tile = game_map[ny][nx]
            if not tile.passable: continue
            if (nx, ny) in occupied: continue
            if (nx, ny) not in came_from:
                came_from[(nx, ny)] = (x, y)
                q.append((nx, ny))
    if (tx, ty) not in came_from:
        return None  # no path
    # reconstruct
    path = []
    cur = (tx, ty)
    while cur is not None:
        path.append(cur)
        cur = came_from[cur]
    path.reverse()
    return path

# -----------------------------
# Game class
# -----------------------------
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Mini TBS — Blobbo Edition (Pygame prototype)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 18)
        self.bigfont = pygame.font.SysFont("Consolas", 32, bold=True)

        # create map: simple open map with some obstacles
        self.map = [[Tile(x, y) for x in range(MAP_W)] for y in range(MAP_H)]
        # randomly add some obstacles for variety
        for _ in range(int(MAP_W * MAP_H * 0.08)):
            rx = random.randrange(MAP_W)
            ry = random.randrange(MAP_H)
            self.map[ry][rx].passable = False

        # units
        self.units = []
        # player units (left side)
        self.units.append(Unit(1, 1, "player", name="Thorn", hp=14, atk=5, mov=4, range_=1))
        self.units.append(Unit(1, 3, "player", name="Caterina", hp=12, atk=4, mov=5, range_=1))
        # enemy units (right side)
        self.units.append(Unit(MAP_W-2, 2, "enemy", name="Goblin", hp=10, atk=3, mov=3, range_=1))
        self.units.append(Unit(MAP_W-2, 5, "enemy", name="Squire", hp=12, atk=4, mov=3, range_=1))

        # turn management
        self.turn = "player"  # or "enemy"
        self.selected_unit = None
        self.reachable = set()
        self.path_preview = []
        self.message = "Click one of your units to select it. SPACE to end turn."
        self.running = True

    def get_unit_at(self, x, y):
        for u in self.units:
            if u.alive() and (u.x, u.y) == (x, y):
                return u
        return None

    def world_to_grid(self, px, py):
        gx = px // TILE_SIZE
        gy = py // TILE_SIZE
        return gx, gy

    def grid_to_world(self, gx, gy):
        return gx * TILE_SIZE, gy * TILE_SIZE

    def select_unit(self, unit):
        if unit and unit.team == self.turn and unit.alive():
            self.selected_unit = unit
            self.reachable = compute_reachable(unit.pos(), self.map, self.units, unit.mov if not unit.has_moved else 0)
            self.path_preview = []
            self.message = f"Selected {unit.name} (HP:{unit.hp} ATK:{unit.atk} MOV:{unit.mov})"
        else:
            self.selected_unit = None
            self.reachable = set()
            self.path_preview = []
            self.message = "No selectable unit there."

    def handle_player_click(self, gx, gy):
        if self.turn != "player":
            return
        clicked_unit = self.get_unit_at(gx, gy)
        if clicked_unit and clicked_unit.team == "player":
            # select/deselect
            self.select_unit(clicked_unit)
            return

        if not self.selected_unit:
            self.message = "Select a unit first."
            return

        # If clicked on reachable tile -> attempt to move
        if (gx, gy) in self.reachable:
            path = find_path(self.selected_unit.pos(), (gx, gy), self.map, self.units)
            if path:
                # Move the unit along path (instant)
                self.selected_unit.x, self.selected_unit.y = gx, gy
                self.selected_unit.has_moved = True
                self.reachable = compute_reachable(self.selected_unit.pos(), self.map, self.units, 0)  # can't move again
                self.path_preview = []
                self.message = f"{self.selected_unit.name} moved to {gx},{gy}."
        else:
            # If clicked on enemy in attack range -> attack
            target = self.get_unit_at(gx, gy)
            if target and target.team != self.selected_unit.team:
                dist = manhattan(self.selected_unit.pos(), target.pos())
                if dist <= self.selected_unit.range:
                    # attack
                    damage = self.selected_unit.atk
                    target.hp -= damage
                    self.selected_unit.has_acted = True
                    self.message = f"{self.selected_unit.name} attacked {target.name} for {damage} dmg!"
                    if target.hp <= 0:
                        self.message += f" {target.name} falls!"
                else:
                    self.message = "Target out of range."
            else:
                self.message = "Can't move/attack there."

    def end_player_turn(self):
        # reset movement/actions for enemy units before switching
        for u in self.units:
            u.has_moved = False
            u.has_acted = False
        self.turn = "enemy"
        self.selected_unit = None
        self.reachable = set()
        self.message = "Enemy turn..."
        pygame.time.set_timer(pygame.USEREVENT + 1, 500)  # schedule enemy actions

    # Very basic enemy AI: for each enemy, find nearest player, path toward them and attack if in range
    def enemy_phase(self):
        enemies = [u for u in self.units if u.team == "enemy" and u.alive()]
        players = [u for u in self.units if u.team == "player" and u.alive()]
        if not enemies or not players:
            self.turn = "player"
            self.message = "Player turn."
            return

        for e in enemies:
            if not players:
                break
            # find nearest player
            players_alive = [p for p in players if p.alive()]
            if not players_alive:
                break
            target = min(players_alive, key=lambda p: manhattan(e.pos(), p.pos()))
            # if in range, attack
            if manhattan(e.pos(), target.pos()) <= e.range:
                target.hp -= e.atk
                self.message = f"{e.name} attacked {target.name} for {e.atk}!"
                if target.hp <= 0:
                    self.message += f" {target.name} falls!"
            else:
                # move toward target one step at a time up to mov
                for _ in range(e.mov):
                    # choose neighbor that reduces distance and is passable/unoccupied
                    best = None
                    bestd = manhattan(e.pos(), target.pos())
                    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                        nx, ny = e.x + dx, e.y + dy
                        if not in_bounds(nx, ny): continue
                        tile = self.map[ny][nx]
                        if not tile.passable: continue
                        if self.get_unit_at(nx, ny) is not None: continue
                        d = manhattan((nx, ny), target.pos())
                        if d < bestd:
                            bestd = d
                            best = (nx, ny)
                    if best:
                        e.x, e.y = best
                    else:
                        break
                # After moving, if now in range, attack
                if target.alive() and manhattan(e.pos(), target.pos()) <= e.range:
                    target.hp -= e.atk
                    self.message = f"{e.name} moved and attacked {target.name} for {e.atk}!"
                    if target.hp <= 0:
                        self.message += f" {target.name} falls!"

        # After enemy actions, switch back
        self.turn = "player"
        # reset player unit moved/acted flags for next player turn
        for p in self.units:
            if p.team == "player":
                p.has_moved = False
                p.has_acted = False
        self.message += " Player turn."

    def update(self, dt):
        # cleanup dead units
        for u in self.units:
            if u.hp <= 0:
                u.hp = 0

    def draw(self):
        self.screen.fill(DARK)
        # draw grid
        for y in range(MAP_H):
            for x in range(MAP_W):
                tile = self.map[y][x]
                rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                color = LIGHT_GRAY if tile.passable else (100,100,100)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, BLACK, rect, 1)

        # highlight reachable tiles if unit selected
        if self.selected_unit:
            s = self.selected_unit
            for (gx, gy) in self.reachable:
                rect = pygame.Rect(gx*TILE_SIZE, gy*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                surf.fill((120, 220, 180, 90))
                self.screen.blit(surf, rect.topleft)

        # draw units
        for u in self.units:
            if not u.alive():
                continue
            wx, wy = self.grid_to_world(u.x, u.y)
            u_rect = pygame.Rect(wx+6, wy+6, TILE_SIZE-12, TILE_SIZE-12)
            color = BLUE if u.team == "player" else RED
            pygame.draw.rect(self.screen, color, u_rect, border_radius=6)
            # health bar
            hp_ratio = u.hp / max(1, u.max_hp)
            hb_rect = pygame.Rect(wx+6, wy+TILE_SIZE-14, int((TILE_SIZE-12)*hp_ratio), 8)
            pygame.draw.rect(self.screen, GREEN, hb_rect)
            # unit label
            label = self.font.render(u.name[0], True, WHITE)
            self.screen.blit(label, (wx+TILE_SIZE//2-6, wy+TILE_SIZE//2-12))

            # selection ring
            if self.selected_unit == u:
                pygame.draw.rect(self.screen, YELLOW, u_rect, 3, border_radius=6)

        # HUD area
        hud_rect = pygame.Rect(0, MAP_H * TILE_SIZE, SCREEN_W, 100)
        pygame.draw.rect(self.screen, BLACK, hud_rect)
        # message
        msg_surf = self.font.render(self.message, True, WHITE)
        self.screen.blit(msg_surf, (8, MAP_H * TILE_SIZE + 8))

        # draw selected unit stats
        if self.selected_unit:
            su = self.selected_unit
            stats = f"{su.name}  HP: {su.hp}/{su.max_hp}  ATK: {su.atk}  MOV: {su.mov}  RANGE: {su.range}"
            s_surf = self.font.render(stats, True, WHITE)
            self.screen.blit(s_surf, (8, MAP_H * TILE_SIZE + 36))

        # draw turn info
        turn_surf = self.bigfont.render(f"Turn: {self.turn.upper()}", True, WHITE)
        self.screen.blit(turn_surf, (SCREEN_W - 220, MAP_H * TILE_SIZE + 10))

        # draw instructions
        instr = "Click player unit to select → click tile to move → click enemy to attack. SPACE to end turn."
        i_surf = self.font.render(instr, True, GRAY)
        self.screen.blit(i_surf, (8, MAP_H * TILE_SIZE + 64))

        pygame.display.flip()

    def run(self):
        enemy_action_pending = False
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    if my < MAP_H * TILE_SIZE:
                        gx, gy = self.world_to_grid(mx, my)
                        if self.turn == "player":
                            self.handle_player_click(gx, gy)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.turn == "player":
                            self.end_player_turn()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                elif event.type == pygame.USEREVENT + 1:
                    # time to run enemy actions
                    pygame.time.set_timer(pygame.USEREVENT + 1, 0)
                    self.enemy_phase()

            self.update(dt)
            self.draw()

            # check win/lose
            player_alive = any(u.alive() and u.team == "player" for u in self.units)
            enemy_alive = any(u.alive() and u.team == "enemy" for u in self.units)
            if not player_alive:
                self.message = "All players defeated. YOU LOSE. (R to restart)"
            if not enemy_alive:
                self.message = "All enemies defeated. YOU WIN! (R to restart)"

            # quick restart keys
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                self.__init__()  # re-init the whole game
            # end run loop if escape pressed handled above

        pygame.quit()
        sys.exit()

# -----------------------------
# Run the game
# -----------------------------
if __name__ == "__main__":
    Game().run()
