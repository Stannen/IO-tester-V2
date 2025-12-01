from datetime import datetime
import os
import pandas as pd
import numpy as np 
import csv 
import yaml

def dirOperator(path, make=True, returnList=False):
    ''' make=False (return True if path is correct else False) 
        make=True (if folder is not avaible make a new folder 
        returnList=True and Make=False (return list of all the folders)'''        
    
    if make:
        splitedPath = path.split('/')
        scanPath = '' 

        for i in range(0, len(splitedPath)):
            if i == 0: scanPath = splitedPath[i]               
            else: scanPath += f'/{splitedPath[i]}'
                
            if not os.path.isdir(scanPath):
                os.mkdir(scanPath)  

    elif returnList:
        if os.path.isdir(path):
            return os.listdir(path) 
        else:
            return [] 
    else:
        return os.path.isdir(path) 
      

def fileOperator(path, returnList=False, deleteExtension=True):
    ''' returnList=False (check if file exist)
        returnList=True (return list of files)'''

    if returnList:
        if os.path.exists(path):
            returnData = [] 
            for root, dirs, files in os.walk(path):   
                if not path == root:
                    continue                
                
                if deleteExtension:
                    for select in files:
                        str_len = len(select)
                        for i in range(str_len):
                            if select[str_len - (i+1)] == '.':
                                returnData.append(select[:str_len-(i+1)])
                                break 
                         
                else:
                    for select in files:     
                        returnData.append(select) 
            return returnData

    else:
        return os.path.isfile(path)


def SeriesOperator(filePath, series=None): 
    ''' series=None (load series)
        series=not None (save series)'''

    if not filePath.count('/') > 0 or not filePath.count('.') == 1:
        return None 
        
    path, extension = filePath.split('.')
    fileName = path.split('/')[-1]
    path = path.replace(f'/{fileName}', '')

    if extension == 'csv' or extension == 'npy':
        if series == None:   
            if not os.path.isfile(filePath):     
                return False
            returnData = None 

            if extension == 'csv':
                returnData = []
                
                with open(filePath,'r') as file:
                    csvFile = csv.reader(file)
                    
                    for row in csvFile:
                        returnData.append([veld.strip() for veld in row])                       
                
            elif extension == 'npy':
                returnData = np.load(filePath, allow_pickle=True)
                returnData = np.array(returnData)
                
            return returnData

        else:
            if not os.path.isdir(path):
                dirOperator(path)
                print('path bestaat niet')           
                     
            if extension == 'csv':    
                with open(filePath, 'w', newline='') as file:      
                    csvFile = csv.writer(file)
                    
                    for row in series:   
                        try:
                            csvFile.writerow([veld.strip() for veld in row])       
                        except:
                            csvFile.writerow(row)       
                            
            elif extension == 'npy':
                np.save(filePath, np.array(series, dtype=object), allow_pickle=True)
                            
            if not os.path.isfile(filePath):
                print('file is niet aangemaakt')
                return None  


def yamlOperator(path, fileName, data=None): 
    ''' series=None (load series)
        series=not None (save series)
        
        extension=csv 
        extension=npy'''

    if fileName.count('.') == 0:
        fileName += '.yaml'

    filePath = f'{path}/{fileName}'

    if data == None:
        if not os.path.isfile(filePath):
            return None 
        
        with open(filePath, 'r') as file:
            return yaml.safe_load(file)  

    else:
        with open(filePath, 'w') as file:
            yaml.dump(data, file)


def modelConfigFile(socket):
    data = dict() 
    
    data["instrument"] = socket.instrument
    
    indicatorArray = [] 
    instrumentArray = [] 

    for select in socket.indicator.info:
        subArray = []
        
        subArray.append(select.id)
        subArray.append(select.type)
        subArray.append(select.value)
        
        indicatorArray.append(subArray)
        
    for select in socket.instrument.info:
        subArray = []
        subArray.append(select.type)
        subArray.append(select.value)
        
        instrumentArray.append(subArray)

    data["indicators"] = indicatorArray
    data["types"] = instrumentArray 
    

def create_datetime(bars, index):
    year  = bars.loc[index, 'year']
    month = bars.loc[index, 'month']
    day   = bars.loc[index, 'day']
    hour  = bars.loc[index, 'hour']
    minute= bars.loc[index, 'minute']
    return datetime(int(year), int(month), int(day), int(hour), int(minute))




def drawObject(drawSeries, drawType, tag='', beginBarsAgo=0, endBarsAgo=0, startY=0.0, endY=0.0, color='Red'):
    draw_columns = ["drawType", "tag", "startBarsAgo", "endBarsAgo", "startY", "endY", "color"]
   
    df = pd.DataFrame(data=[[drawType.value, tag, beginBarsAgo, endBarsAgo, startY, endY, color]], columns=draw_columns)

    if len(drawSeries[draw_columns[0]]) == 0:
        drawSeries = df 
    else:   
        drawSeries = pd.concat([drawSeries, df])

    return drawSeries


def checkEnum(Enum, enumState):
    check = False 
                      
    if type(enumState) == str:
        check = Enum.name == enumState
            
    elif type(enumState) == int:
        check = Enum.value == enumState 
    else: 
        check = Enum.value == enumState.value
    return check 


def formatOperator(format, formatItems=None, formatToDecrypt=None):
    formatItemList, formatSpaceList = [], []
    itemStartIndex, itemEndIndex, index = [], [], 0 
    item, space, enable = '', '', False 
    

    for char in format:
        if char == '%':
            if enable == False:
                formatSpaceList.append(space)
                itemStartIndex.append(index)
                space = ''
                enable = True 
            else:
                formatItemList.append(item)
                itemEndIndex.append(index)
                item = ''
                enable = False 
                
        elif enable:
            item += char
            
        else:
            space += char
        index += 1 
            

    returnData = None 
    if not formatItems == None:
        returnData = '' 
        
        logic = len(formatItemList) > len(formatSpaceList)
        itemIndex, spaceIndex = 0, 0    
        
        for i in range(len(formatItemList) + len(formatSpaceList)):
           
            if logic:
                returnData += str(formatItems[formatItemList[itemIndex]])
                itemIndex +=1 
                logic = False 
            else:
                returnData += formatSpaceList[spaceIndex]
                spaceIndex +=1
                logic = True 
        
    elif not formatToDecrypt == None:
        returnData = dict()
        decryptedData = [] 
        
        index, listIndex, decryptValue, inRange = 0, 0, '', False 
        for char in formatToDecrypt:
            
            if index > itemStartIndex[listIndex] and index < formatItemList[listIndex]:
                decryptValue += char 
                inRange = True 
                
            elif inRange:
                listIndex += 1 
                decryptedData.append(decryptValue)
                decryptValue = '' 
                inRange = False 
  
            index += 1 
            
        for item in formatItemList:
            returnData[item] = decryptedData[formatItemList.index(item)]
        
    else:
        returnData = formatItemList
               
    return returnData