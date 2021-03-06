import math
import pygame
import main
import board
import tiles
import hexes
import player

BOARD_COLOR = (0, 30, 100) #blue
BOARD_HEX_BORDER_COLOR = (100, 100, 100) #grey
BOARD_HEX_BORDER_WIDTH = 2
BOARD_HEX_WIDTH = 23
BOARD_MAX_LEVEL = 5

# return the number of tiles the board can fit
def get_num_board_zones():
    return int((math.pow(BOARD_MAX_LEVEL + 1, 2) + BOARD_MAX_LEVEL + 1) / 2)

class Board(object):
    _game_engine = None
    _board_screen = None
    _tiles = None
    _board_zones_collection = None
    board_max_level = None

    def __init__(self, screen, new_game_engine):
        self._game_engine = new_game_engine
        self._board_screen = screen

        # build tiles
        self._tiles = tiles.Tiles(self._game_engine)
        # build zones on board where tiles fit
        self._board_zones_collection = []
        for i in range(get_num_board_zones()):
            self._board_zones_collection.append(hexes.Hexes())
            self._board_zones_collection[i].number = i

    # given a point, return coordinates for a hex to paint hex
    def _return_hex_coordinates(self, location_x, location_y):
        pl = [(location_x - BOARD_HEX_WIDTH, location_y),
              (location_x - BOARD_HEX_WIDTH/2, location_y - BOARD_HEX_WIDTH),
              (location_x + BOARD_HEX_WIDTH/2, location_y - BOARD_HEX_WIDTH),
              (location_x + BOARD_HEX_WIDTH, location_y),
              (location_x + BOARD_HEX_WIDTH/2, location_y + BOARD_HEX_WIDTH),
              (location_x - BOARD_HEX_WIDTH/2, location_y + BOARD_HEX_WIDTH)]
        return pl

    # build the empty board.
    def _build_tile_holder(self, zone_num, color, location_x, location_y):
        hex0x = location_x
        hex0y = location_y
        hex1x = location_x + 1.5*BOARD_HEX_WIDTH
        hex1y = location_y - BOARD_HEX_WIDTH
        hex2x = hex1x + 1.5*BOARD_HEX_WIDTH
        hex2y = location_y
        hex3x = hex2x
        hex3y = hex2y + 2*BOARD_HEX_WIDTH
        hex4x = hex1x
        hex4y = hex1y + 4*BOARD_HEX_WIDTH
        hex5x = hex0x
        hex5y = hex1y + 3*BOARD_HEX_WIDTH
        hex6x = hex1x
        hex6y = hex1y + 2*BOARD_HEX_WIDTH
        for i in range(0, 7):
            exec("pl" + str(i) + " = self._return_hex_coordinates(hex" + str(i) + "x, hex" + str(i) + "y)")
            self._board_zones_collection[zone_num].hex_collection[i].polygon = eval('pl' + str(i))
            pygame.draw.polygon(self._board_screen, color, eval('pl' + str(i)))
            pygame.draw.polygon(self._board_screen, BOARD_HEX_BORDER_COLOR, eval('pl' + str(i)), BOARD_HEX_BORDER_WIDTH)
    
    # return tile number and hex number based upon mouse coordinates
    def get_board_zone(self, coordinates):
        click_x, click_y = coordinates
        for zone_num in range(board.get_num_board_zones()):
            for hex_num in range(7):
                if self.point_inside_polygon(click_x, click_y, self._board_zones_collection[zone_num].hex_collection[hex_num].polygon):
                    return (zone_num, hex_num)
                
    # return coordinates based upon tile location and hex number
    # yes the logic is duplicated code from _build_tile_holder and should be refactored
    def get_coordinates(self, tile_location, hex_num):
        h = (math.sin(math.radians(30))*BOARD_HEX_WIDTH)
        tile_x, tile_y = tile_location
        hex0x = tile_x
        hex0y = tile_y
        hex1x = tile_x + 1.5*BOARD_HEX_WIDTH
        hex1y = tile_y - BOARD_HEX_WIDTH
        hex2x = hex1x + 1.5*BOARD_HEX_WIDTH
        hex2y = tile_y
        hex3x = hex2x
        hex3y = hex2y + 2*BOARD_HEX_WIDTH
        hex4x = hex1x
        hex4y = hex1y + 4*BOARD_HEX_WIDTH
        hex5x = hex0x
        hex5y = hex1y + 3*BOARD_HEX_WIDTH
        hex6x = hex1x
        hex6y = hex1y + 2*BOARD_HEX_WIDTH

        coord_x = eval("hex" + str(hex_num) + "x")
        coord_y = eval("hex" + str(hex_num) + "y")
        
        return (coord_x, coord_y)

    # mouse dragging on board.  moving player and tile exploration is handled here
    # also indirectly handles mouse clicks for debugging purposees only
    def check_mousedrag(self, mousedown_coordinates, mouseup_coordinates):
        mousedown_location = self.get_board_zone(mousedown_coordinates)
        mouseup_location = self.get_board_zone(mouseup_coordinates)
        
        # make sure click was on board and not elsewhere that doesn't concern this board
        if(mousedown_location != None and mouseup_location != None):
            # mouse has been dragged and clicked.  not just clicked
            # check for exploration
            if mousedown_location != mouseup_location:
                chosen_player = None
                if self._game_engine.chosen_player == player.ARYTHREA:
                    chosen_player = self._game_engine.arythrea
                #check if clicked on player sprite and if dragged to adjacent hex
                if chosen_player.rect.collidepoint(mousedown_coordinates) and \
                     self.return_if_hexes_adjacent(mousedown_coordinates, mouseup_coordinates): 
                        # check if dragged from tile to board 
                        if isinstance(self._tiles.tile_collection[mouseup_location[0]].hexes.hex_collection[mouseup_location[1]], hexes.HexNonPlaceholder) == False \
                            and chosen_player.move >= 2:
                            new_tile = self._tiles.draw()
                            if new_tile == None:
                                print("No more tiles left")
                                return False
                            else:
                                # first load the image - to be drawn once and only once
                                # place new tile in tile collection to be placed on board when building board
                                # and place in game engine's sprite collection and tile group to be drawn - to be magnified
                                new_tile.load()
                                self._tiles.tile_collection[mouseup_location[0]] = new_tile
                                self._game_engine.magnify_collection.append(new_tile)
                                self._game_engine.tile_group.add(new_tile)
                                chosen_player.move -= 2
                                print("Movement Cost: 2" + " | Move Points: " + str(chosen_player.move))
                        else:
                            movement_cost = None
                            try:
                                movement_cost = self._tiles.tile_collection[mouseup_location[0]].hexes.hex_collection[mouseup_location[1]].movement_cost
                            except TypeError:
                                print("Is Either Forest or Desert")
                            try:
                                movement_cost = self._tiles.tile_collection[mouseup_location[0]].hexes.hex_collection[mouseup_location[1]].movement_cost(self._game_engine.time_of_day)
                            except TypeError:
                                print("Not Forest or Desert")
                            # check for walls. add 1 if crossing wall
                            if self._tiles.tile_collection[mouseup_location[0]].walls.return_if_cross_wall(mousedown_location[1], mouseup_location[1]):
                                if movement_cost:
                                    movement_cost += 1
                            if movement_cost != None and chosen_player.move >= movement_cost:
                                # update player location
                                chosen_player.location_tile_num = mouseup_location[0]
                                chosen_player.location_hex_num = mouseup_location[1]
                                chosen_player.move -= movement_cost
                                print("Movement Cost: " + str(movement_cost) + " | Move Points: " + str(chosen_player.move))
                            else:
                                print("Unable to Cross. Movement Cost: " + str(movement_cost) + "  Move Points: " + str(chosen_player.move))
                                return False
            else:
                print("Mousedown Location - Tile #:" +str(mousedown_location[0])+ " | Hex #:" + str(mousedown_location[1]))
                print("Mouseup Location - Tile #:" +str(mouseup_location[0])+ " | Hex #:" + str(mouseup_location[1]))
                if isinstance(self._tiles.tile_collection[mousedown_location[0]], tiles.TileNonPlaceholder):
                    print(self._tiles.tile_collection[mousedown_location[0]].hexes.hex_collection[mousedown_location[1]])
        return True
    
    # based upon the distance between the two coordinates.  cludgy way of determining whether hexes are adjacent                                
    def return_if_hexes_adjacent(self, hex1_coordinates, hex2_coordinates):
        dist = math.hypot(hex2_coordinates[0] - hex1_coordinates[0], hex2_coordinates[1] - hex1_coordinates[1])
        if dist > 2 * BOARD_HEX_WIDTH:
            return False
        else:
            return True

    # determine if a point is inside a given polygon or not
    # Polygon is a list of (x,y) pairs.
    # http://www.ariel.com.au/a/python-point-int-poly.html
    def point_inside_polygon(self, x,y,poly):
        n = len(poly)
        inside =False

        p1x,p1y = poly[0]
        for i in range(n+1):
            p2x,p2y = poly[i % n]
            if y > min(p1y,p2y):
                if y <= max(p1y,p2y):
                    if x <= max(p1x,p2x):
                        if p1y != p2y:
                            xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x,p1y = p2x,p2y
        return inside

    # build board -> then paint tiles -> then paint tokens -> then player 
    def build(self):
        h = (math.sin(math.radians(30))*BOARD_HEX_WIDTH)
            
        #level 0
        x0 = main.GAME_SCREEN_WIDTH/5
        y0 = 2*BOARD_HEX_WIDTH
        self._build_tile_holder(0, BOARD_COLOR, x0, y0)
    
        board_zone_num = 0
        first_time_num_for_current_level = 0
        first_board_zone_num_on_previous_level = 0
        for level in range(1, BOARD_MAX_LEVEL+1):
            for board_zone_num_for_level in range(level+1):
                board_zone_num += 1
                # if drawing the last tile for the level
                if board_zone_num_for_level == level:
                    exec("x" +str(board_zone_num)+ " = 2*h+2*BOARD_HEX_WIDTH+x" +str(board_zone_num-level-1))
                    exec("y" +str(board_zone_num)+ " = 4*BOARD_HEX_WIDTH+y" +str(board_zone_num-level-1))
                # if drawing the first tile for the level
                elif board_zone_num_for_level == 0:
                    exec("x" +str(board_zone_num)+ " = -h-BOARD_HEX_WIDTH+x" +str(first_board_zone_num_on_previous_level+board_zone_num_for_level))
                    exec("y" +str(board_zone_num)+ " = 5*BOARD_HEX_WIDTH+y" +str(first_board_zone_num_on_previous_level+board_zone_num_for_level))
                    first_time_num_for_current_level = first_board_zone_num_on_previous_level 
                    first_board_zone_num_on_previous_level = board_zone_num
                # if drawing all other tiles
                else:
                    exec("x" +str(board_zone_num)+ " = -h-BOARD_HEX_WIDTH+x" +str(first_time_num_for_current_level+board_zone_num_for_level))
                    exec("y" +str(board_zone_num)+ " = 5*BOARD_HEX_WIDTH+y" +str(first_time_num_for_current_level+board_zone_num_for_level))
                self._build_tile_holder(board_zone_num, eval("[i + 20 * " +str(level)+ " for i in BOARD_COLOR]"), eval("x" +str(board_zone_num)), eval("y" +str(board_zone_num)))
        # paint tiles
        for i in range(len(self._tiles.tile_collection)):
            if isinstance(self._tiles.tile_collection[i], tiles.TileNonPlaceholder):
                self._tiles.tile_collection[i].set_board_location(eval("x" + str(i)), eval("y" + str(i)))
        self._game_engine.tile_group.draw(self._board_screen)
        
        # then paint tokens
        
        # paint player miniature
        if self._game_engine.chosen_player == player.ARYTHREA:
            x, y = self.get_coordinates((eval("x" + str(self._game_engine.arythrea.location_tile_num)), eval("y" + str(self._game_engine.arythrea.location_tile_num))), self._game_engine.arythrea.location_hex_num)
            self._game_engine.arythrea.set_board_location(x, y)

        self._game_engine.player_group.draw(self._board_screen)