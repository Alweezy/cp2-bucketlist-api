from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort

from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()


def create_app(config_name):
    from app.models import BucketList, BucketListItem, User
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/api/v1/bucketlists/', methods=['POST', 'GET'])
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
    def bucketlist_manipulation(id, **kwargs):
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

    return app
