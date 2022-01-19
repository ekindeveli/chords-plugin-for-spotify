import threading
import time
import SpotiAuth
import ChordScraper
from tkinter import *
import codecs


def backend_script():
    retrieved_song = "none"
    while True:
        token = SpotiAuth.token_response2
        song, artist, is_playing = SpotiAuth.SpotiAuth.currently_playing(token)
        if is_playing:
            if song != retrieved_song:
                lyrics_to_get = f'{song} - {artist}'
                html_source_text, retrieved_song = ChordScraper.ChordScraper.get_chords(song, artist)
                # Show the retrieved lyrics on the GUI
                with open('song_chords.txt', 'w+', encoding='utf-16') as lyrics_file:
                    lyrics_file.write(f'\n{lyrics_to_get}\n\n{html_source_text}')
                txt = Text(root, height=40, width=64, background='#0066CC', foreground='white',
                           wrap=WORD, font='Courier')
                scrollb = Scrollbar(root, command=txt.yview)
                txt['yscrollcommand'] = scrollb.set
                txt.grid(row=0, rowspan=3, columnspan=4, sticky='news')
                with codecs.open('song_chords.txt', 'r', 'utf-16') as f:
                    txt.insert(INSERT, f.read())
                txt.config(state=DISABLED)
                root.update()
            else:
                pass
        else:
            # Print to the GUI 'Spotify is currently not playing any tracks.'
            with open('song_lyrics.txt', 'w+', encoding='utf-16') as lyrics_file:
                lyrics_file.write(f'Spotify is currently not playing any tracks.')
            root.update()
        time.sleep(10)


# Thread 1: Establishing and Maintaining Spotify OAuth Connection
token_response = SpotiAuth.SpotiAuth.initializer()
first_start = True
threading.Thread(target=SpotiAuth.SpotiAuth.recursive_reinit,
                 args=[token_response, first_start], daemon=True).start()

# Creating the Window for the GUI
root = Tk()
root.title("Spotify Chords Plugin")
root.configure(background='#0066CC')
root.minsize(420, 220)
root.maxsize(880, 920)
root.rowconfigure([0, 1, 2], minsize=60, weight=1)
root.columnconfigure([0, 1, 2], minsize=75, weight=1)
root.rowconfigure([3], minsize=60, weight=0)
btn_quit = Button(root, text="Quit", width=12, bg='#0080FF', fg='white', command=root.destroy) \
    .grid(row=3, column=1, sticky='s', padx=5, pady=5)

# Thread 2: Backend Script
threading.Thread(target=backend_script, daemon=True).start()

# Thread 3 (Main Thread): Start GUI
root.mainloop()
