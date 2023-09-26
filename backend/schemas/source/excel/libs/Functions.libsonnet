local Sheets = import 'Sheets.libsonnet';

local getColumn(idx) =
  if idx < 26 then std.char(65 + idx)
  else std.char(65 + (idx / 26 - 1)) + std.char(65 + (idx % 26));

{
  // base is the base object; e.g. Sheets.open_range
  // row is the cell row; e.g. 3
  // arrs is the array-of-arrays that the objects are built from.
  make_open_ranges(row, arrs)::
    std.mapWithIndex(function(ndx, a) a[0] {
      title: a[2],
      range_name: a[3],
      title_cell: getColumn(ndx) + std.toString(row),
      validation: a[1],
    }, arrs),

  make_open_ranges_with_column(row, arrs)::
    std.mapWithIndex(function(ndx, a) a[0] {
      title: a[2],
      range_name: a[3],
      title_cell: a[0].title_cell[0] + std.toString(row),
      validation: a[1],
    }, arrs),

  make_aln_prefixes(lon)::
    std.join(
      ',',
      std.map(function(num) std.toString(num), lon)
    ),
}
