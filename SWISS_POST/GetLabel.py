import json
import datetime
import time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
#from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from pprint import pprint  #json read
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import datetime
from reportlab.graphics.barcode import code39
from reportlab.graphics.barcode import code93
from reportlab.graphics.barcode import code128

def getLabel(event,context):
    #name_file = str(time.time()) + ".pdf"


    data = {
      "return_id" : "4444" ,
      "origin": {"first_name": "Ithyvan",
               "last_name": "Schreys" ,
               "street_number": "11",
               "line1": "avenue de la habette du maraicher",
               "zipcode": "10012",
               "city": "lausanne",
               "country_code": "CH"
               },
       "destination":{"company": "WITHINGS"}
    }



    return_id = data['return_id']
    firstName = data['origin']['first_name']
    lastName = data['origin']['last_name']
    streetNumber = data['origin']['street_number']
    line1 = data['origin']['line1']
    zipCode = data['origin']['zipcode']
    city = data['origin']['city']
    countryCode = data['origin']['country_code']
    company = data['destination']['company']

    returnIdCondition = return_id.zfill(8)

    c = canvas.Canvas("GetLabel.pdf")
    c.setFont('Helvetica-Bold', 20)
    c.setLineWidth(1)
    c.rect(8,520,450,315, stroke=1, fill=0)


    c.setFont('Helvetica', 12)
    c.rotate(90)
    c.drawString(540,-47, firstName + " " + lastName)
    c.drawString(540,-62, streetNumber + " " + line1)
    c.drawString(540,-77, zipCode + " " + city )
    c.drawString(540,-92, countryCode )
    GASbarcode = 'GAS-barcode.png'
    c.drawImage(GASbarcode, 687, -320, width=86, height=50)
    #c.drawString(700,-280,'GAS')

    #c.drawString(400,-200,'BORDEREAU')
    #barcode=code39.Extended39("1234",barWidth=0.2*mm,barHeight=10*mm)
    # drawOn puts the barcode on the canvas at the specified coordinates
    #barcode.drawOn(c,680,-320)


    c.rotate(-90)
    c.setFont('Helvetica-Bold', 14)
    c.drawString(160,596, company)
    c.drawString(160,579,'c/o Alois Scherrer AG')
    c.drawString(160,562,'Nebengrabenstrasse 16')
    c.drawString(160,545,'9430 St. Margrethen')


    c.setFont('Helvetica', 12)
    SwissPost = 'Swiss_Post.png'
    c.drawImage(SwissPost,115,770, width=105, height=27)
    #c.drawString(90,760,'SWISS POST')
    #barcode=code93.Extended93("996012141900010081",barWidth=0.335*mm,barHeight=20*mm)
    # drawOn puts the barcode on the canvas at the specified coordinates
    #barcode.drawOn(c,15,700)
    c.setFont('Helvetica', 18)
    c.drawString(32,680,"99.60.121419."+returnIdCondition)

    barcode = code128.Code128("9960121419"+returnIdCondition ,barWidth=0.5*mm,barHeight=25*mm)
    barcode.drawOn(c,15,700)
        # the multiwidth barcode appears to be broken
        #barcode128Multi = code128.MultiWidthBarcode(barcode_value)



    c.save()


