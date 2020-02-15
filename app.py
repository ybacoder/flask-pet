from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pets.sqlite"
db = SQLAlchemy(app)

class DictMixIn:
    def to_dict(self):
        return {
            column.name: getattr(self, column.name)
            if not isinstance(getattr(self, column.name), datetime.datetime)
            else getattr(self, column.name).isoformat()
            for column in self.__table__.columns
        }


class Pet(db.Model, DictMixIn):
    __tablename__ = "pet"

    id = db.Column(db.Integer(), primary_key=True)
    date = db.Column(db.Date())
    age = db.Column(db.Integer())
    name = db.Column(db.String())
    type = db.Column(db.String())
    color = db.Column(db.String())


@app.before_first_request
def init_app():
    db.create_all()
    db.session.add(Pet(date=datetime.datetime.utcnow() - datetime.timedelta(days=7), name="Sample Pet 1", age=12, type="fish", color="green"))
    db.session.add(Pet(date=datetime.datetime.utcnow() - datetime.timedelta(days=7), name="Sample Pet 2", age=13, type="dog", color="green"))
    db.session.add(Pet(date=datetime.datetime.utcnow() - datetime.timedelta(days=3), name="Sample Pet 3", age=14, type="cat", color="green"))
    db.session.add(Pet(date=datetime.datetime.utcnow(), name="felix", age=14, type="cat", color="green"))
    db.session.add(Pet(date=datetime.datetime.utcnow(), name="felix", age=14, type="dog", color="green"))


    db.session.commit()


@app.route("/")
def home():
    return "Welcome to Pet Lister!"


@app.route("/all_pets")
def show_all():
    pets = Pet.query.all()
    return jsonify([pet.to_dict() for pet in pets])


@app.route("/pet_page/<pet_id>")
def pet_page(pet_id):

    try:
        pet = Pet.query.filter(Pet.id == int(pet_id)).first()
        return pet.to_dict()

    except Exception as e:
        return jsonify({"status": "failure", "error": str(e)})

    return "Pet not found!", 404


@app.route("/add_pet", methods=["POST"])
def collect():

    try:
        data = request.json

        db.session.add(
            Pet(
                date=datetime.datetime.utcnow(),
                name=data["name"],
                age=int(data["age"]),
                type=data["type"],
                color=data["color"],
            )
        )

        db.session.commit()

        return {"status": "sucess"}

    except Exception as e:
        return jsonify({"status": "failure", "error": str(e)})

@app.route("/search_type")
def search_type():

    request_type = request.args.get("type")
    request_name = request.args.get("name")
    request_start = request.args.get("start")
    request_end = request.args.get("end")
    try:
        base_cmd = Pet.query

        if request_type:
            base_cmd = base_cmd.filter(Pet.type == request_type)
        
        if request_name:
            base_cmd = base_cmd.filter(Pet.name == request_name)
        
        if request_start:
            base_cmd = base_cmd.filter(Pet.date >= datetime.datetime.strptime(request_start, "%Y-%m-%d"))
        
        if request_end:
            base_cmd = base_cmd.filter(Pet.date <= datetime.datetime.strptime(request_end, "%Y-%m-%d"))

        data = base_cmd.all()

        return jsonify([pet.to_dict() for pet in data])

    except Exception as e:
        return jsonify({"status": "failure", "error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
