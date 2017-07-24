from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort, make_response


from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()


def create_app(config_name):
    from app.models import BucketList, BucketListItem, User
    from .auth_wrapper import evaluate_auth
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/api/v1/bucketlists/', methods=['POST', 'GET'])
    @evaluate_auth
    def bucketlists(user_id):
        if request.method == "POST":
            name = str(request.data.get('name', ''))
            if name:
                bucketlist = BucketList(name=name, created_by=user_id)
                bucketlist.save()
                response = jsonify({
                    'id': bucketlist.id,
                    'name': bucketlist.name,
                    'date_created': bucketlist.date_created,
                    'date_modified': bucketlist.date_modified,
                    'created_by': user_id
                })
                response.status_code = 201
                return response
        else:
            # GET
            bucketlists = BucketList.get_all()
            results = []

            for bucketlist in bucketlists:
                obj = {
                    'id': bucketlist.id,
                    'name': bucketlist.name,
                    'date_created': bucketlist.date_created,
                    'date_modified': bucketlist.date_modified
                }
                results.append(obj)
            response = jsonify(results)
            response.status_code = 200
            return response

    @app.route('/api/v1/bucketlists/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    @evaluate_auth
    def bucketlist_manipulation(id, *args, **kwargs):
        # retrieve a buckelist using it's ID
        bucketlist = BucketList.query.filter_by(id=id).first()
        if not bucketlist:
            # Raise an HTTPException with a 404 not found status code
            abort(404)

        if request.method == 'DELETE':
            bucketlist.delete()
            return {
                       "message": "bucketlist {} deleted successfully".format(bucketlist.id)
                   }, 200

        elif request.method == 'PUT':
            name = str(request.data.get('name', ''))
            bucketlist.name = name
            bucketlist.save()
            response = jsonify({
                'id': bucketlist.id,
                'name': bucketlist.name,
                'date_created': bucketlist.date_created,
                'date_modified': bucketlist.date_modified,
                'created_by': bucketlist.created_by
            })
            response.status_code = 201
            return response
        else:
            # GET
            items = BucketListItem.query.filter_by(bucketlist_id=id)
            bucketlist_items = []
            for item in items:
                data = {
                    "id": item.id,
                    "name": item.name,
                    "date_created": item.date_created,
                    "date_modified": item.date_modified,
                    "done": item.done
                }
                bucketlist_items.append(data)

            response = jsonify({
                'id': bucketlist.id,
                'name': bucketlist.name,
                'date_created': bucketlist.date_created,
                'date_modified': bucketlist.date_modified,
                'created_by': bucketlist.created_by,
                'items': bucketlist_items

            })
            response.status_code = 200
            return response

    @app.route('/api/v1/bucketlists/<int:id>/items/', methods=['GET', 'POST'])
    @evaluate_auth
    def bucketlist_items(id, user_id, *args, **kwargs):
        bucketlist = BucketList.query.filter_by(id=id).first()
        if not bucketlist:
            abort(404)

        if request.method == 'GET':
            items = BucketListItem.query.filter_by(bucketlist_id=id)
            results = []

            for item in items:
                data = {
                    "id": item.id,
                    "name": item.name,
                    "date_created": item.date_created,
                    "date_modified": item.date_modified,
                    "bucketlist_id": item.bucketlist_id,
                    "done": item.done
                }
                results.append(data)
            return make_response(jsonify(results)), 200
        elif request.method == 'POST':
            name = str(request.data.get("name", ""))
            if name:
                item = BucketListItem(name=name, bucketlist_id=id)
                item.save()
                response = jsonify({
                    "id": item.id,
                    "name": item.name,
                    "date_created": item.date_created,
                    "date_modified": item.date_modified,
                    "bucketlist_id": item.bucketlist_id,
                    "done": item.done,
                    "created_by": user_id
                    })
                return make_response(response), 201

    @app.route('/api/v1/bucketlists/<int:id>/items/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
    @evaluate_auth
    def bucketlist_item_manipulation(id, item_id, user_id, *atgs, **kwargs):
        item = BucketListItem.query.filter_by(bucketlist_id=id).filter_by(
            id=item_id).first()
        if not item:
            abort(404)

        if request.method == "DELETE":
            item.delete()
            response = jsonify({
                "message": "Item {} has been successfully deleted"
                .format(item.name)})
            response.status_code = 204
            return response

        elif request.method == "PUT":
            name = str(request.data.get("name", ""))
            done = str(request.data.get("done", ""))
            if name:
                item.name = name
                item.save()
                response = jsonify({
                    "id": item.id,
                    "name": item.name,
                    "date_created": item.date_created,
                    "date_modified": item.date_modified,
                    "bucketlist_id": item.bucketlist_id,
                    "created_by": user_id,
                    "done": item.done})

                return make_response(response), 201

            elif done:
                item.done = done
                item.save()
                response = jsonify({
                    "id": item.id,
                    "name": item.name,
                    "date_created": item.date_created,
                    "date_modified": item.date_modified,
                    "bucketlist_id": item.bucketlist_id,
                    "created_by": user_id,
                    "done": item.done})

                return make_response(response), 200

        elif request.method == "GET":
            all_items = BucketListItem.query.filter_by(id=item_id)
            results = []

            for item in all_items:
                obj = {
                    "id": item.id,
                    "name": item.name,
                    "date_created": item.date_created,
                    "date_modified": item.date_modified,
                    "bucketlist_id": item.bucketlist_id,
                    "done": item.done
                }
                results.append(obj)

            return make_response(jsonify(results)), 200

    from app.auth import authenticate_blueprint
    app.register_blueprint(authenticate_blueprint)
    return app
