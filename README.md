# ServeKCInfoSystem

## Preparation / dependencies
1. Install python libraries
```
pip install meetup-api
pip install flatten_json
```
2. Clone repository or download zip file
3. Edit ServceKCInfoSystem.py and add your API key into the variable toward the top of the script
```
APIKEY = "<insert key here>"
```
4. Run script (see Usage section below)

## Usage
In terminal:
```
python ServeKCInfoSystem.py -o ServeKC
```

Sample output:
```
--- ServeKC information collection ---
29/30 (10 seconds remaining)
-Getting events info
28/30 (10 seconds remaining)
27/30 (7 seconds remaining)
26/30 (2 seconds remaining)
...
-Getting attendance info
27/30 (7 seconds remaining)
Getting Attendance - 0 %
16/30 (9 seconds remaining)
...
15/30 (9 seconds remaining)
Getting Attendance - 100 %
...
-files written: ServeKC-events.csv, and ServeKC-attendance.csv
```

This will create two files: ServeKC-events.csv and ServeKC-attendance.csv
These files will list events, and attendance records respectively.
