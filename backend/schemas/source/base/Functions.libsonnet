local _flatten_types(arr) = std.flatMap(function(t) if std.isArray(t.type) then t.type else [t.type], arr);

{
  compound_type(arr):: {
    /*
    compound_type([{type: 'string'}, {type: ['integer', 'null']}])
    ->
    {type: ['string', 'integer', 'null'])
    */

    type: _flatten_types(arr),
  },
  join_types(obj, arr):: obj {
    /*
    Create an object from an object and an array of objects with types, and return the object with its type updated to include the types from the array.

    Every object involved must have a type property.

    join_types({whatever: 1, type: 'boolean'}, [{type: 'string'}, {type: ['integer', 'null']}]
    ->
    {whatever: 1, type: ['string', 'integer', 'null', 'boolean']}
    */
    type: _flatten_types(arr + [obj]),
  },

}
