# CS512-project
OSU Data Science Tools and Programs CS 512

Project: "Work Norms of the Early U.S. Supreme Court"

This project examines the productivity patterns of the U.S. Supreme Court during its early formative years (1789 to 1889). Specifically, this analysis seeks to answer three questions about how the work patterns of the early Supreme Court changed over the course of three different eras: the Early Republic (from 1783 to 1860), the Civil War years (1861 to 1856), and the Reconstruction and Industrialization era (1866 to 1899).
1)	How does the pattern of day-to-day work of the Supreme Court vary throughout the early Supreme Court years?
2)	How does the annual court calendar change during the early Supreme Court years?
3)	How does the length of time to deliberate a case change during the early Supreme Court years?

The data for this project was scraped from the API of Oyez.org, an online multimedia database containing the history of the caseload and judicial personnel of the Supreme Court of the United States (SCOTUS). 

Files:
scotus_norms.py - python file to get data, process it, convert to a database, and analyze and create plots
cases.json - sample of records obtained from the Oyez.org API
cases.sql - output of the first 10 cases from phpMyAdmin


From the command line:
python escotus_norms.py

