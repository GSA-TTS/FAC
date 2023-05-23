local Sheets = import 'Sheets.libsonnet';

local columns = [
    "A", "B", "C", "D", "E",
    "F", "G", "H", "I", "J",
    "K", "L", "M", "N", "O",
    "P", "Q", "R", "S", "T",
    "U", "V", "W", "X", "Y",
    "Z",
];

{
// base is the base object; e.g. Sheets.open_range
// row is the cell row; e.g. 3
// arrs is the array-of-arrays that the objects are built from.
make_open_ranges(row, arrs)::
    std.mapWithIndex(function(ndx, a) a[0] + {
        title: a[2],
        range_name: a[3],
        title_cell: columns[ndx] + std.toString(row),
        validation: a[1],
    }, arrs),

make_open_ranges_with_column(row, arrs)::
    std.mapWithIndex(function(ndx, a) a[0] + {
        title: a[2],
        range_name: a[3],
        title_cell: a[0].title_cell[0] + std.toString(row),
        validation: a[1],
    }, arrs),

make_aln_prefixes(lon)::
    std.join(
        ",",
        std.map(function(num) std.toString(num), lon)
    ),
}
