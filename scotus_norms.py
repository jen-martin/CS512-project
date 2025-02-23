""" Work Norms of the Early U.S. Supreme Court Project

This script uses the Oyez.com API (https://api.oyez.org)
to get U.S. Supreme Court case summaries for a set of years,
create a database to store data, do some calculations based
on case dates, and plots the result.

"""

import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import pymysql
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

def main():
    """ Wrapper function to get data and generate output files. """

    #Global variables

    #Variables to Get Data from API
    #SCOTUS Terms - early years are batched into 50-year groups
    TERMS = ["1789-1850", "1850-1900"]
    #API endpoint url for SCOTUS cases
    API_BASE_URL = 'https://api.oyez.org/cases?per_page=0&filter=term:'

    #Variables for database
    DB_PARAMS = {"host": "localhost", "port": 3306, "user": "root", "database":"scotus"}

    
    #initialize variables
    #stores case info as list
    cases = []

    ###
    action = {"event":"", "year":0, "month":0, "day":0, "weekday":"", "href":""}
    weekdays = {"Sunday":0, "Monday":0, "Tuesday":0, "Wednesday":0, "Thursday":0, "Friday":0, "Saturday":0}
    #variables for plotting data
    day_counts = {
        "All": {"Sunday": 0, "Monday": 0, "Tuesday": 0, "Wednesday": 0, "Thursday": 0, "Friday": 0, "Saturday": 0},
        "Argued": {"Sunday": 0, "Monday": 0, "Tuesday": 0, "Wednesday": 0, "Thursday": 0, "Friday": 0, "Saturday": 0},
        "Decided": {"Sunday": 0, "Monday": 0, "Tuesday": 0, "Wednesday": 0, "Thursday": 0, "Friday": 0, "Saturday": 0},
    }
    #counter to use for event primary key in database
    event_id_tally = 0 
    #variable to store case dates for TSV for further analysis
    scotus_dates = []
    ###

    #SCOTUS Cases are organized by term years, so iterate over the list of terms
    for term in TERMS:
        #Create the API URL from the base URL (api_base_url) plus the term and read as JSON
        api_url = API_BASE_URL + term
        Oyez_API = requests.get(api_url)
        scotus_data = Oyez_API.json()

        # status code check
        print(str(term) + ": " + f"status code: {Oyez_API.status_code}")

        # get all info for each case
        for row in scotus_data:
            # convert dates to year, month, day, weekday and add additional case stats
            case = get_date_stats(row)
            # add to list of cases
            cases.append(case)
    print("Data successfully imported")

    #Export case data to database
    add_data_to_db(DB_PARAMS, cases) 
    print("Data successfully added to scotus database in phpMyAdmin")

    #create plots
    generate_plots(cases)
    print("Complete")


def get_date_stats(case):
    """ This function takes the raw case data (dict) and 
        returns a new dict. It expands the UNIX time stamp
        into year, month, day and weekday, and creates 
        new stats for the case duration."""
    
    #initialze variables for case duration statistics
    date_decided = 0
    min_date_arg = 0
    max_date_arg = 0
    date_rearg = 0
    total_argued = 0
    total_reargued = 0

    #rename Case ID and case href to be compatible with database
    case["case_id"] = case.pop("ID")
    case["case_href"] = case.pop("href")

    #expand timeline so there is one date and one event
    updated_case = case
    new_timeline = []
    for action in case["timeline"]: 
        #keys and value types in action = {event(str), dates(list of ints), href(str)}
        
        #gather case timepoints for duration calculation
        if action["event"] == "Decided":
            date_decided = action["dates"][0]
        if action["event"] == "Argued":
            min_date_arg = action["dates"][0]
            max_date_arg = action["dates"][-1]
            total_argued = len(action["dates"])
        if action["event"] == "Reargued":
            date_rearg = action["dates"][0]
            total_reargued = len(action["dates"])

        for date in action["dates"]:
            #convert Unix timestamp to year, month, day, weekday
            new_action = convert_UTC(date)
            #add remaining items are append to timeline
            #(rename key to be compatible with database)
            new_action["case_id"] = case["case_id"] 
            new_action["event"] = action["event"]
            new_timeline.append(new_action)
    
    #replace case timeline with new timeline
    updated_case["timeline"] = new_timeline

    #calculate case duration statistics
    #add include number of days reargued in total days argued
    updated_case["argued_duration"] = total_argued + total_reargued
    #factor reargued date into dates argued max
    if date_rearg != 0 and date_rearg > max_date_arg:
        max_date_arg = date_rearg
    #total duration from 1st argued to decided
    unix_datespan = date_decided - min_date_arg
    dt = datetime.fromtimestamp(unix_datespan)
    updated_case["case_duration"] = dt.strftime("%d")
    # duration between last argued datae and decision
    unix_datespan = date_decided - max_date_arg
    dt = datetime.fromtimestamp(unix_datespan)
    updated_case["delib_duration"] = dt.strftime("%d")
    
    return updated_case 

