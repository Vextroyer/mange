import os
from functools import wraps
from json.encoder import JSONEncoder
import re
import logging

from flask import Blueprint, Flask, request, make_response
from flask_classful import FlaskView, route
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import sqlalchemy

from mange.api import Client
from mange.db import Base
from mange.conf import settings
from mange.log import logged


log = logging.getLogger("global")

app = Flask(__name__)
CORS(app)
api = Blueprint("api", __name__, url_prefix="/api")

class ModelSerializer(JSONEncoder):
    def default(self, o):
        if isinstance(o, Base):
            return o.as_dict()
        return super().default(o)

encoder = ModelSerializer()

client = Client()

# REST API
def output_json(data, code, headers=None):
    content_type = "application/json"
    dumped = encoder.encode(data)
    if headers:
        headers.update({"Content-Type": content_type})
    else:
        headers = {"Content-Type": content_type}
    response = make_response(dumped, code, headers)
    return response

def protected(decorated):
    """
    Protect a method against db failure
    """
    @wraps(decorated)
    def internal(*args, **kwargs):
        try:
            res = decorated(*args, **kwargs)
            return res
        except (
            sqlalchemy.exc.ProgrammingError,
            sqlalchemy.exc.InternalError,
            sqlalchemy.exc.IntegrityError,
        ) as e:
            log.error(e)
            client.session.rollback()
            raise APIException()

    return internal

@logged
class APIView(FlaskView):
    representations = {"application/json": output_json}
    model = None
    pk_field = "id"
    excluded_methods = ["get_queryset"]
    route_base = None

    def __new__(cls, *args, **kwargs):
        name = re.sub("APIView", "", cls.__name__).lower()
        cls.model = cls.model or name
        cls.route_base = cls.route_base or f"/{name}"

        return FlaskView.__new__(cls, *args, **kwargs)

    def get_queryset(self, method, *args, **kwargs):
        cli = client
        return getattr(cli, f"{method}_{self.model}")(*args, **kwargs)

    @protected
    def post(self):
        # it returns the event object
        return self.get_queryset("create", **request.json).as_dict()

    @protected
    def index(self):
        return self.get_queryset("get").all()

    @protected
    def get(self, id: str):
        if not id.isdigit():
            raise APIException("The ID field must be an integer")
        id = int(id)
        return self.get_queryset("get", **{self.pk_field: id}).one()

    @protected
    def update(self, id):
        # here I would get the post data and update stuff
        kwargs = request.json

        obj = self.get_queryset("get", **{self.pk_field: id}).one()
        nu_obj = client.update(obj, **kwargs)

        return nu_obj.as_dict()

    @protected
    def delete(self, id):
        obj = self.get_queryset("get", **{self.pk_field: id}).one()

        client.session.remove(obj)

        return {}

class APIException(HTTPException):
    code = 400
    description = "bad request"

    def get_description(
        self,
        environ=None,
        scope=None,
    ) -> str:
        """Get the description."""
        if self.description is None:
            description = ""
        elif not isinstance(self.description, str):
            description = str(self.description)
        else:
            description = self.description
        return description

    def get_body(
        self,
        environ=None,
        scope=None,
    ) -> str:
        """Get the HTML body."""
        return encoder.encode(
            {"status_code": self.code, "errors": self.get_description()}
        )

    def get_headers(
        self,
        environ=None,
        scope=None,
    ):
        """Get a list of headers."""
        return {
            "Content-Type": "application/json",
        }

# error handling
@app.errorhandler(APIException)
def handle_exception(e):
    return output_json(e.get_body(), e.code, e.get_headers())

@app.errorhandler(sqlalchemy.exc.NoResultFound)
def handle_not_found(e):
    e = APIException("Resource not found")
    e.code = 404
    return output_json(e.get_body(), e.code, e.get_headers())

def get_auth_token(request):
    return request.headers.get("Authorization", None)

def is_role(role_name):
    def is_role_decorator(fun):
        def wraps(*args, **kwargs):
            if request.user.group.name == role_name:
                return fun(*args, **kwargs)

            exc = APIException("Insufficient credentials") # not allowed
            exc.code = 403
            raise exc
        return wraps
    return is_role_decorator

def is_admin():
    return is_role("Admin")

@app.teardown_appcontext
def shutdown_session(exception=None):
  client.session.remove()

class SucursalAPIView(APIView):
	pass
    
class RegistroAPIView(APIView):
	pass

class EquipoAPIView(APIView):
    pass

class AreaAPIView(APIView):
    pass

class UserAPIView(APIView):
    
    @route("/login/")
    def login(self):
        post_data = request.json
        if not "name" in post_data and "password" in post_data:
            raise APIException("fields ('name','password') are required")
        
        name = post_data["name"]
        password = post_data["password"]

        return {
            "token": client.login(name=name, password=password).value
        }

class GroupAPIView(APIView):
    pass

# populate urls
_loc = locals().copy()
_keys = _loc.keys()
for namespace in _keys:
    if namespace.endswith("APIView") and namespace != "APIView":
        if issubclass(_loc[namespace], APIView):
            view = _loc[namespace]
            view.register(api)

@app.route("/")
def index():
    return "OK"

app.register_blueprint(api)

def runserver():
    app.run(port=5050)
