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
# Install the tools

`brew install pyenv pyenv-virtualenv`

If your tools are previously installed, you may need to

`brew update && brew upgrade pyenv` 

to have all of the most recent versions of Python available. This could be slow if you haven't updated in a while. Get a cup of ☕. 

(Your setup process on Windows/Linux will vary. Currently, we assume local development in a Linux-like environment.)

## Update your environment

You will likely need to [update your shell](https://stackoverflow.com/questions/33321312/cannot-switch-python-with-pyenv).

```
eval "$(pyenv init --path)"
```

should end up somewhere in `~/.bash_profile`, `~/.bashrc`, or whatever flavor of shell you're using.

## Set link flags

You *might* need to set link flags. Otherwise, when you `make install`, there could be failures in the building of `psycog2`. YMMV.

```
export LDFLAGS="-L/usr/local/opt/openssl/lib -L/usr/local/lib -L/usr/local/opt/expat/lib" && export CFLAGS="-I/usr/local/opt/openssl/include/ -I/usr/local/include -I/usr/local/opt/expat/include" && export CPPFLAGS="-I/usr/local/opt/openssl/include/ -I/usr/local/include -I/usr/local/opt/expat/include"
```

# Create a virtual environment

You may need to install the Python version being used by the team. The following take place in the `backend` directory of the checked out repository.

```
FAC_PYTHON_VERSION=`cat .python-version`
pyenv install $FAC_PYTHON_VERSION
```

Then, set up the virtualenv.

`pyenv virtualenv $FAC_PYTHON_VERSION FAC`

# Activate your new virtual environment

`pyenv activate FAC`

Depending on how you feel about seeing the virtualenv in your prompt:

```
pyenv-virtualenv: prompt changing will be removed from future release. configure `export PYENV_VIRTUALENV_DISABLE_PROMPT=1' to simulate the behavior.
```

# Install python dependencies

```    
python -m pip install --upgrade pip
pip install pip-tools
```

