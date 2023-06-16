local single_cell = {
  type: 'single_cell',
  title: 'Example Cell',
  range_name: 'example_cell',
  title_cell: 'A1',
  range_cell: 'B1',
};


local open_range = {
  type: 'open_range',
  title: 'Example open range',
  range_name: 'Example open range',
  title_cell: 'A1',
  // Range start is redundant.
  // It should start below the title cell.
  // range_start: "B1"
};

local y_or_n_range = open_range {
  type: 'yorn_range',
  title: 'Example YorN range',
  range_name: 'Example YorN range',
};

// MAX_ROWS here is equal to MAX_ROWS in render.py plus 1 to account for the header row.
local MAX_ROWS = 3001;

{
  single_cell: single_cell,
  open_range: open_range,
  y_or_n_range: y_or_n_range,
  MAX_ROWS: MAX_ROWS,
}
