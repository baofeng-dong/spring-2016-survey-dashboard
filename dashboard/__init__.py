# Copyright (C) 2016 Jeffrey Meyers, Baofeng Dong
# This program is released under the "MIT License".
# Please see the file COPYING in the source
# distribution of this software for license terms.


from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('config')
app.debug = True
db = SQLAlchemy(app)

# make debug and error logging easier
debug = app.logger.debug
error = app.logger.error




from dashboard import views
