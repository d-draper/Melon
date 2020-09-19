############################################################

# Manga to Anki, V1.4
# 16/07/2020 Momodath -_-

############################################################

import tkinter as tk
from tkinter import ttk

import os, io, csv, re, numpy, blend_modes, wave
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

# --- root loop ---

root = tk.Tk()


# --- Regular functions ---


def original_coords(A_coords, crop_box, new_thumbnail):
    
    #A_co_ords = the coordinate we want to translate
    #crop_box = the co-ordinates of the crop on the larger image
    #new_thumbnail = the new sized thumbnail crop

    new_ratio = (crop_box[2] - crop_box[0]) / new_thumbnail.width
    B_coords = [(i * new_ratio) for i in A_coords]
    C_coords = [(crop_box[0] + B_coords[0]), (crop_box[1] + B_coords[1])]
    return C_coords


# --- Event functions

def click(event):
    global one_x, one_y
    one_x, one_y = event.x, event.y

def click_move(event):
    if zoom_io:
        pass
    else:
        canvas.delete('rec', 'refline')

        cropbox_shadow = canvas.create_rectangle((one_x+1, one_y+1, event.x+1, event.y+1), outline="purple", dash= (10,10), width=2, tags='rec')  
        cropbox = canvas.create_rectangle((one_x, one_y, event.x, event.y), outline="yellow", dash= (10,10), width=2, tags='rec')

def upclick(event):
    if zoom_io:
        zoom_in(event)
    else:
        global cropped_image
        global image_replace
        global thumb_cropbox
        global adj_w, adj_h

        cropbox = canvas.create_rectangle((one_x, one_y, event.x, event.y), tags='rec')
        cbox = canvas.coords(cropbox)
        cbox[0:4] = cbox[0]-adj_w, cbox[1]-adj_h, cbox[2]-adj_w, cbox[3]-adj_h

        firstx, firsty, secondx, secondy = cbox

        canvas.delete('rec')

        if secondx > cropped_image.width:
            secondx = cropped_image.width
        if secondy > cropped_image.height:
            secondy = cropped_image.height

        if firstx < 0:
            firstx = 0
        if firsty < 0:
            firsty = 0

        #Image replacement
        thumb_cropbox = [original_coords(i, thumb_cropbox, cropped_image) for i in ([firstx,firsty],[secondx,secondy])]
        thumb_cropbox = thumb_cropbox[0] + thumb_cropbox[1]
        
        cropped_image = imagelist[img_index].crop(box=thumb_cropbox)
        cropped_image.thumbnail(working_size)
        
        image_replace = ImageTk.PhotoImage(cropped_image)
        canvas.itemconfig(image_id, image=image_replace)

        # There should be a way to do this cleaner (not call it twice):
        adj_w = (working_size[0]/2) - ((cropped_image.width)/2)
        adj_h = (working_size[1]/2) - ((cropped_image.height)/2)


def outer_click(event):
    global direction
    global horiz_area, vert_area

    #For the checkerboard display
    horiz_area = range(int(adj_w),int(working_size[0]-adj_w))
    vert_area = range(int(adj_h),int(working_size[1]-adj_h))

    if event.x <= outerbr_width:
        direction = 'l'

    elif event.x >= working_size[0]:
        direction = 'r'

    elif event.y <= outerbr_width:
        direction = 't'

    elif event.y >= working_size[1]:
        direction = 'b'

def ref_line(event):
    global refline #So we can retrive the coordinates

    canvas.delete('refline')

    checker_space = 4

    if direction == 'l' or direction == 'r':
        refline_xy = (event.x, 0, event.x, working_size[1])        
        if direction == 'l':
            checker = [canvas.create_line(horiz_area[0],i, event.x, i) for i in vert_area[::checker_space] if event.x>horiz_area[0]] 
        if direction == 'r':
            checker = [canvas.create_line(horiz_area[-1],i, event.x, i) for i in vert_area[::checker_space] if event.x<vert_area[-1]] 
    if direction == 't' or direction == 'b':
        refline_xy = (0, event.y, working_size[0], event.y)
        if direction == 't':
            checker = [canvas.create_line(i,vert_area[0], i, event.y) for i in horiz_area[::checker_space] if event.y>vert_area[0]] 
        if direction == 'b':
            checker = [canvas.create_line(i,vert_area[-1], i,event.y) for i in horiz_area[::checker_space] if event.x<vert_area[-1]]

    [canvas.itemconfig(i, width=1, dash=(1,checker_space), fill='orange', tags='refline') for i in checker]
        
    refline_shadow = canvas.create_line(refline_xy, dash= None, width=1, fill='red', tags='refline')
    refline = canvas.create_line(refline_xy, dash= (10,5), width=1, fill='cyan', tags='refline')

