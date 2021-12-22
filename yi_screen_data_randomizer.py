import random
import struct
import itertools
import copy

class Screen_Exit_Data:
    def __init__(self, target_page, destination, x_coord, y_coord, entrance_or_return):
        self.target_page = target_page
        self.destination = destination
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.entrance = entrance_or_return

    @staticmethod
    def from_bytes(bytes):
        """Returns a Screen Exit Data object from a 5 byte chunk."""
        #print('b', bytes, len(bytes))
        return Screen_Exit_Data(bytes[0], bytes[1], bytes[2], bytes[3], bytes[4])

    def __str__(self):
        return '{:02X} {:02X} {:02X} {:02X} {:02X}'.format(self.target_page, self.destination, self.x_coord, self.y_coord, self.entrance)

    def data_overlay(self, new_exit):
        """Returns a 5 byte chunk with the new exit data."""
        return struct.pack('@BBBBB', self.target_page, new_exit.destination, new_exit.x_coord, new_exit.y_coord, new_exit.entrance)


class Level(object):
    def __init__(self, path):
        self.path = path
        self.stage = None
        self.old_exits = None
        self.new_exits = None

        with open(path, 'rb') as f:
            blob = f.read()

            start_byte = 0
            # Find the starting index for the screen exit data by iterating backwards.
            for index in range(len(blob)-2, 0, -5):
                if blob[index] == 0xFF:
                    start_byte = index + 1
                    break

            self.stage = blob[:start_byte]
            # Create a list of Screen Exit Data objects from the level data.
            self.old_exits = [Screen_Exit_Data.from_bytes(blob[k:k+5]) for k in range(start_byte, len(blob), 5) if len(blob[k:k+5]) == 5]

    def take_new_exits(self, exit_list):
        """Assign new exit data to the Level object."""
        self.new_exits = []
        for _ in range(len(self.old_exits)):
            self.new_exits.append(exit_list.pop())

    def output_data(self):
        """Returns constructed level data with new exit(s), if any exist."""
        print('Level {}\nold exits:'.format(self.path))
        for exit in self.old_exits:
            print(exit)
        print('new exits:')
        for exit in self.new_exits:
            print(exit)
        exit_data = b''.join([old_exit.data_overlay(new_exit) for (old_exit, new_exit) in zip(self.old_exits, self.new_exits)])
        return self.stage + exit_data + b'\xff'

    def write(self):
        """Writes the level data to file."""
        with open(self.path, 'wb') as f:
            f.write(self.output_data())

EXCLUDED_LEVELS = [125]                 # Levels that don't follow proper formatting.
LAST_LEVEL = 222

# Create a list of Level objects from each level binary.
levels = [Level('level/level-{:02X}-obj.bin'.format(l)) for l in range(LAST_LEVEL+1) if l not in EXCLUDED_LEVELS]
# Create a list of Screen Exit Data objects from all Levels.
all_exits = list(itertools.chain(*[l.old_exits for l in levels]))
random.shuffle(all_exits)               # Randomize order.

new_levels = copy.deepcopy(levels)
for nl in new_levels:
    nl.take_new_exits(all_exits)        # Assign new exit data.
    nl.write()
