#! /usr/bin/python
# -*- coding: utf-8 -*-

import wx
import os
import wx.lib.mixins.rubberband
try:
    from PIL import Image
except ImportError:
    try:
        import Image
    except ImportError:
        Image = None
        print 'Python Imaging Library (PIL or Pillow) is required'
print wx.version()

class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MainFrame, self).__init__(*args, **kwargs)
        
        #Controls
        mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        
        vsizer = wx.BoxSizer(wx.VERTICAL)
        self.panel = wx.Panel(self)
        self.pil_img = wx.NullBitmap
        self.staticbmp = wx.StaticBitmap(self.panel, wx.ID_ANY, self.pil_img)
        vsizer.Add(self.panel, -1, wx.EXPAND|wx.ALIGN_CENTER)
        
        mainsizer.Add(vsizer, -1, wx.EXPAND|wx.ALL, 5)
        
        grid = wx.FlexGridSizer(2, 0, 0, 0)
        
        tsize = (52, 52)
        open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN,
                                            wx.ART_TOOLBAR, tsize)
        next_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD,
                                            wx.ART_TOOLBAR, tsize)
        rotate_bmp = wx.ArtProvider.GetBitmap(wx.ART_REDO,
                                              wx.ART_TOOLBAR, tsize)
        save_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS,
                                            wx.ART_TOOLBAR, tsize)
        close_bmp= wx.ArtProvider.GetBitmap(wx.ART_QUIT,
                                            wx.ART_TOOLBAR, tsize)
        
        tb = wx.ToolBar(self, style=wx.TB_VERTICAL
                                    |wx.TB_RIGHT
                                    |wx.NO_BORDER
                                    |wx.TB_FLAT
                                    )
        
        tb.SetToolBitmapSize(tsize)
        
        tb.AddLabelTool(1, 'Abrir', open_bmp, shortHelp='Abrir')
        tb.AddLabelTool(2, 'Siguiente', next_bmp, shortHelp='Siguiente')
        tb.AddLabelTool(3, 'Rotar', rotate_bmp, shortHelp='Rotar')
        tb.AddLabelTool(4, 'Guardar', save_bmp, shortHelp='Guardar')
        tb.Realize()
        
        tb2 = wx.ToolBar(self, style=wx.TB_VERTICAL
                                    |wx.TB_RIGHT
                                    |wx.NO_BORDER
                                    |wx.TB_FLAT
                                    )
        tb2.SetToolBitmapSize(tsize)
        tb2.AddLabelTool(5, 'Salir', close_bmp, shortHelp='Salir')        
        tb2.Realize()
        
        grid.AddMany([(tb, 0, wx.EXPAND), (tb2, 0)])
        grid.AddGrowableRow(0, 0)

        mainsizer.Add(grid, 0, wx.EXPAND)
        
        self.SetSizer(mainsizer)
        
        self.statusBar = self.CreateStatusBar(2)
        self.statusBar.SetStatusWidths([-4, -1])
        
        #Event binding
        self.Bind(wx.EVT_TOOL, self.OnFilesDialog, id=1)
        self.Bind(wx.EVT_TOOL, self.OnNextFile, id=2)
        self.Bind(wx.EVT_TOOL, self.OnRotateRight, id=3)
        self.Bind(wx.EVT_TOOL, self.OnSaveThumbnail, id=4)
        self.Bind(wx.EVT_TOOL, self.OnClose, id=5)
        self.panel.Bind(wx.EVT_SIZE, self.OnEvtSize)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        #Properties
        self.pil_img = None
        self.zoom = 1
        self.rubberband = wx.lib.mixins.rubberband.RubberBand(self.staticbmp)
        self.img_path = os.getcwd()
        self.save_path = self.img_path
        self.target_size = (100, 100)
        self.index = 0
        
        #Frame size and layout
        self.SetSizeHints(450,450)
        self.Maximize(True)
        self.Layout()
        
        wx.CallAfter(self.FilesDialog)
        
    def pil_to_wximage(self, pil, alpha=True):
        """ Method will convert PIL Image to wx.Image """
        if alpha:
            wximage = apply( wx.EmptyImage, pil.size )
            try:
                wximage.SetData( pil.convert( "RGB").tobytes() )
                wximage.SetAlphaData(pil.convert("RGBA").tobytes()[3::4])
            except:
                wximage.SetData( pil.convert( "RGB").tostring() )
                wximage.SetAlphaData(pil.convert("RGBA").tostring()[3::4])
        else:
            wximage = wx.EmptyImage(pil.size[0], pil.size[1])
            new_wximage = pil.convert('RGB')
            try:
                data = new_wximage.tobytes()
            except:
                data = new_wximage.tostring()
            wximage.SetData(data)
        return wximage
    
    def pil_thumb_S1(self, pil_img, (target_w, target_h)):
        ''' Devuelve una copia de la imagen escalada en calidad normal,
            manteniendo sus proporciones, usando la libreria PIL '''
        temp = pil_img.copy()
        temp.thumbnail((target_w, target_h))
        return temp
    
    def pil_thumb_S2(self, pil_img, (target_w, target_h)):
        ''' Devuelve la imagen pil_img escalada en calidad ANTIALIAS
            manteniendo sus proporciones, usando la libreria PIL '''
        pil_img.thumbnail((target_w, target_h, Image.ANTIALIAS))
        return pil_img
    
    def SetSaveProperties(self, save_path, target_size):
        self.save_path = save_path
        self.target_size = target_size
        
    def GetSaveProperties(self):
        return self.save_path, self.target_size
        
    def OnFilesDialog(self, evt):
        self.FilesDialog()
        
    def FilesDialog(self):
        wildcard = "All files (*.*)|*.*"
        dialog = wx.FileDialog(None, "Choose a file",
                               os.path.dirname(self.img_path),
                               "", wildcard,
                               wx.FD_MULTIPLE|wx.FD_FILE_MUST_EXIST
                               #wx.OPEN
                               )
        if dialog.ShowModal() == wx.ID_CANCEL:
            return
        
        self.files = dict(enumerate(dialog.GetPaths()))
        self.index = 0
        self.OnLoadImage(self.index)
            
    def OnLoadImage(self, index):
        self.ClearAll()
        self.img_path = self.files[index]
        try:
            file = open(self.img_path, 'rb')
        except IOError:
            msg = u'No se puede acceder el archivo\n{}'.format(self.img_path)
            wx.MessageDialog(self, msg, 'Error de lectura',
                             wx.OK | wx.ICON_ERROR).ShowModal()
            wx_img = wx.NullBitmap
        except MemoryError:
            msg = u'''El sistema se ha quedado sin memoria al intentar abrir\n{}
                   '''.format(self.img_path)
            wx.MessageDialog(self, msg, 'Error de memoria',
                             wx.OK | wx.ICON_ERROR).ShowModal()
            wx_img = wx.NullBitmap
            
        else:
            try:
                self.pil_img = Image.open((file))
                wx_img = wx.BitmapFromImage(self.pil_to_wximage(self.pil_img))
            except:
                msg = u'Formato de archivo incorrecto\n{}'.format(self.img_path)
                wx.MessageDialog(self, msg, 'Error',
                                wx.OK | wx.ICON_ERROR).ShowModal()
                wx_img = wx.NullBitmap
            
        self.staticbmp.SetBitmap(wx_img)
        #self.Fit()
        self.Layout()
        text = u'{} - {}/{}'.format(self.img_path, index + 1, len(self.files))
        self.statusBar.SetStatusText(text, 0)
            
    def OnNextFile(self, evt):
        if self.index + 1 in self.files.keys():
            self.index += 1
            
        else:
            wx.MessageDialog(self, u'Fin de la lista de archivos', 'Info',
                                   wx.OK | wx.ICON_INFORMATION).ShowModal()
            self.index = 0
            
        self.OnLoadImage(self.index)
        
    def OnSaveThumbnail(self, evt):
        ''' Crea un thumbnail de la seleccion usando la libreria PIL en 2 pasos,
            primero: con el doble de tamaño del target en calidad normal,
            segundo: tamaño del target en calidad ANTIALIAS
            Con esta tecnica se obtiene un thumbnail de mayor calidad,
            sin mermar demasiado la velocidad, en imagenes muy grandes'''
        dlg = SaveDialog(self, -1, 'Guardar miniatura como...', size=(400,400))
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
            
        print 'Guardar como:', self.save_path
        print 'Tamaño del thumb:', self.target_size
        if not self.save_path:
            return
        elif os.path.exists(self.save_path):
            text = u'''El archivo ya existe:\n\n{}\n
¿Desea sobrescribirlo?.'''.format(self.save_path)
            msg = wx.MessageDialog(self, text, 'Sobrescribir',
                                   wx.YES_NO|wx.CANCEL |
                                   wx.ICON_QUESTION).ShowModal()
            if msg == wx.ID_NO or msg == wx.ID_CANCEL:
                self.statusBar.SetStatusText(u'Cancelado, no se ha guardado', 0)
                return
            
        cropped_img = self.GetCroppedImg()
        img_w, img_h = cropped_img.size
        target_w, target_h = self.target_size
        if img_w > target_w * 2 or img_h > target_h * 2:
            #Step 1: Thumb to double target size with low quality
            cropped_img = self.pil_thumb_S1(cropped_img, (target_w, target_h))
        #Step 2: Thumb to target size with hight quality
        thumb = self.pil_thumb_S2(cropped_img, (target_w, target_h))
        # Save file
        self.statusBar.SetStatusText('Guardando...', 0)
        try:
            thumb.save(self.save_path)
        except IOError:
            print "cannot create thumbnail for", self.save_path
            msg = u'''No se puede guardar el archivo:\n\n{}\n
Compruebe la ruta y el nombre de archivo.'''.format(self.save_path)
            wx.MessageDialog(self, msg, 'Error de escritura',
                             wx.OK | wx.ICON_ERROR).ShowModal()
            self.statusBar.SetStatusText(u'Error, no se ha guardado', 0)
        else:
            text = u'Guardado en {}'.format(self.save_path)
            self.statusBar.SetStatusText(text, 0)
        
    def GetCroppedImg(self):
        ''' Devuelve la porcion de imagen original seleccionada,
            o toda si no hay seleccion.
            Y elimina los bordes que excedan las medidas del StaticBitmap '''
        try:
            left, top, right, bottom = self.rubberband.getCurrentExtent()
        except TypeError:
            # None extent = Full size selection
            left, top = 0, 0
            right, bottom = self.staticbmp.GetSize()
        else:
            # Prevents the rubberband to exceed the StaticBitmap
            if left < 0:
                left = 0
            if top < 0:
                top = 0
            if right > self.staticbmp.GetSize()[0]:
                right = self.staticbmp.GetSize()[0]
            if bottom > self.staticbmp.GetSize()[1]:
                bottom = self.staticbmp.GetSize()[1]
        
        cropped_img = self.pil_img.crop((int(left / self.zoom),
                                         int(top / self.zoom),
                                         int(right / self.zoom),
                                         int(bottom / self.zoom)
                                         ))
        return cropped_img
        
    def ClearAll(self):
        # Resets the rubber band and zoom scale
        self.zoom = 1
        self.ClearRB()
        
    def ClearRB(self):
        # Resets the rubber band
        self.rubberband.reset()
        
    def OnEvtSize(self, evt):
        wx.CallAfter(self.ReSize)
        evt.Skip()
        
    def ReSize(self):
        if not hasattr(self.pil_img, 'size'):
            return
        target_w, target_h = self.panel.GetSize()
        img_w, img_h = self.pil_img.size
        if target_w < img_w or target_h < img_h:
            #La imagen no cabe, hay que redimensionarla
            self.zoom = min(float(target_w) / img_w, float(target_h) / img_h)
            thumb = self.pil_thumb_S1(self.pil_img, (target_w, target_h))
            wx_img = self.pil_to_wximage(thumb)
            self.staticbmp.SetBitmap(wx.BitmapFromImage(wx_img))
            self.ClearRB()
        else:
            if self.zoom < 1:
                #Hay q restaurar el tamaño original de la imagen
                wx_img = self.pil_to_wximage(self.pil_img)
                self.staticbmp.SetBitmap(wx.BitmapFromImage(wx_img))
                self.ClearAll()
            
        self.statusBar.SetStatusText(u'Zoom: {}%'.format(
                                                    int(self.zoom * 100)),
                                                    1)
        
    def GetPreviewImg(self, size=(200, 200)):
        ''' Devuelve un preview de la imagen cargada con formato wxpython
            de tamaño (200, 200) y calidad normal '''
        preview = self.pil_thumb_S1(self.GetCroppedImg(), size)
        return self.pil_to_wximage(preview)
            
    def OnRotateRight(self, evt):
        self.ClearRB()
        self.pil_img = self.pil_img.rotate(-90)
        wx_img = self.pil_to_wximage(self.pil_img)
        self.staticbmp.SetBitmap(wx.BitmapFromImage(wx_img))
        self.Layout()
        
    def OnClose(self, evt):
        self.Destroy()
        
        
