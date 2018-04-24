"""Error Page"""
from flask import render_template

from . import main

@main.app_errorhandler(404)
def page_not_found(e):
    """404 Page Not Found"""
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    """500 Internal Server Error"""
    return render_template('500.html'), 500