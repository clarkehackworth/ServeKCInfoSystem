#!/usr/bin/python
import time
import meetup.api
import sys
import getopt
import csv 
from flatten_json import flatten
from decimal import Decimal


###### Constants ######

APIKEY = ""

URL_NAME = 'ServeKC'

REQUEST_DELAY = 0 #seconds to wait between requests, default is 0 as API library handles back off

REQUEST_RETRIES = 5 #retries if no JSON data recieved. Should be handled by API library, but doesn't appear to be handled well

CSV_DELIMITER=','


###### main program ######

client = meetup.api.Client(APIKEY)


def collectData(filenamebase='ServeKC'):

    print '--- '+URL_NAME+' information collection ---'

    ###### get group info ######
    group_info = client.GetGroup({'urlname': URL_NAME})

    eventsInfo = getEventsInfo(groupId=group_info.id)

    writeCSV(filenamebase+'-events.csv',eventsInfo)
    

    ###### get attendance info ######
    eventIds = []
    for eventsInfo in eventsInfo:
        if eventsInfo['id'] not in eventIds:
            eventIds.append(eventsInfo['id'])

    attendanceInfo = getAttendanceInfo(eventIdArray=eventIds)

    print '-cumulative errors-'
    for error in attendanceInfo['errors']:
        print 'error - event: '+str(error['eventId'])+' message: '+error['message']+' code: '+error['code']
    writeCSV(filenamebase+'-attendance.csv',attendanceInfo['data'])
    print '-files written: '+filenamebase+'-events.csv, and '+filenamebase+'-attendance.csv'

def getEventsInfo(groupId=0):
    print '-Getting events info'
    eventsInfoCombo = []
    results = True
    page = 1
    retries = 0
    while results:
        try: 
            eventsInfo = client.GetEvents(group_id=groupId,status="upcoming,past,proposed,suggested,cancelled,draft",offset=page)
            if eventsInfo.results:
                eventsInfoCombo.extend(eventsInfo.results)
                page=page+1
                time.sleep(REQUEST_DELAY)
            else:
                results = False

        except ValueError as e:
            if retries > REQUEST_RETRIES:
                raise e
            retries=retries+1
            print e
            print 'retry '+str(retries)
            time.sleep(1) 
    return eventsInfoCombo


def getAttendanceInfo(eventIdArray=[]): 
    print '-Getting attendance info'
    attendanceInfoCombo = []
    errors = []
    count = 0
    retries = 0
    for eventsId in eventIdArray:
        try:
            attendanceInfo = client.GetGroupEventsAttendance(id=eventsId,urlname=URL_NAME,page=200)

            if hasattr(attendanceInfo, 'errors'):

                for error in attendanceInfo.errors:
                    print 'event: '+str(eventsId)+' message: '+error['message']+' code: '+error['code']
                    error['eventId'] = eventsId
                    errors.append(error)
            if hasattr(attendanceInfo, 'items') and len(attendanceInfo.items)>0:
                for attendanceInfoItem in attendanceInfo.items:
                
                    #add event id to object
                    attendanceInfoItem['event_id']=eventsId

                    attendanceInfoCombo.append(attendanceInfoItem)
            count = count + 1
            print 'Getting Attendance - '+str( int((Decimal(count) / Decimal(len(eventIdArray)))*100) )+" %"

            time.sleep(REQUEST_DELAY)

        except ValueError as e:
            if retries > REQUEST_RETRIES:
                raise e
            retries=retries+1
            print e
            print 'retry '+str(retries)
            time.sleep(1)
    return {'data':attendanceInfoCombo,'errors':errors}


def writeCSV(fileName, data):
    fileData = open(fileName, 'w')

    # create the csv writer object
    csvwriter = csv.writer(fileData, delimiter=CSV_DELIMITER)

    headers = []
    for item in data:
        item = flatten(item)

        for key in item.keys():
           if key not in headers:
                headers.append(key)
    #print 'headers'
    #print headers

    count = 0
    for item in data:
        if count == 0:
             csvwriter.writerow(headers)
             count += 1
        item = flatten(item)
        #print item
        row = []
        for header in headers:
            if header in item:
                row.append(parseData(item[header]))
            else:
                row.append('')
        csvwriter.writerow(row)
    fileData.close()


def parseData(data):
    if isinstance(data, unicode):
       return data.encode('utf-8')
    else:
       return data

def usage():
    print "Usage: "+sys.argv[0]+' -o <output_file_base_name>'

try:
    opts, args = getopt.getopt(sys.argv[1:], 'o:h', ['output=', 'help'])
    if not opts:
        usage()
except getopt.GetoptError:
    usage()
    sys.exit(2)

outputName = ""
for opt, arg in opts:
    if opt in ('-h', '--help'):
        usage()
        sys.exit(2)
    elif opt in ('-o', '--output'):
        collectData(filenamebase=arg)
    else:
        usage()
        sys.exit(2)

