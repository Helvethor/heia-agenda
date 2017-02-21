#!/usr/bin/python3 

import sys, argparse, datetime
import requests
from heia import *

if __name__ == '__main__':

    date = lambda x: datetime.date(*map(int, x.split("-")))

    parser = argparse.ArgumentParser(
        description = "Create an .ics calendar for courses given at HEIA.")
    parser.add_argument("-username", required = True,
        help = "Your HEIA username")
    parser.add_argument("-password", required = True,
        help = "Your HEIA password")
    parser.add_argument("-section", dest = "section", required = True,
        help = "Your HEIA section (I-1d, T-3a...)")
    parser.add_argument("-start", required = True, type = date,
        help = "Beginning of semester (ISO, yyyy-mm-dd)")
    parser.add_argument("-end", required = True, type = date,
        help = "End of semester (ISO, yyyy-mm-dd)")
    parser.add_argument("vacation_weeks", metavar = "W", type = int, nargs = '*',
        help = "Week numbers (ISO) of vacations")
    parser.add_argument("-output", default = "calendar.ics",
        help = "Output file")
    parser.add_argument("-cache", dest = 'cache', action='store_true',
        help = "Use cached files, for debugging purpose")

    args = parser.parse_args()

    sys.stdout.write("Retrieving classes informations... ")
    sys.stdout.flush()
    cla = classes.get(args.section, args.username, args.password, args.cache)
    sys.stdout.write("OK\n")

    sys.stdout.write("Creating calendar... ")
    sys.stdout.flush()
    cal = calendar.get(cla, args.start, args.end, args.vacation_weeks)
    sys.stdout.write("OK\n")

    sys.stdout.write("Writing to file {}... ".format(args.output))
    sys.stdout.flush()
    with open(args.output, "wb") as f:
        f.write(cal.to_ical())
    sys.stdout.write("OK\n")

