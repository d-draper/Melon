############################################################

# Melon, V0.3
# 21/09/2020 Daniel Draper

############################################################

import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle

from tkinter import filedialog

import os, io, csv, re, numpy, blend_modes, wave, ffmpeg
import matplotlib.pyplot as plt

import jpverb7 as jp
from PIL import Image, ImageTk, ImageDraw

import simpleaudio
from pydub.playback import _play_with_simpleaudio, play
from pydub import AudioSegment

############################################################

from google.oauth2 import service_account
from google.cloud import vision
from google.cloud.vision import types

credential_json = service_account.Credentials.from_service_account_file('/Users/earth/Documents/Programming/cloud_API_keys/Japanese_OCR-b901ac6b092c.json')

client = vision.ImageAnnotatorClient(credentials=credential_json)

############################################################

class mainwindow:
    image_exts = ['jpg','jpeg','png']
    movie_exts = ['mov']
    

#    src_folder = filedialog.askdirectory()+"/"
#    print(src_folder)

    #anki_folder = '/Users/earth/Library/Application Support/Anki2/User 1/collection.media/'
    #anki_folder = '/Users/earth/Downloads/'

    def __init__(self, master):

        self.master = master

        style = ThemedStyle(master)
        style.theme_use('equilux')

        self.master.configure(background='#464646')


        # --- define images ----

        self.img_index = 0
        #This is iterated over later

        self.seen_images = set()
        #A set we will add to

        self.zoom_io = False
        self.zoomed = False

        self.working_size = (600, 600)
        self.outerbr_width = 10

        #self.anki_folder = '/Users/earth/Library/Application Support/Anki2/User 1/collection.media/'
        #anki_folder = '/Users/earth/Downloads/'

        #self.src_folder = '/Users/earth/Documents/Japanese/Media/Manga/OCR screens/'


        # --- GUI elements and bindings ---

        #Frames
        self.canvas_frame = ttk.Frame(self.master, borderwidth= self.outerbr_width, relief = "sunken")
        self.info_frame = ttk.Frame(self.master, borderwidth= 20, relief = "flat")
        self.output_frame = ttk.Frame(self.info_frame)
        self.player_frame = ttk.Frame(self.info_frame, borderwidth= 2, relief='flat')
        #Set edges of canvas frame to be interactive
        self.canvas_frame.bind('<Button-1>', self.outer_click)
        self.canvas_frame.bind('<B1-Motion>', self.ref_line)

        # Canvas
        self.canvas = tk.Canvas(self.canvas_frame, width=self.working_size[0], height=self.working_size[1])
        #Cropbox functionality
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<B1-Motion>", self.click_move)
        self.canvas.bind("<ButtonRelease-1>", self.upclick)

        # Buttons
        self.reset_button = ttk.Button(self.master, text="RESET", command= self.reset_image)
        self.prev_button = ttk.Button(self.master, text="Previous Image", command= self.prev_image)
        self.next_button = ttk.Button(self.master, text="Next Image", command= self.next_image)
        self.save_button = ttk.Button(self.master, text="Delete", command= self.delete_image)

        self.zoom_button = ttk.Button(self.master, text="Zoom", command= self.toggle_zoom)
        self.OCR_button = ttk.Button(self.master, text="OCR", command = self.Google_OCR)
        self.lookup_button = ttk.Button(self.master, text="Lookup", command = self.keyword_finder)
        self.box_remove_button = ttk.Button(self.master, text="Remove box", command = lambda: self.box_removal(self.canvas.coords('refline')))
        self.export_button = ttk.Button(self.master, text="Export", command = self.export)
        self.open_dir_button = ttk.Button(self.master, text="OPEN", command = self.open_dir)
        #TEST button (for testing new features)
        self.test_button = ttk.Button(self.master, text="TEST", command = self.test)


        #Audio player
        self.play_button = ttk.Button(self.player_frame, text="▶", width=2, command = self.play_audio)
        self.pause_button = ttk.Button(self.player_frame, text="❚❚", width=2, command = self.pause_audio)
        self.reload_button = ttk.Button(self.player_frame, text="⟳", width=2, command= self.replay_audio)
        self.chop_button = ttk.Button(self.player_frame, text="✂", width=2, command= self.chop_audio)
        self.prog_bar = ttk.Scale(self.player_frame, orient='horizontal', length=365, from_=1.0, to= 1.0, command=self.scrub)
        #Wave canvas
        self.wave_size = (343,100)
        self.wave_canvas = tk.Canvas(self.player_frame, width = self.wave_size[0], height = self.wave_size[1])

        #OCR_output
        self.OCR_box = tk.Text(self.output_frame, width = 28, height = 8, borderwidth=0, relief="sunken", wrap='word', padx = 10, pady=2 , foreground="#A8E6CE", font="Hiragino\ Maru\ Gothic\ ProN 18", spacing2 = 8)
        self.OCR_scroll = ttk.Scrollbar(self.output_frame, orient='vertical', command= self.OCR_box.yview)
        self.OCR_box.configure(yscrollcommand= self.OCR_scroll.set)

        # Seperators
        sep = ttk.Separator(self.output_frame, orient='horizontal')
        sep1 = ttk.Separator(self.output_frame, orient='horizontal')

        #Info box
        self.info_box = tk.Text(self.output_frame, width = 28, height = 8, borderwidth=0, relief="sunken", wrap='word', padx = 10, pady=2 , foreground="#FF8C94", font="Hiragino\ Maru\ Gothic\ ProN 18", spacing2 = 8)
        self.info_scroll = ttk.Scrollbar(self.output_frame, orient='vertical', command= self.info_box.yview)
        self.info_box.configure(yscrollcommand= self.info_scroll.set)

        # -- Gridding --

        self.canvas_frame.grid(row=1, column=0, columnspan= 5)
        self.info_frame.grid(row=0, rowspan=3, column=5, sticky='NSEW')

        self.canvas.grid()
        self.zoom_button.grid(row = 2, column= 0)
        self.OCR_button.grid(row=2, column=1)
        self.lookup_button.grid(row=2, column=2)
        self.box_remove_button.grid(row=2, column=3)
        self.export_button.grid(row=2, column=4)

        self.reset_button.grid(row=0, column = 0)
        self.prev_button.grid(row=0, column=1)
        self.next_button.grid(row=0, column= 2)
        self.save_button.grid(row=0, column= 3)
        self.open_dir_button.grid(row=0, column=4)
        #TEST BUTTON
        #self.test_button.grid(row=1, column= 0)

        self.output_frame.grid(row=0,column=0, sticky='N')
        self.OCR_box.grid(row=0, column=0, sticky='N')
        self.OCR_scroll.grid(row=0, column=1, sticky='NS')

        sep.grid(row=1,column=0,columnspan=2, pady= 5, sticky='EW')

        self.info_box.grid(row=2, column=0, sticky='NS')
        self.info_scroll.grid(row=2, column=1, sticky='NS')

        sep1.grid(row=3,column=0,columnspan=2, pady= 5, sticky='EW')

        self.player_frame.grid(row = 4, columnspan = 2, sticky='SW')
        self.play_button.grid(row=0, column=0)
        self.pause_button.grid(row=0, column=1)
        self.reload_button.grid(row=0, column=2)
        self.chop_button.grid(row=0, column=3)
        self.prog_bar.grid(row=1, columnspan=4, sticky='W')
        self.wave_canvas.grid(row=2, columnspan=4, sticky='S')

        #self.options_text.grid(row=0, columnspan=2, sticky='N')
        tk_gets = (self.canvas, self.wave_canvas, self.OCR_box, self.info_box)
        for i in tk_gets:
            i.config(bg='#464646', highlightthickness=0)

    # --- Regular functions ---

    def original_coords(self, A_coords, crop_box, new_thumbnail):
        
        #A_co_ords = the coordinate we want to translate
        #crop_box = the co-ordinates of the crop on the larger image
        #new_thumbnail = the new sized thumbnail crop

        new_ratio = (crop_box[2] - crop_box[0]) / new_thumbnail.width
        B_coords = [(i * new_ratio) for i in A_coords]
        C_coords = [(crop_box[0] + B_coords[0]), (crop_box[1] + B_coords[1])]
        return C_coords


    # --- Event functions

    def click(self, event):
        self.one_x, self.one_y = event.x, event.y

    def click_move(self, event):
        if self.zoom_io:
            pass

        else:
            self.canvas.delete('rec', 'refline')

            cropbox_shadow = self.canvas.create_rectangle((self.one_x+1, self.one_y+1, event.x+1, event.y+1), outline="purple", dash= (10,10), width=2, tags='rec')  
            cropbox = self.canvas.create_rectangle((self.one_x, self.one_y, event.x, event.y), outline="yellow", dash= (10,10), width=2, tags='rec')

    def upclick(self, event):

        if self.zoom_io:
            self.zoom_in(event)
            self.canvas.delete('rec')

        else:
            cropbox = self.canvas.create_rectangle((self.one_x, self.one_y, event.x, event.y), tags='rec')
            cbox = self.canvas.coords(cropbox)
            cbox[0:4] = cbox[0]-self.adj_w, cbox[1]-self.adj_h, cbox[2]-self.adj_w, cbox[3]-self.adj_h

            self.firstx, self.firsty, secondx, secondy = cbox

            self.canvas.delete('rec')

            if secondx > self.cropped_image.width:
                secondx = self.cropped_image.width
            if secondy > self.cropped_image.height:
                secondy = self.cropped_image.height

            if self.firstx < 0:
                self.firstx = 0
            if self.firsty < 0:
                self.firsty = 0

            #Image replacement
            self.thumb_cropbox = [self.original_coords(i, self.thumb_cropbox, self.cropped_image) for i in ([self.firstx,self.firsty],[secondx,secondy])]
            self.thumb_cropbox = self.thumb_cropbox[0] + self.thumb_cropbox[1]
            
            self.cropped_image = self.currentfile.image.crop(box=self.thumb_cropbox)
            self.cropped_image.thumbnail(self.working_size)
            
            self.image_replace = ImageTk.PhotoImage(self.cropped_image)
            self.canvas.itemconfig(self.image_id, image=self.image_replace)

            # There should be a way to do this cleaner (not call it twice):
            self.adj_w = (self.working_size[0]/2) - ((self.cropped_image.width)/2)
            self.adj_h = (self.working_size[1]/2) - ((self.cropped_image.height)/2)


    def outer_click(self, event):
        
        #For the checkerboard display
        self.horiz_area = range(int(self.adj_w),int(self.working_size[0]-self.adj_w))
        self.vert_area = range(int(self.adj_h),int(self.working_size[1]-self.adj_h))

        if event.x <= self.outerbr_width:
            self.direction = 'l'

        elif event.x >= self.working_size[0]:
            self.direction = 'r'

        elif event.y <= self.outerbr_width:
            self.direction = 't'

        elif event.y >= self.working_size[1]:
            self.direction = 'b'

    def ref_line(self, event):
        #global refline #So we can retrive the coordinates

        self.canvas.delete('refline')

        checker_space = 4

        if self.direction == 'l' or self.direction == 'r':
            self.refline_xy = (event.x, 0, event.x, self.working_size[1])        
            if self.direction == 'l':
                self.checker = [self.canvas.create_line(self.horiz_area[0],i, event.x, i) for i in self.vert_area[::checker_space] if event.x>self.horiz_area[0]] 
            if self.direction == 'r':
                self.checker = [self.canvas.create_line(self.horiz_area[-1],i, event.x, i) for i in self.vert_area[::checker_space] if event.x<self.vert_area[-1]] 
        if self.direction == 't' or self.direction == 'b':
            self.refline_xy = (0, event.y, self.working_size[0], event.y)
            if self.direction == 't':
                self.checker = [self.canvas.create_line(i,self.vert_area[0], i, event.y) for i in self.horiz_area[::checker_space] if event.y>self.vert_area[0]] 
            if self.direction == 'b':
                self.checker = [self.canvas.create_line(i,self.vert_area[-1], i,event.y) for i in self.horiz_area[::checker_space] if event.x<self.vert_area[-1]]

        [self.canvas.itemconfig(i, width=1, dash=(1,checker_space), fill='orange', tags='refline') for i in self.checker]
            
        refline_shadow = self.canvas.create_line(self.refline_xy, dash= None, width=1, fill='red', tags='refline')
        refline = self.canvas.create_line(self.refline_xy, dash= (10,5), width=1, fill='cyan', tags='refline')

        print(self.canvas.coords('refline'))

    def box_removal(self, xy):

        if self.zoomed:
            cropbox = self.zoombox
        else:
            cropbox = self.thumb_cropbox
        xy = self.original_coords([xy[2]-self.adj_w, xy[3]-self.adj_h], cropbox, self.cropped_image)

        def check_direction():
            if self.direction == 'l':
                return (0,0,  xy[0], self.currentfile.image.height)
            if self.direction == 'r':
                return (xy[0], self.currentfile.image.height, self.currentfile.image.width, 0)
            if self.direction == 't':
                return (0,0, self.currentfile.image.width, xy[1])
            if self.direction == 'b':
                return (0, self.currentfile.image.height, self.currentfile.image.width, xy[1])
        rec_dims = check_direction()

        print(rec_dims)

        RGB_colour = (112,112,112)

        self.currentfile.image = self.currentfile.image.convert('RGBA')
        self.divide_map= Image.new('RGBA', (self.currentfile.image.width, self.currentfile.image.height), color='white')

        self.img1 = ImageDraw.Draw(self.divide_map)
        self.img1.rectangle(rec_dims, fill=RGB_colour, outline=None) #<-- NOT WORKING

        # Import background image
        background_img_raw = self.currentfile.image  # RGBA image
        background_img = numpy.array(background_img_raw)  # Inputs to blend_modes need to be numpy arrays.
        background_img_float = background_img.astype(float)  # Inputs to blend_modes need to be floats.

        # Import foreground image
        foreground_img_raw = self.divide_map  # RGBA image
        foreground_img = numpy.array(foreground_img_raw)  # Inputs to blend_modes need to be numpy arrays.
        foreground_img_float = foreground_img.astype(float)  # Inputs to blend_modes need to be floats.

        # Blend images
        opacity = 1  # The opacity of the foreground that is blended onto the background is 70 %.
        blended_img_float = blend_modes.divide(background_img_float, foreground_img_float, opacity)

        # Convert blended image back into PIL image
        blended_img = numpy.uint8(blended_img_float)  # Image needs to be converted back to uint8 type for PIL handling.
        blended_img_raw = Image.fromarray(blended_img).convert('RGB')  # Note that alpha channels are displayed in black by PIL by default.
                                                        # This behavior is difficult to change (although possible).
                                                        # If you have alpha channels in your images, then you should give
                                                        # OpenCV a try.

        # Display blended image
        self.currentfile.image = blended_img_raw.crop(box=self.thumb_cropbox)
        self.zoomed = False
        self.set_image()

    def toggle_zoom(self):
        if self.zoom_io:
            self.zoom_io = False
            self.master.config(cursor='arrow')
        else:
            self.zoom_io = True
            self.master.config(cursor='crosshair')

    def zoom_in(self, event):
        global zoomed_img #Prevents the image getting garbage collected
        global zoom_io, zoombox, adj_w, adj_h, cropped_image, zoomed

        if self.zoomed:
            self.zoomed = False
            self.toggle_zoom()
            self.set_image()

        else:
            event.x, event.y = event.x - self.adj_w, event.y - self.adj_h
            zoom_coords = self.original_coords([event.x,event.y], self.thumb_cropbox, self.cropped_image)
            #These if statements adjust for the user clicking out of bounds
            if zoom_coords[0] > self.currentfile.image.width:
                zoom_coords[0] = self.currentfile.image.width
            if zoom_coords[1] > self.currentfile.image.height:
                zoom_coords[1] = self.currentfile.image.height
            if zoom_coords[0] < 0:
                zoom_coords[0] = 0
            if zoom_coords[1] < 0:
                zoom_coords[1] = 0

            x_buffer = self.working_size[0]/2
            y_buffer = self.working_size[1]/2

            scale = 10

            self.zoombox = [zoom_coords[0]-(x_buffer/scale), zoom_coords[1]-(y_buffer/scale), zoom_coords[0]+(x_buffer/scale), zoom_coords[1]+(y_buffer/scale)]
            #thumb_cropbox = zoombox
            zoomed_img = self.currentfile.image.crop(self.zoombox)
            zoomed_img = zoomed_img.resize([zoomed_img.width*scale,zoomed_img.height*scale], resample = 0)

            self.adj_w = (self.working_size[0]/2) - ((zoomed_img.width)/2)
            self.adj_h = (self.working_size[1]/2) - ((zoomed_img.height)/2)
            self.cropped_image = zoomed_img

            zoomed_img = ImageTk.PhotoImage(image=zoomed_img)
            self.canvas.itemconfig(self.image_id, image=zoomed_img)

            self.zoomed = True
            self.zoom_io = True


    def next_image(self):

        self.save_image() #Saves current crop before moving on

        if self.img_index == len(self.input_files)-1:
            self.img_index = 0
        else:
            self.img_index += 1

        self.set_image()
        self.lookup()

    def prev_image(self):

        self.save_image() #Saves current crop before moving on

        if self.img_index > 0:
            self.img_index -= 1
        else:
            self.img_index = len(self.input_files)-1

        self.set_image()
        self.lookup()

    def reset_image(self):
        
        self.currentfile.image = Image.open(self.currentfile.img_src)

        self.set_image()


    def set_image(self):

        simpleaudio.stop_all()
        self.prog_bar["value"] = 0
        self.canvas.delete('refline')
        self.info_box.delete('1.0', 'end')
        self.OCR_box.delete('1.0', 'end')
        self.wave_canvas.delete('chopline','playline','wave_img')

        self.currentfile = self.input_files[self.img_index]
        #Needed to redefine the new current image

        current_thumbnail = (self.currentfile.image).copy()
        current_thumbnail.thumbnail(self.working_size)
        self.image_replace = ImageTk.PhotoImage(current_thumbnail)
        self.canvas.itemconfig(self.image_id, image=self.image_replace)

        self.thumb_cropbox = (0,0, self.currentfile.image.width,self.currentfile.image.height)
        self.cropped_image = current_thumbnail

        self.adj_w = (self.working_size[0]/2) - ((self.cropped_image.width)/2)
        self.adj_h = (self.working_size[1]/2) - ((self.cropped_image.height)/2)

        self.seen_images.add(self.img_index)

        self.OCR_box.insert('1.0', self.currentfile.OCR_text)

        if self.currentfile.type == 'video':
            self.EnableButtons()
            self.audio_file = self.currentfile.audio
            self.sound = AudioSegment.from_file(self.audio_file, format('wav'))
            self.end_time = len(self.sound)
            self.prog_bar["to"] = self.end_time
            self.wave_ratio = self.wave_size[0]/self.end_time
            self.waveform_image = ImageTk.PhotoImage(self.currentfile.waveform.resize(self.wave_size))
            self.wave_canvas.create_image(self.wave_size[0]/2,self.wave_size[1]/2,image=self.waveform_image, tags='wave_img')

            if self.currentfile.ChopPoint:
                self.wave_canvas.create_line(self.currentfile.ChopPoint*self.wave_ratio,0,self.currentfile.ChopPoint*self.wave_ratio,self.wave_size[1], width=2, fill='red', tags='chopline')


        else:
            self.DisableButtons()

    def lookupbox_fill(self, definition):
        meaning_readout = self.currentfile.keywords[self.parsedex]+"\n--------\n"+definition+'\n\n'
        self.info_box.insert('end', meaning_readout)
        self.currentfile.expression = definition.replace('\n','<br />').replace('{','<span class="keyword" style="color:#cb4b16">').replace("}","</span>")
        self.currentfile.reading = jp.generate_furigana(self.currentfile.expression)
        self.anki_txt[self.img_index] = f'''{self.currentfile.expression}\t{self.currentfile.reading}\t{("<br />").join([i[0] for i in self.currentfile.meanings])}\t'<img src="{self.currentfile.image}">\t'''
        self.parsedex +=1
        self.parse()


    def keyword_finder(self):
        jptextfinder = re.compile(r'''[\u4E00-\u9FBF|\u3005-\u30FF]+''')
        filename_keywords = jptextfinder.findall(self.currentfile.filename)
        OCR_text_box = self.OCR_box.get('1.0','end').strip()
        squiggle_word = re.compile(r'''(?:{)(.+?)(?:})''')

        def pp():
            self.defs = [jp.jplookup(key) for key in self.currentfile.keywords]
            self.parsedex = 0
            self.parse()

        if filename_keywords:
            self.currentfile.keywords = filename_keywords
            self.expression = ("・").join(self.currentfile.keywords)
            pp()

        elif OCR_text_box != '':
            self.currentfile.keywords = squiggle_word.findall(OCR_text_box)
            self.expression = OCR_text_box
            pp()

    def parse(self):
        lookup = self.defs[self.parsedex]
        def pp():
                self.lookupbox_fill(definition)

        if self.parsedex < len(self.defs):
            if lookup[0]: 
                if len(lookup[0].senses) > 1:
                    self.def_choose(lookup[0])
                else:
                    glosses = lookup[0].senses[0]
                    if len(glosses) > 1:
                        definition = "\n".join([f'{num+1}. {glosses[num]}' for num in range(len(glosses))])
                        pp()
                    else:
                        definition = glosses[0]
                        pp()

            else:
                definition = "PLEASE LOOKUP MANUALLY"
                pp()


    def def_choose(self, lookup):
        word = self.currentfile.keywords[self.parsedex]
        choicebox = tk.Toplevel(self.master)
        style = ThemedStyle(choicebox)
        choicebox.configure(background='#464646')

        headerframe=ttk.Frame(choicebox)
        headerframe.grid(column=0, row=0)

        headertext = tk.Label(headerframe, text="There's a few things this word", font="Tsukushi\ A\ Round\ Gothic\ Regular 20", bg='#464646', fg='#1CA7EC')
        keywordtext = tk.Label(headerframe, text=f'「{word}」', font="Tsukushi\ A\ Round\ Gothic\ Regular 20", bg='#464646', fg='white')
        headertext2 = tk.Label(headerframe, text= "could be:", font="Tsukushi\ A\ Round\ Gothic\ Regular 20", bg='#464646', fg='#1CA7EC')
        headertext.grid(column=0,row=0, pady=20)
        keywordtext.grid(column=1,row=0,pady=20)
        headertext2.grid(column=2,row=0,pady=20)

        sep = ttk.Separator(choicebox, orient='horizontal')
        sep.grid(row=1, column=0, sticky="NSEW", pady=10)

        myframe=ttk.Frame(choicebox)
        myframe.grid(column=0,row=2)

        canvas=tk.Canvas(myframe, width = 750, height=500)
        multichoice=ttk.Frame(canvas)
        myscrollbar=ttk.Scrollbar(myframe,orient="vertical",command=canvas.yview)

        canvas.configure(scrollregion=canvas.bbox("all"), yscrollcommand=myscrollbar.set, background='#464646', highlightthickness=0)

        myscrollbar.grid(column=1, row=0, sticky= "NS")
        canvas.grid(column=0, row=0)
        canvas.create_window((0,0),window=multichoice,anchor='nw')
        multichoice.bind("<Configure>", lambda i : canvas.configure(scrollregion=canvas.bbox("all")) )

        class chosen_sense:
            def __init__(self, glosses):
                self.senses = [glosses]

        def commit():
            indexval = int(user_choice.get())
            self.defs[self.parsedex] = [chosen_sense(choice_list[indexval])]
            choicebox.destroy()
            self.parse()

        user_choice = tk.StringVar()

        COMMIT_button = ttk.Button(choicebox, text="COMMIT", command=commit)
        COMMIT_button.grid(column=0, row=3)

        choice_list = lookup.senses

        for i in range(len(choice_list)):

            definitions = choice_list[i]
            core_frame = ttk.Frame(multichoice)
            core_frame.grid(row=i, column=0, sticky="NW")

            choice_frame = ttk.Frame(core_frame)
            choice_frame.grid(row=0,column=0, sticky="NW")

            radio = tk.Radiobutton(choice_frame, text = i+1, variable=user_choice, value=i, bg='#464646', fg='white', font="Hiragino\ Maru\ Gothic\ ProN 25", padx=10)
            radio.grid(row=0,column=0, sticky="NW")

            def_title = tk.Label(choice_frame, text=word, font="Hiragino\ Maru\ Gothic\ ProN 25", bg='#464646', fg='white')
            def_title.grid(row=0,column=1, sticky="NW")

            definitions_frame = ttk.Frame(core_frame)
            definitions_frame.grid(row=0,column=1, sticky="NW", pady=8)
            
            for j in range(len(definitions)):
                gloss = ttk.Label(definitions_frame, text=definitions[j], wraplength=500, font="Helvetica\ Neue\ Light 15", width=750)
                gloss.grid(row=j, column=0, sticky="NW", pady=5)

            s = ttk.Separator(core_frame, orient='horizontal')
            s.grid(row=1, column=0, columnspan=2, sticky="NSEW", pady=10)

    def save_image(self):
        self.OCR_text = self.OCR_box.get('1.0','end').strip()
        self.currentfile.image = self.currentfile.image.crop(box=self.thumb_cropbox)

    def delete_image(self):

        del self.input_files[self.img_index]
        del self.anki_txt[self.img_index]
        self.seen_images.remove(self.img_index)
        self.prev_image()


    def export(self):
        self.save_image()

        anki_msg = "Choose Anki media folder"
        csv_msg = "Choose where to save CSV file"
        self.anki_folder = filedialog.askdirectory(title = anki_msg, message = anki_msg, parent=self.master)+"/"
        self.csvfile = filedialog.asksaveasfilename(initialfile="ANKI", defaultextension="csv", title = csv_msg, parent=self.master)
        import csv

        thewriter = csv.writer(open(self.csvfile, 'w'))

        for i in self.seen_images:
            file = self.input_files[i]
            thewriter.writerow((file.expression , file.reading , "<br />".join(file.meanings) , f'<img src = "{file.filename}.jpg" />' , file.soundfile))

            file.image.save(f'{self.anki_folder}{file.filename}.jpg')

            if file.type == 'video':
                audioexp = file.sound[file.ChopPoint:]
                audioexp.export(f"{self.anki_folder}{file.filename}.mp3", format="mp3")


    def Google_OCR(self):
        self.currentfile.img_src.seek(0)
        image = vision.types.Image(content=self.currentfile.img_src.read())

        response = client.document_text_detection(image=image, image_context={"language_hints": ["ja"]})
        ocr_text = response.full_text_annotation.text.strip()

        self.OCR_box.insert('1.0', ocr_text)


    def play_audio(self):
        if self.currentfile.type == 'video':

            self.audio_time = self.prog_bar.get()
            playback_sound = self.currentfile.sound[self.audio_time:self.end_time]

            simpleaudio.stop_all()
            
            if self.bar_update:
                self.master.after_cancel(self.bar_update)

            playback = _play_with_simpleaudio(playback_sound)

            self.audio_bar()
        else:
            pass

    def audio_bar(self):

        self.wave_canvas.delete('playline')
        self.audio_time += 100

        self.prog_bar["value"] = self.audio_time

        if self.audio_time < self.end_time:
            self.bar_update = self.master.after(100, self.audio_bar)
            self.wave_canvas.create_line(self.audio_time*self.wave_ratio,0,self.audio_time*self.wave_ratio,self.wave_size[1], width=1, fill='#F8B195', tags='playline')

    def scrub(self, position):
        self.wave_canvas.delete('playline')
        self.audio_time = self.prog_bar.get()

        self.wave_canvas.create_line(self.audio_time*self.wave_ratio,0,self.audio_time*self.wave_ratio,self.wave_size[1], width=1, fill='orange', tags='playline')

    def pause_audio(self):

        if self.bar_update:
            self.master.after_cancel(self.bar_update)

        simpleaudio.stop_all()
        current_time = self.prog_bar.get()

    def replay_audio(self):
        
        self.prog_bar["value"] = self.currentfile.ChopPoint
        self.play_audio()

    def chop_audio(self):
        current_time = self.prog_bar.get()
        self.currentfile.ChopPoint = current_time
        self.wave_canvas.delete('chopline')
        self.wave_canvas.create_line(current_time*self.wave_ratio,0,current_time*self.wave_ratio,self.wave_size[1], width=2, fill='red', tags='chopline')


    def DisableButtons(self):
        self.play_button["state"] = "disabled"
        self.pause_button["state"] = "disabled"
        self.reload_button["state"] = "disabled"
        self.chop_button["state"] = "disabled"
        self.prog_bar.state(['disabled'])

    def EnableButtons(self):
        self.play_button["state"] = "normal"
        self.pause_button["state"] = "normal"
        self.reload_button["state"] = "normal"
        self.chop_button["state"] = "normal"
        self.prog_bar.state(['!disabled'])

    def meaning_choice(self, choice):
        print(choice)

    def open_dir(self):
        open_msg = "Choose a directory of images and videoclips to open"
        mainwindow.src_folder = filedialog.askdirectory(title = open_msg, message = open_msg)+"/"

        self.file_list = os.listdir(self.src_folder)
        self.input_files = [Filetype(file) for file in self.file_list]
        self.input_files = [Filetype.Filesplit(file) for file in self.input_files if file.type != 'none']


        self.currentfile = self.input_files[self.img_index]

        self.anki_txt = ['' for i in self.file_list]
        self.thumb_cropbox = (0,0, self.currentfile.image.width, self.currentfile.image.height)
        #Tells the program the initial thumbnail is an exact proportion to the initial image (this is updated with the new shape when we crop)

        # --- Defaults
        self.current_thumbnail = self.currentfile.image.copy()
        self.current_thumbnail.thumbnail(self.working_size)
        self.main_image = ImageTk.PhotoImage(image=self.current_thumbnail)

        self.cropped_image = self.current_thumbnail
        self.audio_time = 0
        self.bar_update = None

        # -- Changing elements

        # set first image on canvas
        self.image_id = self.canvas.create_image(self.working_size[0]/2, self.working_size[1]/2, image=self.main_image)
        #The values we need to offset our coordinates by for them to be accurate
        self.adj_w = (self.working_size[0]/2) - ((self.cropped_image.width)/2)
        self.adj_h = (self.working_size[1]/2) - ((self.cropped_image.height)/2)


        self.set_image()
        self.keyword_finder()

    def test(self):
        pass
            

