"""
Author:         Yanto Christoffel
Project Title:  LetterboxdRSS
"""

import requests
from main import (
    get_last_n,
    compare_ratings,
    compare_titles,
    compare_years,
    sort_movies,
)
from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
def home():
    """Displays the home page."""
    # Go to the page of the username in the input box
    if request.method == "POST":
        if "username" in request.form:
            usr = request.form["username"]
            return redirect(url_for("user", usr=usr))
        else:
            return redirect(url_for("home"))

    # The input box is empty
    return render_template("index.html", movie_list=[], username="")


@app.route("/<usr>", methods=["POST", "GET"])
def user(usr):
    """Shows the most recent movies for the given username."""
    # Go to another user page if another username is posted
    if request.method == "POST":
        if "username" in request.form:
            usr = request.form["username"]

            if usr == "":
                return redirect(url_for("home"))

            return redirect(url_for("user", usr=usr))

    # Obtain the most recent movies for the username
    url = f"https://letterboxd.com/{usr}/rss/"
    result = requests.get(url)
    page_text = str(result.content)
    movies = get_last_n(page_text, 50)

    # Obtain the selected sorting method in the dropdown list
    sorting_method = request.args.get("sorting")

    # Sort according to the selected sorting method
    # (defaults to sort by Watched Date)
    if sorting_method:
        if sorting_method == "Title":
            movies = sort_movies(movies, compare_titles)
        elif sorting_method == "Rating":
            movies = sort_movies(movies, compare_ratings)
        elif sorting_method == "Release Year":
            movies = sort_movies(movies, compare_years)

    return render_template("index.html", movie_list=movies, username=usr)


if __name__ == "__main__":
    app.run(debug=True)
