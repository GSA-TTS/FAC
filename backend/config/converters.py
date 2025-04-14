class PublicDataPathConverter:
    # Must begin with a character and have at least two characters
    # Allow characters we'd expect in a file path, such as '-' and '.'
    regex = r"[A-Za-z][A-Za-z0-9\/\-.\\_]+"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value
