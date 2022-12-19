import re
from collections import defaultdict

comment_re = "--([^\n\r-]|-[^\n\r-])*(--|-?[\n\r])"
range_re = "\(\s*(MIN|\d+(\.\d*)?)\s*\.\.\s*(MAX|\d+(\.\d*)?)\s*\)"

 
def createAllObjectsDict(totalList, partialList):
 
  for i in partialList:
    curr = mib_generic(type(i))
    curr.name = i.name
    curr.parent = i.parent
    curr.number = i.number
    totalList[curr.name] = curr
 
  return totalList   
 
def createOIDs(totalListDict, startObjectName):
  startObj = totalListDict[startObjectName]
  oid = startObj.number

  # Search through the dictionary to gather all the oid values
  while startObj.parent != None:
    if startObj.parent not in totalListDict:
      oid = "." + oid
      break
    startObj = totalListDict[startObj.parent]
    oid = startObj.number + "." + oid

  return oid

def createWordOIDs(totalListDict, startObjectName):
  oid = startObjectName
  startObj = totalListDict[startObjectName]

  # Search through the dictionary to gather all the oid values
  while startObj.parent != None:
    if startObj.parent not in totalListDict:
      oid = startObj.parent + "." + oid
      break
    startObj = totalListDict[startObj.parent]
    oid = startObj.name + "." + oid

  return oid

def fillOid(obj, my_dict):
  oidNum = createOIDs(my_dict, obj.name)
  oidWordNum = createWordOIDs(my_dict, obj.name)
  return oidNum, oidWordNum
 
# Class Structure Goes Here
class mib_generic:
  original_type = None
  name = None
  parent = None
  number = None

  def __init__(self, original_type):
    self.original_type = original_type
 
  def print_mib_generic(self):
    print('\n')
    print("Name: ", self.name)
    print("Parent: ", self.parent)
    print("Number: ", self.number)
    print("Original Type: ", self.original_type)  
 
class mib_notification_type:
  name = None
  objects = None
  status = None
  description = None
  parent = None
  number = None
  def __init__(self, name):
    self.name = name
 
  def print_notification_type(self):
    print('\n')
    print("Name: ", self.name)
    print("Objects: ", self.objects)
    print("Status: ", self.status)
    print("Description: ", self.description)
    print("Parent: ", self.parent)
    print("Number: ", self.number)

class mib_module_identity:
  name = None
  last_updated = None
  organization = None
  contact_info = None
  description = None
  parent = None
  number = None

  def __init__(self, name):
    self.name = name
 
  def print_module_identity(self):
    print('\n')
    print("Name: ", self.name)
    print("Last Updated: ", self.last_updated)
    print("Organization: ", self.organization)
    print("Contact Info: ", self.contact_info)
    print("Description: ", self.description)
    print("Parent: ", self.parent)
    print("Number: ", self.number)

# Class object definition for NOTIFICATION-GROUP instances
class mib_notification_group:
  name = None
  notifications = None
  status = None
  description = None
  parent = None
  number = None

  def __init__(self, name):
    self.name = name
 
  def print_notification_group(self):
    print('\n')
    print("Name: ", self.name)
    print("Notifications: ", self.notifications)
    print("Status: ", self.status)
    print("Description: ", self.description)
    print("Parent: ", self.parent)
    print("Number: ", self.number)    

# Class object definition for OBJECT IDENTIFIER instances
class mib_object_identifier:
  name = None
  parent = None
  number = None
  def __init__(self, name):
    self.name = name
 
  def print_obj_identifier(self):
    print("Name: ", self.name)
    print("Parent: ", self.parent)
    print("Number: ", self.number) 
 
# Class object definition for OBJECT-TYPE instances
class mib_object:
  name = None
  syntax = None
  access = None
  description = ""
  parent = None
  number = None
 
  def __init__(self, name):
    self.name = name # sub resource prefix
  
  def mib_print(self):
    print("Name:", self.name)
    print("Syntax:", self.syntax)
    print("Access:", self.access)
    print("Description:", self.description)
    print("Parent:", self.parent)
    print("Oid Number:", self.number, "\n")
   
