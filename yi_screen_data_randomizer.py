import random

class Screen_Exit_Data:
    def __init__(self, target_page, destination, x_coord, y_coord, entrance_or_return):
        self.target_page = target_page
        self.destination = destination
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.entrance = entrance_or_return

    def __str__(self):
        return '{:02X} {:02X} {:02X} {:02X} {:02X}'.format(self.target_page, self.destination, self.x_coord, self.y_coord, self.entrance)



level = 0
screen_exits_master = []
while '{:02X}'.format(level) < 'DE':                                    # Hardcoded for vanilla, can alternatively just run until file not found exception
    try:
        with open("level-{:02X}-obj.bin".format(level), "rb") as f:
            bytes_read = f.read()
        f.close()
        index = 2                                                       # screen exit data exists at the end of the level object binaries;
        screen_exits = []                                               # preceded, and followed, by one byte of value FF
        print('Level {:02X}'.format(level))
        while True:                                                     # iterate backwards from the end of the file
            if bytes_read[-index] == 255: # and (index - 2) % 5 == 0:   # each screen exit entry is always 5 bytes, the last byte will never be FF
                break                                                   # so, if the last byte is FF, we've processed all screen exit data, or none exists
            else:                                                       # if it is screen exit data, create the object and add to screen exit data list
                screen_exits.append(Screen_Exit_Data(bytes_read[-(index+4)],bytes_read[-(index+3)],bytes_read[-(index+2)],bytes_read[-(index+1)],bytes_read[-index]))
                index += 5                                              # attempt to find the next entry
        for x in screen_exits:
            screen_exits_master.append(x)                               # if no exceptions, add all the data to the master list of screen exit data
        for x in screen_exits:
            print('\t{}'.format(x))
    except Exception as e:
        print('{} at level = {}'.format(e,level))
    level += 1
#for x in screen_exits_master:
#    print('{:02X} {:02X} {:02X} {:02X} {:02X}'.format(x.target_page, x.destination, x.x_coord, x.y_coord, x.entrance))
randomized = screen_exits_master.copy()                                 # unnecessary copy
random.shuffle(randomized)

level = 0
while '{:02X}'.format(level) < 'DE':
    with open("level-{:02X}-obj.bin".format(level), "rb") as f:
        bytes_read = f.read()
    f.close()
    bytes_read_list = list(bytes_read)                                  # the binary structure is indexable, but immutable, so convert to a list to reassign bytes
    index = 2
    while True:
        if bytes_read[-index] == 255: # and (index - 2) % 5 == 0:
            break
        else:
            bytes_read_list[-(index+3)] = randomized[0].destination     # replace the existing screen exit data with a random entry
            bytes_read_list[-(index+2)] = randomized[0].x_coord
            bytes_read_list[-(index+1)] = randomized[0].y_coord
            bytes_read_list[-(index)] = randomized[0].entrance
            index += 5
            del randomized[0]                                           # screen exit data has been used, so get rid of it ;TODO: just increment an index (for performance reasons)
    #print(bytes(bytes_read_list))
    with open("level-{:02X}-obj.bin".format(level), "wb") as f:
        f.write(bytes(bytes_read_list))                                 # convert the list to bytes and write back to file 
    f.close()
    level += 1
    if level == 125:                                                    # this one level doesn't follow the convention of FF before and after screen data, and has no screen exit data anyway, so ignore it completely
        level += 1
