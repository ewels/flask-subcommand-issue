# flask-subcommand-issue
Minimal test example for flask / click subcommand problem.

I asked this as a question on Stack Overflow - this is the minimal example to demonstrate the problem.
See https://stackoverflow.com/questions/55270786/how-to-make-a-flask-app-run-as-a-click-subcommand

## Use case
I have a python package using a `click` group to have multiple command line subcommands.
In addition to this, I would like to have a small flask application.

The other subcommands are the primary function of the package - _not_ the flask application.
As such, I would like the flask commands to be nested under their own group.

## Example
### What works
In this minimal example, I set up a mini flask installation that runs with the `fsksc_server` command.
This is thanks to a setuptools `console_scripts` entry point hook in `setup.py`.

The command works perfectly, exactly as you would expect:

```
$ fsksc_server --help

Usage: fsksc_server [OPTIONS] COMMAND [ARGS]...

  Run the fsksc server flask app

Options:
  --version  Show the flask version
  --help     Show this message and exit.

Commands:
  routes  Show the routes for the app.
  run     Runs a development server.
  shell   Runs a shell in the app context.
```

```
$ fsksc_server run

 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```
_(I haven't set up any routes, so visiting the URL throws a 404, but the server is running fine..)_

To get the flask commands in a click subcommand I have used flask `add_command` with the flask group.
This main command is `fsksc`. The flask subcommand should be `shell`.
The intention is to make `fsksc shell run` launch the development server.

The commands show up properly, so this part seems to work:

```
$ fsksc --help

Usage: fsksc [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  cmd1
  cmd2
  server  Run the fsksc server flask app
```

### What doesn't work
When doing anything under the `server` subcommand, I get a warning message about a `NoAppException` exception:

```
$ fsksc server --help

Traceback (most recent call last):
  File "/Users/ewels/miniconda2/envs/work/lib/python2.7/site-packages/Flask-1.0.2-py2.7.egg/flask/cli.py", line 529, in list_commands
    rv.update(info.load_app().cli.list_commands(ctx))
  File "/Users/ewels/miniconda2/envs/work/lib/python2.7/site-packages/Flask-1.0.2-py2.7.egg/flask/cli.py", line 384, in load_app
    'Could not locate a Flask application. You did not provide '
NoAppException: Could not locate a Flask application. You did not provide the "FLASK_APP" environment variable, and a "wsgi.py" or "app.py" module was not found in the current directory.
Usage: fsksc server [OPTIONS] COMMAND [ARGS]...

  Run the fsksc server flask app

Options:
  --version  Show the flask version
  --help     Show this message and exit.

Commands:
  routes  Show the routes for the app.
  run     Runs a development server.
  shell   Runs a shell in the app context.
```

Trying to run the server gives a similar error:

```
$ fsksc server run

 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: off
Usage: fsksc server run [OPTIONS]

Error: Could not locate a Flask application. You did not provide the "FLASK_APP" environment variable, and a "wsgi.py" or "app.py" module was not found in the current directory.
```

### Crappy workaround
I can fix this by defining the `FLASK_APP` environment variable correctly.
Then `flask run` works as expected:

```
$ export FLASK_APP=/Users/ewels/GitHub/flask-subcommand-issue/fsksc/server/app.py:create_fsksc_app

$ fsksc server run

 * Serving Flask app "/Users/ewels/GitHub/flask-subcommand-issue/fsksc/server/app.py:create_fsksc_app"
 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

`flask run` also works.

_But_ - I don't want to have to get my users to do this!
I also don't want to pollute my main command group with the flask subcommands
(in reality I have a lot more subcommands in the main group).

## Solution 1
Answered by _Grey Li_ on Stack Overflow: https://stackoverflow.com/a/55272314/713980

Flask can load environment variables from a file using the `python-dotenv` package:
http://flask.pocoo.org/docs/1.0/cli/#environment-variables-from-dotenv

TL;DR; - add `python-dotenv` as a dependency, create a `.flaskenv` file with the `FLASK_APP` variable
and load this in the main script by using `flask.cli.load_dotenv(path)`.

The problem with this approach is that flask loads `FLASK_APP` using the _working directory_  as the root
for any relative paths. This means that the contents of that file has to either be absolute (and won't work
for other users installing the package) or the server has to be run from the correct directory.

## Solution 2
Sometimes the best solutions are the simplest. Using the builtin python `os` library, you can set
environment variables. I'd tried this before with no success, but the key is that it has to be set
very early on in execution. Specifically, in the main launch script, immediately after imports.

Now we can define the path to the flask app dynamically, based on the location of the installed script.
This should work for anyone installing the package. We set this to `FLASK_APP` and everything seems to work!

```python
flaskenv_app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fsksc', 'server', 'app.py')
flaskenv_app_func = '{}:create_fsksc_app'.format(flaskenv_app_path)
os.environ['FLASK_APP'] = flaskenv_app_func
```

> Again: the location of this code is key. It has to be immediately after Python execution begins.
