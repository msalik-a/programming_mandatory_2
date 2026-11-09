import requests
import json
import sqlite3
from pathlib import Path
import datetime

# Configuration
API_BASE = "(BASE-API)"
EMAIL = "(AUTHORIZED-EMAIL)"

# Get token
def get_token():
    response = requests.post(f"{API_BASE}/api/auth/token", json={"email": EMAIL})
    return response.json()["token"]

# Get incidents
def get_incidents(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/api/incidents?$top=100", headers=headers)

    # Incidents returned:
    data_json = response.json()
    if "value" in data_json:
        print(f"Returned: {len(data_json['value'])} incidents.")
        
    return response.json()


# Getting the data
try:
    
    token = get_token()
    incidents = get_incidents(token)
   
    # Parsing to JSON
    with open("mandatory2.json", "w",) as x:
        json.dump(incidents["value"],x,indent=4) 

    with open("mandatory2.json", "r") as read:
        data = json.load(read)
        
except Exception as e: print(e)



# Outputting the data to SQL
try:
    n=0
    con = sqlite3.connect("output.db")
    c = con.cursor()

    for incident in data:  

        if "alerts" in incident:

            for x in incident["alerts"]:
                
                alert_id = x.get("alertId")
                incident_id = incident.get("incidentId") #incident.get cuz its in same indent as "alerts", not inside it like the rest
                severity = x.get("severity")
                category = x.get("category")
                machine_id = x.get("machineId")
                first_seen = x.get("firstSeen")
                timestamp = datetime.datetime.now().isoformat() #isoformat() cuz DeprecationWarning if not formatted
                detection_source = x.get("detectionSource")

                n+=1
                # print(f"-----{n}-----")
                # print(f"Alert ID: {alert_id}")
                # print(f"Incident ID: {incident_id}") 
                # print(f"Severity: {severity}")
                # print(f"Category: {category}")
                # print(f"Machine ID: {machine_id}")
                # print(f"First Seen: {first_seen}")
                # print(f"Timestamp: {timestamp}")
                # print(f"Detection Source: {detection_source}")

                # SQL:
                incident_table = (alert_id, incident_id, severity, category, machine_id, first_seen, timestamp, detection_source)
                
                c.execute("""
                    CREATE TABLE IF NOT EXISTS INCIDENTS (
                        ALERT_ID TEXT, 
                        INCIDENT_ID TEXT, 
                        SEVERITY TEXT, 
                        CATEGORY TEXT, 
                        MACHINE_ID TEXT, 
                        FIRST_SEEN TEXT, 
                        TIMESTAMP TEXT, 
                        DETECTION_SOURCE TEXT
                    )
                    """)

                    
                c.execute("""
                    INSERT INTO INCIDENTS (
                    ALERT_ID, INCIDENT_ID, SEVERITY, CATEGORY, 
                    MACHINE_ID, FIRST_SEEN, TIMESTAMP, DETECTION_SOURCE
                    ) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, incident_table)

                con.commit()
                
    c.close()
    con.close()
except Exception as e: print(e)


            


