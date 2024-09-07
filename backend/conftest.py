import pytest

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass

def pytest_addoption(parser):
    argdests = {arg.dest for arg in parser.getgroup('xdist').options}
    if 'numprocesses' not in argdests:
        parser.getgroup('xdist').addoption(
            '--numprocesses', dest='numprocesses', metavar='numprocesses', action='store',
            help="placeholder for xdist's numprocesses arg; passed value is ignored if xdist is not installed"
    )