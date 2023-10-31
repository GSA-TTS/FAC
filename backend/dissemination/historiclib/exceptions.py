
class MigrationMappingError(Exception):
    def __init__(
        self,
        message="An error occurred while mapping data",
        source=None,
        dest=None,
    ):
        self.message = message
        self.source = source
        self.dest = dest
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} (Source: {self.source} Dest: {self.dest})"
