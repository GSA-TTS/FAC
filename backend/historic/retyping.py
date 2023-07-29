def to_int_to_str(df, column):
    new = df.astype({column: int})
    new = new.astype({column: str})
    return new


def to_boolean(df, column):
    df[column] = df[column].apply(lambda x: True if x == "Y" else False)
    return df

