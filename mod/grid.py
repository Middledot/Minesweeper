"""Grid object used for the minefield"""

class Grid:
    def __init__(self, width, height, default):
        self._grid = [[default for i in range(width)] for j in range(height)]

    @property
    def cellno(self):
        return self.cols() * self.rows()

    def __str__(self):
        out = ""
        for row in self._grid:
            out += str(row) +"\n"
        return out

    def __iter__(self):
        for y in range(len(self._grid)):
            for x in range(len(self._grid[y])):
                yield (x, y)

    def get(self, pos):
        """Get the values of given coordinates on the grid."""
        x, y = pos
        # TODO: assuming this is dangerous (!!!)
        return self._grid[y][x]

    def set(self, pos, value):
        """Set the value of a cell. Refer to the data guide."""
        x, y = pos
        self._grid[y][x] = value
    
    def set_all(self, value):
        #set all cells to the given value
        for x, y in self:
            self.set((x, y), value)
    
    def cols(self):
        """Return the number of columns in a grid."""
        return len(self._grid[0])
    
    def rows(self):
        """Return the number of rows in the grid."""
        return len(self._grid)

    def iterneighbours(self, pos):
        """Iterate the valid neighbours of a coordinate."""
        x, y = pos

        if y > 0:
            yield x, y-1
        if y < self.rows()-1:
            yield x, y+1
        if x > 0:
            yield x-1, y
            if y > 0:
                yield x-1, y-1
            if y < self.rows()-1:
                yield x-1, y+1
        if x < self.cols()-1:
            yield x+1, y
            if y > 0:
                yield x+1, y-1
            if y < self.rows()-1:
                yield x+1, y+1
