from flask import render_template, session, redirect, request, url_for
from flask_app import app
from flask_app.controllers import users
from flask_app.controllers import products


if __name__ == "__main__":
    app.run(debug=True)