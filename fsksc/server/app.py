#!/usr/bin/env python
"""
nf-core monitor flask app
"""

import click
import flask

def create_fsksc_app():
    app = flask.Flask('fsksc.server.app')
    return app

# Default flask cli group. Gives run / routes / shell subcommands
@click.group(cls=flask.cli.FlaskGroup, create_app=create_fsksc_app)
def server():
    """
    Run the fsksc server flask app
    """
