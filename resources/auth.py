from flask_restful import Resource

class Signup(Resource):
    def post(self):
        return {"message": "Signup endpoint"}, 200