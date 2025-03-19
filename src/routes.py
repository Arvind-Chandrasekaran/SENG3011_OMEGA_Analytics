from flask import Blueprint  # , request, jsonify
# import analysis

routes = Blueprint("routes", __name__)

#
# Add routes here, e.g.
# @routes.route('/analyse', methods=['POST'])
# def analyse():
#


def register_routes(app):
    app.register_blueprint(routes)