def add_data_to_db(db_info, data):
    """ This function takes two arguments (a dict containing database connection
        paramters and a dict of SCOTUS data) and saves to a phpMyAdmin database.

        Calls the following functions:
        * init_tables, add_case_to_db, add_case_dates_to_db
    """
    
    try:
        #Connect to phpMyAdmin database  and initialize
        db = pymysql.connect(host=db_info["host"], port=db_info["port"], user=db_info["user"], database=db_info["database"])
        print("Connected to scotus database")
        cursor = db.cursor()
        #initialize all the database tables
        init_tables(db)
        
        #write the data to the database
        #keep track of number of events for db primary key
        event_id_tally = 0
        for row in data:
            #add summary info to db
            add_case_to_db(db, row)
            event_id_tally = add_case_dates_to_db(db, row["timeline"], event_id_tally)


    #handle DB errors
    except pymysql.Error as e:
        print(f"Database Error: {e}")

    #close DB when done 
    finally:
        if db.open:
            cursor.close()
            db.close()
            print("Closing database")

def init_tables(db):
    #initialize database tables
    cursor = db.cursor()
    #delete old tables if needed
    cursor.execute("DROP TABLE IF EXISTS cases_events")
    cursor.execute("DROP TABLE IF EXISTS citations")
    cursor.execute("DROP TABLE IF EXISTS cases")
    cursor.execute("DROP TABLE IF EXISTS events")
    cursor.execute("DROP TABLE IF EXISTS event_types")

    #create event_types table
    sql = """ CREATE TABLE event_types (
        type_id INT NOT NULL,
        name VARCHAR(20),
        PRIMARY KEY (type_id)
    ); """
    cursor.execute(sql)
    sql = "INSERT INTO event_types (type_id, name) VALUES (%s, %s)"
    items = [(1, "Argued"),(2, "Decided"), (3, "Reargued")]
    cursor.executemany(sql, items)
    db.commit()

    #create cases table
    sql = """ CREATE TABLE cases (
        case_id INT NOT NULL,
        name VARCHAR(100) NOT NULL,
        case_href VARCHAR(100),
        view_count INT,
        docket_number VARCHAR(10),
        question MEDIUMTEXT,
        term VARCHAR(15),
        description VARCHAR(255),
        justia_url VARCHAR(100),
        case_duration INT,
        argued_duration INT,
        delib_duration INT,
        PRIMARY KEY (case_id)
    ); """
    cursor.execute(sql)
    #create citations table
    sql = """ CREATE TABLE citations (
        case_id INT NOT NULL,
        volume INT,
        page INT,
        year INT,
        href VARCHAR(100),
        PRIMARY KEY (case_id),
        FOREIGN KEY (case_id) REFERENCES cases(case_id)
    ); """
    cursor.execute(sql)

    #create events table
    sql = """ CREATE TABLE events (
        event_id INT NOT NULL,
        type_id INT NOT NULL,
        month INT,
        year INT,
        day INT,
        weekday VARCHAR(10),
        PRIMARY KEY (event_id),
        FOREIGN KEY (type_id) REFERENCES event_types(type_id)
    ); """
    cursor.execute(sql)
    #create cases events join table
    sql = """ CREATE TABLE cases_events (
        event_id INT NOT NULL,
        case_id INT NOT NULL,
        FOREIGN KEY (event_id) REFERENCES events(event_id),
        FOREIGN KEY (case_id) REFERENCES cases(case_id)
    ); """
    cursor.execute(sql)

def add_case_dates_to_db(db, eventlist, counter):
    #adds event info to events table args: databse handle, 
    #list of events, tally of total events so far for PK.
    #returns an updated counter
    
    cursor = db.cursor()
    for event in eventlist:
        counter += 1
        #assign event type id
        if event["event"] == "Argued":
            event["type_id"] = 1
        elif event["event"] == "Decided":
            event["type_id"] = 2
        elif event["event"] == "Reargued":
            event["type_id"] = 3
        
        rows = ["event_id", "type_id", "year", "month", "day", "weekday"]
        event["event_id"] = counter
        sql = generate_insert_dict("events", rows)
        cursor.execute(sql, event)
        db.commit()
        #add to cases events join table
        sql = "INSERT INTO cases_events "
        sql += "(event_id, case_id)"
        sql += "VALUES (%s, %s)"
        items = (counter, event["case_id"])
        cursor.execute(sql, items)
        db.commit()

    return counter

