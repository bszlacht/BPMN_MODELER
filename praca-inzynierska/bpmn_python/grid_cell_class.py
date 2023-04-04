# coding=utf-8
"""
GridCell represents a single cell with node element on two-dimensional grid layout. It is used in diagram layouting
process
"""


class GridCell(object):
    """
    Helper class used for Grid cell representation. Contains cell coordinates (row and column) and reference to fow node
    """

    def __init__(self, row, col, branches, node_id):
        self.row = row
        self.col = col
        self.branches = branches
        self.node_id = node_id

    def __str__(self):
        return repr(self.row + " " + self.col + " " + self.node_id)