class SaveDialog(wx.Dialog):
    ''' Custom dialog para la introduccion de la ruta destino del thumbnail
        y su tamaño.
        Obtiene ruta y tamaño inicial del thumb.
        Devuelve ruta y tamaño elegido por el usuario'''
    def __init__(self, parent, *args, **kwargs):
        super(SaveDialog, self).__init__(parent, *args, **kwargs)
        
        self.parent = parent
        self.save_path, target_size = self.parent.GetSaveProperties()
        
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        
        # Path and filename
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, -1,
                              'Nombre de archivo:')
        sizer1.Add(label, 0, wx.EXPAND|wx.ALL, 5)
        h_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.text_path = wx.TextCtrl(self, -1, self.save_path,
                                     style=wx.TE_RIGHT|wx.TE_PROCESS_ENTER,
                                     name='path')
        self.button_path = wx.Button(self, -1, '...')
        h_sizer1.Add(self.text_path, -1)
        h_sizer1.Add(self.button_path, 0)
        sizer1.Add(h_sizer1, -1, wx.EXPAND)
        mainsizer.Add(sizer1, 0, wx.EXPAND|wx.ALL, 5)
        
        # Image preview
        preview = wx.BitmapFromImage(self.parent.GetPreviewImg())
        staticbmp = wx.StaticBitmap(self, wx.ID_ANY, preview, size=(200,200))
        mainsizer.Add(staticbmp, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        
        # Thumbnail target size
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, -1,
                              'Ancho y Alto de la miniatura (en pixeles)',
                              style=wx.TE_CENTER)
        sizer2.Add(label, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        h_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.text_size_w = wx.TextCtrl(self, -1, str(target_size[0]),
                                       style=wx.TE_PROCESS_ENTER|wx.TE_RIGHT,
                                       name='width')
        self.text_size_h = wx.TextCtrl(self, -1, str(target_size[1]),
                                       style=wx.TE_PROCESS_ENTER|wx.TE_RIGHT,
                                       name='height')
        self.text_size_w.SetMaxLength(3)
        self.text_size_h.SetMaxLength(3)
        h_sizer2.Add(self.text_size_w, 0, wx.TE_CENTER)
        h_sizer2.Add(self.text_size_h, 0, wx.TE_CENTER)
        sizer2.Add(h_sizer2, -1, wx.ALIGN_CENTER)
        mainsizer.Add(sizer2, 0, wx.EXPAND|wx.ALL, 5)
        
        # Separated buttons sizer
        but_sizer = self.CreateSeparatedButtonSizer(wx.OK|wx.CANCEL)
        mainsizer.Add(but_sizer, 0, wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, 5)
        
        BUT_ID_OK = wx.FindWindowById(wx.ID_OK, self)
        BUT_ID_CLOSE = wx.FindWindowById(wx.ID_CANCEL, self)
        BUT_ID_OK.SetName('OK')
        
        self.SetSizer(mainsizer)
        
        #Event binding
        self.text_size_w.Bind(wx.EVT_CHAR, self.on_keypress)
        self.text_size_h.Bind(wx.EVT_CHAR, self.on_keypress)
        self.button_path.Bind(wx.EVT_LEFT_DOWN, self.on_but_click)
        BUT_ID_OK.Bind(wx.EVT_LEFT_DOWN, self.OnOk)
        BUT_ID_CLOSE.Bind(wx.EVT_LEFT_DOWN, self.OnClose)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.text_path.SetFocus()
        
    def on_keypress(self, evt):
        # Evita la introduccion de caracteres no numericos
        k_code = evt.GetKeyCode()
        t_object = evt.GetEventObject()
        t_name = t_object.GetName()
        #print t_name
        #print k_code
        valid_k_codes = (9, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 8, 13,
                         127, 314, 315, 316, 317, 324, 325, 326, 327, 328,
                         329, 330, 331, 332, 333, 391)
        valid_objt_names = ('width', 'height')
        if k_code in valid_k_codes and t_name in valid_objt_names:
            evt.Skip()
        
    def on_text_enter(self, evt):
        # Pasa el foco al siguiente TextCtrl cuando se presiona INTRO
        t_object = evt.GetEventObject()
        t_name = t_object.GetName()
        objt_names = ('path', 'width', 'height', 'OK')
        if not objt_names[objt_names.index(t_name)] == objt_names[-1]:
            next_obj = objt_names[objt_names.index(t_name) + 1]
            self.FindWindowByName(next_obj).SetFocus()
            if next_obj == 'OK':
                self.OnOk(evt)
            
    def on_but_click(self, evt):
        ''' Abre el dialogo estandar wx.FileDialog y
            establece la ruta seleccionada en el TextCtrl '''
        #wildcard = "PNG files (*.png)|*.png"
        wildcard = "JPEG files (*.jpg)|*.jpg|PNG files (*.png)|*.png"
        dialog = wx.FileDialog(None, "Save thumbnail",
                               os.path.dirname(self.save_path),
                               "", wildcard,
                               wx.SAVE
                               #|wx.FD_OVERWRITE_PROMPT
                               )
        if dialog.ShowModal() == wx.ID_CANCEL:
            return
        
        self.save_path = dialog.GetPath()
        valid = (self.save_path.endswith('.jpg')
                 or self.save_path.endswith('.png'))
        if not valid:
            self.save_path = u'{}{}'.format(self.save_path, '.jpg')
        self.text_path.SetValue(self.save_path)
        self.text_path.SetInsertionPointEnd()
        
    def OnOk(self, evt):
        # Valida y envia los parametros elegidos al frame y finaliza el dialogo
        if not self.text_path.GetValue():
            self.text_path.SetFocus()
            return
        if not self.text_size_w.GetValue():
            self.text_size_w.SetFocus()
            return
        if not self.text_size_h.GetValue():
            self.text_size_h.SetFocus()
            return
        
        self.save_path = self.text_path.GetValue()
        valid = (self.save_path.endswith('.jpg')
                 or self.save_path.endswith('.png'))
        if not valid:
            self.save_path = u'{}{}'.format(self.save_path, '.jpg')
            
        target_size = (int(self.text_size_w.GetValue()),
                       int(self.text_size_h.GetValue())
                       )
        self.parent.SetSaveProperties(self.save_path, target_size)
        self.EndModal(wx.ID_OK)
            
    def OnClose(self, evt):
        # Finaliza el dialogo Cancelado
        self.EndModal(wx.ID_CANCEL)
        
           
if __name__ == '__main__':
    app = wx.App(redirect=False)
    frm = MainFrame(None, title="Easy Thumbnailer")
    frm.Show()
    app.MainLoop() 