def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="local")


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    option_value = metafunc.config.option.env
    if "env" in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("env", [option_value])
