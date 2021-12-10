**Brunhilda** the test runner
=============================

Brunhilda is a custom test runner supported python unittest test-cases.

Contributing
------------

Here is a short guide to environment setup to ease you up contributing to the
project. Start by installing and creating virtual environment

```shell
pip install virtualenv
virtualenv venv
```

Now you should see `venv` folder in the project structure. Activate virtual
environment

```shell
source venv/bin/activate    # Linux
venv\Scripts\activate.bat   # Windows
```

After that you should see `(venv)` as prefix to your command line cursor. You
have to to repeat activation every time you close the terminal. To install
package in development mode call:

```shell
pip install -e .
```

Now you can use `BRunhilda` package directly from command line and all changes
to source code are instantly applied.
