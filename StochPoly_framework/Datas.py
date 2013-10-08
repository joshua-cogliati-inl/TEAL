'''
Created on Feb 16, 2013

@author: alfoa
'''
from __future__ import division, print_function, unicode_literals, absolute_import
import warnings
warnings.simplefilter('default',DeprecationWarning)
if not 'xrange' in dir(__builtins__):
  xrange = range

import xml.etree.ElementTree as ET
from BaseType import BaseType
from Csv_loader import CsvLoader as ld
import DataBases
#from hdf5_manager import hdf5Manager as AAFManager
#import h5py as h5


class Data(BaseType):
  def __init__(self):
    BaseType.__init__(self)
    self.inputs  = []   # input  parameters
    self.outputs = []   # output parameters
    self.inpParametersValues   = {}  # input parameters as keys, corresponding values 
    self.outParametersValues   = {}  # output variables as keys, corresponding values
    self.toLoadFromList = []
  
  def readMoreXML(self,xmlNode):
    self.inputs  = xmlNode.find('Input' ).text.strip().split(',')
    self.outputs = xmlNode.find('Output').text.strip().split(',')
    try:self.hist_name = xmlNode.find('Input' ).attrib['name']
    except:self.hist_name = None
    try:
      time = xmlNode.attrib['time']
      if time == 'end' or time == 'all':
        self.time = time 
      else:
        try: self.time = float(time)
        except:self.time = float(time.split(','))
    except:self.time = None

  def addInitParams(self,tempDict):
    for i in range(len(self.inputs)): 
      tempDict['Input_'+str(i)] = self.inputs[i]
    for i in range(len(self.outputs)): 
      tempDict['Output_'+str(i)] = self.outputs[i]
    tempDict['Time'] = self.time
    return tempDict

#  def finalize(self):
#    pass 

  def addOutput(self,toLoadFrom):
    # this function adds the file name/names to the
    # filename list
    print('DATAS       : toLoadFrom -> ')
    print(toLoadFrom)
    
    self.toLoadFromList.append(toLoadFrom)
    return

  def getInpParametersValues(self):
    return self.inpParametersValues  

  def getOutParametersValues(self):
    return self.outParametersValues 
  
  def getParam(self,typeVar,keyword):
    if typeVar == "input":
      if keyword in self.inpParametersValues.keys():
        return self.inpParametersValues[keyword]
      else:
        raise Exception("parameter " + keyword + 
              " not found in inpParametersValues dictionary. Function: Data.getParam")    
    elif typeVar == "output":
      if keyword in self.outParametersValues.keys():
        return self.outParametersValues[keyword]    
      else:
        raise Exception("parameter " + keyword + 
              " not found in outParametersValues dictionary. Function: Data.getParam")
    else:
      raise Exception("type " + typeVar + " is not a valid type. Function: Data.getParam")

class TimePoint(Data):
  def addOutput(self,toLoadFrom):
    Data.addOutput(self, toLoadFrom)
    try:
      typeVar = self.toLoadFromList[0].type
      if typeVar == "HDF5":
        attributes = {}
        attributes['type']     = "TimePoint"
        attributes['outParam'] = self.outputs
        attributes['inParam' ] = self.inputs
        attributes['filter'  ] = "whole"
        if(not self.hist_name): raise IOError('DATAS     : ERROR: In order to create an history data, a history name must be provided')
        attributes['history'] = self.hist_name
        if self.time: attributes['time']  = self.time
        else:attributes['time']='end'
        tupleVar = self.toLoadFromList[0].retrieveData(attributes)
        self.inpParametersValues = tupleVar[0]
        self.inpParametersValues = tupleVar[1]
    except:
      tupleVar = ld().csvLoaderForTimePoint(self.toLoadFromList[0],self.time,self.inputs,self.outputs)
      self.inpParametersValues = tupleVar[0]
      self.outParametersValues = tupleVar[1]
    
