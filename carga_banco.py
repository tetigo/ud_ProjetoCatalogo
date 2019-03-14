from app import db
from models import User, Category, Item

c1 = Category()
c1.name = 'Hockey'
c2 = Category()
c2.name = 'Baseball'
db.session.add(c1)
db.session.add(c2)
db.session.commit()
