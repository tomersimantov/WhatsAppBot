import datetime, re, googlemaps, requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from bearer_token import GOOGLE_TOKEN, BITLY_TOKEN

app = Flask(__name__)
tasks = []


@app.route("/")
def hello():
    return "WhatsApp Bot is online."


def phone_num(phone):
    return f'https://wa.me/972' + (''.join(i for i in phone if i.isdigit())[-9:])

# shorten a given url
def url_shortener(url):
    headers = {
        'Authorization': f'Bearer {BITLY_TOKEN}',
        'Content-Type': 'application/json',
    }
    data = '{{ "long_url": "{}", "domain": "bit.ly" }}'.format(url)
    response = requests.post('https://api-ssl.bitly.com/v4/shorten', headers=headers, data=data)
    print(response.json())
    return "קישור מקוצר" + "\n" + response.json()['link']


# waze or google links for a given address
def navigation(address):
    gmaps = googlemaps.Client(key=GOOGLE_TOKEN)
    geocode_result = gmaps.geocode(address)
    place_id = geocode_result[0]["place_id"]
    lat = geocode_result[0]["geometry"]["location"]["lat"]
    lng = geocode_result[0]["geometry"]["location"]["lng"]
    google_navi = f'https://www.google.com/maps/search/?api=1&query=Google&query_place_id={place_id}'
    waze_navi = f'https://www.waze.com/ul?ll={lat}%2C{lng}&navigate=yes'
    return f'ניווט דרך גוגל מפות (Google Maps):' \
           f'{google_navi}\n\n' \
           f'ניווט דרך וויז (Waze):\n' \
           f'{waze_navi}'


def task(msg):
    first_word = msg.split()[0]
    if first_word == "משימה":
        msg = msg.replace('משימה', '').lstrip()
        tasks.append(msg)
        return "משימה התווספה"
    elif first_word == "מחק":
        try:
            num = int(msg.split()[1])
        except:
            return "לא ציינת מספר."
        print(num, "מספר")
        if type(num) == int:
            print(num - 1, "אינדקס למחוק")
            tasks.pop(num - 1)
            print(tasks)
            return "משימה נמחקה"
    elif first_word == "משימות":
        tasks_list = ""
        if not tasks:
            return "אין משימות."
        for ind, ele in enumerate(tasks, start=1):
            tasks_list += f"{ind}. {ele}\n"
        return tasks_list


@app.route("/sms", methods=['POST'])
def reply():
    # fetching the message
    found = 0
    msg = request.form.get('Body')
    resp = MessagingResponse()
    # communication response list
    texting = {
        "מה השעה": datetime.datetime.now().strftime("%d/%m/%Y\n%H:%M:%S"),
        "שעה": datetime.datetime.now().strftime("%d/%m/%Y\n%H:%M:%S"),
        "תאריך": datetime.datetime.now().strftime("%d/%m/%Y\n%H:%M:%S"),
        "מה שלומך": "מעולה, תודה!",
        "מה נשמע": "מעולה, תודה!",
        "מה קורה": "מעולה, תודה!",
        "נעים להכיר": 'נעים להכיר גם אותך!',

    }

    # url
    url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.search(url_regex, msg)
    if url is not None:
        resp.message(url_shortener(url.group(0)))

    phone_regex = r"\(?\+?[0-9]{1,3}\)? ?-?[0-9]{1,3} ?-?[0-9]{3,5} ?-?[0-9]{4}( ?-?[0-9]{3})? ?(\w{1,10}\s?\d{1,6})?"
    phone = re.search(phone_regex, msg)
    if phone is not None:
        resp.message(phone_num(phone.group(0)))

    elif msg.split()[0] in ["משימה", "מחק", "משימות"]:
        task_list = task(msg)
        resp.message(task_list)

    # navigation
    elif msg.split()[0] == "ניווט":
        msg = msg.replace("ניווט", '')
        resp.message(navigation(msg))

    # communication
    else:
        for query in texting:
            found = msg.find(query)
            if found > -1:
                resp.message(texting[query])
                found = 0
                break
        if found == -1:
            resp.message("מתנצל, אך לא הצלחתי להבין.")

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