def box_removal(xy):
    global imagelist #preserves our RGBA conversion
    global image_replace #prevents garbage collection 
    global adj_w, adj_h, cropped_image, thumb_cropbox, zoomed

    print(zoomed)
    if zoomed:
        cropbox = zoombox
    else:
        cropbox = thumb_cropbox
    xy = original_coords([xy[0]-adj_w, xy[1]-adj_h], cropbox, cropped_image)

    def check_direction():
        if direction == 'l':
            return (0,0,  xy[0], imagelist[img_index].height)
        if direction == 'r':
            return (xy[0], imagelist[img_index].height, imagelist[img_index].width, 0)
        if direction == 't':
            return (0,0, imagelist[img_index].width, xy[1])
        if direction == 'b':
            return (0, imagelist[img_index].height, imagelist[img_index].width, xy[1])
    rec_dims = check_direction()

    RGB_colour = (112,112,112)

    imagelist[img_index] = imagelist[img_index].convert('RGBA')
    divide_map= Image.new('RGBA', (imagelist[img_index].width, imagelist[img_index].height), color='white')

    img1 = ImageDraw.Draw(divide_map)
    img1.rectangle(rec_dims, fill=RGB_colour, outline=None)

    # Import background image
    background_img_raw = imagelist[img_index]  # RGBA image
    background_img = numpy.array(background_img_raw)  # Inputs to blend_modes need to be numpy arrays.
    background_img_float = background_img.astype(float)  # Inputs to blend_modes need to be floats.

    # Import foreground image
    foreground_img_raw = divide_map  # RGBA image
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
    imagelist[img_index] = blended_img_raw.crop(box=thumb_cropbox)
    zoomed = False
    set_image()

def toggle_zoom():
    global zoom_io
    if zoom_io == False:
        zoom_io = True
        root.config(cursor='crosshair')
    else:
        zoom_io = False
        root.config(cursor='arrow')

def zoom_in(event):
    global zoomed_img #Prevents the image getting garbage collected
    global zoom_io, zoombox, adj_w, adj_h, cropped_image, zoomed

    if zoomed:
        zoomed = False
        toggle_zoom()
        set_image()

    else:
        event.x, event.y = event.x - adj_w, event.y - adj_h
        zoom_coords = original_coords([event.x,event.y], thumb_cropbox, cropped_image)
        #These if statements adjust for the user clicking out of bounds
        if zoom_coords[0] > imagelist[img_index].width:
            zoom_coords[0] = imagelist[img_index].width
        if zoom_coords[1] > imagelist[img_index].height:
            zoom_coords[1] = imagelist[img_index].height
        if zoom_coords[0] < 0:
            zoom_coords[0] = 0
        if zoom_coords[1] < 0:
            zoom_coords[1] = 0

        x_buffer = working_size[0]/2
        y_buffer = working_size[1]/2

        scale = 10

        zoombox = [zoom_coords[0]-(x_buffer/scale), zoom_coords[1]-(y_buffer/scale), zoom_coords[0]+(x_buffer/scale), zoom_coords[1]+(y_buffer/scale)]
        #thumb_cropbox = zoombox
        zoomed_img = imagelist[img_index].crop(zoombox)
        zoomed_img = zoomed_img.resize([zoomed_img.width*scale,zoomed_img.height*scale], resample = 0)

        adj_w = (working_size[0]/2) - ((zoomed_img.width)/2)
        adj_h = (working_size[1]/2) - ((zoomed_img.height)/2)
        cropped_image = zoomed_img

        zoomed_img = ImageTk.PhotoImage(image=zoomed_img)
        canvas.itemconfig(image_id, image=zoomed_img)

        zoomed = True
        zoom_io = True


def next_image():
    global img_index

    save_image() #Saves current crop before moving on

    if img_index == len(imagelist)-1:
        img_index = 0
    else:
        img_index += 1

    set_image()
    lookup()

def prev_image():
    global img_index

    save_image() #Saves current crop before moving on

    if img_index > 0:
        img_index -= 1
    else:
        img_index = len(imagelist)-1

    set_image()
    lookup()

def reset_image():
    global imagelist
    
    original_image = Image.open(src_folder+'/'+image_files[img_index])
    imagelist[img_index] = original_image

    set_image()


