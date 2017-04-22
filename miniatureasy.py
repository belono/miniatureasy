#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
wxPython app for easy and fast thumbnail extraction from your images
with the help of PIL/Pillow.

This application allows the user to multiload, view, rotate, crop and save a
hight quality miniature of the selection in just a few clicks.

It loads all image formats supported by PIL/Pillow and
saves thumbnails in JPEG or PNG formats.

@author: Benito López
@license: GNU GPL v3
"""

import wx
import os
import logging
import wx.lib.mixins.rubberband
try:
    from PIL import Image
except ImportError:
    try:
        import Image
    except ImportError:
        Image = None
        
logging.basicConfig(format='%(levelname)s: %(message)s',
                    level=logging.WARNING)

try:
    bgstyle = wx.BG_STYLE_PAINT
except:
    bgstyle = wx.BG_STYLE_CUSTOM
    
class MainFrame(wx.Frame):
    '''
    Main frame contains a Panel to display image,
    a ToolBar aligned to the right side of the frame and
    an StatusBar to display info and current zoom.
    
    Image will be proportionaly streched if exceeds the panel size in
    default PIL/Pillow quality, so this application is not intended to be a
    high quality viewer.
    
    To create a thumbnail:
    1 - Load an image file.
    2 - (Optional) If you want to save a thumb from a portion of the image:
        Drag mouse over the image to draw an adjustable RubberBand.
    3 - Click on Save button, check out the miniature preview,
        set a pathname and size for the thumb and then click OK.
        A hight quality miniature will be created.
    '''
    def __init__(self, *args, **kwargs):
        super(MainFrame, self).__init__(*args, **kwargs)
        
        #Controls
        mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundStyle(bgstyle)
        mainsizer.Add(self.panel, -1, wx.EXPAND|wx.ALL, 5)
        
        grid = wx.FlexGridSizer(2, 0, 0, 0)
        
        tsize = (64, 64)
        theme_folder = 'oxygen'
        icon_open = wx.Bitmap(
                    os.path.normpath(
                    os.path.join(
                    os.getcwd(),
                    "resources/{}/folder-image.png".format(theme_folder)
                    )),
                    wx.BITMAP_TYPE_PNG
                    )
        icon_next = wx.Bitmap(
                    os.path.normpath(
                    os.path.join(
                    os.getcwd(),
                    "resources/{}/go-next.png".format(theme_folder)
                    )),
                    wx.BITMAP_TYPE_PNG
                    )
        icon_rotate = wx.Bitmap(
                      os.path.normpath(
                      os.path.join(
                      os.getcwd(),
                      "resources/{}/transform-rotate.png".format(theme_folder)
                      )),
                      wx.BITMAP_TYPE_PNG
                      )
        icon_save = wx.Bitmap(
                    os.path.normpath(
                    os.path.join(
                    os.getcwd(),
                    "resources/{}/document-save.png".format(theme_folder)
                    )),
                    wx.BITMAP_TYPE_PNG
                    )
        icon_close = wx.Bitmap(
                     os.path.normpath(
                     os.path.join(
                     os.getcwd(),
                     "resources/{}/application-exit.png".format(theme_folder)
                     )),
                     wx.BITMAP_TYPE_PNG
                     )
        
        #Since wx v.3.0.3 Phoenix
        tool_args = [
                     (1, 'Open', icon_open, wx.NullBitmap, wx.ITEM_NORMAL,
                      'Open',
                      'Load one or more files'),
                     (2, 'Next', icon_next, wx.NullBitmap, wx.ITEM_NORMAL,
                      'Next',
                      'Next file loaded'),
                     (3, 'Rotate', icon_rotate, wx.NullBitmap, wx.ITEM_NORMAL,
                      'Rotate',
                      'Rotate image 90º'),
                     (4, 'Save as', icon_save, wx.NullBitmap, wx.ITEM_NORMAL,
                      'Save thumbnail...', 
                      'Preview and save a thumbnail of the selection'),
                     (5, 'Quit', icon_close, wx.NullBitmap, wx.ITEM_NORMAL,
                      'Quit',
                      'Exit program')
                     ]
        
        #Before wx v.3.0.3 Phoenix
        tool_args_legacy = [
                    (1, icon_open, wx.NullBitmap, wx.ITEM_NORMAL,
                    'Open',
                    'Load one or more files'),
                    (2, icon_next, wx.NullBitmap, wx.ITEM_NORMAL,
                    'Next',
                    'Next file loaded'),
                    (3, icon_rotate, wx.NullBitmap, wx.ITEM_NORMAL,
                    'Rotate',
                    'Rotate image 90º'),
                    (4, icon_save, wx.NullBitmap, wx.ITEM_NORMAL,
                    'Save thumbnail...',
                    'Preview and save a thumbnail of the selection'),
                    (5, icon_close, wx.NullBitmap, wx.ITEM_NORMAL,
                    'Quit',
                    'Exit program')
                    ]
                        
        tb = wx.ToolBar(self, style=wx.TB_VERTICAL
                                    |wx.TB_RIGHT
                                    |wx.NO_BORDER
                                    |wx.TB_FLAT,
                                    name='tb1'
                                    )
        
        tb.SetToolBitmapSize(tsize)
        
        try:
            [tb.AddTool(*tool_args[i]) for i in range(4)]
        except:
            tool_args = tool_args_legacy
            [tb.AddTool(*tool_args[i]) for i in range(4)]
        
        tb.Realize()
        
        tb2 = wx.ToolBar(self, style=wx.TB_VERTICAL
                                        |wx.TB_RIGHT
                                        |wx.NO_BORDER
                                        |wx.TB_FLAT
                                        )
        tb2.SetToolBitmapSize(tsize)
        
        tb2.AddTool(*tool_args[4])
        
        tb2.Realize()
        
        grid.AddMany([(tb, 0, wx.EXPAND),
                      (tb2, 0)])
        grid.AddGrowableRow(0, 0)

        mainsizer.Add(grid, 0, wx.EXPAND)
        
        self.SetSizer(mainsizer)
        
        self.statusBar = self.CreateStatusBar(2)
        self.statusBar.SetStatusWidths([-4, -1])
        
        #Event binding
        self.Bind(wx.EVT_TOOL, self.on_files_dialog, id=1)
        self.Bind(wx.EVT_TOOL, self.on_next_file, id=2)
        self.Bind(wx.EVT_TOOL, self.on_rotate_right, id=3)
        self.Bind(wx.EVT_TOOL, self.on_save_thumbnail, id=4)
        self.Bind(wx.EVT_TOOL, self.on_close, id=5)
        self.panel.Bind(wx.EVT_SIZE, self.on_evt_size)
        self.panel.Bind(wx.EVT_PAINT, self.on_evt_paint)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
        #Properties
        self.pil_img = Image.new('RGB', (1, 1))
        self.has_alpha = False
        self.boundingbox = None
        self.zoom = 1
        self.rubberband = wx.lib.mixins.rubberband.RubberBand(self.panel)
        self.img_path = os.getcwd()
        self.save_path = self.img_path
        self.target_size = (200, 200)
        self.index = 0
        
        #Frame size and layout
        self.SetSizeHints(450,450)
        self.Maximize(True)
        
        if not Image:
            txt = u'Python Imaging Library (PIL or Pillow) is required'
            self.statusBar.SetStatusText(u'ERROR: {}'.format(txt), 0)
        self.enable_tbbuttons(False)
        wx.CallAfter(self.on_files_dialog)
        
    def enable_tbbuttons(self, bool):
        tb1 = wx.FindWindowByName('tb1')
        [tb1.EnableTool(id, bool) for id in [2, 3, 4]]
        
    def pil_to_wximage(self, pil):
        '''Convert PIL Image to wx.Image checking if it has alpha channel'''
        if self.has_alpha:
            wximage = self._get_wximage_alpha(pil)
        else:
            wximage = self._get_wximage_noalpha(pil)
            
        return wximage
    
    def _get_wximage_alpha(self, pil):
        'Private method to convert PIL image with alpha channel to wx.Image'
        data = pil.convert("RGB")
        alpha = pil.convert("RGBA")
        try:
            #python3
            data = data.tobytes()
            alpha = alpha.tobytes()[3::4]
        except:
            #python2
            data = data.tostring()
            alpha = alpha.tostring()[3::4]
            
        try:
            #wxpython phoenix => 3.0.3
            wximage = wx.Image(*pil.size)
            wximage.SetData(data)
            wximage.SetAlpha(alpha)
        except:
            #wxpython classic < 3.0.3
            wximage = wx.EmptyImage(*pil.size)
            wximage.SetData(data)
            wximage.SetAlphaData(alpha)
            
        return wximage
            
    def _get_wximage_noalpha(self, pil):
        'Private method to convert PIL image with no alpha channel to wx.Image'
        data = pil.convert('RGB')
        try:
            #python3
            data = data.tobytes()
        except:
            #python2
            data = data.tostring()
        try:
            #wxpython phoenix => 3.0.3
            wximage = wx.Image(*pil.size)
        except:
            #wxpython classic < 3.0.3
            wximage = wx.EmptyImage(*pil.size)
        wximage.SetData(data)
        
        return wximage
    
    def pil_thumb_loq(self, pil_img, target_w, target_h):
        '''Proportionaly scale to target size a COPY of the image
        in DEFAULT quality with PIL/Pillow'''
        temp = pil_img.copy()
        temp.thumbnail((target_w, target_h))
        return temp
    
    def pil_thumb_hiq(self, pil_img, target_w, target_h):
        '''Proportionaly scale image to target size in ANTIALIAS quality.
        with PIL/Pillow'''
        pil_img.thumbnail((target_w, target_h, Image.ANTIALIAS))
        return pil_img
    
    def set_save_properties(self, save_path, target_size):
        '''Update properties path and size to save the thumb'''
        self.save_path = save_path
        self.target_size = target_size
        
    def get_save_properties(self):
        '''Return thumbnail save properties path and size'''
        return self.save_path, self.target_size
        
    def on_files_dialog(self, event=None):
        '''Open standard multiselect FileDialog and load first file'''
        wildcard = "All files (*.*)|*.*|\
JPEG files (*.jpg)|*.jpg|\
PNG files (*.png)|*.png|\
BMP files (*.bmp)|*.bmp|\
GIF files (*.gif)|*.gif"
        dialog = wx.FileDialog(None, "Choose one or more files",
                               os.path.dirname(self.img_path),
                               "", wildcard,
                               wx.FD_MULTIPLE|wx.FD_FILE_MUST_EXIST
                               )
        if dialog.ShowModal() == wx.ID_CANCEL:
            return
        
        self.files = dict(enumerate(dialog.GetPaths()))
        self.index = 0
        self.on_load_image(self.index)
            
    def on_load_image(self, index):
        '''Load image on memory and call update_drawing'''
        self.clear_all()
        self.img_path = self.files[index]
        try:
            file = open(self.img_path, 'rb')
        except IOError:
            msg = u'Cannot open the file\n{}'.format(self.img_path)
            wx.MessageDialog(self, msg, 'Read error',
                             wx.OK | wx.ICON_ERROR).ShowModal()
            self.pil_img = Image.new('RGB', (1, 1))
            return
        except MemoryError:
            msg = u'''Not enought memory to open the file\n{}
                   '''.format(self.img_path)
            wx.MessageDialog(self, msg, 'Memory error',
                             wx.OK | wx.ICON_ERROR).ShowModal()
            self.pil_img = Image.new('RGB', (1, 1))
            return
        else:
            try:
                self.pil_img = Image.open((file))
            except:
                msg = u'Wrong image format\n{}'.format(self.img_path)
                wx.MessageDialog(self, msg, 'Error',
                                wx.OK | wx.ICON_ERROR).ShowModal()
                self.pil_img = Image.new('RGB', (1, 1))
                #return
            
        self.has_alpha = self.pil_img.mode == 'RGBA'
        self.update_drawing()
        self.enable_tbbuttons(True)
        text = u'{} - {}/{}'.format(self.img_path, index + 1, len(self.files))
        self.statusBar.SetStatusText(text, 0)
            
    def on_next_file(self, evt):
        '''Get next file from the list and call method on_load_image'''
        if self.index + 1 in self.files.keys():
            self.index += 1
            
        else:
            wx.MessageDialog(self, u'End of file list, restarting', 'Info',
                                   wx.OK | wx.ICON_INFORMATION).ShowModal()
            self.index = 0
            
        self.on_load_image(self.index)
        
    def on_save_thumbnail(self, evt):
        '''Open SaveDialog, get a high quality thumbnail from the image and
        save to disk '''
        dlg = SaveDialog(self, -1, 'Save thumbnail as...',
                         size=(400,400)
                         )
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
            
        logging.info(u'Save as: {}'.format(self.save_path))
        logging.info(u'Thumb size: {}'.format(self.target_size))
        if not self.save_path:
            return
        elif os.path.exists(self.save_path):
            text = u'''File exists:\n\n{}\n
¿Overwrite?.'''.format(self.save_path)
            msg = wx.MessageDialog(self, text, 'Overwrite',
                                   wx.YES_NO|wx.CANCEL |
                                   wx.ICON_QUESTION).ShowModal()
            if msg == wx.ID_NO or msg == wx.ID_CANCEL:
                self.statusBar.SetStatusText(u'Canceled, not saved', 0)
                return
            
        cropped_img = self.get_cropped_img()
        img_w, img_h = cropped_img.size
        target_w, target_h = self.target_size
        if img_w > target_w * 2 or img_h > target_h * 2:
            # Step 1: Thumb to double the target size with default quality
            cropped_img = self.pil_thumb_loq(cropped_img, target_w, target_h)
        # Step 2: Thumb to target size with best quality
        thumb = self.pil_thumb_hiq(cropped_img, target_w, target_h)
        # Save file
        self.statusBar.SetStatusText('Saving...', 0)
        try:
            thumb.save(self.save_path, optimize=True)
        except IOError:
            logging.error(u'Cannot create thumbnail: {}'.format(self.save_path))
            msg = u'''Cannot save file:\n\n{}\n
Check path and filename.'''.format(self.save_path)
            wx.MessageDialog(self, msg, 'Write error',
                             wx.OK | wx.ICON_ERROR).ShowModal()
            self.statusBar.SetStatusText(u'Error, not saved', 0)
        except SystemError:
            logging.error(u'Cannot create thumbnail: {}'.format(self.save_path))
            msg = u'''Cannot save file:\n\n{}\n
Check target size: {}'''.format(self.save_path, self.target_size)
            wx.MessageDialog(self, msg, 'Write error',
                             wx.OK | wx.ICON_ERROR).ShowModal()
            self.statusBar.SetStatusText(u'Error, not saved', 0)
            
        else:
            text = u'Saved: {}'.format(self.save_path)
            self.statusBar.SetStatusText(text, 0)
        
    def get_cropped_img(self):
        '''Get rubberband coords removing borders exceeding the boundingbox.
        Return cropped image or full image if no rubberband is drawn'''
        try:
            left, top, right, bottom = self.rubberband.getCurrentExtent()
        except TypeError:
            # None extent = Full size selection
            left, top, right, bottom = self.boundingbox
        else:
            # Prevents the rubberband to exceed the image
            if left < self.boundingbox[0]:
                left = self.boundingbox[0]
            if top < self.boundingbox[1]:
                top = self.boundingbox[1]
            if right > self.boundingbox[2]:
                right = self.boundingbox[2]
            if bottom > self.boundingbox[3]:
                bottom = self.boundingbox[3]
        
        '''Convert rubberband coords to original img coords correcting the
           center align and the zoom'''
        left, top, right, bottom = (left - self.boundingbox[0],
                                    top - self.boundingbox[1],
                                    right - self.boundingbox[0],
                                    bottom - self.boundingbox[1])
        cropped_img = self.pil_img.crop((int(left / self.zoom),
                                         int(top / self.zoom),
                                         int(right / self.zoom),
                                         int(bottom / self.zoom)
                                         ))
        return cropped_img
        
    def clear_all(self):
        '''Reset the rubberband extent and zoom scale'''
        self.zoom = 1
        self.clear_rb()
        
    def clear_rb(self):
        '''Reset the rubberband extent if is drawn'''
        if self.rubberband.getCurrentExtent():
            self.rubberband.reset()
        
    def on_evt_size(self, evt):
        'Reset rubberband and call method update_drawing after panel EVT_SIZE'
        self.clear_rb()
        self.update_drawing()
        evt.Skip()
        
    def on_evt_paint(self, evt):
        'Reduces flicker on windows platform, no efect on gtk'
        self.update_drawing(dc=wx.AutoBufferedPaintDC(self.panel))
        
    def get_resized_center_bmp(self):
        '''Compare panel size with original image size.
        Scale image to fit the panel or restore original image size and
        calculate the applied zoom with a maximum of 100%.
        Return the resulting bitmap object and position needed to center the
        bitmat on the panel'''
        if not hasattr(self.pil_img, 'size'):
            return
        target_w, target_h = self.panel.GetSize()
        img_w, img_h = self.pil_img.size
        thumb = self.pil_thumb_loq(self.pil_img, target_w, target_h)
        thumb_w, thumb_h = thumb.size
        wx_img = self.pil_to_wximage(thumb)
        position = ((target_w - thumb_w) / 2,
                    (target_h - thumb_h) / 2)
        self.zoom = min(float(target_w) / img_w,
                        float(target_h) / img_h,
                        1) #100% Max zoom allowed
        
        self.statusBar.SetStatusText(u'Zoom: {}%'.format(
                                                    int(self.zoom * 100)),
                                                    1)
        return (wx_img.ConvertToBitmap(), position)
        
    def update_drawing(self, dc=None):
        '''Draw the bitmap on the panel and update the bounding box coords'''
        if not dc:
            dc = wx.ClientDC(self.panel)
        dc.Clear()
        bmp, position = self.get_resized_center_bmp()
        dc.DrawBitmap(bmp,
                      *position
                      )
        self.boundingbox = dc.GetBoundingBox()
        
    def get_preview_img(self, size=(200, 200)):
        '''Return a default quality, resized preview of the cropped image
           in wxpython image format'''
        preview = self.pil_thumb_loq(self.get_cropped_img(), size[0], size[1])
        return self.pil_to_wximage(preview)
            
    def on_rotate_right(self, evt):
        '''Rotate loaded image 90º to the right then call update_drawing'''
        self.clear_rb()
        self.pil_img = self.pil_img.rotate(-90, expand=True)
        self.update_drawing()
        
    def on_close(self, evt):
        '''Quit the application'''
        exit()
        
        
class SaveDialog(wx.Dialog):
    '''Custom dialog for thumbnail pathname and size introduction'''
    def __init__(self, parent, *args, **kwargs):
        super(SaveDialog, self).__init__(parent, *args, **kwargs)
        
        self.parent = parent
        self.save_path, target_size = self.parent.get_save_properties()
        
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        
        # Path and filename
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, -1,
                              'File name:')
        sizer1.Add(label, 0, wx.EXPAND|wx.ALL, 5)
        h_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.text_path = wx.TextCtrl(self, -1, self.save_path,
                                     style=wx.TE_RIGHT|wx.TE_PROCESS_ENTER,
                                     name='path')
        self.button_path = wx.Button(self, -1, '...')
        h_sizer1.Add(self.text_path, -1, wx.TOP, 3)
        h_sizer1.Add(self.button_path, 0)
        sizer1.Add(h_sizer1, 0, wx.EXPAND)
        mainsizer.Add(sizer1, 0, wx.EXPAND|wx.ALL, 5)
        
        # Image preview
        preview = self.parent.get_preview_img().ConvertToBitmap()
        staticbmp = wx.StaticBitmap(self, wx.ID_ANY, preview, size=(200,200))
        mainsizer.Add(staticbmp, -1, wx.ALIGN_CENTER|wx.ALL, 5)
        
        # Thumbnail target size
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, -1,
                              'Thumbnail width and height (in pixels)',
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
        sizer2.Add(h_sizer2, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        mainsizer.Add(sizer2, 0, wx.EXPAND)
        
        # Separated buttons sizer
        but_sizer = self.CreateSeparatedButtonSizer(wx.OK|wx.CANCEL)
        mainsizer.Add(but_sizer, 0, wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, 5)
        
        BUT_ID_OK = wx.FindWindowById(wx.ID_OK, self)
        BUT_ID_CLOSE = wx.FindWindowById(wx.ID_CANCEL, self)
        BUT_ID_OK.SetName('OK')
        
        self.SetSizer(mainsizer)
        self.SetSizeHints(400,400)
        
        #Event binding
        self.text_size_w.Bind(wx.EVT_CHAR, self.on_keypress)
        self.text_size_h.Bind(wx.EVT_CHAR, self.on_keypress)
        self.button_path.Bind(wx.EVT_LEFT_DOWN, self.on_but_click)
        BUT_ID_OK.Bind(wx.EVT_LEFT_DOWN, self.on_ok)
        BUT_ID_CLOSE.Bind(wx.EVT_LEFT_DOWN, self.on_close)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
        self.text_path.SetFocus()
        
    def on_keypress(self, evt):
        '''Avoid non numerical characters'''
        k_code = evt.GetKeyCode()
        t_object = evt.GetEventObject()
        t_name = t_object.GetName()
        valid_k_codes = (9, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 8, 13,
                         127, 314, 315, 316, 317, 324, 325, 326, 327, 328,
                         329, 330, 331, 332, 333, 391)
        valid_objt_names = ('width', 'height')
        if k_code in valid_k_codes and t_name in valid_objt_names:
            evt.Skip()
        
    def on_text_enter(self, evt):
        '''Set focus on the next control when INTRO is pressed'''
        t_object = evt.GetEventObject()
        t_name = t_object.GetName()
        objt_names = ('path', 'width', 'height', 'OK')
        if not objt_names[objt_names.index(t_name)] == objt_names[-1]:
            next_obj = objt_names[objt_names.index(t_name) + 1]
            self.FindWindowByName(next_obj).SetFocus()
            if next_obj == 'OK':
                self.on_ok(evt)
            
    def on_but_click(self, evt):
        '''Start an standard wx.FileDialog
        Get pathname from user, validate extension and set property'''
        wildcard = "JPEG files (*.jpg)|*.jpg|PNG files (*.png)|*.png"
        dialog = wx.FileDialog(None, "Save thumbnail",
                               os.path.dirname(self.save_path),
                               "", wildcard,
                               wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT
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
        
    def on_ok(self, evt):
        '''Validate save values, set save properties to the frame with
        user values and end dialog'''
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
        self.parent.set_save_properties(self.save_path, target_size)
        self.EndModal(wx.ID_OK)
            
    def on_close(self, evt):
        '''Cancel dialog'''
        self.EndModal(wx.ID_CANCEL)
        
           
if __name__ == '__main__':
    app = wx.App(redirect=False)
    app.locale = wx.Locale(wx.LANGUAGE_DEFAULT)
    frm = MainFrame(None, title="Easy Thumbnailer")
    frm.Show()
    app.MainLoop() 
