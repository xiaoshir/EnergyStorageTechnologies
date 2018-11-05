from energystoragetechnologies import db

class Technology(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    parameter = db.relationship('Parameter', backref='technology', lazy=True)
    level = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return self.name


class Parameter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float)
    technology_name = db.Column(db.String, db.ForeignKey('technology.name'), nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey('source.id'), nullable=False)
    unit = db.Column(db.String(50))

class Source(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(1000))
    articletitle = db.Column(db.String(1000))
    author = db.Column(db.String(1000))
    releaseyear = db.Column(db.Integer)
    parameter = db.relationship('Parameter', backref='source', lazy=True)