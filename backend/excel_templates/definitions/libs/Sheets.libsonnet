local SingleCell = {
    type: "single_cell",
    title: "Example Cell",
    range_name: "example_cell",
    title_cell: "A1",
    range_cell: "B1"
};


local OpenRange = {
    type: "open_range",
    title: "Example open range",
    range_name: "Example open range",
    title_cell: "A1",
    // Range start is redundant. 
    // It should start below the title cell.
    // range_start: "B1" 
};

local YorNRange = OpenRange + {
        type: "yorn_range",
        title: "Example YorN range",
        range_name: "Example YorN range"
};


{
    SingleCell: SingleCell,
    OpenRange: OpenRange,
    YorNRange: YorNRange
}