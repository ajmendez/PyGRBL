import curses, curses.textpad, sys, time
import readline, rlcompleter




def validator(c):
  if c == curses.ascii.NL or c == curses.ascii.CR:
    return curses.ascii.BEL
  elif c == curses.erasechar():
    return curses.ascii.BS
  else:
    return c
def docommand(c=' '):
  if c == curses.ascii.BS:
    c=''
    return True
  # elif c == ord(curses.ascii.ctrl('d')):
  #   return ''
  return False




# class Textbox(curses.textpad.Textbox):
#   def __init__(self, window, insert_mode=False):
#     curses.textpad.Textbox.__init__(self, window, insert_mode=insert_mode)
#   def edit(self, validate=None):
#     while 1:
#       ch=


def main(screen):
  height, width = screen.getmaxyx()
  
  
  box = curses.textpad.Textbox(screen)
  text = box.edit()
  
  sys.exit()
  
  # screen.nodelay(1)
  # readline.parse_and_bind('tab: complete')
  screen.border()
  screen.addstr(1,1,'Enter some text:')
  screen.refresh()
  
  
  
  
  
  
  textwin = curses.newwin(1,width-2,2,1)
  textwin.scrollok(True)
  box = curses.textpad.Textbox(textwin,insert_mode=True)
  # box.docommand = docommand
  i=3
  while 1:
    textwin.erase()
    text = box.edit(validator)
    
    
    
    # curses.nocbreak()
    # screen.keypad(0)
    # curses.echo()
    # curses.noraw()
    # screen.refresh()
    # text = raw_input()
    # # text = sys.stdin.readline() 
    # curses.noecho()
    # curses.cbreak()
    # screen.keypad(1)
    # curses.raw()
    
    screen.addstr(i,4,"%d, %s"%(i, text.encode('utf_8')))
    screen.refresh()
    i += 1
    if i > height: i=3
    if 'q' in text: break
  sys.exit()
  


curses.wrapper(main)