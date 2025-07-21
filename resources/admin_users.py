from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import User, db
from utils.logger import log_action

status_parser = reqparse.RequestParser()
status_parser.add_argument("status", type=str, required=True)  #active/banned

role_parser = reqparse.RequestParser()
role_parser.add_argument("role", type=str, required=True)  #attendee,organizer,admin

class AllUsers(Resource):
    @jwt_required()
    def get(self):
        admin = User.query.get(get_jwt_identity())
        if not admin or admin.role != "admin":
            return {"message": "Admins only."}, 403

        users = User.query.order_by(User.created_at.desc()).all()
        return [
            u.to_dict(only=(
                "id", "first_name", "last_name", "email", "phone", "role", "status", "created_at"
            ))
            for u in users
        ], 200

class BanOrUnbanUser(Resource):
    @jwt_required()
    def patch(self, id):
        admin = User.query.get(get_jwt_identity())
        if not admin or admin.role != "admin":
            return {"message": "Admins only."}, 403

        user = User.query.get(id)
        if not user:
            return {"message": "User not found."}, 404

        data = status_parser.parse_args()
        new_status = data["status"].strip().lower()

        if new_status not in ["active", "banned"]:
            return {"message": "Invalid status. Use 'active' or 'banned'."}, 400

        try:
            user.status = new_status
            db.session.commit()

            log_action(
                user_id=admin.id,
                action=f"{'Banned' if new_status == 'banned' else 'Unbanned'} User",
                target_type="User",
                target_id=user.id,
                status="Success",
                ip_address=request.remote_addr
            )

            return {"message": f"User status updated to {new_status}."}, 200

        except Exception as e:
            db.session.rollback()
            log_action(
                user_id=admin.id,
                action="Update User Status",
                target_type="User",
                target_id=user.id,
                status="Failed",
                ip_address=request.remote_addr,
                extra_data=str(e)
            )
            return {"message": "Failed to update user status."}, 500
        

class UpdateUserRole(Resource):
    @jwt_required()
    def patch(self, id):
        admin = User.query.get(get_jwt_identity())
        if not admin or admin.role != "admin":
            return {"message": "Admins only."}, 403

        user = User.query.get(id)
        if not user:
            return {"message": "User not found."}, 404

        data = role_parser.parse_args()
        new_role = data["role"].strip().lower()

        if new_role not in ["attendee", "organizer", "admin"]:
            return {"message": "Invalid role."}, 400

        try:
            user.role = new_role
            db.session.commit()

            log_action(
                user_id=admin.id,
                action="Updated User Role",
                target_type="User",
                target_id=user.id,
                status="Success",
                ip_address=request.remote_addr,
                extra_data={"new_role": new_role}
            )

            return {"message": f"User role updated to {new_role}."}, 200

        except Exception as e:
            db.session.rollback()
            log_action(
                user_id=admin.id,
                action="Update User Role",
                target_type="User",
                target_id=user.id,
                status="Failed",
                ip_address=request.remote_addr,
                extra_data=str(e)
            )
            return {"message": "Failed to update user role."}, 500


