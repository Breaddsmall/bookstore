from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import user
import sqlalchemy

bp_auth = Blueprint("auth", __name__, url_prefix="/auth")


@bp_auth.route("/login", methods=["POST"])
def login():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    terminal = request.json.get("terminal", "")
    u = user.User()
    code, message, token = u.login(user_id=user_id, password=password, terminal=terminal)
    return jsonify({"message": message, "token": token}), code


@bp_auth.route("/logout", methods=["POST"])
def logout():
    user_id: str = request.json.get("user_id")
    token: str = request.headers.get("token")
    u = user.User()
    code, message = u.logout(user_id=user_id, token=token)
    return jsonify({"message": message}), code


@bp_auth.route("/register", methods=["POST"])
def register():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    u = user.User()
    code, message = u.register(user_id=user_id, password=password)
    return jsonify({"message": message}), code


@bp_auth.route("/unregister", methods=["POST"])
def unregister():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    u = user.User()
    code, message = u.unregister(user_id=user_id, password=password)
    return jsonify({"message": message}), code


@bp_auth.route("/password", methods=["POST"])
def change_password():
    user_id = request.json.get("user_id", "")
    old_password = request.json.get("oldPassword", "")
    new_password = request.json.get("newPassword", "")
    u = user.User()
    code, message = u.change_password(user_id=user_id, old_password=old_password, new_password=new_password)
    return jsonify({"message": message}), code


@bp_auth.route("/search_author", methods=["POST"])
def search_author():
    author = request.json.get("author", "")
    u = user.User()
    code, message = u.search_author(author=author)
    return jsonify({"message": message}), code


@bp_auth.route("/search_book_intro", methods=["POST"])
def search_book_intro():
    book_intro = request.json.get("book_intro", "")
    u = user.User()
    code, message = u.search_book_intro(book_intro=book_intro)
    return jsonify({"message": message}), code


@bp_auth.route("/search_tags", methods=["POST"])
def search_tags():
    tags = request.json.get("tags", "")
    u = user.User()
    code, message = u.search_tags(tags=tags)
    return jsonify({"message": message}), code


@bp_auth.route("/search_title", methods=["POST"])
def search_title():
    title = request.json.get("title", "")
    u = user.User()
    code, message = u.search_title(title=title)
    return jsonify({"message": message}), code


@bp_auth.route("/search_author_in_store", methods=["POST"])
def search_author_in_store():
    author = request.json.get("author", "")
    store_id = request.json.get("store_id", "")
    u = user.User()
    code, message = u.search_author_in_store(author=author, store_id=store_id)
    return jsonify({"message": message}), code


@bp_auth.route("/search_book_intro_in_store", methods=["POST"])
def search_book_intro_in_store():
    book_intro = request.json.get("book_intro", "")
    store_id = request.json.get("store_id", "")
    u = user.User()
    code, message = u.search_book_intro_in_store(book_intro=book_intro, store_id=store_id)
    return jsonify({"message": message}), code


@bp_auth.route("/search_tags_in_store", methods=["POST"])
def search_tags_in_store():
    tags = request.json.get("tags", "")
    store_id = request.json.get("store_id", "")
    u = user.User()
    code, message = u.search_tags_in_store(tags=tags, store_id=store_id)
    return jsonify({"message": message}), code


@bp_auth.route("/search_title_in_store", methods=["POST"])
def search_title_in_store():
    title = request.json.get("title", "")
    store_id = request.json.get("store_id", "")
    u = user.User()
    code, message = u.search_title_in_store(title=title, store_id=store_id)
    return jsonify({"message": message}), code


@bp_auth.route("/search_book_intro_index_version", methods=["POST"])
def search_book_intro_index_version():
    book_intro = request.json.get("book_intro", "")
    u = user.User()
    code, message = u.search_book_intro_index_version(book_intro=book_intro)
    return jsonify({"message": message}), code


@bp_auth.route("/search_book_intro_index_version_in_store", methods=["POST"])
def search_book_intro_index_version_in_store():
    book_intro = request.json.get("book_intro", "")
    store_id = request.json.get("store_id", "")
    u = user.User()
    code, message = u.search_book_intro_index_version_in_store(book_intro=book_intro, store_id=store_id)
    return jsonify({"message": message}), code