class oid:

  container = []

  resrc = None
  oid_name = None
  number = None
  poll_freq = None
  subr_pfx = None
  subr_name = None
  param_name = None
  trap = None
  alarm = None
  modal_type = None
  modal_ctrl1 = None
  modal_ctrl2 = None
  status = None
  implemented = None
  comments = None

  def fitToContainer(self):
    self.container.append(self.resrc)
    self.container.append(self.oid_name)
    self.container.append(self.number)
    self.container.append(self.poll_freq)
    self.container.append(self.subr_pfx)
    self.container.append(self.subr_name)
    self.container.append(self.param_name)
    self.container.append(self.trap)
    self.container.append(self.alarm)
    self.container.append(self.modal_type)
    self.container.append(self.modal_ctrl1)
    self.container.append(self.modal_ctrl2)
    self.container.append(self.status)
    self.container.append(self.implemented)
    self.container.append(self.comments)

  def oid_print(self):
    print("Resource:", self.resrc)
    print("Oid name:", self.oid_name)
    print("Oid number:", self.number)
    print("Polling frequency:", self.poll_freq)
    print("Subresource prefix:", self.subr_pfx)
    print("Subresource:", self.subr_name)
    print("Parameter name:", self.param_name)
    print("Trap:", self.trap)
    print("Alarm:", self.alarm)
    print("Modal type:", self.modal_type)
    print("Modal control 1:", self.modal_ctrl1)
    print("Modal control 2:", self.modal_ctrl2)
    print("Status:", self.status)
    print("Implemented:", self.implemented)
    print("Comments:", self.comments, "\n")

# Helper function to make resource name more human-readable
def name_generator(str):
  str_array = []
  array2 = []
  ptr = 0
  for i in range(1, len(str)):
    if str[i].isupper() or str[i] == "_":
      str_array.append(str[ptr:i])
      ptr = i
    elif str[i] == "_":
      str_array.append(str[ptr:i])
      ptr = i + 1
  str_array.append(str[ptr:])
  for x in str_array:
    array2.append(x.capitalize())
  return " ".join(array2)

# Helper function to parse enumerated integers with value names
def select(str):
  pattern = "[a-zA-Z][a-zA-Z0-9-_]*\s*\(\s*\d+\s*\)"
  mylist = re.findall(pattern, str)
  strlist = []
  numlist = []
  for item in mylist:
    strlist.append(re.search('[a-zA-Z][a-zA-Z0-9-_]*', item).group())
    numlist.append(re.search('\d+', item).group())
  return ";".join(strlist), ";".join(numlist)

# Converts OBJECT-TYPE raw data object into data dictionary object
def obj_to_data(object):
    my_data = oid()
    my_data.oid_name = None
    my_data.number = None

    my_data.subr_pfx = object.parent
    my_data.subr_name = object.name
    my_name = object.name
    my_data.param_name = name_generator(object.name)
    
    
    if (object.access == "read-write"):
      my_data.status = "Control"
      if "INTEGER" in object.syntax or "Integer" in object.syntax:
        if "{" in object.syntax:
          my_data.modal_type = "select"
          my_data.modal_ctrl1, my_data.modal_ctrl2 = select(object.syntax)
        elif re.search(range_re, object.syntax) != None:
          my_data.modal_type = "quantity/select"
          my_data.modal_ctrl1 = "integer"
          my_range = re.search(range_re, object.syntax).group()
          my_range = re.findall("(MIN|MAX|\d+)", my_range)
          my_data.modal_ctrl2 = "min=\"" + my_range[0] + "\" max=\"" + my_range[1] + "\""
        else:
          my_data.modal_type = "quantity"
          my_data.modal_ctrl1 = "integer"
          my_data.modal_ctrl2 = "full-range"
      elif "REAL" in object.syntax:
        my_data.modal_type = "quantity"
        my_data.modal_ctrl1 = "real"
        if re.search(range_re, object.syntax) != None:
          my_range = re.search(range_re, object.syntax).group()
          my_range = re.findall("(MIN|MAX|\d+\.\d*)", my_range)
          my_data.modal_ctrl2 = "min=\"" + my_range[0] + "\" max=\"" + my_range[1] + "\""
        else:
          my_data.modal_ctrl2 = "full-range"
      else:
        my_data.modal_type = "textarea"
        my_data.modal_ctrl1 = "n/a"
        my_data.modal_ctrl2 = "n/a"

      
    else:
      my_data.status = "Status"
      my_data.modal_type = "n/a"
      my_data.modal_ctrl1 = "n/a"
      my_data.modal_ctrl2 = "n/a"

    my_data.implemented = "no"
    my_data.comments = object.description

    return my_data



