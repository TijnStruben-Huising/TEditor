#!/bin/python3
import sys, curses, os.path

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
            self.selected = {}
        
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
                if not os.path.isfile(filename):
                    with open(filename, "w") as file:
                        pass
                with open(filename) as f:
                    content = f.read().split('\n')
                    for row in content:
                        self.buff.append([ord(c) for c in row])
                self.filename = filename
            except:
                print("error in opening Files")
                sys.exit(1)


        def new_file(self):
            self.reset()
            self.filename = "Untitled.txt"
            self.buff.append([])


    def __init__(self):
        self.currentFile = TEditor.File()
        self.stdscr = None
        curses.init_pair(1,0,1);curses.init_pair(2,2,4);curses.init_pair(3,3,4)
        self.colors = {"Selected":curses.color_pair(1),"GREEN":curses.color_pair(2),"BLUE":curses.color_pair(3)}
        self.mode = 1 #1 is normal #2 is select #3 is edit #4 is command
        self._tempSelect = None

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
        if num == -1:
            return "    |"
        strVersion = str(abs(num) % 1000)
        while len(strVersion) < 3:
            strVersion += " "
        strVersion += " |"
        return strVersion

    def get_selected(self,y):
        def trunc_to_line(self,y):
            currentBest = None
            for selection in self.currentFile.selected:
                if selection == y:
                    return (0, len(self.currentFile.buff[y]))
                elif selection[0][0] <= y and selection[1][0] >= y: #encompases
                    if selection[0][0] < y:
                        xbegin = 0
                    else:
                        xbegin = selection[0][1]
                    if selection[1][0] > y:
                        xend = len(self.currentFile.buff[y])
                    else:
                        xend = selection[1][1]
                    if currentBest == None:
                        currentBest = [(xbegin,xend)]
                    else:
                        currentBest.append((xbegin,xend))
                else:
                    pass
            return currentBest
        truncked = self.trunc_to_line(y)
        ret = []
        for part in truncked:
            index = 0
            while index <= len(ret):
                if index == len(ret):
                    ret.append(part)
                    break
                elif ret[index][0] <= part[0] <= ret[index][1] or ret[index][0] <= part[1] <= ret[index][1]:
                    ret[index] = (min(ret[index][0],part[0]), max(ret[index][1],part[1]))
                    break
                else:
                    index += 1
        return sorted(ret,key= lambda c: c[0])

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

            lineSelection = self.get_selected(index)

            for subLine in range(self.currentFile.lineSizes[index]):

                if termIndex + subLine >= HEIGHT:
                    break


                if subLine == 0:
                    self.stdscr.addstr(termIndex, 0, self.get_line_begin(index) + "".join([chr(x) for x in self.currentFile.buff[index][subLine * WIDTH: (subLine+1) * WIDTH]]))
                else:
                    curses.init_color(1,1000,1000,1000)
                    self.stdscr.addstr(termIndex, 0, self.get_line_begin(-1) + "".join([chr(x) for x in self.currentFile.buff[index][subLine * WIDTH: (subLine+1) * WIDTH]]))
                
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

        #for row, line in enumerate(self.currentFile.buff):
        #    if row < HEIGHT:
        #        self.stdscr.addstr(row, 0, "".join([chr(x) for x in line]))
        #for row, line in enumerate(self.currentFile.buff):
            
        #self.stdscr.move(2,174)

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
        parthesis_end = {ord(x[0]):ord(x[1]) for x in {"{}", "[]", "()"}}
        def ctrl(k): return ((k) & 0x1f)

        k = self.stdscr.getch()

        if k == 265:
            self.mode = 1
        elif k == 266:
            self.mode = 2
        elif k == 267:
            self.mode = 3
        elif k == 268:
            self.mode = 4

        if self.mode == 1:
            if k == ctrl(ord("s")): self.currentFile.save()
            elif k == ctrl(ord("k")): sys.exit(0)

            elif k == 9: [self.insert_ord_char(ord(' ')) for i in range(4)] #enter
            elif k == 8: [self.delete_char() for i in range(4)] #ctrl backspace
            elif k == curses.KEY_BACKSPACE: self.delete_char()
            elif k == ord("\n"): self.insert_line()

            elif k in {curses.KEY_DOWN,curses.KEY_UP,curses.KEY_RIGHT,curses.KEY_LEFT}: self.move_cursor(k)
            elif k == 575: self.currentFile.screenLineNum -= 1 #ctrl up
            elif k == 534: self.currentFile.screenLineNum += 1 #ctrl down
            elif k == 27: self.currentFile.cursx = 0 #esc?
            
            elif ctrl(k) != k: self.insert_ord_char(k)

            if k in parthesis_end:
                self.insert_ord_char(parthesis_end[k])
                self.move_cursor(curses.KEY_LEFT)
            
        elif self.mode == 2:
            if k in {curses.KEY_DOWN,curses.KEY_UP,curses.KEY_RIGHT,curses.KEY_LEFT}: self.move_cursor(k)
            if k == 32: #space
                if self._tempSelect == None:
                    self._tempSelect == (self.currentFile.cursy,self.currentFile.cursx)
                elif self._tempSelect == (self.currentFile.cursy,self.currentFile.cursx):
                    self.currentFile.selected[self.currentFile.cursy] == True #can add ceveral types later on
                    self._tempSelect = None
                else:
                    if self._tempSelect[0] < self.currentFile.cursy:
                        self.currentFile.selected[(self._tempSelect,(self.currentFile.cursy,self.currentFile.cursx))] = True
                    elif self._tempSelect[0] < self.currentFile.cursy:
                        if self._tempSelect[1] < self.currentFile.cursx:
                            self.currentFile.selected[(self._tempSelect,(self.currentFile.cursy,self.currentFile.cursx))] = True
                        else:
                            self.currentFile.selected[((self.currentFile.cursy,self.currentFile.cursx),self._tempSelect)] = True
                    else:
                        self.currentFile.selected[((self.currentFile.cursy,self.currentFile.cursx),self._tempSelect)] = True

            
            if k == 27: #esc
                self.currentFile.selected = {}
        
        #elif k == 27:
        #    self.stdscr.nodelay(True)
        #    k2 = self.stdscr.getch()
        #    if k2 == 127: [self.delete_char() for i in range(4)]
        #    self.stdscr.nodelay(False)

        #PASS BETWEEN MODES WITH FN KEYS OR WITH CTRL NUMBERS
        #modes: write, command, select&move, process(ex make caps)
        


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

        self.stdscr.nodelay(False)
        self.stdscr.keypad(True)
        
        while True: self.main_loop()

def main(stdscr):
    curses.raw()
    t = TEditor()
    t.run(stdscr)

#s = curses.initscr()
#s.addstr(0,0,"a",c)

if __name__ == "__main__":
    curses.wrapper(main)