class TimePointSet(Data):
  def addOutput(self,toLoadFrom):
    Data.addOutput(self, toLoadFrom)
    try:
      typeVar = self.toLoadFromList[0].type
      if typeVar == "HDF5":
        attributes = {}
        attributes['type']     = "TimePointSet"
        attributes['outParam'] = self.outputs
        attributes['inParam' ] = self.inputs
        attributes['filter'  ] = "whole"
        if self.time: attributes['time']  = self.time
        else:attributes['time']='end'
        #  Retrieve the ending groups' names
        attributes['histories'] = self.toLoadFromList[0].getEndingGroupNames()
        tupleVar = self.toLoadFromList[0].retrieveData(attributes)
        self.inpParametersValues = tupleVar[0]
        self.outParametersValues = tupleVar[1]
      #add here the specialization for loading from other source
    except:      
      tupleVar = ld().csvLoaderForTimePointSet(self.toLoadFromList,self.time,self.inputs,self.outputs)
      self.inpParametersValues = tupleVar[0]
      self.outParametersValues = tupleVar[1]

class History(Data):
  def addOutput(self,toLoadFrom):
    Data.addOutput(self, toLoadFrom)
    try:
      typeVar = self.toLoadFromList[0].type
      if typeVar == "HDF5":
        attributes = {}
        attributes['type']     = "History"
        attributes['outParam'] = self.outputs
        attributes['inParam' ] = self.inputs
        attributes['filter'  ] = "whole"
        if(not self.hist_name): raise IOError('DATAS     : ERROR: In order to create an history data, a history name must be provided')
        attributes['history'] = self.hist_name
        tupleVar = self.toLoadFromList[0].retrieveData(attributes)
        self.inpParametersValues = tupleVar[0]
        self.inpParametersValues = tupleVar[1]
    except:      
      tupleVar = ld().loader.csvLoaderForHistory(self.toLoadFromList[0],self.time,self.inputs,self.outputs)
      self.inpParametersValues = tupleVar[0]
      self.outParametersValues = tupleVar[1]

class Histories(Data):
  def __init__(self):
    Data.__init__(self)

  def addOutput(self,toLoadFrom):
    Data.addOutput(self, toLoadFrom)
    try:
      typeVar = self.toLoadFromList[0].type
      if typeVar == "HDF5":
        attributes = {}
        attributes['type']     = "History"
        attributes['outParam'] = self.outputs
        attributes['inParam' ] = self.inputs
        attributes['filter'  ] = "whole"
        #if self.time: attributes['time']  = self.time
        #  Retrieve the ending groups' names
        endGroupNames = self.toLoadFromList[0].getEndingGroupNames()
        #  Construct a dictionary of all the histories
        for index in range(len(endGroupNames)):
          attributes['history'] = endGroupNames[index]
          tupleVar = self.toLoadFromList[0].retrieveData(attributes)
          self.inpParametersValues[index] = tupleVar[0]
          self.outParametersValues[index] = tupleVar[1]
    except:  
      loader = ld()
      print(xrange(len(self.toLoadFromList)))
      for index in xrange(len(self.toLoadFromList)):
        tupleVar = loader.csvLoaderForHistory(self.toLoadFromList[index],self.time,self.inputs,self.outputs)
        # dictionary of dictionary key = i => ith history ParameterValues dictionary
        self.inpParametersValues[index] = tupleVar[0]
        self.outParametersValues[index] = tupleVar[1]
        
        del tupleVar
    return
   
def returnInstance(Type):
  base = 'Data'
  InterfaceDict = {}
  InterfaceDict['TimePoint'   ] = TimePoint
  InterfaceDict['TimePointSet'] = TimePointSet
  InterfaceDict['History'     ] = History
  InterfaceDict['Histories'   ] = Histories
  try:
    if Type in InterfaceDict.keys():
      return InterfaceDict[Type]()
  except:
    raise NameError('not known '+base+' type'+Type)
  
  
  