def parseFile(filePath):

  KEYWORDS = {"::=", "INDEX", "STATUS", "DESCRIPTION", "SYNTAX", "INDEX", "REFERENCE", "MAX-ACCESS", "ACCESS", "UNITS"}

  mibList = []
  objIdentifierList = []  
  notificationTypeList = []
  notificationGrpList = []
  moduleIdentityList = []

  with open(filePath, 'r') as file_object:
    line = file_object.readline()

    while line:

      # Removes all comments
      line = re.sub(comment_re, '', line, 1)

      if "MODULE-IDENTITY" in line: # Pulls data relating to MODULE-IDENTITY
        # Skips import line
        if ',' in line:
          line = file_object.readline()
          continue

        # obtains MODULE-IDENTITY name from line
        name = line.replace("MODULE-IDENTITY", '').strip()

        # Skips import line if keyword is on its own line
        if len(name) == 0:
          line = file_object.readline()
          continue

        modIden = mib_module_identity(name)
        moduleIdentityList.append(modIden)

        while "::=" not in line:
          line = file_object.readline()

        # filters out the unnecessary characters from line
        
        line = line.replace("{", '')
        line = line.replace("}", '')
        line = line.replace("::=", '')
        curr_line = line.split()

        # pulls the parent and number from inside the brackets
        modIden.parent =  curr_line[0]
        modIden.number = curr_line[1]

        line = file_object.readline()
        continue

      elif "OBJECT IDENTIFIER" in line: # Pulls data relating to OBJECT-IDENTIFIER
        # filters out the unnecessary characters from line
        line = line.replace("{", '')
        line = line.replace("}", '')
        line = line.replace("::=", '')
        curr_line = line.split()
 
        # pulls the first element from the object identifier
        objIdentifier = mib_object_identifier(curr_line[0])
        # append the object identifier to its list 
        objIdentifierList.append(objIdentifier) 
 
        # pulls the parent and number from inside the brackets
        objIdentifier.parent =  curr_line[3]
        objIdentifier.number = curr_line[4]
      
        line = file_object.readline()
        continue

      elif "NOTIFICATION-GROUP" in line: # Pulls data relating to NOTIFICATION-GROUP
        # Skips import line
        if ',' in line:
          line = file_object.readline()
          continue
 
        # parses the name of the notification-group and initializes our object
        name = line.replace("NOTIFICATION-GROUP", '')
        name = name.replace(" ", '')
        name = " ".join(name.split())

        # Skips import line if keyword is on its own line
        if len(name) == 0:
          line = file_object.readline()
          continue

        # create the notification-type object
        notifGrp = mib_notification_group(name)
 
        # append the notification-group object to its list 
        notificationGrpList.append(notifGrp)
        line = file_object.readline()
 
        # parse the NOTIFICATIONS section
        notifications_str = ""
        if "NOTIFICATIONS" in line:
          while '}' not in line:
            notifications_str += line
            line = file_object.readline()
          notifications_str += line
 
          # filter the unnecessary characters from the objects data         
          notifications_str = notifications_str.replace("NOTIFICATIONS", '') 
          notifications_str = notifications_str.replace("{", '')
          notifications_str = notifications_str.replace("}", '')
          # removes extra spacing to make the string more readable
          notifications_str = " ".join(notifications_str.split())
 
          # split the string around to commas to obtain the list of notifications
          notifications_list = notifications_str.split(",")    
 
          # add the list of objects to our notification-group object
          notifGrp.notifications = notifications_list
          line = file_object.readline()
 
        # parse the STATUS section
        if "STATUS" in line:
          status_type = line.replace("STATUS", '')
          status_type = status_type.replace(" ", '')
          status_type = " ".join(status_type.split())
          notifGrp.status = status_type
          line = file_object.readline()
 
        # parse the DESCRIPTION section
        description_str = ""
        if "DESCRIPTION" in line:
          line = file_object.readline()
          while "::=" not in line:
            description_str += line
            line = file_object.readline()
          # removes extra spacing and quotation marks and adds to description field
          notifGrp.description = description_str.strip()[1:-1]
 
        # parse the parent and number section
        reference_str = ""
        if "::=" in line:
          line = line.replace("{", '')
          line = line.replace("}", '')
          line = line.replace("::=", '')
          reference_str = line.split()
 
          notifGrp.parent = reference_str[0]
          notifGrp.number = reference_str[1] 
 
        line = file_object.readline()
        continue

      elif "NOTIFICATION-TYPE" in line: # Pulls data relating to NOTIFICATION-TYPE
        # Skips import line
        if ',' in line:
          line = file_object.readline()
          continue
 
        # parses the name of the notification-type and intializes our object
        name = line.replace("NOTIFICATION-TYPE", '')
        name = name.replace(" ", '')
        name = " ".join(name.split())

        # create the notification-type object
        notifType = mib_notification_type(name)
 
        # append the notification-type object to its list 
        notificationTypeList.append(notifType)
        line = file_object.readline()
 
        # parse the OBJECTS section
        objects_str = ""
        if "OBJECTS" in line:
          while '}' not in line:
            objects_str += line
            line = file_object.readline()
          objects_str += line
 
          # filter the unnecessary characters from the objects data         
          objects_str = objects_str.replace("OBJECTS", '') 
          objects_str = objects_str.replace("{", '')
          objects_str = objects_str.replace("}", '')
          # removes extra spacing to make the string more readable
          objects_str = " ".join(objects_str.split())
 
          # split the string around to commas to obtain the list of objects
          objects_list = objects_str.split(",")    
 
          # add the list of objects to our notification-type object
          notifType.objects = objects_list
          line = file_object.readline()
 
        # parse the STATUS section
        if "STATUS" in line:
          status_type = line.replace("STATUS", '')
          status_type = status_type.replace(" ", '')
          status_type = " ".join(status_type.split())
          notifType.status = status_type
          line = file_object.readline()
 
        # parse the DESCRIPTION section
        description_str = ""
        if "DESCRIPTION" in line:
          # TODO: If not ending in ".", we will read the whole file
          line = file_object.readline()
          while '."' not in line:
            description_str += line
            line = file_object.readline()
          description_str += line
          # filter the unnecessary characters from the objects data         
          description_str = description_str.replace('"', '')  
 
          # removes extra spacing to make the string more readable
          description_str = " ".join(description_str.split()) 
 
          # add the list of objects to our notification-type object
          notifType.description = description_str
          line = file_object.readline()
 
        # parse the parent and number section
        reference_str = ""
        if "::=" in line:
          line = line.replace("{", '')
          line = line.replace("}", '')
          line = line.replace("::=", '')
          reference_str = line.split()
 
          notifType.parent = reference_str[0]
          notifType.number = reference_str[1] 
 
        line = file_object.readline()
        continue

      elif "OBJECT-TYPE" in line: # Pulls data relating to OBJECT-TYPE
        # Skips import line
        if ',' in line:
          line = file_object.readline()
          continue

        obj_name = line.replace("OBJECT-TYPE", '').strip()

        # Skips import line if keyword is on its own line
        if len(obj_name) == 0:
          line = file_object.readline()
          continue

        mib = mib_object(obj_name)
        mibList.append(mib)
        line = file_object.readline()

        # Read lines from start until next keyword is found
        while all(word not in line for word in KEYWORDS):
          line = file_object.readline()

        # Loop to read bulk of the data
        while "::=" not in line:
          tmp_string = ""
          curr_keyword = ""

          # Determines which keyword is the next one found
          for x in KEYWORDS:
            if x in line:
              curr_keyword = x
              break

          # Special case, since "MAX-ACCESS" contains keyword "ACCESS"
          if "MAX-ACCESS" in line:
            curr_keyword = "MAX-ACCESS"
          tmp_string = line
          line = file_object.readline()

          # Reads and stores all lines until next keyword is found
          while all(word not in line for word in KEYWORDS):
            tmp_string += line
            line = file_object.readline()
          tmp_string = " ".join(tmp_string.split())

          # Handles written data according to which preceding keyword was found
          if curr_keyword == "SYNTAX":
            mib.syntax = tmp_string.replace("SYNTAX", '').strip()
          elif curr_keyword == "UNITS":
            mib.description = "Units:" + tmp_string.replace("UNITS", '').strip()[1:-1] + "\n"
          elif curr_keyword == "MAX-ACCESS":
            mib.access = tmp_string.replace("MAX-ACCESS", '').strip()
          elif curr_keyword == "ACCESS":
            mib.access = tmp_string.replace("ACCESS", '').strip()
          elif curr_keyword == "DESCRIPTION":
            mib.description += tmp_string.replace("DESCRIPTION", '').strip()[1:-1]

        # Handles last line of "OBJECT-TYPE" entry
        if "::=" in line:
          parent = ""
          parent = line.replace("{", '')
          parent = parent.replace("}", '')
          parent = parent.replace("::=", '')
          parent = parent.split()
          mib.parent = parent[0]
          mib.number = parent[1]
          line = file_object.readline()

      else: # Not beginning of any new object, skip line
        line = file_object.readline()  

  # This return statement is not needed since all the needed lists are filled just by running this function
  return mibList, objIdentifierList, notificationTypeList, notificationGrpList, moduleIdentityList