class Filetype:
    def __init__(self, file):

        file_ext = file.split(".")[-1]

        self.filename = file.split(".")[0]
        self.file_src = file

        if file_ext in mainwindow.movie_exts:
            self.type = 'video'

        elif file_ext in mainwindow.image_exts:
            self.type = 'image'

        else:
            self.type = 'none'

    def Filesplit(file):

        file.OCR_text = ''
        file.ChopPoint = 0
        file.meanings = ''
        file.formatted_meanings = ''

        if file.type == 'video':

            clip = f'{mainwindow.src_folder}{file.file_src}'
            #FFMPEG pull last frame as png

            try:
                imagebytes, _ = (
                ffmpeg
                .input(clip, sseof=-0.1)
                .output(f'pipe:', vframes=1, format='image2', vcodec='png')
                .run(capture_stdout=True, capture_stderr=True)
                )

            except ffmpeg.Error as e:
                print('stdout:', e.stdout.decode('utf8'))
                print('stderr:', e.stderr.decode('utf8'))
                raise e

            imagedata = io.BytesIO(imagebytes)
            file.img_src = imagedata

            file.image = Image.open(imagedata)
            
            #FFMPEG rip audio as wav
            audiobytes, _ = (
            ffmpeg
            .input(clip)
            .output('pipe:', format='wav')
            .run(capture_stdout=True)
            )

            file.audio = io.BytesIO(audiobytes)

            buf = io.BytesIO()
            buf.seek(0)

            wave_file = wave.open(file.audio, "r")

            # Extract Raw Audio from Wav File
            signal = wave_file.readframes(-1)
            signal = numpy.frombuffer(signal, "<i2")

            fig = plt.figure(figsize=(25,10))
            plt.plot(signal,color='#F67280')
            plt.gca().set_axis_off()
            plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
            plt.margins(0,0)
            plt.savefig(buf,format='png',transparent=True, dpi=20)

            file.waveform = Image.open(buf)
            file.sound = AudioSegment.from_file(file.audio, format('wav'))
            file.soundfile = f'[sound: {file.filename}.mp3]'

            return file


        elif file.type == 'image':
            file.img_src = open(f'{mainwindow.src_folder}{file.file_src}','rb')
            file.image = Image.open(f'{mainwindow.src_folder}{file.file_src}')
            file.soundfile = None
            return file

def TK_LOOP(): 
    root = tk.Tk()
    app = mainwindow(root)
    root.mainloop()

if __name__ == '__main__':
    TK_LOOP()