#!/usr/bin/python
# coding: utf-8

# 4, 7, 10, 13
# 3, 6, 9, 12
# 2, 5, 8, 11

# 2 => '00' | '01'
# 3 => '012' | '000' | '001' | '011'

class TileStyleRecord:
    def __init__(self):
        self.tsr_segment = {
                [4] = {},
                [7] = {},
                [10] = {},
                [13] = {},
                [3] = {},
                [6] = {},
                [9] = {},
                [12] = {},
                [2] = {},
                [5] = {},
                [8] = {},
                [11] = {},
                }

    def __del__(self):
        pass

    def load(self):
        pass

    def save(self):
        pass

    # tile_segment : '01123456'
    # kind : '0'
    def add_one_record(self, tile_segment, kind):
        seg_length = len(tile_segment)
        ts_info = self.tsr_segment[seg_length][tile_segment]
        if ts_info == None:
            self.tsr_segment[seg_length][tile_segment] = { kind : 1 }
        else:
            if ts_info[kind] == None:
                ts_info[kind] = 1
            else:
                ts_info[kind] += 1      # times + 1

    def add_records(self, records):
        for v in records:
            self.add_one_record(v.tile_segment, v.kind)

