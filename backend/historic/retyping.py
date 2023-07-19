def to_int_to_str(df, column):
    new = df.astype({column: int})
    new = new.astype({column: str})
    return new