def set_image():
    global cropped_image, adj_w,adj_h
    global image_replace # to stop it getting deleted from memory
    global thumb_cropbox

    #If you tidy this be very aware of the memory cache! (it is not deleted immediately)
    #That is why we have image_replace set to global, to make sure it doesn't get deleted from memory

    canvas.delete('refline')
    info_box.delete('1.0', 'end')
    OCR_box.delete('1.0', 'end')

    current_thumbnail = imagelist[img_index].copy()
    current_thumbnail.thumbnail(working_size)
    image_replace = ImageTk.PhotoImage(current_thumbnail)
    canvas.itemconfig(image_id, image=image_replace)

    thumb_cropbox = thumb_cropbox = (0,0,   imagelist[img_index].width,imagelist[img_index].height)
    cropped_image = current_thumbnail

    adj_w = (working_size[0]/2) - ((cropped_image.width)/2)
    adj_h = (working_size[1]/2) - ((cropped_image.height)/2)

    seen_images.add(img_index)
    
def lookup():
    global anki_txt
    
    jptextfinder = re.compile(r'''[\u4E00-\u9FBF|\u3005-\u30FF]+''')
    filename_keywords = jptextfinder.findall(image_files[img_index])

    squiggle_word = re.compile(r'''(?:{)(.+?)(?:})''')
    OCR_text_box = OCR_box.get('1.0','end').strip()

    keywords = filename_keywords
    expression = ("・").join(filename_keywords)

    if filename_keywords:
        meanings = [jp.jplookup(keyword) for keyword in filename_keywords]

    elif OCR_text_box != '':
        OCR_keywords = squiggle_word.findall(OCR_text_box)
        meanings = [jp.jplookup(keyword) for keyword in OCR_keywords]
        keywords = OCR_keywords
        expression = OCR_text_box


    else:
        meanings = ["No lookup word found in file: " + image_files[img_index]]
        
    for i in range(len(keywords)):
        info_box.insert('1.0', keywords[i] + "\n--------\n" + meanings[i][0] + "\n\n")
    
    expression = expression.replace('\n','<br />').replace('{','<span class="keyword" style="color:#cb4b16">').replace("}","</span>")
    reading = jp.generate_furigana(expression)

    anki_txt[img_index] = f'''{expression}\t{reading}\t{("<br />").join([i[0] for i in meanings])}\t'<img src="{image_files[img_index]}">\t'''

def save_image():
    global imagelist

    imagelist[img_index] = imagelist[img_index].crop(box=thumb_cropbox)

def delete_image():
    global image_files
    global imagelist
    global anki_txt
    global seen_images

    del image_files[img_index]
    del imagelist[img_index]
    del anki_txt[img_index]
    seen_images.remove(img_index)

    set_image()
    lookup()


def export():

    save_image()

    with open(src_folder+"Manga_export.txt", "w") as output:
        output.write(("\n").join([anki_txt[i] for i in seen_images]))

    [i.save(anki_folder+f"{image_files[imagelist.index(i)]}") for i in seen_images]
    
    print("\nExported.")
    print("txt saved to: " + src_folder+"Manga_export.txt")
    print("Images saved anki media folder ("+anki_folder+")")

def Google_OCR():
    
    img_src = f'{src_folder}{image_files[img_index]}'

    with io.open(img_src, 'rb') as img_file:
        content = img_file.read()

    image = vision.types.Image(content=content)

    response = client.document_text_detection(image=image, image_context={"language_hints": ["ja"]})
    ocr_text = response.full_text_annotation.text.strip()

    OCR_box.insert('1.0', ocr_text)


def play_audio():

    global end_time
    global audio_time

    audio_time = prog_bar.get()
    playback_sound = sound[audio_time:end_time]

    simpleaudio.stop_all()
    
    if bar_update:
        root.after_cancel(bar_update)

    playback = _play_with_simpleaudio(playback_sound)

    audio_bar()

def audio_bar():
    global audio_time
    global bar_update

    audio_time += 20

    prog_bar["value"] = audio_time
    if audio_time < end_time:
        bar_update = root.after(20, audio_bar)


def pause_audio():

    if bar_update:
        root.after_cancel(bar_update)

    simpleaudio.stop_all()

    current_time = prog_bar.get()
    print(current_time)

def replay_audio():
    
    prog_bar["value"] = 0
    play_audio()

def chop_audio():
    pass


# --- define images ----

img_index = 0
#This is iterated over later

seen_images = set()
#A set we will add to

zoom_io = False
zoomed = False

working_size = (600, 600)
outerbr_width = 15

anki_folder = '/Users/earth/Library/Application Support/Anki2/User 1/collection.media/'
#anki_folder = '/Users/earth/Downloads/'

src_folder = '/Users/earth/Documents/Japanese/Media/Manga/OCR screens/'

file_list = os.listdir(src_folder)
video_files = [i for i in file_list if i[-4:] in ['.mov']]

image_files = [i for i in os.listdir(src_folder) if i[-4:] in ['.jpg','.jpeg','.png']]
imagelist = [Image.open(src_folder+filename) for filename in image_files]

anki_txt = ['' for i in file_list]

