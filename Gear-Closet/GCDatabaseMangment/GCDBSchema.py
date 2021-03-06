from flask_sqlalchemy import SQLAlchemy
from GCDatabaseMangment.GCDBQuery import inventoryMangment
import datetime
db = SQLAlchemy()

class Inventory(db.Model):
    __tablename__ = "Inventory"
    query_class = inventoryMangment
    id = db.Column(db.Integer, primary_key=True)#id to make itreation easy
    itemName = db.Column(db.String(120))#name
    quantityAvailable = db.Column(db.Integer)# Number avalible to checkout
    quantityOut = db.Column(db.Integer)# Number out of inv
    quantityInProcessing = db.Column(db.Integer)
    processing = db.Column(db.Boolean)# This indicates if the gear needs to be checked over before returing
    price = db.Column(db.Integer)# How much we will charge people when they dont give us shit back
    category = db.Column(db.String(120), db.ForeignKey("Category.categoryName"))# will be used to sort gear for future applicatons
    checkedOutRetationship = db.relationship("checkedOut")
    processingRelationship = db.relationship("Processing")

    def __init__(self, form=None):
        self.itemName = form['itemName']
        self.quantityAvailable = form['itemQuantity']
        self.quantityOut = 0
        self.quantityInProcessing = 0
        self.price = form['itemPrice']
        self.category = form['itemCategory']
        self.processing = form['itemProcessingRequired']

    @property
    def serializeTable(self):
        """ Return object data in easily serializeable format
            https://stackoverflow.com/questions/7102754/jsonify-a-sqlalchemy-result-set-in-flask?noredirect=1&lq=1
        """
        return {
            'id': self.id,
            # Lol this is a total hack but it works so whatever
            'itemName': "<span class='itemName'"+ " id="+str(self.id) +"><a  href='#'>" + self.itemName + "</a></span>",#create tag for later use as jquery identifyer
            'itemQuantity': self.quantityAvailable,
            'itemQuantityOut': self.quantityOut,
            'itemPrice' : self.price,
            'itemCatagory' : self.category,
            'itemProcessingRequired' : self.processing
            }

    @property
    def serializePopUp(self):
        return{
            'id': self.id,
            'itemName':  self.itemName,
            'itemQuantity': self.quantityAvailable,
            'itemQuantityOut': self.quantityOut,
            'itemPrice' : self.price,
            'itemCatagory' : self.category,
            'itemProcessingRequired' : self.processing
            }


#TODO: working on Inv and Checkedout rlationship http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html#one-to-one
class Processing(db.Model):
    __tablename__ = "Processing"
    id = db.Column(db.Integer, primary_key=True)
    itemName = db.Column(db.String(120))  # name
    clientID = db.Column(db.Integer)
    itemCheckingTime =  db.Column(db.DateTime)
    inventoryID = db.Column(db.Integer, db.ForeignKey("Inventory.id"))

    def __init__(self, item, clientID, checkInTime=datetime.datetime.today()):
        """
        :param item: instance of the Inventory class
        """
        self.itemName = item.itemName
        self.itemCheckingTime = checkInTime
        self.inventoryID = item.id
        self.clientID = clientID



class checkedOut(db.Model):
    __tablename__ = "checkedOut"
    id = db.Column(db.Integer, primary_key=True)
    # Checked Out Gear- this is a relationship many to one discribing gear they have out
    clientCheckoutID = db.Column(db.Integer, db.ForeignKey("Client.studentID"))
    # above defines the Many to one relationship of Client and checkedOut
    inventory = db.Column(db.Integer, db.ForeignKey("Inventory.id"))
    numberOut = db.Column(db.Integer)
    dateCheckedOut = db.Column(db.Date)
    dateDue = db.Column(db.Date)

    def __init__(self, studentID, inventoryID, numberOut=1, date=datetime.date.today(), dateDue=datetime.date.today() + datetime.timedelta(days=7)):
        self.clientCheckoutID = studentID
        self.inventory = inventoryID
        self.numberOut = numberOut
        self.dateCheckedOut = date
        self.dateDue = dateDue

    # @property
    def serializeTable(self, client, item):
        return {
            "id": str(self.id),
            "studentID": str(self.clientCheckoutID),
            "inventoryID": str(self.inventory),
            "numberOut": str(self.numberOut),
            "dateCheckedOut": str(self.dateCheckedOut),
            "clientName": str(client.name),
            "itemName": str(item.itemName)
        }
    # def serializeForCheckin(self):



class Client(db.Model):
    __tablename__ = "Client"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))# so we can adress emails to the person
    studentID = db.Column(db.Integer)# cause why not?
    email = db.Column(db.String(120))# to send info about gear out and late gear
    phoneNumber = db.Column(db.Integer)# for contacting for late returns
    employee = db.Column(db.Boolean)# Lets keep track of who employees are
    numberCheckedOut = db.Column(db.Integer)
    gearOut = db.relationship("checkedOut")# Defines the one to Many relationship of Client and checkedOut

    def __init__(self, user):
        self.name = user['clientName']
        self.phoneNumber = user['phoneNumber']
        self.email = user['emailAddress']
        self.studentID = user['studentID']
        self.employee = user['Employee']
        self.numberCheckedOut = 0

    @property
    def serializeTable(self):
        """ Return object data in easily serializeable format
            https://stackoverflow.com/questions/7102754/jsonify-a-sqlalchemy-result-set-in-flask?noredirect=1&lq=1
        """
        data = self.serializeTableClean
        data['clientName'] = "<span class='clientName'" + " id="+str(self.id) +"><a  href='#'>" + self.name + "</a></span>"
        return data

    @property
    def serializeTableClients(self):
        data = self.serializeTableClean
        data.pop("clientEmployee", None)
        data["button"] = """<a href="#" class="btn btn-sm btn-success" id="""+ str(self.id) + "viewOrders" +"""><span class="glyphicon glyphicon-shopping-cart"></span></a>""" \
        + """<a href="#" class="btn btn-sm btn-primary" id="""+  str(self.id) + "editUser" +"""><span class="glyphicon glyphicon-cog"></span></a>"""
        return data

    @property
    def serializeCheckIn(self):
        """ Return object data in easily serializeable format
            https://stackoverflow.com/questions/7102754/jsonify-a-sqlalchemy-result-set-in-flask?noredirect=1&lq=1
        """
        data = self.serializeTableClean
        return data

    @property
    def serializeTableClean(self):
        return {
            'id': self.id,
            'clientName': self.name,
            'clientPhoneNumber': self.phoneNumber,
            'clientEmail': self.email,
            'clientStudentId' : self.studentID,
            'clientEmployee' : self.employee,
            'numberCheckedOut' : self.numberCheckedOut
            }

class Category(db.Model):
    __tablename__ = "Category"
    id = db.Column(db.Integer, primary_key=True)
    categoryName = db.Column(db.String(120), nullable=False, unique=True)
    relationship = db.relationship("Inventory")

    def __init__(self, category):
        self.categoryName = category















