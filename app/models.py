from app import db

class Task(db.Model):                                                                                                                                                                         
    id = db.Column(db.String(35), primary_key=True)                                                                                                                                           
    host = db.Column(db.String(256))                                                                                                                                                          
    user = db.Column(db.String(256))                                                                                                                                                          
    status = db.Column(db.String(2048))                                                                                                                                                       
    command = db.Column(db.String(2048))                                                                                                                                                      
    result = db.Column(db.String(2048))

db.create_all()
