# Melon

Melon is a Python program for creating fully featured [Anki](https://apps.ankiweb.net/) format flashcards from images and video clips

## Features
**Lookup**

*Melon* uses [EDICT](https://www.edrdg.org/jmdict/edict.html) to provide English definitions of any word highlighted by the user.
It is able to automatically conjugate verbs and adjectives using the custom written plugin JpVerb.
It also has the ability to split a string correctly into seperate words using [SudachiPy](https://github.com/WorksApplications/SudachiPy)

**Audio and frame extraction**

If given a videoclip, *Melon* will extract the audio and the last frame of the video to use as an image.
It will then allow the user to choose a cut point for when they want the audio to begin on their flashcard

**Furigana generation**

The included plugin JpVerb will generate accurate furigana, as well as split it per each individual Kanji.
It can also recognise if the reading is Onyomi or Kunyomi, and will give the furigana in Hiragana or Katakana respectively
For example, the furigana generated for "漢字辞典" would be "漢[かん]字[じ]辞[ジ]典[テン]" rather than "漢字辞典[かんじじてん]"

**OCR**

*Melon* uses the Google vision API to provide accurate OCR for Japanese text in any images, including those extracted from videoclips. This means you can give Melon an image that has onscreen Japanese text (such as a subtitle, or screen from a videogame) and Melon will extract the text from it to allow you to lookup.

**Crop**

*Melon* can crop images to be used on your flashcard - this is useful for manga and other examples where you do not want to put the entire image on the front of your flashcard

**Box Removal**

Melon can remove the grey box from screenshots taken with [OCR Manga Reader](https://sourceforge.net/projects/ocrmangareaderforandroid/)
It can also zoom in to allow you to do this with more precision

**Anki friendly export**

*Melon* will export all media generated with the program (images and audio) along side a CSV file formatted to display beautifully in Anki
Reccomended to use alongside the Melon Anki template (TBC)

## Installation
WIP

## Goals / to do
- [x] ~~Add requirements.txt (urgent)~~ **Done**
- [ ] Installation section
- [x] ~~When a word has multiple definitions, give the user a graphical prompt to choose the correct one~~ **Done**
- [x] ~~Allow user to configure the directory of the clips to be processed, and the save directory~~ **Done**
- [ ] Allow user to provide their own Google API key for OCRing text
- [ ] Convert the application from TkInter to PyQt
- [ ] Create a web based application
- [ ] Reduce the dependencies:
    - [ ] Simpler way to show waveform, without needing matplotlib
    - [ ] Divide images without blend_modes import (or remove divide function)
    - [ ] ~~Remove all JamDict dependecy from JpVerb~~ **Done**
- [x] ~~Redesign UI to be more less ugly~~ **Done**
-  Add User friendly touches:
    - [ ] A "start" screen, with an Open dialog
    - [ ] A carousel of thumbnails of all the cards that have been loaded
    - [ ] Progress bars for cards being loaded in (especially movie clips)
- [ ] Allow user to choose Hiragana or Katakana only for Furigana
- [ ] Allow APKG ecxport
- [ ] Create a repo for the Melon Anki template

## License
[AGPL 3.0](https://choosealicense.com/licenses/agpl-3.0/)
