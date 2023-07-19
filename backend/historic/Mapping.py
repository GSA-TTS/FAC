from historic.base import NoMapping, MapOneOf, MapRetype, MapLateRemove

class Mapping:

    def __init__(self):
        self.mapping = {}
        # A list of strings; columns to drop
        self.to_drop = []
        # A dict of MapRetype structs
        self.to_retype = []
        # A list of MapOneOf structs
        self.many_to_one = []
        # Remove late in the process
        self.to_drop_late = []

    def add_mapping(self, k, v):
        self.mapping[k] = v
    
    def add_mappings(self, h):
        for k, v in h.items():
            if isinstance(v, NoMapping):
                self.to_drop.append(k)
            elif isinstance(v, MapOneOf):
                self.many_to_one.append(v)
            elif isinstance(v, MapRetype):
                self.mapping[k] = v.map_to
                self.to_retype.append(v)
            elif isinstance(v, MapLateRemove):
                self.to_drop_late.append(k)
            else:
                self.mapping[k] = v
    
    def add_column_to_drop(self, k):
        self.to_drop.append(k)

    def add_column_to_retype(self, mrt):
        self.to_retype.append(mrt)

    def drop_columns(self, df, when='early'):
        if when == 'early':
            return df.drop(columns=list(self.to_drop))
        elif when == 'late':
            return df.drop(columns=list(self.to_drop_late))

    def apply_mapping(self, df):
        return df.rename(columns=self.mapping)

    def apply_retyping(self, df):
        new = df
        for mrt in self.to_retype:
            new = mrt.retype(new, mrt.map_to)
        return new