import arcpy
import datetime
import smtplib
import pandas

def sendEmail(fromaddr,toaddrs,msg):
    print("Sending an email")
    params = pandas.read_excel("domainParameters.xlsx", sheetname='email')
    print(params)
    username=params.iat[0,0]
    password=params.iat[0,1]
    print(username)
    print(password)
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username, password)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()

# Create string from date and time
time = datetime.datetime.now()  # Get system time
if len(str(time.month)) == 1:
    month = "0" + str(time.month)
else:
    month = str(time.month)
if len(str(time.day)) == 1:
    day = "0" + str(time.day)
else:
    day = str(time.day)
if len(str(time.hour)) == 1:
    hour = "0" + str(time.hour)
else:
    hour = str(time.hour)
if len(str(time.minute)) == 1:
    minute = "0" + str(time.minute)
else:
    minute = str(time.minute)
if len(str(time.second)) == 1:
    second = "0" + str(time.second)
else:
    second = str(time.second)

dateString = str(time.year) + month + day + "_" + hour + minute + second

backupPath = r"\\Igswzcwwgsrio\loco\Geology\SDE_Stuff\DomainTables\TableBackups\DomainTableBackups.gdb"

locogeo=r"Database Connections\Connection to igswzcwggsmoki.wr.usgs.gov_LOCOGEO_SDE.sde"
rscgeo=r"Database Connections\Connection to igswzdwgdbkiva.wr.usgs.gov_RSCGEO_DBO.sde"
locomaps=r"Database Connections\Connection to igswzcwggsmoki.wr.usgs.gov_LOCOMAPS_DBO.sde"

#TODO generate these lists from the domainParameters excel file

domainName=["PKHMapUnits",
            "DataSourceID",
            "HPGPS_Purpose",
            "SUND_MapUnits",
            "LOCOGroupMapUnit"]
domainDescription=["PKH list of map units",
                   "Source of data",
                   "Purpose for HPGPS data",
                   "Original SUND map units",
                   "LOCO group map units"]
excelFile = [r"\\igswzcwwgsrio\loco\Geology\SDE_Stuff\DomainTables\MasterTables\PKH_LMU_MASTER.xlsx",
             r"\\igswzcwwgsrio\loco\Geology\SDE_Stuff\DomainTables\MasterTables\DataSource_MASTER.xlsx",
             r"\\Igswzcwwgsrio\loco\Geology\SDE_Stuff\DomainTables\MasterTables\AttributeDomains_MASTER.gdb\HPGPS_Purpose",#Not an excelsheet consider renaming list name
             r"\\igswzcwwgsrio\loco\Geology\SDE_Stuff\DomainTables\MasterTables\SUND_MapUnits_MASTER.xls",
             r"\\Igswzcwwgsrio\loco\Geology\SDE_Stuff\DomainTables\MasterTables\LOCOGroup_MASTER.xlsx"]
sheetName = [r"PKH_LMU$", #Need $ after sheet names
             r"DataSourceID$",
             "",
             "SUND_MapUnits_MASTER$",#If arc table BLANK sheetname
             "LOCOGroupMaster$"]
codeField = ["mapunit",
             "Code",
             "Code",
             "Code",
             "MapUnit"]
descriptionField = ["DomainDesc",
                    "DomDesc",
                    "DomainDescrip",
                    "DomainDescrip",
                    "DomainDesc"]

DBs = [[locogeo,rscgeo,locomaps],
       [locogeo,rscgeo,locomaps],
       [locogeo],
       [rscgeo],
       [locogeo]]

emailString = 'At least one of the following SDE domains has been updated: '
length=len(domainName)
for d in range(len(domainName)):
    count=0
    for DB in DBs[d]:
        #MAKE A BACKUP OF THE EXISTING DOMAINS
        if count == 0: #Domains should be the same for all the DBs if the script is working right
            arcpy.DomainToTable_management(in_workspace=DB,
                                           domain_name=domainName[d],
                                           out_table=backupPath+"\\"+domainName[d]+dateString,
                                           code_field=codeField[d],
                                           description_field=descriptionField[d])
            print("Backup made of: "+domainName[d])
            if d==len(domainName)-1:
                emailString = emailString + domainName[d]
            else:
                emailString = emailString + domainName[d]+ ", "
        count=count+1

        arcpy.TableToDomain_management(in_table=excelFile[d]+"\\"+sheetName[d],
                                       code_field=codeField[d],
                                       description_field=descriptionField[d],
                                       in_workspace=DB,
                                       domain_name=domainName[d],
                                       domain_description=domainDescription[d],
                                       update_option="REPLACE")
        #TODO Sort Domain with Sort Coded Value Domain
        print(domainName[d]+" updated in DB: "+DB)

#Email addresses for use in sending emails
fromaddr = pandas.read_excel("domainParameters.xlsx", sheetname='email').iat[0,0] #get email address from param file
toErrorAddrs = pandas.read_excel("domainParameters.xlsx", sheetname='email').iat[0,0] #get email address from param file
toaddrs = ['crow.ryan@gmail.com', 'tfelger@usgs.gov', 'pkhouse@gmail.com', 'khouse@usgs.gov', 'rcrow@usgs.gov', 'emennow@usgs.gov', 'ccassidy@usgs.gov', 'sbeard@usgs.gov', 'dblock@usgs.gov']
#toaddrs = ['crow.ryan@gmail.com', 'tfelger@usgs.gov']


msg = "\r\n".join([
    "From: " + fromaddr,
    "To: " + ", ".join(toaddrs),
    "Subject: FYI: SDE domains have been updated ",
    "", emailString+". See Ryan for details."])
sendEmail(fromaddr,toaddrs,msg)