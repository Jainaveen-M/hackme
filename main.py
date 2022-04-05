from crypt import methods
import json
import pathlib
import sys
from flask import Flask, jsonify, request
from numpy import deg2rad, rec

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import *
import logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text

Base = declarative_base()

session_maker = None
engine = None


def init_db(
    db_str,
    pool_size=10,
    pool_recycle=3600,
    isolation_level="READ COMMITTED",
    convert_unicode=True,
):
    global session_maker, engine
    SQL_ALCHEMY_DATABASE_URI = db_str
    engine = create_engine(
        SQL_ALCHEMY_DATABASE_URI,
        pool_size=pool_size,
        pool_recycle=pool_recycle,
        isolation_level=isolation_level,
        convert_unicode=convert_unicode,
    )
    session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# used as a decorator for db sessions, @with_session
# def with_session(func, db_session=None, close_session=True, *args):
# while calling the functions that use this decorator, MUST specify all arguments as keyword arguments.
def with_session(func=None):
    def inner(db_session=None, close_session=True, **kwargs):
        if db_session is None:
            db_session = scoped_session(session_maker)
        kwargs.update({"db_session": db_session})
        res = func(**kwargs)
        if close_session:
            if db_session is not None:
                db_session.close()
        return res

    return inner


app = Flask(__name__)
app_name = "hacke_me"


def init(db_str):
    init_db(db_str)


@app.route("/", methods=["GET"])
def home():
    return "Hack me app please. M horny."

@app.route('/getcustomer',methods=['GET'])
def getCustomer():
    global engine
    query = str("select * from customer;")
    result = engine.execute(query)
    data = []
    for record in result:
        data.append({
            "id":record.id,
            "name":record.name,
            "email":record.email,
            "nationality":record.nationality
        })
    return jsonify({"result":data})

@app.route('/insert/customer',methods=['POST'])
def insertCustomer():
    global engine
    data = request.json
    query = text("insert into customer(name,email,nationality) values(:name, :email, :nationality);")
    engine.execute(query,data)
    return jsonify({"result":"customer insert successfully"})

@app.route('/getcustomer/<id>')
def getCustomerById(id):
    global engine
    query = f"select * from customer where ctid = {id};"
    result = engine.execute(query)
    id = [row[0] for row in result]
    return jsonify({"message":result})
    

# MODELS
class Customer(Base):
    __tablename__ = "customer"
    id = Column(Integer, primary_key=True, autoincrement=True,nullable=False)
    name = Column(String(40),nullable=False)
    email = Column(String(40),nullable=False)
    nationality = Column(String(40),nullable=False)


# CONTROLLERS


def get_customers():
    global engine
    query = "select * from customer;"
    result = engine.execute(query)
    return result


def get_customer_by_id(ctid=None, db_session=None):
    global engine
    query = "select * from customer where ctid= {ctid}"
    result = engine.execute(query)
    return result


if __name__ == "__main__":
    db_str = "mysql+pymysql://root:root12345@localhost:3306/hackme"
    init(db_str)
    app.run(host="0.0.0.0", port=5055, debug=True, threaded=True)