def add_case_to_db(db, case):
    #add case summary info to cases table
    cursor = db.cursor()
    
    #get subset of keys and values
    cols = [
        "case_id", "name", "case_href", 
        "view_count", "docket_number", 
        "question", "term", "description", 
        "justia_url", "case_duration", 
        "argued_duration", "delib_duration"]
    case_dict = {k: case[k] for k in cols if k in case}

    sql = "INSERT INTO cases ("
    sql += ", ".join(cols)
    sql += ") VALUES (%(" 
    sql += ")s, %(".join(cols)
    sql += ")s)"
    sql = generate_insert_dict("cases", cols)
    cursor.execute(sql, case_dict)
    db.commit()

    #citations table
    sql = "INSERT INTO citations "
    sql += "(case_id, volume, page, year, href)"
    sql += "VALUES (%s, %s, %s, %s, %s)"
    items = (
        case["case_id"],
        case["citation"]["volume"],
        case["citation"]["page"],
        case["citation"]["year"],
        case["citation"]["href"]
    )
    cursor.execute(sql, items)
    db.commit()

def generate_plots(data):
    """ Generates several different kinds of plots """ 
    print("Processing data for plots")

    #Compare early US Historic Eras
    # The New Nation (1783-1860)
    # Civil War (1861-1865)
    # Reconstruction/Industrialization (1866-1889)
    eras = [
        {"name": "Early Republic", "start": 1783, "end": 1860},
        {"name": "Civil War", "start": 1861, "end": 1865},
        {"name": "Reconstruction/Industrialization", "start": 1866, "end": 1889}
    ]
    weekdays = {"Sunday":0, "Monday":0, "Tuesday":0, "Wednesday":0, "Thursday":0, "Friday":0, "Saturday":0}
    months = {"1":0, "2":0, "3":0, "4":0, "5":0, "6":0, "7":0, "8":0, "9":0, "10":0, "11":0, "12":0}
    
    weekday_counts = []
    #initialize case stats
    for e in eras:
        e["ttl_cases"] = 0
        e["ttl_events"] = 0
        e["delib_duration"] = []
        e["day_counts"] = {}
        e["day_counts"].update(weekdays)
        e["month_counts"] = {}
        e["month_counts"].update(months)

    #iterate over all cases
    for case in data:
        #assign era by citation year
        dd = int(case["citation"]["year"])
        n = 0
        if dd >= eras[0]["start"] and dd <= eras[-1]["end"]:
            if dd <= eras[0]["end"]:
                n = 0
            elif dd <= eras[1]["end"]:
                n = 1
            else:
                n = 2
            #total number of cases
            eras[n]["ttl_cases"] += 1
            #Total number of events
            eras[n]["ttl_events"] += len(case["timeline"])
            #add the days deliberated to the list of entries
            eras[n]["delib_duration"].append(int(case["delib_duration"]))
            #iterate over all events in the case to get weekday and month stats
            for event in case["timeline"]:
                #add weekday and month info
                wd = event["weekday"]
                if wd in weekdays:
                    eras[n]["day_counts"][wd] += 1
                m = str(int(event["month"]))
                #m = (str(event["month"]))
                if m in months:
                    eras[n]["month_counts"][m] += 1
    make_plots(eras)

