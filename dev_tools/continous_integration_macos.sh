#!/bin/bash
# This script should only be run by Travis
if [ "$TRAVIS_OS_NAME" == "osx" ]; then

    # Install some custom requirements on macOS
    # e.g. brew install pyenv-virtualenv
    PYTHON=3.6.0
    brew update
    brew install openssl readline pyenv-virtualenv
    brew outdated pyenv || brew upgrade pyenv
    pyenv install $PYTHON
    export PYENV_VERSION=$PYTHON
    export PATH="$(pwd)/.pyenv/shims:${PATH}"
    pyenv virtualenv venv
    source /Users/travis/.pyenv/versions/3.6.0/envs/venv/bin/activate
    pip install -r requirements.txt
    pip install -r cirq/contrib/contrib-requirements.txt
    pip install -r dev_tools/conf/pip-list-dev-tools.txt
    #`import matplotlib` throws a  RuntimeError without this
    mkdir -p ~/.matplotlib && echo "backend: TkAgg" >> ~/.matplotlib/matplotlibrc
else
    echo "This operating system is not osx"
    exit 1
fi

