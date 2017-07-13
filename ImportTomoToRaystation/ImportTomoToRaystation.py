import wpf
import glob
import dicom as dcm
import sys
import clr
import collections as cols
from operator import attrgetter


#clr.AddReference("System.Windows.Wpf")
clr.AddReference("System.Windows.Forms")

from System.Windows.Forms import Application, Form, StatusBar, ToolBar, ToolBarButton, FolderBrowserDialog, DialogResult

from System.Windows import Application, Window
from System.Windows.Controls import ListBox, ListBoxItem, TextBlock


#set variables
#default path
path = r"D:\\"


class MyWindow(Window):
    def __init__(self):
        wpf.LoadComponent(self, 'ImportTomoToRaystation.xaml')

        
    

    #get the files, organize the patients in container class
    #puplate unique patients. filter out dqa plans. Warn for uncomplete files
    #using uids
    def populateList(self):
        files = glob.glob(self.path +'*.dcm')
        self.patsort = Patients(files)
        self.patsort.ReadFiles()
        defpatlistsorted = self.patsort.SortDicomInfo()

        #sort on id in listbox
        for id, patlist in defpatlistsorted:

            list_item = ListBoxItem()
            list_item.FontFamily = TextBlock.FontFamily("Courier New")
            list_item.FontSize = 14
            list_item.Content = id.strip()
            
            #add to listbox
            self.listBoxPatients.Items.Add(list_item)
       
        



    def MenuPath_Click(self, sender, e):
        dialog = FolderBrowserDialog()
        result = dialog.ShowDialog()

        if result == result.OK:
            self.path = dialog.SelectedPath

        
        pass
    
    def LoadButton_Click(self, sender, e):
        populateList()
        
    

#takes list of filepaths, order and orginize the patients
class Patients:
    files = []
    #namedtuple to hold the dicominfo
    dcmpatients = cols.namedtuple('dcmpatients', 'id name dcmtype path sopuid seriesuid foruid')
    defpatientlist= cols.defaultdict(list)
    patientlist = {}
    planuid = {}
    dcmfiles = {}

    def __init__(files):
        self.files = files
   
    #read all the files, store uids, filename/path, type.
    def ReadFiles(self):
        
        for file in self.files:
            self.dcmfiles[file]= dcm.read_file("path", stop_before_pixels=True)

        #put the files based on dicominfo   in container 
        for temppath,dcmfile in dcmfiles.iteritems():
            #differnet places for different modalities?
            if dcmfile.Modality=='CT':
                tempid=dcmfile.PatientID
                tempname=dcmfile.PatientName
            
                tempmod=dcmfile.Modality
                tempsop=dcmfile.SOPInstanceUID
                tempsuid=dcmfile.SeriesInstanceUID
                tempforuid=dcmfile.FrameOfReferenceUID
            if dcmfile.Modality=='RP':
                planuid[tempid]= FrameOfReferenceUID
    
            #in tuplecollection
            pattemp = self.dcmpatients(id=tempid , name=tempname,dcmtype=tempmod,path=temppath, sopuid=tempsop, seriesuid=tempsuid, foruid=tempforuid)
            #self.patientlist.append(pattemp)
            #holds the patients with lists under id as key
            self.defpatientlist[tempid].append(pattemp)

   #sorts the dicom info
    def SortDicomInfo(self):
        #sort_by_id= sorted(self.patientlist, key=attrgetter('id'))

        #check for unique values, true if all same
        def checkEqual(lst):
            return lst[1:] == lst[:-1]
        #get unique ids
        ids= []
        #only unique ids
        junk=[ids.append(x.id) for x in patientlist if not x.id in ids ]
        
        #check if patients have all modalities
        for id,patlist in self.defpatientlist.iteritems():
            suid = []
            foruid = []
            reppatlist = []

             #chech if all files are connected, frame
            #only files with same uid as plans
            temppats = [pat for pat in patlist if pat.foruid == planuid[id]]
                
               
            self.defpatientlist[id] = temppats
        #returns a defualtdict with list of namedtuple, each tuple a file with same
        #frame of reference and id as the plan with same id. contains for,sop, path, id, name, type
        return self.defpatientlist      
           
                
            
 
           

        


if __name__ == '__main__':
    Application().Run(MyWindow())
