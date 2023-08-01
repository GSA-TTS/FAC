import pandas as pd
import numpy as np
from dissemination.models import General
from historic.base import NoMapping, MapOneOf, MapRetype, MapLateRemove


class mapper:
    def __init__(self, c2g_mapping):
        self.c2g_map = {}
        # A list of strings; columns to drop
        self.to_drop = []
        # A dict of MapRetype structs
        self.to_retype = []
        # A list of MapOneOf structs
        self.many_to_one = []
        # Remove late in the process
        self.to_drop_late = []

        self.add_mappings(c2g_mapping)

    def add_mappings(self, c2g_mapping):
        for k, v in c2g_mapping.items():
            if isinstance(v, NoMapping):
                self.to_drop.append(k)
            elif isinstance(v, MapOneOf):
                self.many_to_one.append(v)
            elif isinstance(v, MapRetype):
                self.c2g_map[k] = v.map_to
                self.to_retype.append(v)
            elif isinstance(v, MapLateRemove):
                self.to_drop_late.append(k)
            else:
                self.c2g_map[k] = v

    def _drop_columns(self, df, when="early"):
        if when == "early":
            df = df.drop(columns=list(self.to_drop))
            return df
        elif when == "late":
            return df.drop(columns=list(self.to_drop_late))

    def apply_mappings_to_df(self, df, make_report_id=False):
        df = df.drop("id", axis=1)  # drop django id col
        df = self._drop_columns(df, when="early")
        df = df.rename(columns=self.c2g_map)
        df = self.apply_retyping(df)
        df = self.set_report_id(df, make_report_id)
        df = self._drop_columns(df, when="late")
        return df

    def apply_retyping(self, df):
        new = df
        for mrt in self.to_retype:
            new = mrt.retype(new, mrt.map_to)
        return new

    def add_fun_column_to_df(self, df, column, fun):
        df[column] = df.apply(fun, axis=1)
        return df

    def add_const_column_to_df(self, df, column, value):
        df[column] = value
        return df

    def set_report_id(self, df, make_report_id):
        if make_report_id:
            df["report_id"] = np.arange(len(df))
            df["report_id"] = (
                df["fy_start_date"].astype(str) + "_" + df["report_id"].astype(str)
            )

            # str(df["audit_year"])
            # + str(df["fy_start_date"])
        else:
            rid_dbkey_df = pd.DataFrame.from_records(
                General.objects.all().values("hist_dbkey", "report_id")
            )
            df = pd.merge(
                df, rid_dbkey_df, left_on="DBKEY", right_on="hist_dbkey", how="left"
            )
            df = df.drop(columns="hist_dbkey")
        return df
