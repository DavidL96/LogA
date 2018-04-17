import re  # The Python regular expression library

from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from geolite2 import geolite2

app = Flask(__name__)


def parse_file_contents(data):
    ips = []
    for each in data:
        each = each.decode(errors='replace')
        new_ips = re.findall(r'[0-9]+(?:\.[0-9]+){3}', each)
        ips.extend(new_ips)
    return list(set(ips))


@app.route("/getLoc", methods=['POST'])
def getip():
    ipAddr = request.form['ipAddr']
    subd = []
    reader = geolite2.reader()
    try:
        match = reader.get(ipAddr)
    except Exception:
        return 'Match Failed Anywhere'

    print(match)

    if not(match) is False:
        city = match['city']['names']['en']
        continent = match['continent']['names']['en']
        country = match['country']['names']['en']
        latitude = match['location']['latitude']
        longitude = match['location']['longitude']
        timezone = match['location']['time_zone']
        postal = match.get('postal', None)
        if postal is not None:
            postal = postal['code']
        for each in match['subdivisions']:
            subd.append(each['names']['en'])
        subd = ' '.join(subd)

    out = {
        'latlong': {'lat': latitude, 'lng': longitude},
        'raw': ' '.join([str(x) for x in [
            subd, city, country,
            continent, latitude, longitude, timezone, postal]])
    }

    return jsonify(out)


@app.route("/", methods=['GET', 'POST'])
def hello():
    if request.method == "POST":
        file = request.files['inputFile']
        data = file.readlines()

        out = parse_file_contents(data)
        # if user does not select file, browser also
    else:
        out = []
    return render_template('index.html', ctx=out)

if __name__ == "__main__":
    app.run(debug=True)
    
