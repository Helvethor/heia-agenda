import os, copy, datetime, calendar
from bs4 import BeautifulSoup
import pickle, requests, pprint


_url_base = 'https://webapp.heia-fr.ch/horaire/bloc-jsp/'
_dir = os.path.dirname(os.path.realpath(__file__))

_cache = True
_cache_pickle =  "{}/cache/{}.pickle".format(_dir, __name__)
_auth = None


def get(section, username, password, cache = True):
    global _cache, _auth
    _cache = cache
    _auth = requests.auth.HTTPBasicAuth(username, password)

    # Read from cache
    if _cache and os.path.isfile(_cache_pickle):
        with open(_cache_pickle, 'rb') as f:
            classes = pickle.load(f)

    # Or write to it
    else:
        html = get_html(section)
        classes = merge_periods(parse(html))
        with open(_cache_pickle, 'wb') as f:
            classes_byte = pickle.dump(classes, f)

    return classes


def get_html(section):
    url = _url_base + 'horaire_par_classe.jsp'
    payload = {'filiere': section}
    return requests.post(url, auth = _auth, data = payload).text


def parse(html):

    days = {"Lundi": 0, "Mardi": 1, "Mercredi": 2, "Jeudi": 3, "Vendredi": 4,
        "Samedi": 5, "Dimanche": 6}
    classes = []
    day = 0
    teacher_cache = {}

    # Parse events from webapp.heia-fr.ch
    # Courses over multiple periods are first parsed into one event,
    # then split into multiple events if the time between the Periods
    # is less than 10 minutes
    soup = BeautifulSoup(html, 'html.parser')
    for row in soup("table")[-1]("tr")[1:]:

        cells = row("td")

        # Day
        d = cells[0].div.string.strip()
        if len(d) > 0:
            day = days[d] 
        event = {"day": day}

        # Classe
        class_ = cells[2].div.string
        if class_ == None:
            continue
        event["class"] = class_.strip()

        # Periods
        periods = list(map(lambda x: x.split('-'), 
            map(lambda x: x.string.strip(), cells[1].div.find_all("div"))))
        event["periods"] = periods

        # Rooms
        rooms = cells[4].div("div")
        event["rooms"] = list(map(lambda x: x.string.strip(), rooms))

        # Teachers
        teachers = cells[3].div("div")
        event["teachers"] = []

        for teacher in teachers:

            shortname = teacher.a.string
            if shortname in teacher_cache:
                event["teachers"] += [teacher_cache[shortname]]
                continue

            # Get precise information about teacher
            url = (_url_base + teacher.a["onclick"].split(";")[0]
                .split("(")[1].split(")")[0].split(',')[0][1:-1])
            t_soup = BeautifulSoup(requests.get(url, auth = _auth).text, "html.parser")
            rows = t_soup("table")[-1]("tr")
            teacher_data = {"name": str(rows[0]("td")[1]).split(">")[1].split("<")[0].strip()}

            # The most beautiful snippet of code
            room = rows[1]("td")[1].string
            if room != None:
                teacher_data["room"] = room.strip()
            phone = rows[2]("td")[1].string
            if phone != None:
                teacher_data["phone"] = phone.strip()
            email = rows[3]("td")[1].string
            if email != None:
                teacher_data["email"] = email.strip()

            teacher_cache[shortname] = teacher_data
            event["teachers"] += [teacher_data]

        classes += [event]

    return classes


def merge_periods(classes):
    # Split or merge courses periods

    max_difference = datetime.timedelta(minutes = 10)

    str_to_dtime = lambda t: datetime.timedelta(
        hours = int(t.split(":")[0]), minutes = int(t.split(":")[1]))
    p_to_interval = lambda p: list(map(lambda i: str_to_dtime(p[i]), (0, 1)))

    new_classes = []
    for event in classes:

        merged_periods = []
        periods = event["periods"]

        i = 0
        while i < len(periods) - 1:
            j = i + 1

            interval1 = p_to_interval(periods[i])
            while j < len(periods):

                interval2 = p_to_interval(periods[j])
                if interval2[0] - interval1[1] > max_difference:
                    break

                j += 1

            start = periods[i][0]
            end = periods[j - 1][1]

            merged_periods += [[start, end]]
            i = j

        for period in merged_periods:
            e = copy.copy(event)
            del e["periods"]
            e["period"] = period
            new_classes += [e]

    return new_classes
