# -*- coding: utf-8 -*-
import os, sys
import wx
import exifread
import glob


# some global variables
inDir = ""
currDir = os.getcwd()
outFile = ""
kmlFile = ""
kml=False
csv=False

# KML header, trailer, and template for placemark
kml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"  xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom ">
<Folder>
'''
place_mark = '''<Placemark>  
  <name>{}</name>  
  <description>{} 
    <p><img alt="" src="images/{}" width="{}" height="{}" /></p> 
  </description> 
  <Point>  
    <coordinates>{},{},0</coordinates>  
  </Point>  
</Placemark>  
'''

kml_trailer = '''</Folder>
</kml>
'''

#---------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        #create a Frame
        wx.Frame.__init__(self, parent=None, id=wx.ID_ANY, title="EXIF Reader", size=(540,570),
                style = wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX ^ wx.RESIZE_BORDER)

        self.SetIcon(wx.Icon('IMG_2161.ico', wx.BITMAP_TYPE_ICO))


                
        # create a Panel
        panel = wx.Panel(self, wx.ID_ANY)
        
        wx.StaticText(parent=panel, label="輸入資料夾 ", pos=(10,10))
        self.a = wx.TextCtrl(parent=panel,pos=(90,10),size=(340,20))
        self.btn1 = wx.Button(parent=panel,label="選擇檔案",pos=(450,10),size=(80,20))
        self.Bind(wx.EVT_BUTTON, self.OnBtn1, self.btn1)

        wx.StaticText(parent=panel, label="輸出資料檔 ", pos=(10,40))
        self.b = wx.TextCtrl(parent=panel,pos=(90,40),size=(340,20))
        self.btn2 = wx.Button(parent=panel,label="選擇檔案",pos=(450,40),size=(80,20))
        self.Bind(wx.EVT_BUTTON, self.OnBtn2, self.btn2)

        wx.StaticText(parent=panel, label="欲轉換格式 ", pos=(10,70))
        # self.cb1 = wx.CheckBox(panel, label = 'csv',pos = (90,70)) 
        # self.cb2 = wx.CheckBox(panel, label = 'kml',pos = (150,70)) 
        # self.Bind(wx.EVT_CHECKBOX,self.onChecked) 
        # self.Centre() 
        # self.Show(True) 
        self.rb1 = wx.RadioButton(panel, label = 'csv',pos = (90,70), style = wx.RB_GROUP) 
        self.rb2 = wx.RadioButton(panel, label = 'kml',pos = (150,70)) 
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadiogroup) 

        self.txtCtrl = wx.TextCtrl(panel, id=wx.ID_ANY, style=wx.TE_MULTILINE, pos=(10,100), size=(520,390))

        self.btn3 = wx.Button(parent=panel,label=" Clear",pos=(10,510),size=(50,20))
        self.Bind(wx.EVT_BUTTON, self.OnBtn3, self.btn3)

        self.btn4 = wx.Button(parent=panel,label=" Convert ",pos=(465,510),size=(65,20))
        self.Bind(wx.EVT_BUTTON, self.OnBtn4, self.btn4)


    def OnBtn1(self, evt):
        global inDir
        dlg = wx.DirDialog(
            self, message="選擇輸入資料夾:",
            style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
            )
                     
        # If the user selects OK, then we process the dialog's data.
        # This is done by getting the path data from the dialog - BEFORE
        # we destroy it. 
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            path = dlg.GetPath()
            self.a.SetValue(path)
            inDir = self.a.GetValue()
            inDir = inDir.replace('\\', '/')
            
        # Only destroy a dialog after you're done with it.
        dlg.Destroy()

    def OnBtn2(self, evt):
        global outFile
        
        # Choose the output file. 
        dlg = wx.FileDialog(
            self, message="選擇輸出資料檔:",
            defaultDir=currDir, 
            defaultFile="",
            wildcard="*.csv",
            style= wx.FD_OVERWRITE_PROMPT | wx.FD_SAVE
            )
                     
        # If the user selects OK, then we process the dialog's data.
        # This is done by getting the path data from the dialog - BEFORE
        # we destroy it. 
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            path = dlg.GetPath()
            self.b.SetValue(path)
            outFile = self.b.GetValue()
            outFile = outFile.replace('\\', '/')
            
        # Only destroy a dialog after you're done with it.
        dlg.Destroy()

    def OnBtn3(self, evt):
        
        self.txtCtrl.Clear()

    def OnBtn4(self, evt):
        
        try:
            result=self.read_exif()
            if result==0:
                self.txtCtrl.WriteText('失敗!\n')
            else:
                self.txtCtrl.WriteText('成功!\n')
        except:
            self.txtCtrl.WriteText('失敗!\n')
            print('ERROR')


    # def onChecked(self, e):
    #     global csv,kml

    #     cb = e.GetEventObject()
    #     print(cb.GetLabel(),' is clicked',cb.GetValue())
    #     if cb.GetLabel()=="kml" and cb.GetValue()==True:
    #         kml=True
    #     else:
    #         kml=False
    #     if cb.GetLabel()=="csv" and cb.GetValue()==True:
    #         csv=True
    #     else:
    #         csv=False
    def OnRadiogroup(self, e): 
        global csv,kml

        cb = e.GetEventObject()
        print(cb.GetLabel(),' is clicked',cb.GetValue())
        if cb.GetLabel()=="kml" and cb.GetValue()==True:
            kml=True
        else:
            kml=False
        if cb.GetLabel()=="csv" and cb.GetValue()==True:
            csv=True
        else:
            csv=False


        
    def read_exif(self):
        global kmlFile, outFile,kml,csv


        kmlFile = outFile[:-3] + 'kml'
            
        img_list = glob.glob('%s/*.jpg' % inDir)
        
        num_img = len(img_list)
        
        
        if num_img == 0:
            self.txtCtrl.WriteText('cannot find JPG file!\n')
            return 0

        if csv==True:
            fout = open(outFile, 'w')
            header = 'Name,DateTime,Longtitude,Latitude,ImageWidth,ImageLength,Orientation\n'
            fout.write(header)

        if kml==True:
            kml_out = open(kmlFile, 'w')
            kml_out.write(kml_header)
        
        for i in range(num_img):
            basename = os.path.basename(img_list[i])
            
            tags = exifread.process_file(open(img_list[i],'rb'))
            time = tags['Image DateTime']
            width = int(str(tags['EXIF ExifImageWidth']))
            height = int(str(tags['EXIF ExifImageLength']))
            new_w = int(width / 10)
            new_h = int(height / 10)
            Orientation=tags['Image Orientation']
            
            
            try:
                lat_str = str(tags['GPS GPSLatitude'])
                lat = format_lat_lon(lat_str)
                lon_str = str(tags['GPS GPSLongitude'])
                lon = format_lat_lon(lon_str)
                
                data = '{},{},{},{},{},{},{}\n'.format(basename, time, lon, lat,width,height,Orientation)
                if kml==True:
                    kml_out.write(place_mark.format(basename,basename,basename,new_w,new_h,lon,lat))
            except:
                self.txtCtrl.WriteText('%s has no GPS info\n' % basename)
                data = '{},{}\n'.format(basename, time)
                

            if csv==True:
                fout.write(data)
        if csv==True:
            fout.close()

        if kml==True:
            kml_out.write(kml_trailer)
            kml_out.close()

#---------------------------------------------------------------------------

def format_lat_lon(data):
    t = data.replace('[', '').replace(']', '').split(',')
    dd = float(t[0].strip())
    mm = float(t[1].strip()) / 60
    s = t[2].strip().split('/')
    ss = float(s[0]) / float(s[1]) / 3600
    
    result = dd + mm + ss
    return result

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
    
#---------------------------------------------------------------------------

# Every wxWidgets application must have a class derived from wx.App
class MyApp(wx.App):

    # wxWindows calls this method to initialize the application
    def OnInit(self):

        # Create an instance of our customized Frame class
        frame = MyFrame(None, -1, "Create Worldfile")
        frame.Show(True)

        # Tell wxWindows that this is our main window
        self.SetTopWindow(frame)

        # Return a success flag
        return True
        
#---------------------------------------------------------------------------
    
if __name__ == '__main__':
    app = MyApp(0)
    app.MainLoop()

