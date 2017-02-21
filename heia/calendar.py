import os, datetime, socket
import pprint
import icalendar as ic

pp = pprint.PrettyPrinter(indent = 2)


def uid():
    
    num = 0
    pid = os.getpid()
    hostname = socket.gethostname()

    while True:
        yield "{}-{}@{}".format(pid, num, hostname)
        num += 1

uid = uid()


def get(classes, start, end, vacation_weeks):

    one_day = datetime.timedelta(days = 1)
    time_offset = lambda x: datetime.timedelta(
        hours = int(x[:2]), minutes = int(x[-2:]))

    start_week = datetime.date.isocalendar(start)[1]
    end_week = datetime.date.isocalendar(end)[1]
    weeks = [w for w in range(start_week, end_week + 1)
        if w not in vacation_weeks]

    calendar = ic.Calendar()
    calendar.add("prodid", ic.vText("-//heia-agenda//shabang.ch//"))
    calendar.add("version", ic.vText("2.0"))

    dtstamp = ic.vDatetime(datetime.datetime.now())

    # We could have used something like this...
    #recur = ic.vRecur({
    #    "freq":  ic.vFrequency("weekly"),
        #"until":  ic.vDatetime(datetime.datetime(
        #    year = end.year,
        #    month = end.month,
        #    day = end.day,
        #    hour = 23
        #)),
    #    "byweekno": weeks
    #})

    for event in classes:
        # Rrule are not well supported accross softwares
        # Just create every event...
        for week in weeks:

            summary = ic.vText(event["class"])

            dtstart = ic.vDatetime(datetime.datetime(
                year = start.year,
                month = start.month,
                day = start.day)
                + time_offset(event["period"][0])
                + event["day"] * one_day
                + (week - start_week) * 7 * one_day)

            dtend = ic.vDatetime(datetime.datetime(
                year = start.year,
                month = start.month,
                day = start.day)
                + time_offset(event["period"][1])
                + event["day"] * one_day
                + (week - start_week) * 7 * one_day)

            description = ic.vText("\n\n".join(
                "\n".join("{}: {}".format(k.capitalize(), v)
                for k, v in teacher.items())
                for teacher in event["teachers"]))

            vevent = ic.Event()
            vevent.add("dtstart", dtstart)
            vevent.add("dtend", dtend)
            vevent.add("dtstamp", dtstamp)
            vevent.add("summary", summary)
            vevent.add("description", description)
            vevent.add("uid", next(uid))
            
            calendar.add_component(vevent)

    #print(calendar.to_ical().decode())

    return calendar



