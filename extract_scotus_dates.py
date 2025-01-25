import requests
import json

#range of years of SCOTUS data to get
start_year = 2019
end_year = 2020
#variable to store dates for SCOTUS trials
scotus_dates = []
#scotus_dates = ["Year", "Title", "Granted", "Argued", "Decided"]

#API endpoint url for SCOTUS cases
api_base_url = 'https://api.oyez.org/cases?per_page=0&filter=term:'

#SCOTUS Cases are organized by Year, so iterate over the range of years
for i in range(start_year, end_year+1):
    #Create the API URL from the base URL (api_base_url) plus the year
    api_url = api_base_url + str(i)
    # send GET request to the Oyez API
    Oyez_API = requests.get(api_url)
    #
    scotus_data = Oyez_API.json()

    # status code check
    print(str(i) + ": " + f"status code: {Oyez_API.status_code}")


    # ==== DATA FOR ANALYSIS =====
    #iterate over each case in scotus_data list
    for row in scotus_data:
        #temporary list for dates
        line = [str(i)]
        #get name of case
        line.append(row.get('name', []))
        #first, get the timeline data as a list
        timeline = row.get('timeline', [])
        #print(timeline) #debug
        #now get each "event" (Granted, Argued, Decided)
        for item in timeline:
            if item is None:
                # do something
                line.append(" ")
            else:
                line.append(str(item["dates"][0]))
        scotus_dates.append(line)

    #print(scotus_dates) #debug


# ===== WRITE DATA TO CSV =======
with open ("scotus_dates.csv", "w") as outfile:
    #write header row
    outfile.write("Year, Title, Date Granted, Date Argued, Date Decided\n")
    #iterate through each row of the data, join with a comma, and write to file
    for row in scotus_dates:
        line = ", ".join(row)
        outfile.write(line + "\n")

# ===== WRITE DATA TO JSON =======
# # Save data to a JSON file
# outfile = "scotus_data_" + str(i) + ".json" 
# with open (outfile, "w") as outfile:
#     json.dump(scotus_data, outfile)







