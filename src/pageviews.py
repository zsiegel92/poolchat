from interactions import quick_rules,pester,text_rules,process_referral#Note: have to import webhookviews at bottom of app
from collections import OrderedDict
import requests
from flask import render_template

from app import app,request,abort
from database import db


@app.route('/', methods=['GET', 'POST'])
def index():
	errors = []
	results = {}
	if request.method == "POST":
		# get url that the user has entered
		try:
			url = request.form['url']
			r = requests.get(url)
			print(r.text)
			results = {"hey":"dude","who":"are","you":"?"}
		except:
			errors.append(
				"Unable to get URL. Please make sure it's valid and try again."
			)
	return render_template('index.html', errors=errors, results=results)

