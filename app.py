import os
basedir = os.path.abspath(os.path.dirname(__file__))
import requests
import simplejson as json
import serial
import time
import pdfkit
import sqlite3


from datetime import datetime
from flask import Flask, make_response, session, render_template, jsonify, request, redirect, url_for, flash, abort

from flask_session import Session
#from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import create_engine
#from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import asc
#from sqlalchemy import update

from models import *

from passlib.hash import sha256_crypt


#Configuration to generate pdfs:
#1options = {'enable-local-file-access': None,'javascript-delay': 3000}
#2path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
#3config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

app = Flask(__name__)

# Set the secret key to some random bytes. (for session)
# python3 -c 'import os; print(os.urandom(16))'
app.secret_key = b"\x04\x02\xd7 \xd4.\xb0\x9a\x08\xe4E\xe2\x91\x12i'"

# Configure session to use filesystem
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(basedir, 'config_db.db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#engine = create_engine('sqlite:///' + os.path.join(basedir, 'configurator_schema2.db', echo = True)

#db = SQLAlchemy(app)#, session_options={"autoflush": False})
db.init_app(app)

# Configure session to use filesystem
#app.config["SESSION_PERMANENT"] = False
#app.config["SESSION_TYPE"] = "filesystem"
#db.init_app(app)
#wkhtmltopdf = Wkhtmltopdf(app)

'''
DATABASE_CONNECTION_INFO = 'sqlite:///configurator_schema2.db'
engine = create_engine(DATABASE_CONNECTION_INFO, echo=False)
db = scoped_session(
    sessionmaker(
        autoflush=True,
        autocommit=False,
        bind=engine
    )
)
'''


@app.route("/", methods=["GET", "POST"])
def index():

    if 'username' in session:

        #pdfkit.from_file("./configurator/templates/prod_details.html", "out.pdf", configuration=config)
        #pdfkit.from_file('./configurator/templates/index.html', 'out.pdf')

        return render_template("index.html")
    #return "You are not logged in <br><a href = '/login'>" + "click here to log in</a>"
    return redirect(url_for('login'))


@app.route("/create", methods=["GET", "POST"])
def create():

    if 'username' in session:
    
        orders = Order.query.all()
        products = Product.query.all()
        components = Component.query.all()

        return render_template("create.html", orders=orders, products=products, components=components)
    return redirect(url_for('login'))


@app.route("/prod/<int:prod_id>", methods=["GET", "POST"])
def view(prod_id):

    if 'username' in session:

        a = request.args.get('a')

        # db.execute("SELECT * FROM components WHERE id = :id", {"id": prod_id}).fetchall()
        
        #Product = Product.query.get(prod_id)
        products = Product.query.all()
        BOM = Component.query.filter_by(product_id=prod_id).all()
        
        for item in BOM:
            print(item.name)

        return render_template("create.html", BOM=BOM, products=products, result=a)

    return redirect(url_for('login'))
         
######################################### TEST ################################

@app.route('/_show', methods=["GET", "POST"])
def show():
    #a = request.args.get('a')
    #print(a)

    if request.method == "POST":
        comp_id = request.form.get("comp_id") 
        component = Component.query.get(comp_id)
        print(component.product_id)
        
        material_name = request.form.get("material_name")
        eData_value = float(request.form.get("eData_value"))
        UUID = request.form.get("UUID")
        #print(a, material_name, eData_value, eData_unit)

        component.add_property(material_name=material_name, emissionData_value=eData_value, ref_LCI = UUID)

        print(f"Added component for {component}: material_name {material_name} | eData_value: {eData_value} | UUID: {UUID}.")

        return redirect(f'/prod/{component.product_id}')

######################################### Create component ################################

@app.route("/createComponent", methods=["POST"])
def createComponent():

    prod_id = request.form.get("prod_id")
    print("The choice number is : ", prod_id)

    prod = Product.query.get(prod_id)

    if prod:

        C_name = request.form.get("C_name")
        part_no = request.form.get("part_no")
        specs = request.form.get("dimensions")

        print(C_name,part_no, specs)

        prod.add_component(C_name, part_no, specs)
        print(f"Added component for {prod}: component {C_name} | part number: {part_no} | specs: {specs}.")
    
    else:
        order = Order()
        db.session.add(order)
        db.session.commit()

        name = request.form.get("P_name")
        order.add_product(name)
        
        
    return redirect(url_for('create'))

######################################### Create property ################################


######################################### Customize model ################################
@app.route("/configurator", methods=["GET", "POST"])
def configurator():
    
    if 'username' in session:

        if request.method == "GET":
            products = Product.query.all()

            return render_template("configurator.html", products=products)


        if request.method == "POST":

            p_name = request.form.get("P_name")

            user = User.query.filter_by(username=session['username']).first()
            print("the user is:", user.name)

            # Assign an order
            #order = Order()
            #db.session.add(order)
            #db.session.commit()

            prod = Product(name=p_name, user_id=user.id)
            db.session.add(prod)
            db.session.commit()

            prod_id = prod.id
            print("The product created is:", prod.name)

            return redirect(f'/model/{prod_id}')

        return render_template("configurator.html")
        
    else:
        return redirect(url_for('login'))


@app.route("/model/<int:prod_id>", methods=["GET", "POST"])
def start(prod_id):

    if request.method == "POST":
        
        # Extract the user input
        prod_id = request.form.get('c')
        d = request.form.get('d')
        
        # Convert from JSON to Python                                        #https://www.w3schools.com/python/python_json.asp
        dJSON = json.loads(d)
        print("AJAX createModel:", dJSON, "the product ID:", prod_id)

        for item in dJSON:
            # Extract the user input (Chosen properties)
            # Query the db for the chosen property object 
            prop = Property.query.get(item["id"])
            print("The property is",prop.material_name, "e_value:", prop.emissionData_value)
        
            # Query db for the parent of property (component):
            comp = Property.query.filter_by(id=item["id"]).first().components
            print("The associated component for property is", comp.name)

            # Add component to db:
            component = Component(name=comp.name, part_no=comp.part_no, specs=comp.specs, product_id=prod_id)
            db.session.add(component)
            db.session.commit()
            
            # Add propertyy
            propertyy = Property(material_name=prop.material_name, emissionData_value=prop.emissionData_value, component_id=component.id)
            db.session.add(propertyy)
            db.session.commit()
            
            # Total LCI
            prod = Product.query.filter_by(id=prod_id).first()
            co = prod.components

            list1 = []

            for el in co:
                for item in el.properties:
                    list1.append(item.emissionData_value)

            total = sum(list1)
            print("Total for component....:", total)

            prod.total_LCI = round(total,4) 
            db.session.commit()

            
            #order = Product.query.filter_by(id=prod_id).first().order
            #order.m_amount = m_amount

        return redirect(url_for('createOrder'))#f'/order/{prod_id}')

    elif request.args.get('a'):

        # Extract the user input (selected components)
        a = request.args.get('a')
        prod_id = request.args.get('b')

        # Parse JSON to Python dictionary                                      #https://www.w3schools.com/python/python_json.asp
        aJSON = json.loads(a)
        print("AJAX createModel:", aJSON, "the product id:", prod_id)
    
        responseList = []
        compList = []
        serverList = {"component": [], "property": [], "id": [],"emissionValue": [] }  
        propList = []
        propIdList = []
        emisValueList = []
        emisUnitList = []
        
        for item in aJSON:

            # Query db for matching components
            c = Component.query.filter_by(name=item["name"]).first()
            print("Here is the component:", c.name, c.part_no, c.specs, c.properties)

            if c.name == "Bottom housing":
                # Append the component name to the component list
                compList.append(c.name)
                # Append the component list to the coresponding server entry list
                serverList["component"].append(compList)

                # Iterate through the components properties and append to property list
                for el in c.properties:
                    print(el.material_name)
                    propList.append(el.material_name)
                    propIdList.append(el.id)
                    emisValueList.append(el.emissionData_value)
                    
                # Append the "property", "emissionValue" list to the coresponding serverList entry
                serverList["property"].append(propList)
                serverList["id"].append(propIdList)
                serverList["emissionValue"].append(emisValueList)

                # Append the server list to the response list
                responseList.append(serverList)

                # Clear lists and dictionaries for the next loop
                serverList = {"component": [], "property": [], "id": [],"emissionValue": [] }  
                compList = []
                propList = []
                propIdList = []
                emisValueList = []
                emisUnitList = []

                print("if Bottom:", responseList)              
                        
            elif c.name == "Printed circuit board (PCB)":
                # Append the component name to the component list
                compList.append(c.name)
                # Append the component list to the coresponding server entry list
                serverList["component"].append(compList)

                # Iterate through the components properties and append to property list
                for el in c.properties:
                    print(el.material_name)
                    propList.append(el.material_name)
                    propIdList.append(el.id)
                    emisValueList.append(el.emissionData_value)
                    
                # Append the "property", "emissionValue" list to the coresponding serverList entry
                serverList["property"].append(propList)
                serverList["id"].append(propIdList)
                serverList["emissionValue"].append(emisValueList)

                # Append the server list to the response list
                responseList.append(serverList)

                # Clear lists and dictionaries for the next loop
                serverList = {"component": [], "property": [], "id": [],"emissionValue": []}  
                compList = []
                propList = []
                propIdList = []
                emisValueList = []
                emisUnitList = []

                print("if PCB:", responseList)

            elif c.name == "Fuse 1":
                # Append the component name to the component list
                compList.append(c.name)
                # Append the component list to the coresponding server entry list
                serverList["component"].append(compList)

                # Iterate through the components properties and append to property list
                for el in c.properties:
                    print(el.material_name)
                    propList.append(el.material_name)
                    propIdList.append(el.id)
                    emisValueList.append(el.emissionData_value)
                    
                # Append the "property", "emissionValue" list to the coresponding serverList entry
                serverList["property"].append(propList)
                serverList["id"].append(propIdList)
                serverList["emissionValue"].append(emisValueList)

                # Append the server list to the response list
                responseList.append(serverList)

                # Clear lists and dictionaries for the next loop
                serverList = {"component": [], "property": [], "id": [],"emissionValue": [] }  
                compList = []
                propList = []
                propIdList = []
                emisValueList = []
                emisUnitList = []

                print("if FUSE1:", responseList)

            elif c.name == "Fuse 2":
                # Append the component name to the component list
                compList.append(c.name)
                # Append the component list to the coresponding server entry list
                serverList["component"].append(compList)

                # Iterate through the components properties and append to property list
                for el in c.properties:
                    print(el.material_name)
                    propList.append(el.material_name)
                    propIdList.append(el.id)
                    emisValueList.append(el.emissionData_value)
                    
                # Append the "property", "emissionValue"  list to the coresponding serverList entry
                serverList["property"].append(propList)
                serverList["id"].append(propIdList)
                serverList["emissionValue"].append(emisValueList)

                # Append the server list to the response list
                responseList.append(serverList)

                # Clear lists and dictionaries for the next loop
                serverList = {"component": [], "property": [], "id": [],"emissionValue": [] }  
                compList = []
                propList = []
                propIdList = []
                emisValueList = []
                emisUnitList = []

                print("if FUSE2:", responseList)

            elif c.name == "Top housing":
                # Append the component name to the component list
                compList.append(c.name)
                # Append the component list to the coresponding server entry list
                serverList["component"].append(compList)

                # Iterate through the components properties and append to property list
                for el in c.properties:
                    print(el.material_name)
                    propList.append(el.material_name)
                    propIdList.append(el.id)
                    emisValueList.append(el.emissionData_value)
                    
                # Append the "property", "emissionValue"  list to the coresponding serverList entry
                serverList["property"].append(propList)
                serverList["id"].append(propIdList)
                serverList["emissionValue"].append(emisValueList)

                # Append the server list to the response list
                responseList.append(serverList)

                # Clear lists and dictionaries for the next loop
                serverList = {"component": [], "property": [], "id": [],"emissionValue": [] }  
                compList = []
                propList = []
                propIdList = []
                emisValueList = []
                emisUnitList = []

                print("if TOP:", responseList)

        
        return jsonify({"success": True, "result": responseList})

    return render_template("configurator2.html", prod_id=prod_id)



@app.route("/product/<int:prod_id>", methods=["GET", "POST"])
def showProd(prod_id):
    
    if request.form.get("pdf"):

        print("You clicked PDF >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print(pdfkit)
        
        prod = Product.query.filter_by(id=prod_id).first()
        print(prod)
        comps = Component.query.filter_by(product_id=prod_id).all()

        products = Product.query.filter_by(id=prod_id).all()
        propData = []

        compList = []
        actList = []
        act_dtime = []
        act_el = []
        act_air = []
        act_Wh = []
        comp_Wh = []
        prod_Wh = []

        prod_info = { "P_ID": [], "components": [], "activities": [], 
        "act_el": [], "act_air":[], "act_Wh":[], "act_dt":[],
        "comp_Wh": [], "total_Wh": [], "prop_LCI":[], "total_gCo2e_kWh": []
                    }

        for prod in products:
            comps = prod.components
            print("Components:",prod, comps)

            prod_info['P_ID'].append(prod.id)



            for comp in comps:
                
                # Query db for operation activities corresponding to the components configuration
                
                for prop in comp.properties:
                    print("------>",prod.id, prop.id, prop.material_name)
    
                    component = Component.query.filter(Component.name==comp.name).first()
                    print("comonent name,id:",component.name, component.id)
                    props = Property.query.filter(Property.material_name==prop.material_name, Property.component_id==component.id).all()
                    
                    compList.append(component.name)
                    
                    for prop in props:

                        # Extract component property emission value:
                        propData.append(prop.emissionData_value) 

                        for act in prop.activities:
                            #print(act,"------->", prod.id, comp.name, comp.id, prop.material_name, prop.id, act.name)
                            act_dt = act.delta_t
                            act_el_Wh = act.el_energy /3600
                            act_air_Wh = act.air_energy / 3600
                            act_TOT_Wh = act_el_Wh + act_air_Wh
                            #print("Wh for el activity", act_el_Wh)
                            #print("Wh for air activity", act_air_Wh)
                            #print("Total Wh for activity", act_TOT_Wh)

                            act_dtime.append(act_dt)
                            act_el.append(round(act_el_Wh,4))
                            act_air.append(round(act_air_Wh,4))
                            act_Wh.append(round(act_TOT_Wh,4))
                            actList.append(act.name)
                            print("List Wh for activity", act_Wh)

                    prod_info['act_dt'].append(act_dtime)
                    prod_info['act_el'].append(act_el)
                    prod_info['act_air'].append(act_air)
                    prod_info['act_Wh'].append(act_Wh)
                    comp_Wh.append(sum(act_Wh))
                    prod_Wh.append(sum(comp_Wh))
                    prod_info['comp_Wh'].append(comp_Wh)
                    prod_info['prop_LCI'].append(sum(propData))
                    
                    act_dtime = []
                    act_el = []
                    act_air = []
                    act_Wh = []
                    comp_Wh = []
                    propData = []

                prod_info['activities'].append(actList)
                actList = []

                prod_info['components'].append(compList)
                compList = []

            prod_info['total_Wh'].append(sum(prod_Wh))
            # Average gCO2e/kWh is 194 (latest in 2018) as stated in https://en.energinet.dk/About-our-reports/Reports/Environmental-Report-2018
            val = prod_info['total_Wh'][0]
            prod_info['total_gCo2e_kWh'] = round(val, 4)
            prod_Wh = []

        #test = json.dumps(prod_info)
        html = render_template("prod_details.html", prod=prod, comps=comps, prod_info=prod_info)

        pdf = pdfkit.from_string(html, False, configuration=config, options=options)
        response = make_response(pdf)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = "attachment; filename=report001.pdf"
        return response

    elif request.method == "GET":    
        propData = []

        compList = []
        actList = []
        act_dtime = []
        act_el = []
        act_air = []
        act_Wh = []
        comp_Wh = []
        prod_Wh = []

        prod_info = { "P_ID": [], "components": [], "activities": [], 
        "act_el": [], "act_air":[], "act_Wh":[], "act_dt":[],
        "comp_Wh": [], "total_Wh": [], "prop_LCI":[], "total_gCo2e_kWh": []
                    }


        products = Product.query.filter_by(id=prod_id).all()
        comps = Component.query.filter_by(product_id=prod_id).all()

        
        for prod in products:
            comps = prod.components
            print("Components:",prod, comps)

            prod_info['P_ID'].append(prod.id)

            for comp in comps:
                
                # Query db for operation activities corresponding to the components configuration
                
                for prop in comp.properties:
                    print("------>",prod.id, prop.id, prop.material_name)
    
                    component = Component.query.filter(Component.name==comp.name).first()
                    print("comonent name,id:",component.name, component.id)
                    props = Property.query.filter(Property.material_name==prop.material_name, Property.component_id==component.id).all()
                    
                    compList.append(component.name)
                    
                    for prop in props:

                        # Extract component property emission value:
                        propData.append(prop.emissionData_value) 

                        for act in prop.activities:
                            #print(act,"------->", prod.id, comp.name, comp.id, prop.material_name, prop.id, act.name)
                            act_dt = act.delta_t
                            act_el_Wh = act.el_energy /3600
                            act_air_Wh = act.air_energy / 3600
                            act_TOT_Wh = act_el_Wh + act_air_Wh
                            #print("Wh for el activity", act_el_Wh)
                            #print("Wh for air activity", act_air_Wh)
                            #print("Total Wh for activity", act_TOT_Wh)

                            act_dtime.append(act_dt)
                            act_el.append(round(act_el_Wh,4))
                            act_air.append(round(act_air_Wh,4))
                            act_Wh.append(round(act_TOT_Wh,4))
                            actList.append(act.name)
                            print("List Wh for activity", act_Wh)

                    prod_info['act_dt'].append(act_dtime)
                    prod_info['act_el'].append(act_el)
                    prod_info['act_air'].append(act_air)
                    prod_info['act_Wh'].append(act_Wh)
                    comp_Wh.append(sum(act_Wh))
                    prod_Wh.append(sum(comp_Wh))
                    prod_info['comp_Wh'].append(comp_Wh)
                    prod_info['prop_LCI'].append(sum(propData))
                    
                    act_dtime = []
                    act_el = []
                    act_air = []
                    act_Wh = []
                    comp_Wh = []
                    propData = []

                prod_info['activities'].append(actList)
                actList = []

                prod_info['components'].append(compList)
                compList = []

            prod_info['total_Wh'].append(sum(prod_Wh))
            # Average gCO2e/kWh is 194 (latest in 2018) as stated in https://en.energinet.dk/About-our-reports/Reports/Environmental-Report-2018
            val = prod_info['total_Wh'][0] 
            prod_info['total_gCo2e_kWh'] = round(val, 4)
            
            prod_Wh = []
            print(prod_info)

            test = json.dumps(prod_info)

        return render_template("prod_details.html", prod=prod, comps=comps, prod_info=prod_info, test=test)


##################### Show order #################################

@app.route("/order/<int:order_id>", methods=["GET", "POST"])
def showOrder(order_id):
    if 'username' in session:

        order = Order.query.get(int(order_id))
        produse = order.products

        for produs in produse:
            prod_id = produs.id

        if request.form.get("pdf"):

            print("You clicked PDF >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            print(pdfkit)

            propData = []
            compList = []
            actList = []
            act_dtime = []
            act_el = []
            act_air = []
            act_Wh = []
            comp_Wh = []
            prod_Wh = []


            prod_info = { "P_ID": [], "o_pcs": [], "components": [], "activities": [], 
            "act_el": [], "act_air":[], "act_Wh":[], "act_dt":[],
            "comp_Wh": [], "total_Wh": [], "prop_LCI":[], "total_gCo2e_Wh": [], "o_EF":[]
                        }
            
            products = Product.query.filter_by(id=prod_id).all()
            comps = Component.query.filter_by(product_id=prod_id).all()

            
            for prod in products:
                comps = prod.components
                print("Components:",prod, comps)

                prod_info['P_ID'].append(prod.id)

                for comp in comps:
                    
                    # Query db for operation activities corresponding to the components configuration
                    
                    for prop in comp.properties:
                        print("------>",prod.id, prop.id, prop.material_name)
        
                        component = Component.query.filter(Component.name==comp.name).first()
                        print("comonent name,id:",component.name, component.id)
                        props = Property.query.filter(Property.material_name==prop.material_name, Property.component_id==component.id).all()
                        
                        compList.append(component.name)
                        
                        for prop in props:

                            # Extract component property emission value:
                            propData.append(prop.emissionData_value) 

                            for act in prop.activities:
                                #print(act,"------->", prod.id, comp.name, comp.id, prop.material_name, prop.id, act.name)
                                act_dt = act.delta_t
                                act_el_Wh = act.el_energy /3600
                                act_air_Wh = act.air_energy / 3600
                                act_TOT_Wh = act_el_Wh + act_air_Wh
                                #print("Wh for el activity", act_el_Wh)
                                #print("Wh for air activity", act_air_Wh)
                                #print("Total Wh for activity", act_TOT_Wh)

                                act_dtime.append(act_dt)
                                act_el.append(round(act_el_Wh,4))
                                act_air.append(round(act_air_Wh,4))
                                act_Wh.append(round(act_TOT_Wh,4))
                                actList.append(act.name)
                                print("List Wh for activity", act_Wh)

                        prod_info['act_dt'].append(act_dtime)
                        prod_info['act_el'].append(act_el)
                        prod_info['act_air'].append(act_air)
                        prod_info['act_Wh'].append(act_Wh)
                        comp_Wh.append(sum(act_Wh))
                        prod_Wh.append(sum(comp_Wh))
                        prod_info['comp_Wh'].append(comp_Wh)
                        prod_info['prop_LCI'].append(sum(propData))
                        
                        act_dtime = []
                        act_el = []
                        act_air = []
                        act_Wh = []
                        comp_Wh = []
                        propData = []

                    prod_info['activities'].append(actList)
                    actList = []

                    prod_info['components'].append(compList)
                    compList = []

                prod_info['total_Wh'].append(sum(prod_Wh))
                # Average gCO2e/kWh is 194 (latest in 2018) as stated in https://en.energinet.dk/About-our-reports/Reports/Environmental-Report-2018
                val = prod_info['total_Wh'][0] * order.EF / 1000# * 194
                prod_info['total_gCo2e_Wh'] = round(val, 2)
                prod_Wh = []
                print(prod_info)

                prod_info['o_pcs'] = order.amount
                prod_info['o_EF'] = order.EF

            #test = json.dumps(prod_info)
            html = render_template("order_details.html", order=order, prod=prod, comps=comps, prod_info=prod_info)

            pdf = pdfkit.from_string(html, False, configuration=config, options=options)
            response = make_response(pdf)
            response.headers["Content-Type"] = "application/pdf"
            response.headers["Content-Disposition"] = "attachment; filename=report001.pdf"
            return response

        elif request.method == "GET":    
            propData = []
            compList = []
            actList = []
            act_dtime = []
            act_el = []
            act_air = []
            act_Wh = []
            comp_Wh = []
            prod_Wh = []


            prod_info = { "P_ID": [], "o_pcs": [], "components": [], "activities": [], 
            "act_el": [], "act_air":[], "act_Wh":[], "act_dt":[],
            "comp_Wh": [], "total_Wh": [], "prop_LCI":[], "total_gCo2e_Wh": [], "o_EF":[]
                        }
            
            products = Product.query.filter_by(id=prod_id).all()
            comps = Component.query.filter_by(product_id=prod_id).all()

            
            for prod in products:
                comps = prod.components
                print("Components:",prod, comps)

                prod_info['P_ID'].append(prod.id)

                for comp in comps:
                    
                    # Query db for operation activities corresponding to the components configuration
                    
                    for prop in comp.properties:
                        print("------>",prod.id, prop.id, prop.material_name)
        
                        component = Component.query.filter(Component.name==comp.name).first()
                        print("comonent name,id:",component.name, component.id)
                        props = Property.query.filter(Property.material_name==prop.material_name, Property.component_id==component.id).all()
                        
                        compList.append(component.name)
                        
                        for prop in props:

                            # Extract component property emission value:
                            propData.append(prop.emissionData_value) 

                            for act in prop.activities:
                                #print(act,"------->", prod.id, comp.name, comp.id, prop.material_name, prop.id, act.name)
                                act_dt = act.delta_t
                                act_el_Wh = act.el_energy /3600
                                act_air_Wh = act.air_energy / 3600
                                act_TOT_Wh = act_el_Wh + act_air_Wh
                                #print("Wh for el activity", act_el_Wh)
                                #print("Wh for air activity", act_air_Wh)
                                #print("Total Wh for activity", act_TOT_Wh)

                                act_dtime.append(act_dt)
                                act_el.append(round(act_el_Wh,4))
                                act_air.append(round(act_air_Wh,4))
                                act_Wh.append(round(act_TOT_Wh,4))
                                actList.append(act.name)
                                print("List Wh for activity", act_Wh)

                        prod_info['act_dt'].append(act_dtime)
                        prod_info['act_el'].append(act_el)
                        prod_info['act_air'].append(act_air)
                        prod_info['act_Wh'].append(act_Wh)
                        comp_Wh.append(sum(act_Wh))
                        prod_Wh.append(sum(comp_Wh))
                        prod_info['comp_Wh'].append(comp_Wh)
                        prod_info['prop_LCI'].append(sum(propData))
                        
                        act_dtime = []
                        act_el = []
                        act_air = []
                        act_Wh = []
                        comp_Wh = []
                        propData = []

                    prod_info['activities'].append(actList)
                    actList = []

                    prod_info['components'].append(compList)
                    compList = []

                prod_info['total_Wh'].append(sum(prod_Wh))
                # Average gCO2e/kWh is 194 (latest in 2018) as stated in https://en.energinet.dk/About-our-reports/Reports/Environmental-Report-2018
                val = prod_info['total_Wh'][0] * order.EF / 1000# * 194 [gCO2e/Wh]
                prod_info['total_gCo2e_Wh'] = round(val, 2)
                prod_Wh = []
                print(prod_info)

                prod_info['o_pcs'] = order.amount
                prod_info['o_EF'] = order.EF

                test = json.dumps(prod_info)


            return render_template("order_details.html", order=order, prod=prod, comps=comps, prod_info=prod_info, userObj=session['name'], test=test)
            
    else:
        return redirect(url_for('login'))

##################### Planned orders #################################

@app.route("/orders", methods=["GET", "POST"])
def plannedOrders():
    
    if 'username' in session:
        orders = User.query.filter_by(username=session['username']).first().orders

        return render_template("orders.html", orders=orders, userObj=session['name'])
        
    else:
        return redirect(url_for('login'))


##################### Order inquiry #################################
@app.route("/inquiry", methods=["GET", "POST"])
def createOrder():

    if 'username' in session:
        
        if request.method == 'GET':
            
            products = User.query.filter_by(username=session['username']).first().products
            print("the orders for the user are:", products) 

            propData = []
            actList = []
            act_dtime = []
            act_el = []
            act_air = []
            act_Wh = []
            comp_Wh = []
            prod_Wh = []

            prod_info = { "P_ID": [], "components": [], "activities": [], 
            "act_el": [], "act_air":[], "act_Wh":[], "act_dt":[],
            "comp_Wh": [],"prod_Wh": [],"prod_Wh_list": [], "total_prod_Wh": [] ,"prop_LCI":[], "total_gCo2e_Wh": []
                        }

            for prod in products:
                comps = prod.components
                print("Components:",prod, comps)

                prod_info['P_ID'].append(prod.id)


                for comp in comps:
                    
                    # Query db for operation activities corresponding to the components configuration
                    
                    for prop in comp.properties:
                        #print("------>",prod.id, prop.id, prop.material_name)
        
                        component = Component.query.filter(Component.name==comp.name).first()
                        #print("comonent name,id:",component.name, component.id)
                        props = Property.query.filter(Property.material_name==prop.material_name, Property.component_id==component.id).all()
                        
                        prod_info['components'].append(component.name)
                        #(prod_info['components'])
                        
                        for prop in props:

                            # Extract component property emission value:
                            propData.append(prop.emissionData_value) 

                            for act in prop.activities:
                                #print(act,"------->", prod.id, comp.name, comp.id, prop.material_name, prop.id, act.name)
                                act_dt = act.delta_t
                                act_el_Wh = act.el_energy / 3600
                                act_air_Wh = act.air_energy / 3600
                                act_TOT_Wh = act_el_Wh + act_air_Wh
                                #print("Wh for el activity", act_el_Wh)
                                #print("Wh for air activity", act_air_Wh)
                                #print("Total Wh for activity", act_TOT_Wh)

                                act_dtime.append(act_dt)
                                act_el.append(round(act_el_Wh,4))
                                act_air.append(round(act_air_Wh,4))
                                act_Wh.append(round(act_TOT_Wh,4))
                                actList.append(act.name)
                                prod_info['activities'].append(actList)
                                #print("Wh for activity",act.name, act_Wh, type(act_Wh))

                        prod_info['act_dt'].append(act_dtime)
                        prod_info['act_el'].append(act_el)
                        prod_info['act_air'].append(act_air)
                        prod_info['act_Wh'].append(act_Wh)
                        comp_Wh.append(sum(act_Wh))
                        #print("component.name |",component.name,"|| comp_Wh",comp_Wh)

                        prod_Wh.append(sum(comp_Wh))

                        prod_info['comp_Wh'].append(comp_Wh)
                        prod_info['prop_LCI'].append(sum(propData))
                        
                        act_dtime = []
                        act_el = []
                        act_air = []
                        act_Wh = []
                        comp_Wh = []
                        propData = []

                    print("Wh for each component configured:",prod_Wh)

                #print(prod.id)
                produs = Product.query.filter_by(id=prod.id).first()
                print(produs.name, produs.id, round(sum(prod_Wh),4), produs.AAU_Wh)

                if produs.AAU_Wh is None:
                    produs.AAU_Wh = round(sum(prod_Wh),4)
                    db.session.commit()
                    print("cheeeeeeeeeeeeeeeck:",produs.id, produs.AAU_Wh)

                prod_info['prod_Wh'].append(prod_Wh)
                #print("prod_info['prod_Wh']",prod_info['prod_Wh'])

                prod_info['prod_Wh_list'].append(sum(prod_Wh))
                
                total_Wh=sum(prod_Wh)
                #print("total_Wh for product",total_Wh)

                prod_info['total_prod_Wh'].append(sum(prod_Wh))
                #print("prod_info['total_prod_Wh']",prod_info['total_prod_Wh']) 

                prod_Wh = []
                
                #print("prod_info['total_gCo2e_Wh']",prod_info['total_gCo2e_Wh'])

            return render_template("o_inquiry.html", products=products, prod_info=prod_info, userObj=session['name'])

        elif request.method == 'POST':

            # Extract the user input
            prod_id = request.form.get('prod_id')
            o_qnty = request.form.get('o_qnty')
            o_pln = request.form.get('o_pln')

            print("****************************from client:", o_qnty, o_pln, prod_id)

            if o_pln:
                
                # Req params from energidataservice API
                url_endpoint = 'https://www.energidataservice.dk/proxy/api/datastore_search_sql'
                CO2_prog = {'sql': 'SELECT DISTINCT "Minutes5DK", "CO2Emission" FROM "co2emisprog" ORDER BY "Minutes5DK" DESC LIMIT 10'}
                resp_prog = requests.get(url_endpoint, params=CO2_prog, data={})
                CO2progJSON=resp_prog.json()

                # Create dict
                CO2e_prog = CO2progJSON['result']['records']
                #t_stamp_prog = CO2progJSON['result']['records'][0]['Minutes5DK']
                minList = []
                CO2e_Dict = {"CO2e": [] ,"t_stamp": []}
                for value in CO2e_prog:
                    print(value['CO2Emission'])
                    CO2e_Dict['CO2e'].append(value['CO2Emission'])
                    CO2e_Dict['t_stamp'].append(value['Minutes5DK'])
                    #minList.append(CO2e_Dict)
                
                # Find minimum value
                CO2min = min(CO2e_Dict['CO2e'])
                print("min value:", CO2min)
                
                # Extract min value and timestamp from list index
                i = CO2e_Dict['CO2e'].index(CO2min)
                print("inddex:", i)
                print("value:", CO2e_Dict['CO2e'][i], "with timestamp:", CO2e_Dict['t_stamp'][i])

                print("--------------------- type: ", type(CO2e_Dict['t_stamp'][i]))

                tISO = datetime.strptime(CO2e_Dict['t_stamp'][i], "%Y-%m-%dT%H:%M:%S")

                print("--------------------- type ISO: ", tISO, type(tISO))
                
                # Query db for user and product
                user = User.query.filter_by(username=session['username']).first()
                prod = Product.query.get(int(prod_id))

                #Format datetime object
                now = datetime.now()
                now_st = now.strftime("%Y-%m-%dT%H:%M:%S")
                t_f = datetime.strptime(now_st,"%Y-%m-%dT%H:%M:%S")

                ####### Computation CO2e for order:
                EF = float(CO2e_Dict['CO2e'][i]) # [ gCO2/kWh ]
                AAU_CO2e = round((prod.AAU_Wh * EF /1000 ),4) # [ gCO2e ] 
                #print("o_qnty",o_qnty,"| AAU_CO2e", AAU_CO2e)

                total_CO2e = AAU_CO2e + prod.total_LCI # [ gCO2e ]
                print("o_qnty",o_qnty,"| total_CO2e", total_CO2e)

                # Add order to db
                order = Order(regTime=t_f, planTime=tISO, amount=o_qnty, total_CO2e=total_CO2e, EF=EF, user_id=user.id)
                db.session.add(order)
                db.session.commit()

                prod.order_id = order.id  
                db.session.commit()
                
                flash(f"Your order is scheduled for production at {CO2e_Dict['t_stamp'][i]} ", "success")
                return redirect(url_for('plannedOrders'))
            
            else:

                url_endpoint = 'https://www.energidataservice.dk/proxy/api/datastore_search_sql'

                
                CO2_now = {'sql': 'SELECT DISTINCT "Minutes5DK", "CO2Emission" FROM "co2emis" ORDER BY "Minutes5DK" DESC LIMIT 1'}
                
                resp_now = requests.get(url_endpoint, params=CO2_now, data={})
                CO2nowJSON=resp_now.json()
                CO2e_now = CO2nowJSON['result']['records'][0]['CO2Emission']
                t_stamp_now = CO2nowJSON['result']['records'][0]['Minutes5DK']

                t_now = datetime.strptime(t_stamp_now, "%Y-%m-%dT%H:%M:%S")
                
                #Format datetime object
                now = datetime.now()
                now_st = now.strftime("%Y-%m-%dT%H:%M:%S")
                t_f = datetime.strptime(now_st,"%Y-%m-%dT%H:%M:%S")
                
                # Query db for user and product
                user = User.query.filter_by(username=session['username']).first()
                prod = Product.query.get(int(prod_id)) 

                ####### Computation CO2e for order:
                EF = float(CO2e_now) # [ gCO2/kWh ]
                AAU_CO2e = round((prod.AAU_Wh * EF /1000 ),4) # [ gCO2 ]
                #print("o_qnty",o_qnty,"| AAU_CO2e", AAU_CO2e)

                total_CO2e = AAU_CO2e + prod.total_LCI # [ gCO2e ]
                print("o_qnty",o_qnty,"| total_CO2e", total_CO2e)
                
                # Add order to db
                order = Order(regTime=t_f, amount=o_qnty, total_CO2e=total_CO2e, EF=EF, user_id=user.id)
                db.session.add(order)
                db.session.commit()

                # Update order ID for product
                prod.order_id = order.id  
                db.session.commit()

                flash("Your order is send as FIFO to production!!!", "danger")
                return redirect(url_for('plannedOrders'))

                #return jsonify({"success": True, "res":CO2progJSON})
        
        else:

            return render_template("o_inquiry.html", products=products, prod_info=prod_info, userObj=session['name'])
    else:
        return redirect(url_for('login'))


##################### Delete Order #################################

@app.route("/del_order/<int:o_id>", methods=["POST"])
def del_order(o_id):

    prod = Product.query.filter_by(order_id=o_id).all()

    for item in prod:
        comps = Component.query.filter_by(product_id=item.id).all()
        db.session.delete(item)
        for comp in comps:
            props = Property.query.filter_by(component_id=comp.id).all()
            db.session.delete(comp)
            for prop in props:
                db.session.delete(prop)
    
    order = Order.query.get(o_id)
    db.session.delete(order)
    db.session.commit()
    flash('Your order has been cancelled!', 'success')
    return redirect(url_for('plannedOrders'))


##################### Resource setup #################################

@app.route("/workplan", methods=["GET", "POST"])
def rSetup():

    comp = Component.query.filter_by(product_id=1).all()
    ops = Workstation.query.order_by(asc(Workstation.step_no)).all()
    ress = Resource.query.all()

    for r in ress:
        img_file = url_for('static', filename='images/' + r.imgFile)

    if request.method == "POST":

        if request.form.get("step_no"):
            comp_id = request.form.get("sel_comp")
            print("compt id:", comp_id)
            step_no = request.form.get("step_no")
            ip_add = request.form.get("ip_add")
            o_desc = request.form.get("o_desc")
            #o_t = request.form.get("o_t")
            #o_val = request.form.get("o_val")

            op = Workstation(step_no=step_no, ip_address=ip_add, description=o_desc)
            db.session.add(op)
            db.session.commit()
            
            ops = Workstation.query.all()

            print("The choice number is : ", op.description)
            
            return redirect(url_for('rSetup'))
        


            
    
    return render_template("rSetup.html", comp=comp, ops=ops, ress=ress)


##################### Operation #################################

@app.route("/operation/<int:op_id>", methods=["GET", "POST"])
def op_show(op_id):

    if 'username' in session:

        print(op_id)
        
        op = Workstation.query.get(op_id)

        ress = Resource.query.filter_by(workstation_id=op_id).all()

        if ress:
            for r in ress:
                img_file = url_for('static', filename='images/' + r.imgFile)

            return render_template("operation.html", op=op, ress=ress, img_file=img_file)

        return render_template("operation.html", op=op)
    else:
        return redirect(url_for('login'))

##################### Delete Operation #################################

@app.route("/del_op/<int:op_id>", methods=["POST"])
def del_op(op_id):

    print(op_id)

    ress = Resource.query.filter_by(workstation_id=op_id).all()

    for item in ress:
        db.session.delete(item)
    
    op = Workstation.query.get(op_id)
    db.session.delete(op)
    db.session.commit()
    flash('Your workstation has been deleted!', 'success')
    return redirect(url_for('rSetup'))

##################### Resources #################################

@app.route("/resources", methods=["GET", "POST"])
def resources():

    if 'username' in session:
        
        propList=[]
        components = Component.query.filter_by(product_id=1).all()

        ops = Workstation.query.all()
        ress = Resource.query.all()

        if request.method == "GET":
            if ress:
                for r in ress:
                    img_file = url_for('static', filename='images/' + r.imgFile)

            return render_template("resources.html", workstations=ops, components=components, ress=ress, img_file=img_file)


        if request.form.get("r_name"):

            op_id = request.form.get("sel_op")
            print("op_id", op_id)
            r_name = request.form.get("r_name")
            r_id = request.form.get("r_id")
            

            re = Resource(name=r_name, workstation_id=op_id)
            db.session.add(re)
            db.session.commit()
            
            ress = Resource.query.filter_by(workstation_id=op_id).all()

            img_file = url_for('static', filename='images/' + re.imgFile)

            return redirect(url_for('resources')) #img_file=img_file

        elif request.form.get("a_name"):
            res_id = request.form.get("sel_res")
            print("sel_res:", res_id)
            propID = request.form.get("sel_prop")
            a_name = request.form.get("a_name")
            a_wt = request.form.get("a_wt")
            a_OpNo = request.form.get("a_OpNo")
            a_ee = request.form.get("a_ee")
            a_pe = request.form.get("a_pe")

            print(a_name,a_wt,a_ee,a_pe)

            activity = Activity(name=a_name, propertyID=propID, prog_no=a_OpNo, delta_t=a_wt, el_energy=a_ee, air_energy=a_pe, resID=res_id)
            db.session.add(activity)
            db.session.commit()


            return redirect(url_for('resources')) #img_file=img_file


    else:
        return redirect(url_for('login'))


##################### Delete Resource #################################

@app.route("/del_res/<int:res_id>", methods=["POST"])
def del_res(res_id):

    print(res_id)

    ress = Resource.query.get(id=res_id)

    db.session.delete(ress)

    db.session.commit()
    flash('Your resources has been deleted!', 'success')
    return redirect(url_for('resources'))


################################ Login & Registration ###################################

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        name = request.form.get("name").capitalize()
        username = request.form.get("username").lower()
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        secure_password = sha256_crypt.encrypt(str(password))

        # Query db for already existing users:
        user_name = User.query.filter_by(name=name).first()
        user_username = User.query.filter_by(username=username).first()

        # If users exist, please retype or login
        if user_name or user_username:
            flash("User already taken. Please login or enter another name.", "danger")
        elif password == "":
                flash("Please enter a password.", "danger")
        else:

            if password == confirm:
                
                user = User(name=name, username=username, password=secure_password)
                db.session.add(user)
                db.session.commit()
                print("User added to database:",user.name)
                '''
                db.execute("INSERT INTO users(name,username,password) VALUES(:name,:username,:password)",
                                {"name":name,"username":username,"password":secure_password})
                db.commit()
                '''
                flash("you are registered and can login", "success")
                return redirect(url_for('login'))

            else:
                flash("The passwords does not match", "danger")
                return render_template("register.html")

    return render_template("register.html")


############################# login ##################################

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        
        session['username'] = request.form['username']#.lower()
        session['password'] = request.form['password']

        user = User.query.filter_by(username=session['username']).first()
        
        #usernamedata = user.name
        #passworddata = user.password
        #usernamedata = db.execute("SELECT username FROM users WHERE username=:username", {"username":session['username']}).fetchone()
        #passworddata = db.execute("SELECT password FROM users WHERE username=:username", {"username":session['username']}).fetchone()

        if user is None:
            flash("User not found. Please register instead.", "warning")
            return render_template("login.html")
        else:
            session['name'] = user.name
            if sha256_crypt.verify(session['password'],user.password):
                session["log"] = True
                #cookies = request.cookies
                #print(cookies)

                flash("You are now logged in", "success")
                return redirect(url_for('index'))
            else:
                flash("Incorect username or password", "danger")
                return render_template("login.html")

    else:
        return render_template("login.html")


############################### logout #############################
@app.route("/logout")
def logout():
    session.pop('username', None)
    session.clear()
    flash("You have been logged out", "success")
    return redirect(url_for('index'))

  

if __name__ == '__main__':
    app.debug = True
    app.run()

#     export DATABASE_URL=postgres://khxxfluukbyqoh:1084ea7b53f5ce4fdbdef299f6c0fc5f334adc6d9d3400e3761b43bf93878c8e@ec2-54-75-246-118.eu-west-1.compute.amazonaws.com:5432/d62ujht21ufg6u
