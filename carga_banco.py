from app import db
from models import User, Category, Item

exists = Category.query.filter_by(name='Hockey').first()
if not exists:
    c1 = Category()
    c1.name = 'Hockey'
    db.session.add(c1)

exists = Category.query.filter_by(name='Baseball').first()
if not exists:
    c2 = Category()
    c2.name = 'Baseball'
    db.session.add(c2)

db.session.commit()

print('------------------------------')
print('Dados adicionados com Sucesso!')
print('------------------------------')
