# Local development

## Contents

* [Tools](#tools)

* [Setting up your python environment](#python)

## Tools

* [Pyenv](https://github.com/pyenv) for managing Python versions
* [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) for managing virtual environments

## Initial Setup
---
**NOTE**

Target python version is defined in [../backend/runtime.txt](../backend/runtime.txt)

---


1. Install the tools listed above
2. Use [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) to create a virtual environment
3. Activate your new virtual environment
4. Install python dependencies

    ```
    pyenv virtualenv <python version> FAC
    pyenv activate FAC
    pip install pip-tools
    make install
    ```
