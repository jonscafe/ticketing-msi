from app import db, User
new_responder = User(username="responder1", password="securepassword", role="Responder")
db.session.add(new_responder)
db.session.commit()
print("Responder added successfully!")
