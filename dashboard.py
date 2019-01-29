import sys,os
import curses
import json
from curses import wrapper

def main(s):


    s = curses.initscr()
    curses.curs_set(2)
    # Clear and refresh the screen for a blank canvas
    s.clear()
    s.refresh()
    sh, sw = s.getmaxyx()

    w = curses.newwin(sh, sw, 0, 0)
    w.keypad(1)
    w.timeout(1000)

    if curses.has_colors():
        curses.start_color()

    #(color id, foreground, background)
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)


    k = 0
    cursor_x = 0
    cursor_y = 0


    #read data file
    with open('data2.txt', 'r') as datafile:
        datafile.seek(0) #start of file
        first_char = datafile.read(1) #get the first character
        if not first_char:
            print ("Data File is Empty - Kindly execute retail.py to start data collection")
            #first character is the empty string..
        else:
            datafile.seek(0) #first character wasn't empty, return to start of file.
            # load file into variables
            data = json.load(datafile)


    while (k != ord('q')):

        if k == curses.KEY_DOWN:
            cursor_y = cursor_y + 1
        elif k == curses.KEY_UP:
            cursor_y = cursor_y - 1
        elif k == curses.KEY_RIGHT:
            cursor_x = cursor_x + 1
        elif k == curses.KEY_LEFT:
            cursor_x = cursor_x - 1

        cursor_x = max(0, cursor_x)
        cursor_x = min(sw, cursor_x)

        cursor_y = max(0, cursor_y)
        cursor_y = min(sh, cursor_y)

        # Declaration of strings
        title = "Retail Video Analytics Dashboard"[:sw-1]
        subtitle = "Written by Clarence"[:sw-1]
        keystr = "Last key pressed: {}".format(k)[:sw-1]
        statusbarstr = "Press 'q' to exit | STATUS BAR | Pos: {}, {}".format(cursor_x, cursor_y)


        # Centering calculations
        start_x_title = int((sw // 2) - (len(title) // 2) - len(title) % 2)
        start_x_subtitle = int((sw // 2) - (len(subtitle) // 2) - len(subtitle) % 2)
        start_x_keystr = int((sw // 2) - (len(keystr) // 2) - len(keystr) % 2)
        start_y = int((sh // 2) - 2)


        # Render status bar
        s.attron(curses.color_pair(3))
        s.addstr(sh-1, 0, statusbarstr)
        s.addstr(sh-1, len(statusbarstr), " " * (sw - len(statusbarstr) - 1))
        s.attroff(curses.color_pair(3))

        # Turning on attributes for title
        s.attron(curses.color_pair(2))
        s.attron(curses.A_BOLD)

        # Rendering title
        s.addstr(start_y, start_x_title, title)

        # Turning off attributes for title
        s.attroff(curses.color_pair(2))
        s.attroff(curses.A_BOLD)


        # Print rest of text
        s.addstr(start_y + 1, start_x_subtitle, subtitle)
        s.addstr(start_y + 3, (sw // 2) - 2, '-' * 4)
        s.addstr(start_y + 5, start_x_keystr, keystr)
        s.move(cursor_y, cursor_x)




        # Rendering some text
        whstr = "   VIDEO RETAIL ANALYTICS - Overview"
        s.addstr(0, 0, whstr, curses.A_REVERSE)
        s.chgat(-1, curses.A_REVERSE)

        itemheaders = ["Date/Time", "Gender", "ID", "Activity", "Attire Top", "Attire Bottom", "Location(x,y)", "Size"]

        colNo = 2
        for item in itemheaders:

            s.addstr(2, colNo, item, curses.color_pair(2))
            s.addstr(3, colNo-1, "-"*(len(item)+2), curses.color_pair(1))
            colNo = colNo + len(item) + 5




        # Refresh the screen
        s.refresh()

        # Wait for next input
        k = s.getch()

wrapper(main)




