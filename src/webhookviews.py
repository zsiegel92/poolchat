#Note: have to import webhookviews at bottom of app.py
from interactions import quick_rules,text_rules,process_referral,postback_rules
from app import app,request,abort


# webhook for facebook to initialize the bot
@app.route('/webhook', methods=['GET'])
def get_webhook():
	if not 'hub.verify_token' in request.args or not 'hub.challenge' in request.args:
		abort(400)
	return request.args.get('hub.challenge')


@app.route('/webhook', methods=['POST'])
def post_webhook():
	data = request.json
	if data["object"] == "page":
		for entry in data["entry"]:
			for messaging_event in entry["messaging"]:
				sender_id = messaging_event["sender"]["id"]
				referral_text = None
				if "referral" in messaging_event:
					referral_text = messaging_event["referral"]["ref"]
				if "message" in messaging_event:
					if "text" in messaging_event["message"]:
						message_text = messaging_event["message"]["text"]
						if "quick_reply" in messaging_event["message"]:
							quick_rules(sender_id,messaging_event["message"]["quick_reply"]["payload"])
						else:
							text_rules(sender_id,message_text=message_text)
				elif "postback" in messaging_event:
					postback_text = messaging_event["postback"]["payload"]
					#referral is in special postbacks see docs
					if "referral" in messaging_event["postback"]:
						referral_text = messaging_event["postback"]["referral"]["ref"]
						process_referral(sender_id,postback_text,referral_text)
					postback_rules(sender_id,postback_text,referral_text=None)
				elif referral_text:
					process_referral(sender_id,referral_text=referral_text)
	return "ok", 200
