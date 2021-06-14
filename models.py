from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)

    username = db.Column(db.String(25), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    orders = db.relationship("Order", backref="user", lazy=True)
    products = db.relationship("Product", backref="user", lazy=True)

    def add_order(self, startTime, amount):
        o = Order(startTime=datetime.utcnow, amount=amount, user_id=self.id)
        db.session.add(o)
        db.session.commit()


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)

    regTime = db.Column(db.DateTime)#, default=datetime.utcnow)
    planTime = db.Column(db.DateTime)

    # Quantity to order
    amount = db.Column(db.Integer)

    # Emission data for product model
    total_CO2e = db.Column(db.Float)

    # Emission factor for order
    EF = db.Column(db.Float) # [gCO2e / kWh]

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    products = db.relationship("Product", backref="order", lazy=True)

    def add_product(self, name):
        p = Product(name=name, order_id=self.id)
        db.session.add(p)
        db.session.commit()


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    #imgFile = db.Column(db.String(30), nullable=False, default='/static/images/xr_test.jpg')

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    #Emission data for components
    total_LCI = db.Column(db.Float)

    #Emission data for assembly activities
    AAU_Wh = db.Column(db.Float)

    #order_rel = db.relationship("Order", backref='product', lazy=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))

    components = db.relationship("Component", backref="product", lazy=True)


    def add_component(self, name, part_no, specs):
        c = Component(name=name, part_no=part_no, specs=specs, product_id=self.id)
        db.session.add(c)
        db.session.commit()
    
#################### BOM ########################

class Component(db.Model):
    __tablename__ = "components"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(20), nullable=False)
    part_no = db.Column(db.Integer, nullable=False)
    specs = db.Column(db.String(25), nullable=False)

    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))#, nullable=False)

    # New
    #operation_id = db.Column(db.Integer, db.ForeignKey("operations.id"), nullable=False)

    #operation = db.relationship("Operation", foreign_keys="[Component.operation_id]", backref='component', lazy=True)
    
    properties = db.relationship("Property", back_populates="components", lazy=True)
    
    def add_property(self, material_name, emissionData_value, ref_LCI):
        prop = Property(material_name=material_name, emissionData_value=emissionData_value, ref_LCI=ref_LCI, component_id=self.id)
        db.session.add(prop)
        db.session.commit()


class Property(db.Model):
    __tablename__ = "properties"
    id = db.Column(db.Integer, primary_key=True)

    material_name = db.Column(db.VARCHAR(25), nullable=False)
    emissionData_value = db.Column(db.Float, nullable=False)
    
    ref_LCI = db.Column(db.String)

    component_id = db.Column(db.Integer, db.ForeignKey("components.id"), nullable=False)
    
    components = db.relationship("Component", back_populates="properties", lazy=True)

    # Rel to activities
    #activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"), nullable=False)
    #activities = db.relationship("Activity", backref='property', lazy=True)

    

#################### Routing ########################

class Workstation(db.Model):
    __tablename__ = "workstations"
    id = db.Column(db.Integer, primary_key=True)

    step_no = db.Column(db.Integer)
    description = db.Column(db.String(25), nullable=False)
    
    #New
    ip_address = db.Column(db.String(25))

    #operation_time = db.Column(db.Float, nullable=False)
    #intensity_value = db.Column(db.Float)

    resource = db.relationship("Resource", backref="workstation", lazy=True)

    def add_resource(self, name, ip_address):
        r = Resource(name=name, workstation_id=self.id)
        db.session.add(r)
        db.session.commit()


class Resource(db.Model):
    __tablename__ = "resources"
    id = db.Column(db.Integer, primary_key=True)

    imgFile = db.Column(db.String(30), nullable=False, default='Festo_w444.png')
    name = db.Column(db.String(25), nullable=False)
    
    ressID = db.Column(db.Integer)

    workstation_id = db.Column(db.Integer, db.ForeignKey("workstations.id"), nullable=False)

    activities = db.relationship("Activity", backref="resource", lazy=True)

    def add_activity(self, name, prog_no, delta_t, el_energy, air_energy, resID):
        a = Activity(name=name, prog_no=prog_no, delta_t=delta_t, el_energy=el_energy, air_energy=air_energy, resID=self.id)
        db.session.add(a)
        db.session.commit()


class Activity(db.Model):
    __tablename__ = "activity"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)

    # New:
    prog_no = db.Column(db.Integer)

    delta_t = db.Column(db.Float)

    el_energy = db.Column(db.Float, nullable=False)
    air_energy = db.Column(db.Float)
    
    resID = db.Column(db.Integer, db.ForeignKey("resources.id"), nullable=False)

    propertyID = db.Column(db.Integer, db.ForeignKey("properties.id"), nullable=False)
    propertY = db.relationship("Property", foreign_keys="[Activity.propertyID]", backref='activities', lazy=True)

########################## ORDER TABLES ###########################


#########################################
# Sintax sqlite3:

# Access a database i nthe same folder:  ".\sqlite3.exe .\test_schema.db"
# Show all tables: ".tables"
# SHow the content of a table: "select * from orders"

# Postgress 4545 port 5432
# Database Superuser: postgres