def make_plots(plt_data):
    #Generate plots with the selected data
    print("\n==== DATA STATISTICS ===")
    
    #common plot elements
    fig_title1 = "SCOTUS Public Proceedings by Day of Week and Historical Era"
    x_labels1 = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    #x_labels1 = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    fig_title2 = "SCOTUS Public Proceedings by Month and Historical Era"
    x_labels2 = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    fig_title3 = "Mean Number of Days to Reach Decision"
    plt_titles = []
    for era in plt_data:
        tstring = era["name"]
        tstring += " (" + str(era["start"]) + " to "
        tstring += str(era["end"]) + ")"
        plt_titles.append(tstring)
    wday_percent = []
    mon_percent = []
    delib_vectors = []
    
    #Plot 1
    #Create and print stats for Plot 1 - Days of Week
    for era in plt_data:
        print("\n" + fig_title1)
        print(era["name"])
        print("--------------\nTOTAL NUMBERS")
        freq = era["day_counts"]
        [print(f"{key}: {value}") for key, value in freq.items()]
        print("PERCENT")
        total = sum(freq.values())
        percent = {}
        for key, value in freq.items():
            x = 100*value/total
            percent[key] = x
            [print(f"{key}: {x:.1f}")]
        wday_percent.append(list(percent.values()))

    #Create Plot 1
    #x labels and x-coordinates
    x = np.arange(7)
    # set plot data
    fig, axes = plt.subplots(3, 1, sharex=True, sharey=True) 
    fig.suptitle(fig_title1, weight="bold")
    for i, ax in enumerate(axes):
        ax.bar(x, wday_percent[i], align="center", color="lightblue", edgecolor="gray")
        ax.set(xticks=x, xticklabels=x_labels1, ylabel="Percent of Days")
        ax.tick_params(axis='y', direction='in')
        ax.yaxis.set_ticks_position('both')
        ax.set_title(plt_titles[i], fontsize=11)
    plt.subplots_adjust(hspace=0.3)
    plt.show()

    #Plot 2
    #Create and print stats for Plot 2 - Months
    for era in plt_data:
        print("\n" + fig_title2)
        print(era["name"])
        print("--------------\nTOTAL NUMBERS")
        freq = era["month_counts"]
        [print(f"{key}: {value}") for key, value in freq.items()]
        print("PERCENT")
        total = sum(freq.values())
        percent = {}
        for key, value in freq.items():
            x = 100*value/total
            percent[key] = x
            [print(f"{key}: {x:.1f}")]
        mon_percent.append(list(percent.values()))

    #Create plot 2
    x = np.arange(12)
    # set plot data
    fig, axes = plt.subplots(3, 1, sharey=True) 
    fig.suptitle(fig_title2, weight="bold", x=0.5, y=0.95)
    for i, ax in enumerate(axes):
        ax.bar(x, mon_percent[i], align="center", color="lightblue", edgecolor="gray")
        ax.set(xticks=x, xticklabels=x_labels2, ylabel="Percent of Days")
        ax.tick_params(axis='y', direction='in')
        ax.yaxis.set_ticks_position('both')
        ax.text(0.5, .9, plt_titles[i], horizontalalignment='center',
            verticalalignment='top', transform=ax.transAxes, fontsize=11)
        #ax.set_title(plt_titles[i])
    plt.subplots_adjust(hspace=0.2)
    plt.show()

    #Plot 3
    #Create and print stats for Plot 3 - Deliberation Duration
    print("\n" + fig_title3 + "\n--------------")
    for i in range(3):
        print(plt_data[i]["name"])
        st = "N: " + str(len(plt_data[i]["delib_duration"]))
        st += ", min: " + str(np.min(plt_data[i]["delib_duration"]))
        st += ", max: " + str(np.max(plt_data[i]["delib_duration"]))
        print(st)
        print("median: ", np.median(plt_data[i]["delib_duration"], axis=0))
        print("mean: ", np.mean(plt_data[i]["delib_duration"], axis=0))
        print("std dev: ", np.std(plt_data[i]["delib_duration"], axis=0))
    print("=================\n")
    data = [np.array(plt_data[2]["delib_duration"]), np.array(plt_data[1]["delib_duration"]), np.array(plt_data[0]["delib_duration"])]
    plt.boxplot(data, vert=False)
    plt.title(fig_title3, weight="bold")
    plt.xlabel('Number of Days')
    plt.text(15, 3.4, plt_titles[0], horizontalalignment='center',
            verticalalignment='top', fontsize=11)
    plt.text(15, 2.4, plt_titles[1], horizontalalignment='center',
            verticalalignment='top', fontsize=11)
    plt.text(15, 1.4, plt_titles[2], horizontalalignment='center',
            verticalalignment='top', fontsize=11)
    plt.yticks([])
    plt.show()


def generate_insert_dict(table, keys):
    #helper function that generate a SQL INSERT command 
    #from the table name and a list of keys; assumes the
    #data are in a dict
    command = "INSERT INTO " + table + " ("
    command += ", ".join(keys)
    command += ") VALUES (%(" 
    command += ")s, %(".join(keys)
    command += ")s)"
    return command

def convert_UTC(d):
    """ This function takes a UNIX timestamp (int) and 
        returns a dict containing the year, month, day and weekday """ 
    #initial idea for formatting provided by "FloLie" at https://stackoverflow.com/questions/65063058/convert-unix-timestamp-to-date-string-with-format-yyyy-mm-dd
    date_dict = {}
    #convert from UTC to EST
    dt = datetime.fromtimestamp(d + 18000)
    date_dict["year"] = dt.strftime("%Y")
    date_dict["month"] = dt.strftime("%m")
    date_dict["day"] = dt.strftime("%d")
    date_dict["weekday"] = dt.strftime("%A")
    return date_dict

if __name__ == '__main__':
    main()

