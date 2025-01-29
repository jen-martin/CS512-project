"""Extract SCOTUS Dates

This script uses the Oyez.com API (https://api.oyez.org)
to get U.S. Supreme Court case summaries and extract the 
term year, case name, and the date when the case was Granted, 
Argued, or Decided for the years 2017 to 2024.

Data are saved in two formats: CSV and JSON. Three files are created:
    * The main CSV output file: "scotus_dates.csv"
    * A JSON version of the main CSV file: "scotus_dates_converted.json"
    * To show that the JSON can be converted back to CSV
        without loss of data, a third file, "scotus_dates_converted.csv",
        is generated.

This script requires the Pandas python library.

Functions:
    * main - the main function of this script
    * write_csv(data_list, outfile) - takes a 5-column list of lists ('data_list') 
        and uses the string argument 'outfile' to write the list to a CSV file.
    * csv_to_json(infile, outfile) - reads in a CSV file, converts to JSON and saves 
        the JSON to a file. 'infile' is the name of the CSV input file. 'outfile' is 
        the name of the JSON formatted outfile.
    * json_to_csv(infile, outfile) - reads in a JSON file, converts the JSON to a 
        list of lists and saves as a CSV. 'infile' is the name of the JSON input file. 
        'outfile' is the name of the CSV outfile. Calls write_csv(data_list, outfile)
        to handle writing the list to a CSV file by passing a list and the name of the
        output file.


Change log:
-modified to output CSV items in JSON "key":"value" pairs, 7:37 pm (JM)
-Fixes spelling and clean up; modified 1/18/2025 at 6:34 pm (JM)
-Add comments and clean up; modified 1/27/2025 at 6:35 pm (JM)
-First documented version: 1/27/2025 at 12:37 AM (JM)
"""

import requests
import json
import pandas as pd
from datetime import datetime

def main():
    """ Wrapper function to get data and generate output files. """

    #range of years of SCOTUS data to get
    start_year = 2017
    end_year = 2024
    #variable to store dates for SCOTUS trials
    scotus_dates = []

    #API endpoint url for SCOTUS cases
    api_base_url = 'https://api.oyez.org/cases?per_page=0&filter=term:'

    #SCOTUS Cases are organized by Year, so iterate over the range of years
    for i in range(start_year, end_year+1):
        #Create the API URL from the base URL (api_base_url) plus the year and read as JSON
        api_url = api_base_url + str(i)
        Oyez_API = requests.get(api_url)
        scotus_data = Oyez_API.json()

        # status code check
        print(str(i) + ": " + f"status code: {Oyez_API.status_code}")


        #Each JSON file contains all cases for a particular term so
        # get year, case title and case dates by iterating over the 'scotus_data' list
        for row in scotus_data:
            #temporary list for dates
            line = [str(i)]
            #get name of case
            line.append(row.get("name",[]))
            # To strip out commas in case names, comment the line above and uncomment the following 3 lines
            #txt = row.get("name", [])
            #txt = txt.replace(",","")
            #line.append(txt)
            #first, get the timeline data as a list
            timeline = row.get("timeline", [])
            #now get each "event" (Granted, Argued, Decided)
            #because 'timeline' can include one or more events, create a dict
            #note: events can also include "Reargued", "Dismissed", "Dismissed" + other words, "Juris Postponed", "Referred to the Court", and other terms
            events = {"Granted": "0", "Argued": "0", "Decided": "0"}
            for item in timeline:
                if item is not None: #check to make sure there isn't a blank item in the list
                    if "event" in item.keys(): #verify the key exists for an event
                        action = item["event"] #get the event value
                        if action in events: #only get the date if the event is granted, argued, or decided
                            #convert epoch time to YYYY-MM-DD, solution provided by "FloLie" at https://stackoverflow.com/questions/65063058/convert-unix-timestamp-to-date-string-with-format-yyyy-mm-dd
                            dt = datetime.fromtimestamp(item["dates"][0])
                            events[action] = dt.strftime("%Y-%m-%d")
            #add dates to line, and then add the line to the primary data variable 'scotus_dates'
            line.append(events["Granted"])
            line.append(events["Argued"])
            line.append(events["Decided"])
            scotus_dates.append(line)

    #Write cleaned data to CSV file
    write_csv(scotus_dates, "scotus_dates.csv")

    #Convert CSV file to JSON file
    csv_to_json("scotus_dates.csv", "scotus_dates_converted.json")

    #Convert JSON file to CSV file (as proof that no data is lost)
    json_to_csv("scotus_dates_converted.json", "scotus_dates_converted.csv")

def write_csv(data_list, outfile):
    """This function takes a list of lists with 5 columns and writes a CSV file."""
    print("Saving file to CSV: " + outfile)
    with open (outfile, "w") as outfile:
        #write header row
        outfile.write("Year, Title, Date_Granted, Date_Argued, Date_Decided\n")
        #iterate through each row of the data, join with a comma, and write to file
        for row in data_list:
            row[0] = str(row[0]) #convert year to string to use join
            row[1] = f'"{row[1]}"' #add quote marks to title
            line = ", ".join(row)
            outfile.write(line + "\n")

def csv_to_json(infile, outfile):
    """This function converts a CSV-formatted file into a JSON-formatted file."""
    df = pd.read_csv(infile, skipinitialspace=True) 
    df.to_json(outfile, orient='records')
    print("Converted CSV file (" + infile + ") to JSON (" + outfile + ")")

def json_to_csv(infile, outfile):
    """This function converts a JSON-formatted file into a CSV-formatted file."""
    with open(infile, "r") as file:
        print("Reading JSON file via json.load()")
        json_list = json.load(file)
        #print results of json.load to screen as noted in assignment
        print("Printing first 10 items from json.load():")
        print(json_list[:10])
        # create a list to hold imported data
        date_list = []
        for row in json_list:
            items = [row["Year"], row["Title"], row["Date_Granted"], row["Date_Argued"], row["Date_Decided"]]
            date_list.append(items)
        write_csv(date_list, outfile)
    print("Converted JSON file (" + infile + ") to CSV (" + outfile + ")")

if __name__ == '__main__':
    main()