thumb_cropbox = (0,0,   imagelist[img_index].width,imagelist[img_index].height)
#Tells the program the initial thumbnail is an exact proportion to the initial image (this is updated with the new shape when we crop)

current_thumbnail = imagelist[img_index].copy()
current_thumbnail.thumbnail(working_size)

main_image = ImageTk.PhotoImage(image=current_thumbnail)

cropped_image = current_thumbnail


audio_file = '/Users/earth/Desktop/GAME/EXPORT/11.5.mp3'
sound = AudioSegment.from_file(audio_file, format('mp3'))
waveform_img = Image.open('/Users/earth/Desktop/GAME/EXPORT/lucas.png')
waveform_img = waveform_img.resize((300,100))
waveform_img = ImageTk.PhotoImage(waveform_img)

end_time = len(sound)

audio_time = 0
bar_update = None


# --- GUI elements and bindings ---

#Frames
canvas_frame = tk.Frame(root, borderwidth= outerbr_width, relief = "sunken")
info_frame = tk.Frame(root, borderwidth= 5, relief = "sunken")
player_frame = tk.Frame(info_frame, height= 100, width = 100, borderwidth= 1, relief = "sunken")


canvas_frame.bind('<Button-1>', outer_click)
canvas_frame.bind('<B1-Motion>', ref_line)

# Canvas
canvas = tk.Canvas(canvas_frame, width=working_size[0], height=working_size[1])
canvas.bind("<Button-1>", click)
canvas.bind("<B1-Motion>", click_move)
canvas.bind("<ButtonRelease-1>", upclick)

# Buttons
reset_button = ttk.Button(root, text="RESET", command=reset_image)
prev_button = ttk.Button(root, text="Previous Image", command= prev_image)
next_button = ttk.Button(root, text="Next Image", command= next_image)
save_button = ttk.Button(root, text="Delete", command= delete_image)

zoom_button = ttk.Button(info_frame, text="Zoom", command=toggle_zoom)

OCR_button = ttk.Button(info_frame, text="OCR", command = Google_OCR)
lookup_button = ttk.Button(info_frame, text="Lookup", command = lookup)
export_button = ttk.Button(info_frame, text="Export", command = export)
box_remove_button = ttk.Button(info_frame, text="Remove box", command = lambda: box_removal(canvas.coords(refline)))

#Audio player
play_button = ttk.Button(player_frame, text="▶", width=2, command = play_audio)
pause_button = ttk.Button(player_frame, text="❚❚", width=2, command = pause_audio)
reload_button = ttk.Button(player_frame, text="⟳", width=2, command=replay_audio)
chop_button = ttk.Button(player_frame, text="✂", width=2, command=chop_audio)
waveform = ttk.Label(player_frame, image=waveform_img)
prog_bar = ttk.Scale(player_frame, orient='horizontal', length=300, from_=1.0, to=end_time)

#OCR_output
OCR_box = tk.Text(info_frame, width = 45, height = 5, borderwidth=2, relief="sunken", wrap='word')

#Info box
info_box = tk.Text(info_frame, width = 45, borderwidth=2, relief="sunken", wrap='word')
info_scroll = ttk.Scrollbar(info_frame, orient='vertical', command=info_box.yview)
info_box.configure(yscrollcommand=info_scroll.set)





# -- Gridding --

canvas.grid()

canvas_frame.grid(row=1, column=0, columnspan= 4)
info_frame.grid(row=0, rowspan=2, column=4, sticky='N,S')
player_frame.grid(row = 8, columnspan = 2)

OCR_box.grid(row=0,column=0, sticky='N')

info_box.grid(row=1, column=0)
info_scroll.grid(row=1, column=1, sticky='N,S,W')

export_button.grid(row=2, columnspan=2, sticky='S')
zoom_button.grid(row = 3, columnspan= 2)
box_remove_button.grid(row=4, columnspan=2)
OCR_button.grid(row=5, columnspan=2)
lookup_button.grid(row=6, columnspan=2)

reset_button.grid(row=0, column = 0)
prev_button.grid(row=0, column=1)
next_button.grid(row=0, column= 2)
save_button.grid(row=0, column =3)

play_button.grid(row=0, column=1)
pause_button.grid(row=0, column=2)
reload_button.grid(row=0, column=3)
chop_button.grid(row=0, column=4)
prog_bar.grid(row=1, columnspan=5)
waveform.grid(row=2, columnspan=5)


# -- Changing elements

# set first image on canvas
image_id = canvas.create_image(working_size[0]/2, working_size[1]/2, image=main_image)
#The values we need to offset our coordinates by for them to be accurate
adj_w = (working_size[0]/2) - ((cropped_image.width)/2)
adj_h = (working_size[1]/2) - ((cropped_image.height)/2)


set_image()
lookup()

# ---- end loop ----
root.mainloop()