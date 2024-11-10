#!/bin/python3
import sys, curses

#with possible inspiration from:
#https://github.com/maksimKorzh/code/blob/master/code.py
#and
#https://wasimlorgat.com/posts/editor.html

class TEditor:
    class File:
        def __init__(self):
            self.cursx = 0
            self.cursy = 0
            self.screenLineNum = 0
            self.buff = []
            self.lineSizes = []
            self.modified = 0
            self.filename = None
        
        def reset(self):
            self.cursx = 0
            self.cursy = 0
            self.screenLineNum = 0
            self.buff = []
            self.lineSizes = []
            self.modified = 0
            self.filename = None

        def update_line_sizes(self,height,width):
            self.lineSizes = []
            for line in self.buff:
                self.lineSizes.append(len(line) // width + (len(line)%width != 0) + (len(line) == 0))

        def save(self):
            self.save_as(self.filename)

        def save_as(self,filename):
            if filename == None:
                sys.exit(1)
                print("cannot save File to None")
            with open(filename, 'w') as f:
                toWrite = ""
                for row in self.buff:
                    toWrite += "".join([chr(c) for c in row]) + '\n'
                f.write(toWrite)
            self.modified = 0
        
        def open_file(self,filename):
            self.reset()
            try:
                with open(filename) as f:
                    content = f.read().split('\n')
                    for row in content:
                        self.buff.append([ord(c) for c in row])
                self.filename = filename
            except:
                sys.exit(1)
                print("error in opening Files")


        def new_file(self):
            self.reset()
            self.filename = "Untitled.txt"
            self.buff.append([])


    def __init__(self):
        self.currentFile = TEditor.File()
        self.stdscr = None

    def adjust_screenLineNum(self):
        HEIGHT , WIDTH = self.stdscr.getmaxyx()
        WIDTH -= 5
        self.currentFile.update_line_sizes(HEIGHT, WIDTH)

        if self.currentFile.cursy < self.currentFile.screenLineNum:
            self.currentFile.screenLineNum = self.currentFile.cursy
        elif self.currentFile.cursy > self.currentFile.screenLineNum:
            def deltaLines():
                ret = 0
                index = self.currentFile.screenLineNum
                while index <= self.currentFile.cursy:
                    ret += self.currentFile.lineSizes[index]
                    index += 1
                return ret
            while deltaLines() > HEIGHT and self.currentFile.cursy != self.currentFile.screenLineNum:
                self.currentFile.screenLineNum += 1
    
    def get_line_begin(self, num):
        strVersion = str(abs(num) % 1000)
        while len(strVersion) < 3:
            strVersion += " "
        strVersion += ": "
        return strVersion

    def refresh_display(self):
        HEIGHT , WIDTH = self.stdscr.getmaxyx()
        WIDTH -= 5
        self.adjust_screenLineNum()

        self.stdscr.erase()

        move_cursor_to = (0,0)

        termIndex = 0
        index = self.currentFile.screenLineNum
        while True:

            if termIndex >= HEIGHT:
                break
            if index >= len(self.currentFile.buff):
                break

            for subLine in range(self.currentFile.lineSizes[index]):

                if termIndex + subLine >= HEIGHT:
                    break
                if subLine == 0:
                    self.stdscr.addstr(termIndex, 0, self.get_line_begin(index) + "".join([chr(x) for x in self.currentFile.buff[index][subLine * WIDTH: (subLine+1) * WIDTH]]))
                else:
                    self.stdscr.addstr(termIndex, 5, "".join([chr(x) for x in self.currentFile.buff[index][subLine * WIDTH: (subLine+1) * WIDTH]]))
                
                if self.currentFile.cursy == index:
                    if subLine * WIDTH <= self.currentFile.cursx < (subLine + 1) * WIDTH:
                        #assert (termIndex,self.currentFile.cursx - subLine * WIDTH) == (0,0), (termIndex,self.currentFile.cursx - subLine * WIDTH)
                        move_cursor_to = (termIndex,self.currentFile.cursx - subLine * WIDTH + 5)

                termIndex += 1
            if self.currentFile.lineSizes[index] == 0:
                self.stdscr.addstr(termIndex, 0, self.get_line_begin(index))
                termIndex += 1
            index += 1
        self.stdscr.move(*move_cursor_to)

    def insert_ord_char(self,char):
        self.currentFile.buff[self.currentFile.cursy].insert(self.currentFile.cursx,char)
        self.currentFile.cursx += 1

    def delete_char(self):
        if self.currentFile.cursx == 0:
            if self.currentFile.cursy == 0:
                pass
            else:
                old = self.currentFile.buff[self.currentFile.cursy]
                del self.currentFile.buff[self.currentFile.cursy]
                self.currentFile.cursy -= 1
                self.currentFile.cursx = len(self.currentFile.buff[self.currentFile.cursy])
                self.currentFile.buff[self.currentFile.cursy].extend(old)
        else:
            del self.currentFile.buff[self.currentFile.cursy][self.currentFile.cursx - 1]
            self.currentFile.cursx -= 1

    def move_cursor(self, which):
        if which == curses.KEY_UP:
            if self.currentFile.cursy == 0:
                self.currentFile.cursx = 0
            else:
                self.currentFile.cursy -= 1
                self.currentFile.cursx = min(self.currentFile.cursx, len(self.currentFile.buff[self.currentFile.cursy]))
        elif which == curses.KEY_DOWN:
            if self.currentFile.cursy == len(self.currentFile.buff) - 1:
                self.currentFile.cursx = len(self.currentFile.buff[self.currentFile.cursy])
            else:
                self.currentFile.cursy += 1
                self.currentFile.cursx = min(self.currentFile.cursx, len(self.currentFile.buff[self.currentFile.cursy]))
        elif which == curses.KEY_LEFT:
            if self.currentFile.cursx == 0:
                if self.currentFile.cursy == 0:
                    pass
                else:
                    self.currentFile.cursy -= 1
                    self.currentFile.cursx = len(self.currentFile.buff[self.currentFile.cursy])
            else:
                self.currentFile.cursx -= 1
        elif which == curses.KEY_RIGHT:
            if self.currentFile.cursx == len(self.currentFile.buff[self.currentFile.cursy]):
                if self.currentFile.cursy == len(self.currentFile.buff) - 1:
                    pass
                else:
                    self.currentFile.cursy += 1
                    self.currentFile.cursx = len(self.currentFile.buff[self.currentFile.cursy])
            else:
                self.currentFile.cursx += 1

    def insert_line(self):
        old = self.currentFile.buff[self.currentFile.cursy][self.currentFile.cursx:]
        self.currentFile.buff[self.currentFile.cursy] = self.currentFile.buff[self.currentFile.cursy][:self.currentFile.cursx]
        self.currentFile.buff.insert(self.currentFile.cursy + 1, old)
        self.currentFile.cursy += 1
        self.currentFile.cursx = 0

    def user_input(self):
        k = self.stdscr.getch()
        def ctrl(k): return ((k) & 0x1f)
        if k == ord("q"): sys.exit(0)
        elif k == ctrl(ord("k")): sys.exit(0)
        elif k == curses.KEY_BACKSPACE: self.delete_char()
        elif k == ord("\n"): self.insert_line()
        elif k in {curses.KEY_DOWN,curses.KEY_UP,curses.KEY_RIGHT,curses.KEY_LEFT}: self.move_cursor(k)
        elif ctrl(k) != k: self.insert_ord_char(k)

    def main_loop(self):
        self.refresh_display()
        self.user_input()

    def run(self,stdscr):
        if len(sys.argv) >= 2:
            fileName = sys.argv[1]
        else:
            fileName = "Untitled.txt"
        self.currentFile.open_file(fileName)

        self.stdscr = stdscr
        
        while True: self.main_loop()

def main(stdscr):
    t = TEditor()
    t.run(stdscr)



if __name__ == "__main__":
    curses.wrapper(main)
