from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort, make_response, render_template


from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()


def create_app(config_name):
    from app.models import BucketList, BucketListItem, User
    from .auth_wrapper import evaluate_auth
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.url_map.strict_slashes = False
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    @app.route('/api/v1/bucketlists/', methods=['POST', 'GET'])
    @evaluate_auth
    def bucketlists(user_id):
        if request.method == "POST":
            name = str(request.data.get('name', ''))
            if name:
                bucketlist = BucketList.query.filter_by(name=name, created_by=user_id).first()
                if not bucketlist:
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
                    res = {
                        "message": "User already has a bucketlist by that name"
                    }
                    return make_response(jsonify(res)), 200
        else:
            # GET
            search = str(request.args.get("q", ""))
            if search:
                search_query = BucketList.query.filter_by(created_by=user_id).filter(
                    BucketList.name.ilike('%'+search+'%')).all()
                if search_query:
                    search_results = []
                    for bucketlist in search_query:
                        items = BucketListItem.query.filter_by(
                            bucketlist_id=bucketlist.id)
                        items_list = []
                        for item in items:
                            item_data = {"id": item.id,
                                         "name": item.name,
                                         "date_created": item.date_created,
                                         "date_modified": item.date_modified,
                                         "done": item.done
                                         }
                            items_list.append(item_data)

                        bucketlist_data = {
                            'id': bucketlist.id,
                            'name': bucketlist.name,
                            'date_created': bucketlist.date_created,
                            'date_modified': bucketlist.date_modified,
                            'items': items_list,
                            'created_by': bucketlist.created_by
                        }
                        search_results.append(bucketlist_data)

                    return make_response(jsonify(search_results)), 200
                else:
                    res = {
                        "message": "Specified bucketlist is not available"
                    }
                    return make_response(jsonify(res)), 404
            else:
                # paginate bucketlist results
                limit = request.args.get("limit")
                if request.args.get("page"):
                    page = int(request.args.get("page"))
                else:
                    # Assign page number arbitrarily if none is given
                    page = 1
                if limit and len(request.args.get("limit")):
                    # use the limit issued with request
                    limit = int(request.args.get("limit"))
                else:
                    # set limit otherwise
                    limit = 20
                paginated_results = BucketList.query.filter_by(
                    created_by=user_id).paginate(page, limit, False)
                if paginated_results.has_next:
                        next_page = request.endpoint + '?page=' + str(
                            page + 1) + '&limit=' + str(limit)
                else:
                    next_page = ""
                if paginated_results.has_prev:
                        previous_page = request.endpoint + '?page=' + str(
                            page - 1) + '&limit=' + str(limit)
                else:
                    previous_page = ""

                paginated_bucketlists = paginated_results.items
                results = []

                for bucketlist in paginated_bucketlists:
                    items = BucketListItem.query.filter_by(bucketlist_id=bucketlist.id)
                    items_list = []
                    for item in items:
                        item_data = {"id": item.id,
                                     "name": item.name,
                                     "date_created": item.date_created,
                                     "date_modified": item.date_modified,
                                     "done": item.done
                                     }
                        items_list.append(item_data)

                    bucketlist_data = {
                        'id': bucketlist.id,
                        'name': bucketlist.name,
                        'date_created': bucketlist.date_created,
                        'date_modified': bucketlist.date_modified,
                        'items': items_list,
                        'created_by': bucketlist.created_by
                    }
                    results.append(bucketlist_data)

                response = {
                            "next_page": next_page,
                            "previous_page": previous_page,
                            "bucketlists": results
                        }

                return make_response(jsonify(response)), 200

    @app.route('/api/v1/bucketlists/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    @evaluate_auth
    def bucketlist_manipulation(id, user_id, *args, **kwargs):
        # retrieve a buckelist using it's ID
        bucketlist = BucketList.query.filter_by(id=id, created_by=user_id).first()
        if not bucketlist:
            # Raise an HTTPException with a 404 not found status code
            abort(jsonify({"message": "Bucketlist does not exist."}))

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
        bucketlist = BucketList.query.filter_by(id=id, created_by=user_id).first()
        if not bucketlist:
            abort(jsonify({"message": "Bucketlist does not exist."}))

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
        user = BucketList.query.filter_by(created_by=user_id).first()
        if not user:
            abort(jsonify({"message": "Bucketlist item does not exist or you don't own it."}))
        item = BucketListItem.query.filter_by(bucketlist_id=id).filter_by(
            id=item_id).first()
        if not item:
            abort(jsonify({"message": "Bucketlist item does not exist."}))

        if request.method == "DELETE":
            item.delete()
            response = jsonify({
                "message": "Item {} has been successfully deleted"
                .format(item.name)})
            return make_response(response), 200

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
