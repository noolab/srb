import random
import sys
from threading import Thread
import time
import datetime
import requests
import Queue
import re
import xml.etree.ElementTree as ET
import os

DHL_USERID="SRBFrance"
DHL_PWD="jXxlVhceKE"
queue = Queue.Queue()

class Pickup(Thread):

    def __init__(self, number):
        Thread.__init__(self)
        self.number = number

    def run(self):
        date = datetime.datetime.now()-datetime.timedelta(days=1)
        alldays=[]
        date += datetime.timedelta(days=self.number)
        onedate=re.sub(r'\s.*','',str(date))
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <p:DCTRequest xsi:schemaLocation="http://www.dhl.com DCT-req.xsd " xmlns:p="http://www.dhl.com" xmlns:p1="http://www.dhl.com/datatypes" xmlns:p2="http://www.dhl.com/DCTRequestdatatypes" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
          <GetQuote>
            <Request>
              <ServiceHeader>
                <SiteID>"""+DHL_USERID+"""</SiteID> 
                <Password>"""+DHL_PWD+"""</Password> 
              </ServiceHeader>
            </Request>
            <From>
              <CountryCode>FR</CountryCode>
              <Postalcode>31100</Postalcode>
              <City>TOULOUSE</City>
            </From>
            <BkgDetails>
              <PaymentCountryCode>FR</PaymentCountryCode>
              <Date>"""+onedate+"""</Date>
              <ReadyTime>PT10H21M</ReadyTime>
              <ReadyTimeGMTOffset>+01:00</ReadyTimeGMTOffset>
              <DimensionUnit>CM</DimensionUnit>
              <WeightUnit>KG</WeightUnit>
              <Pieces>
                <Piece>
                  <PieceID>1</PieceID>
                  <Height>1</Height>
                  <Depth>1</Depth>
                  <Width>1</Width>
                  <Weight>0.5</Weight>
                </Piece>
              </Pieces>
              <PaymentAccountNumber>223932540</PaymentAccountNumber>      
              <IsDutiable>N</IsDutiable>
              <NetworkTypeCode>AL</NetworkTypeCode>
            </BkgDetails>
            <To>
              <CountryCode>BE</CountryCode>
              <Postalcode>1000</Postalcode>
              <City>BRUSSELS</City>
            </To>
          </GetQuote>
        </p:DCTRequest>"""
        headers = {'Content-Type': 'application/xml'} # set what your server accepts
        resp=requests.post('https://xmlpitest-ea.dhl.com/XMLShippingServlet', data=xml, headers=headers).text
        #print resp
        root = ET.fromstring(resp)
        allstartdate=[]
        allslots=[]
        diffMinute=0
        for firstchild in root:
            for nextl in firstchild:
                for nextEl in nextl:
                    for lastnext in nextEl:
                        if lastnext.tag=="PickupCutoffTime":
                            diffMinute=lastnext.text
                            #print "FOUND SIR"
                        else:
                            a=0#print "NOT FOUND SIR"
                            # diffMinute=0
                        if lastnext.tag=="BookingTime":
                            bktime= lastnext.text
                            if bktime in allstartdate:
                                a=0#print "skip it---"
                            else:
                                #print "found"+str(bktime)
                                allstartdate.append(bktime)
                                bktime=re.sub(r'[^\d]','',bktime)
                                newdate=re.sub(r'\s.*',' ',str(date))
                                fullstartdate=str(newdate)+str(bktime)+':00:00:000Z'

                                # d1=date
                                # d2=datetime.datetime.strptime(str(newdate)+str(bktime)+':00:00','%Y-%m-%d %H:%M:%S')
                                # d1_ts = time.mktime(d1.timetuple())
                                # d2_ts = time.mktime(d2.timetuple())
                                # diffMinute= int(d2_ts-d1_ts) / 60
                                # if diffMinute<0:
                                #   diffMinute=0
                                # diffMinute=0
                                tmpslot={
                                    "start_time": fullstartdate,
                                    "duration": diffMinute,
                                    "availability": -1
                                }
                                allslots.append(tmpslot)
        print "-------------------"
        data={
            "date": str(date),
            "slots": allslots
        }
        print data
        #alldays.append(data)

def pickupfunction(number,queue):
    date = datetime.datetime.now()-datetime.timedelta(days=1)
    alldays=[]
    date += datetime.timedelta(days=number)
    onedate=re.sub(r'\s.*','',str(date))
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <p:DCTRequest xsi:schemaLocation="http://www.dhl.com DCT-req.xsd " xmlns:p="http://www.dhl.com" xmlns:p1="http://www.dhl.com/datatypes" xmlns:p2="http://www.dhl.com/DCTRequestdatatypes" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <GetQuote>
        <Request>
          <ServiceHeader>
            <SiteID>"""+DHL_USERID+"""</SiteID> 
            <Password>"""+DHL_PWD+"""</Password> 
          </ServiceHeader>
        </Request>
        <From>
          <CountryCode>FR</CountryCode>
          <Postalcode>31100</Postalcode>
          <City>TOULOUSE</City>
        </From>
        <BkgDetails>
          <PaymentCountryCode>FR</PaymentCountryCode>
          <Date>"""+onedate+"""</Date>
          <ReadyTime>PT10H21M</ReadyTime>
          <ReadyTimeGMTOffset>+01:00</ReadyTimeGMTOffset>
          <DimensionUnit>CM</DimensionUnit>
          <WeightUnit>KG</WeightUnit>
          <Pieces>
            <Piece>
              <PieceID>1</PieceID>
              <Height>1</Height>
              <Depth>1</Depth>
              <Width>1</Width>
              <Weight>0.5</Weight>
            </Piece>
          </Pieces>
          <PaymentAccountNumber>223932540</PaymentAccountNumber>      
          <IsDutiable>N</IsDutiable>
          <NetworkTypeCode>AL</NetworkTypeCode>
        </BkgDetails>
        <To>
          <CountryCode>BE</CountryCode>
          <Postalcode>1000</Postalcode>
          <City>BRUSSELS</City>
        </To>
      </GetQuote>
    </p:DCTRequest>"""
    headers = {'Content-Type': 'application/xml'} # set what your server accepts
    resp=requests.post('https://xmlpitest-ea.dhl.com/XMLShippingServlet', data=xml, headers=headers).text
    #print resp
    root = ET.fromstring(resp)
    allstartdate=[]
    allslots=[]
    diffMinute=0
    for firstchild in root:
        for nextl in firstchild:
            for nextEl in nextl:
                for lastnext in nextEl:
                    if lastnext.tag=="PickupCutoffTime":
                        diffMinute=lastnext.text
                        #print "FOUND SIR"
                    else:
                        a=0#print "NOT FOUND SIR"
                        # diffMinute=0
                    if lastnext.tag=="BookingTime":
                        bktime= lastnext.text
                        if bktime in allstartdate:
                            a=0#print "skip it---"
                        else:
                            #print "found"+str(bktime)
                            allstartdate.append(bktime)
                            bktime=re.sub(r'[^\d]','',bktime)
                            newdate=re.sub(r'\s.*',' ',str(date))
                            fullstartdate=str(newdate)+str(bktime)+':00:00:000Z'

                            # d1=date
                            # d2=datetime.datetime.strptime(str(newdate)+str(bktime)+':00:00','%Y-%m-%d %H:%M:%S')
                            # d1_ts = time.mktime(d1.timetuple())
                            # d2_ts = time.mktime(d2.timetuple())
                            # diffMinute= int(d2_ts-d1_ts) / 60
                            # if diffMinute<0:
                            #   diffMinute=0
                            # diffMinute=0
                            tmpslot={
                                "start_time": fullstartdate,
                                "duration": diffMinute,
                                "availability": -1
                            }
                            allslots.append(tmpslot)
    print "-------------------"
    data={
        "date": str(date),
        "slots": allslots
    }
    print data
    queue.put(data)


# thread_1 = threading.Thread(
#                 target=pickupfunction,
#                 name="Thread1",
#                 args=[1, queue],
#                 )
# thread_2 = threading.Thread(
#                 target=pickupfunction,
#                 name="Thread2",
#                 args=[2, queue],
#                 )
# thread_3 = threading.Thread(
#                 target=pickupfunction,
#                 name="Thread3",
#                 args=[3, queue],
#                 )



# Creation des threads
thread_1 = Pickup(1)
thread_2 = Pickup(2)
thread_3 = Pickup(3)
#thread_4 = Pickup(4)
#thread_5 = Pickup(5)
#thread_6 = Pickup(6)
#thread_7 = Pickup(7)

# Lancement des threads
thread_1.start()
thread_2.start()
thread_3.start()
#thread_4.start()
#thread_5.start()
#thread_6.start()
#thread_7.start()

# Attend que les threads se terminent
thread_1.join()
thread_2.join()
thread_3.join()
#print queue.get()
