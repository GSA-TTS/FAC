
{
    compound_type(arr):: {
        type: std.map(function(t) t.type, arr)
    },
}