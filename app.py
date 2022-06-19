from flask import Flask, request
from flask_restx import Api, Resource

from models import Movie, Genre, Director
from scheme import movies_schema
from setup_db import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 3}

app.app_context().push()
db.init_app(app)
api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


@movie_ns.route("/")
class MovieView(Resource):

    def get(self):
        movies = db.session.query(Movie.id, Movie.title, Movie.description, Movie.rating, Movie.trailer,
                                  Genre.name.label('genre'),
                                  Director.name.label('director')).join(Genre).join(Director)
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        if director_id:
            movies = movies.filter(Movie.director_id == director_id)
        if genre_id:
            movies = movies.filter(Movie.genre_id == genre_id)

        all_movies = movies.all()
        return movies_schema.dump(all_movies), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return f'Новый объект {new_movie.id} создан', 201


@movie_ns.route("/<int:movie_id>")
class MovieView(Resource):

    def get(self, movie_id: int):
        movie = db.session.query(Movie.id, Movie.title, Movie.description, Movie.rating,
                                 Movie.trailer,
                                 Genre.name.label('genre'),
                                 Director.name.label('director')).join(Genre).join(Director).filter(
            Movie.id == movie_id)
        if movie.first():
            return movies_schema.dump(movie), 200
        return 'Фильм не существует', 404

    def put(self, movie_id):
        movie = db.session.query(Movie).get(movie_id)
        if not movie:
            return 'Фильм не существует', 404
        req_json = request.json
        movie.title = req_json['title']
        movie.description = req_json['description']
        movie.trailer = req_json['trailer']
        movie.year = req_json['year']
        movie.rating = req_json['rating']
        movie.genre_id = req_json['genre_id']
        movie.director_id = req_json['director_id']
        db.session.add(movie)
        db.session.commit()
        return f'Фильм с id {movie_id} обновлен', 201

    def delete(self, movie_id):
        movie = db.session.query(Movie).get(movie_id)
        if not movie:
            return 'Фильм не существует', 404
        db.session.delete(movie)
        db.session.commit()
        return f'Фильм с id {movie_id} удален', 201


@director_ns.route("/")
class DirectorView(Resource):

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)
        with db.session.begin():
            db.session.add(new_director)
        return f'Новый объект {new_director.id} создан', 201


@director_ns.route("/<int:director_id>")
class DirectorView(Resource):

    def put(self, director_id):
        director = db.session.query(Director).get(director_id)
        if not director:
            return 'Объект не существует', 404
        req_json = request.json
        director.name = req_json['name']
        db.session.add(director)
        db.session.commit()
        return f'Объект с id {director_id} обновлен', 201

    def delete(self, director_id):
        director = db.session.query(Director).get(director_id)
        if not director:
            return 'Объект не существует', 404
        db.session.delete(director)
        db.session.commit()
        return f'Объект с id {director_id} удален', 201


@genre_ns.route("/")
class GenreView(Resource):

    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)
        with db.session.begin():
            db.session.add(new_genre)
        return f'Новый объект {new_genre.id} создан', 201


@genre_ns.route("/<int:genre_id>")
class GenreView(Resource):

    def put(self, genre_id):
        genre = db.session.query(Genre).get(genre_id)
        if not genre:
            return 'Объект не существует', 404
        req_json = request.json
        genre.name = req_json['name']
        db.session.add(genre)
        db.session.commit()
        return f'Объект с id {genre_id} обновлен', 201

    def delete(self, genre_id):
        genre = db.session.query(Genre).get(genre_id)
        if not genre:
            return 'Объект не существует', 404
        db.session.delete(genre)
        db.session.commit()
        return f'Объект с id {genre_id} удален', 201


if __name__ == '__main__':
    app.run(debug=True)