def interpretFile(filePath):
  mibList, objIdentifierList, notificationTypeList, notificationGrpList, moduleIdentityList = parseFile(filePath)

  # Creating the dictionaries which will be used to create the OIDs
  allObjectsDict = defaultdict(str)
  createAllObjectsDict(allObjectsDict, mibList)
  createAllObjectsDict(allObjectsDict, objIdentifierList)
  createAllObjectsDict(allObjectsDict, notificationTypeList)
  createAllObjectsDict(allObjectsDict, notificationGrpList)
  createAllObjectsDict(allObjectsDict, moduleIdentityList)

  tmp_obj = mib_generic("root")
  tmp_obj.name = "enterprises"
  tmp_obj.number = "1.3.6.1.4.1"
  allObjectsDict["enterprises"] = tmp_obj

  tmp_obj = mib_generic("root")
  tmp_obj.name = "private"
  tmp_obj.number = "1.3.6.1.4"
  allObjectsDict["private"] = tmp_obj

  # Used to gather all the object names
  nameList = []
  for obj in allObjectsDict:
    nameList.append(obj)
  
  
  ### ------- This is the list object that contains what will be rendered in the UI -------- ###
  oidList_UI = []
  ### ------------- ###

  # Creates list of only OBJECT-TYPE objects
  # TODO NOTIFICATION-TYPE objects for alarms and others
  for mib in mibList:
    # Creates the OID number and OID number parent/word version
    currOid = obj_to_data(mib)

    currOid.number, currOid.oid_name = fillOid(mib, allObjectsDict)

    oidList_UI.append(currOid)
  
  return oidList_UI
'''
# All of the MIB file paths used for testing
MibFilePath_Anthony  = "/Users/anthonyimmenschuh/Documents/university/capstone/CapstoneFAA2022/FOTS MIBs/vpwrDcPowerNIC2001.mib"
MibFilePath_Power  = "/Users/anthonyimmenschuh/Documents/university/capstone/CapstoneFAA2022/FOTS MIBs/EltekEnexusPowersystem_branch10_rev69.mib"
MibFilePath_Stephen = "C:/Users/steph/School/CS 4273/Package for Capstone Group/FOTS MIBs/LOOP-O9500R-PTN-V2.03.03.MIB"
MibFilePath_LOOP = "/Users/anthonyimmenschuh/Documents/university/capstone/CapstoneFAA2022/FOTS MIBs/LOOP-O9500R-PTN-V2.03.03.MIB"
MibFilePath_Eltek = "/Users/anthonyimmenschuh/Documents/university/capstone/CapstoneFAA2022/FOTS MIBs/Eltek_Root.mib"

# This loop is just for testing output
for i in interpretFile(MibFilePath_Stephen):
  i.oid_print()
'''