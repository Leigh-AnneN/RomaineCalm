DROP DATABASE IF EXISTS romainecalm;

CREATE DATABASE romainecalm;

from app import app
from models import db, Cupcake


db.drop_all()
db.create_all()

c1 = Cupcake(
    flavor="cherry",
    size="large",
    rating=5,
)

c2 = Cupcake(
    flavor="chocolate",
    size="small",
    rating=9,
    image="https://www.bakedbyrachel.com/wp-content/uploads/2018/01/chocolatecupcakesccfrosting1_bakedbyrachel.jpg"
)

db.session.add_all([c1, c2])
db.session.commit()

def create_app():
  app = Flask(__name__)

  db = SQLAlchemy()
  db.init_app(app)

  seeder = FlaskSeeder()
  seeder.init_app(app, db)

  return app