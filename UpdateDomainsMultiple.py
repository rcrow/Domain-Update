import arcpy
import datetime
import smtplib
import pandas

def nanToBlank(string):
    if pandas.isnull(string):
        return ""
    else:
        return string

def sendEmail(fromaddr,toaddrs,msg):
    print("Sending an email")
    params = pandas.read_excel("domainParameters.xlsx", sheet_name='email')
    #print(params)
    username=params.iat[0,0]
    password=params.iat[0,1]
    #print(username)
    #print(password)
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

backupPath = pandas.read_excel("domainParameters.xlsx", sheet_name='backup').iat[0,0]

connections = pandas.read_excel("domainParameters.xlsx", sheet_name='connections')
dbsNames = connections['dbsNames'].values.tolist()
sdeConnections = connections['sdeConnections'].values.tolist()
dbDict = dict(zip(dbsNames,sdeConnections))

domains = pandas.read_excel("domainParameters.xlsx", sheet_name='domains')
domainName = domains['domain_name'].values.tolist()
domainDescription = domains['domain_description'].values.tolist()
excelFile = domains['excel_file_or_ArcTable'].values.tolist()
sheetName = domains['sheet_name'].values.tolist()
codeField = domains['code_field'].values.tolist()
descriptionField = domains['description_field'].values.tolist()
DBsStrings = domains['DBs'].values.tolist()
DBs = []
for DB in DBsStrings:
    DBs.append(DB.split(","))
print(DBs)

emailString = 'At least one of the following SDE domains has been updated: '
length=len(domainName)
#print(length)
for d in range(len(domainName)):
    #print(domainName[d])
    count=0
    for DB in DBs[d]:
        print(DB)
        #MAKE A BACKUP OF THE EXISTING DOMAINS
        if count == 0: #Domains should be the same for all the DBs if the script is working right so only make a copy from the first db
            arcpy.DomainToTable_management(in_workspace=dbDict[DB],
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

        inTable = excelFile[d]+"\\"+nanToBlank(sheetName[d])
        print("Table name: " + str(inTable))

        arcpy.TableToDomain_management(in_table=inTable,
                                       code_field=codeField[d],
                                       description_field=descriptionField[d],
                                       in_workspace=dbDict[DB],
                                       domain_name=domainName[d],
                                       domain_description=domainDescription[d],
                                       update_option="REPLACE")

        #TODO Sort Domain with Sort Coded Value Domain
        print(domainName[d]+" updated in DB: "+dbDict[DB])

#Email addresses for use in sending emails
fromaddr = pandas.read_excel("domainParameters.xlsx", sheet_name='email').iat[0,0] #get email address from param file
toErrorAddrs = pandas.read_excel("domainParameters.xlsx", sheet_name='email').iat[0,0] #get email address from param file
toaddrs = pandas.read_excel("domainParameters.xlsx", sheet_name='toAddresses')['email'].values.tolist()

msg = "\r\n".join([
    "From: " + fromaddr,
    "To: " + ", ".join(toaddrs),
    "Subject: FYI: SDE domains have been updated ",
    "", emailString+". See Ryan for details."])
sendEmail(fromaddr,toaddrs,msg)