import urllib
import json
import sys 
from flask import Flask, render_template, request, jsonify 
from urllib.parse import urlencode 
import requests
from urllib.request import urlopen

app = Flask(__name__)

class OMDBError(Exception):
    """
    OMDBError represents an error returned by the OMDb API.
    """
    pass
class Movie(object):
    """
    Movie objects contain all information about a particular movie,
    including the title and rating.
    """
    def __init__(self, movie_data):
        self.omdb_data = movie_data
        # Store the raw data in this object so that we can use the
        # data in the getter functions.
    def get_movie_title(self):
        """
        get_movie_title is a getter function that returns the movie title.
        """
        # Return the title from the movie data.
        return self.omdb_data["Title"]
    def get_movie_rating(self, source="Rotten Tomatoes"):
        """
        get_movie_rating is a getter function that returns the rating.
        """
        # Loop through each rating and return it if the source is what's passed in
        for ratings in self.omdb_data["Ratings"]:
            if ratings["Source"] == source:
                return ratings["Value"]
        # If the code makes it here, it hasn't returned in the `for` loop.
        return "- Wait - Rating for source {0} was not found!".format(source)
class OMDB(object):
    def __init__(self, apikey):
        self.apikey = apikey
        #self.
    def build_url(self, **kwargs):
        """
        build_url returns a properly formatted URL to the OMDb API including the
        API key.
        """
        # Add API key to dictionary of parameters to send to OMDb.
        kwargs["apikey"] = self.apikey
        # Start building URL.
        url = "http://www.omdbapi.com/?"
        # urlencode the API parameters dictionary and append it to the URL.
        url += urlencode(kwargs)
        # Return the complete URL.
        return url
    def call_api(self, **kwargs):
        self.url = self.build_url(**kwargs)
        response = urlopen(self.url)
        response_data = response.read()
        response_data_decoded = json.loads(response_data)
        # print(response_data_decoded)
        # Check for an error and throw an exception if needed.
        if "Error" in response_data_decoded:
            raise OMDBError(response_data_decoded["Error"])
        return response_data_decoded
    def get_movie(self, movie_query):
        self.movie_data = self.call_api(t=movie_query)
        return Movie(self.movie_data)

    def search(self, movie_query):
        movie_dictionaries = self.call_api(s=movie_query)
        return movie_dictionaries["Search"]

    
def get_apikey():
    """
    Read api key from file.
    """
    with open("omdb-api-key.txt", "r") as file:
        key = file.read()
        key = key.strip()
        return key
def return_single_movie_object(movie_query):
    """
    Take in the movie title and rating, and return the movie object.
    """
    omdb = OMDB(get_apikey())
    # Get `Movie` object. If OMDb error occurs, print the error message and exit.
    try:
        my_movie_object = omdb.get_movie(movie_query)
        return my_movie_object
    except OMDBError as err:
        print("OMDB Error: {0}".format(err))
        return
def list_search_results(movie_query):
    """
    Print list of movies. Later, print a list of title results from a movie search.
    """
    apikey = get_apikey()

    omdb = OMDB(apikey)

    matching_movie_list = omdb.search(movie_query)

    movie_titles = [each_movie["Title"] for each_movie in matching_movie_list]
    
    # Loop through the list of titles and print them (indented with four spaces).
    for title in movie_titles:
        print("    " + title)
        
def print_single_movie_rating(movie_query):
    """
    Create a `Movie` object and print one movie's Rotten Tomatoes rating.
    """
    my_movie = return_single_movie_object(movie_query)
    # Print the rating. Note that we have to escape the quotes around the movie
    # title because those quotes are inside a string that also uses quotes.
    print("The rating for \"{0}\" is {1}.".format(my_movie.get_movie_title(), my_movie.get_movie_rating()))
def print_all_ratings(movie_list):
    """
    Take in a list of movies, create a movie object for each, and print the rating.
    """
    for movie in movie_list:
        movie_object = return_single_movie_object(movie)
        print("The movie", movie_object.get_movie_title(), "has a rating of", movie_object.get_movie_rating())
# Create one main function that will call everything else.
def cli_app():
    """
    Main is the entry point into the program, and it calls into the search or
    ratings functions, depending on what the user decides to do.
    """
    # A hard-coded movie list with which to test.
    default_movie_list = ["Back to the Future", "Blade", "Spirited Away"]
    apikey = get_apikey()
    #print(apikey)
    # Let's test: Call a `print_all_ratings()` function and pass it the `default_movie_list` as a parameter.
    #print_all_ratings(default_movie_list)
    # We set up an infinite loop (while True) so that we can keep asking the
    # user the same question until they give us valid input ("1" or "2"). As
    # soon as a valid input is reached, the appropriate function runs and the
    # loop is terminated with "break".
    while True:
        search_or_ratings = input("Would you like to search for a movie (1) or find the rating of a specific movie (2)? ")
        if search_or_ratings == "1":
            # If search_or_ratings is 1, call list_search_results().
            movie_query = input("Enter the movie title: ")
            list_search_results(movie_query)
            break
        elif search_or_ratings == "2":
            # If search_or_ratings is 2, call print_movie_rating().
            movie_query = input("Enter the movie title: ")
            print_single_movie_rating(movie_query)
            break
        else:
            # If search_or_ratings is otherwise, give an error.
            print("Error: Your input must be 1 or 2!")


@app.route("/")
def home() :
    # movie_query = input("Enter a movie search term: ")

    movie_query = request.args.get("query", "")
    matching_movie_list = []

    if movie_query != '':
        apikey = get_apikey()
        omdb = OMDB(apikey)

        matching_movie_list = omdb.search(movie_query)
    
    return render_template("home.html", query = movie_query, results = matching_movie_list)

#    return 'hello world'


def flask_app():
    app.run(debug=True)


            
# This line tells Python to run `main()` when it first opens.
if __name__ == "__main__":
    #print("system arguments: ", sys.argv)
    if len(sys.argv) > 1 and sys.argv[1] == 'flask':
        flask_app()
    else:
        print('Run "python movie_app.py flask" for the Flask app.')
        cli_app()

# Define the Flask app starting point.
