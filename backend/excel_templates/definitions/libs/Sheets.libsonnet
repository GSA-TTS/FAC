local single_cell = {
    type: "single_cell",
    title: "Example Cell",
    range_name: "example_cell",
    title_cell: "A1",
    range_cell: "B1"
};


local open_range = {
    type: "open_range",
    title: "Example open range",
    range_name: "Example open range",
    title_cell: "A1",
    // Range start is redundant. 
    // It should start below the title cell.
    // range_start: "B1" 
};

local y_or_n_range = open_range + {
        type: "yorn_range",
        title: "Example YorN range",
        range_name: "Example YorN range"
};

# MAX_ROWS here is equal to MAX_ROWS in render.py plus 1 to account for the header row.
local MAX_ROWS = 3001;

local open_range_a3_w36 = open_range + {
  title_cell: 'A3',
  width: 36,
};

local open_range_c3_w100 = open_range + {
  title_cell: 'C3',
  width: 100,
};

local y_or_n_range_g3_w36 = y_or_n_range + {
  title_cell: 'G3',
  width: 36,
};

local open_range_w12 = open_range + {
  width: 12,
};

local open_range_w48 = open_range + {
  width: 48,
};

{
    single_cell: single_cell,
    open_range: open_range,
    y_or_n_range: y_or_n_range,
    open_range_w12: open_range_w12,
    open_range_w48: open_range_w48,
    open_range_a3_w36: open_range_a3_w36,
    open_range_c3_w100: open_range_c3_w100,
    y_or_n_range_g3_w36: y_or_n_range_g3_w36,
    MAX_ROWS: MAX_ROWS
}