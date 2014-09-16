#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame as pg
import pygame
pg.font.init()

class MenuSystem(list,object):
    
    bgcolor      = pg.Color('grey22')
    fgcolor      = pg.Color('grey91')
    bghightlight = pg.Color('darkorange2')
    fglowlight   = pg.Color('grey10')
    frame_left   = pg.Color((0xff+bgcolor.r*2)//3,(0xff+bgcolor.g*2)//3,(0xff+bgcolor.b*2)//3)
    frame_right  = pg.Color(bgcolor.r//2,bgcolor.g//2,bgcolor.b//2)
    
    class Menu_(pg.Rect,object):
        
        def __init__(self,items,pos,font):
            
            self.scr               = pg.display.get_surface()
            self.items             = items
            self.exc               = items.exc
            self.font              = font
            w,h                    = max([font.size(' %s '%(i.label if type(i)==Menu else i)) for i in items])
            self.interline            = int(h*0.3)
            self.item_h            = h + self.interline
            
            pg.Rect.__init__(self,pos,(w+self.item_h,(self.item_h)*len(items)))
            self.clamp_ip(self.scr.get_rect())
            
            self.itemsrect         = self.copy()
            foo                    = self.clip(self.scr.get_rect())
            self.topleft,self.size = foo.topleft,foo.size
            self.itemsrect.top     = self.top
            self.item_index        = -1
            self.first_opening     = False
            self.offset            = 0
        
        def update(self,ev):
            
            if ev.type == pg.MOUSEMOTION and self.collidepoint(ev.pos):
                x,y             = ev.pos
                self.item_index = (y-self.itemsrect.y)//(self.item_h)-self.offset
                return self.item_index + self.offset
        
        def screen(self):
            
            if not self.first_opening:
                self.bg = self.scr.subsurface(self).copy()
                self.first_opening = True
            self.scr.fill(MenuSystem.bgcolor,self)
            if self.item_index+self.offset>=0 and self.item_index+self.offset not in self.exc: self.scr.fill(MenuSystem.bghightlight,(self.x,self.item_index*(self.item_h)+self.y-(self.top-self.itemsrect.top)%self.item_h,self.w,self.item_h))
            b = self.itemsrect.y+self.interline//2
            for e,i in enumerate(self.items):
                self.scr.blit(self.font.render(' %s '%(i.label if type(i)==Menu else i),1,MenuSystem.fgcolor if e not in self.exc else MenuSystem.fglowlight),(self.x,b))
                if type(i)==Menu:
                    r = pg.Rect(self.right-self.item_h,b-self.interline//2,self.item_h,self.item_h).inflate(-self.interline*3,-self.interline*3)
                    pg.draw.polygon(self.scr,MenuSystem.fgcolor if e not in self.exc else MenuSystem.fglowlight,(r.topleft,r.midright,r.bottomleft),0)
                    pg.draw.aalines(self.scr,MenuSystem.fgcolor if e not in self.exc else MenuSystem.fglowlight,1,(r.topleft,r.midright,r.bottomleft),1)
                b+=self.item_h
            s = self.inflate(-2,-2)
            pg.draw.rect(self.scr,MenuSystem.frame_left,self,1)
            pg.draw.lines(self.scr,MenuSystem.frame_right,0,(s.topright,s.bottomright,s.bottomleft),1)
    
    def __init__(self):
        
        self.OUTPUT   = None
        self.todelete = []
        self.boxid  = self.itemid = -1
    
    def update(self,ev):
        
        self.todelete = []
        if ev.type == pg.MOUSEMOTION and self:
            self.foo = True
            boxid = pg.Rect(ev.pos,(0,0)).collidelistall(self)
            if boxid:
                boxid  = boxid[-1]
                itemid = self[boxid].update(ev)
                if (boxid,itemid) != (self.boxid,self.itemid):
                    self.todelete.extend(self[boxid+1:])
                    del(self[boxid+1:])
                    if type(self[boxid].items[itemid]) == Menu and itemid not in self[boxid].exc:
                        px = self[boxid].right
                        py = self[boxid].itemsrect.top + self[boxid].itemsrect.h//len(self[boxid].items)*itemid
                        self.append(MenuSystem.Menu_(self[boxid].items[itemid],(px,py),self.font))
                    self.boxid,self.itemid = boxid,itemid
                    return True
            else:
                self.boxid,self.itemid     = -1,-1
                ret = self[-1].item_index != -1
                self[-1].item_index        = -1
                return ret
        elif ev.type == pg.MOUSEBUTTONUP and self:
            if pg.Rect(ev.pos,(0,0)).collidelistall(self):
                if self[-1].item_index == -1 or ev.button not in (1,4,5) or self.itemid in self[self.boxid].exc: return
                elif ev.button == 1:
                    self.OUTPUT = [i.item_index+i.offset for i in self]
                    self.boxid,self.itemid     = -1,-1
                elif ev.button == 5:
                    if self[-1].itemsrect.bottom - self[-1].bottom >= self[-1].item_h:
                        self[-1].itemsrect.bottom  -= self[-1].item_h
                        self[-1].offset            += 1
                    else: self[-1].itemsrect.bottom = self[-1].bottom
                    return True
                elif ev.button == 4:
                    if self[-1].top - self[-1].itemsrect.top >= self[-1].item_h:
                        self[-1].itemsrect.top  += self[-1].item_h
                        self[-1].offset         -= 1
                    else: self[-1].itemsrect.top = self[-1].top
                    return True
            if self.foo:
                self.todelete.extend(self)
                del(self[:])
                return True
            else: self.foo = True
            
    
    def set(self,menu,pos,font=pg.font.Font(None,25)):
        
        if self:
            self.todelete.extend(self)
            del(self[:])
        self.boxid  = self.itemid = -1
        self.OUTPUT = None
        self.append(MenuSystem.Menu_(menu,pos,font))
        self.font   = font
        self.foo = False
    
    def erase(self):
        
        ret = self.todelete[:]
        for menu in self.todelete[::-1]:
            menu.scr.blit(menu.bg,menu)
        self.todelete = []
        return ret
    
    def draw(self):
        
        for menu in self:
            menu.screen()
        return self
    
    def screen(self):
        
        return self.erase()+self.draw()
    
    @property
    def mouse_over(self): return self.itemid != -1
    

class Menu(list):
    
    def __init__(self,items,label=None,exc=()):
        
        self.extend(items)
        self.label = label
        self.exc   = exc
        
    def items(self,indices):
        
        foo     = self
        output  = []
        for i in indices:
            foo = foo[i]
            output.append(foo if type(foo) == str else foo.label)
        return output

class BarSystem(pg.Rect,object):
    
    class BarButton(pg.Rect):
        
        def __init__(self,menu,pos,font):
            w,h            = font.size(menu.label)
            self.margin    = font.size('X')[0]
            self.interline = h*0.3
            self.menu      = menu
            self.label     = menu.label
            pg.Rect.__init__(self,pos,(w+self.margin,h*1.3))
            
    def __init__(self,menus,font=pg.font.Font(None,25)):
        self.scr = pg.display.get_surface()
        foo = (0,0)
        self.buttons = []
        for menu in menus:
            self.buttons.append(BarSystem.BarButton(menu,foo,font))
            foo      = self.buttons[-1].topright
        pg.Rect.__init__(self,0,0,self.scr.get_width(),font.size('X')[1]*1.3)
        self.ms = MenuSystem()
        self.actual  = None
        self.memo    = None
        self.OUTPUT  = None
        self.font    = font
    
    def update(self,ev):
        ret     = None
        if self.ms.update(ev): ret = True
        if ev.type == pg.MOUSEMOTION:
            x,y = ev.pos
            idx = pg.Rect(x,y,0,0).collidelist(self.buttons)
            if idx == -1:
                if self.actual > -1:
                    self.actual = None
                    ret = True
            elif self.actual != idx:
                self.actual   = idx
                if self.ms:
                    self.ms.set(self.buttons[self.actual].menu,self.buttons[self.actual].bottomleft,self.font)
                    self.memo = self.actual
                ret = True
        elif ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1 and self.actual > -1:
            self.ms.set(self.buttons[self.actual].menu,self.buttons[self.actual].bottomleft,self.font)
            self.memo = self.actual
            ret       = True
        self.OUTPUT   = ([self.memo]+self.ms.OUTPUT) if self.ms.OUTPUT else None
        return ret
            
    def screen(self):
        r  = self.ms.erase()
        self.scr.fill(MenuSystem.bgcolor,self)
        if self.actual > -1:
            self.scr.fill(MenuSystem.bghightlight,self.buttons[self.actual])
        elif self.ms:
            self.scr.fill(MenuSystem.bghightlight,self.buttons[self.memo])
        for i in self.buttons:
            self.scr.blit(self.font.render(i.label,1,MenuSystem.fgcolor),i.inflate(-i.margin,-i.interline))
        r += self.ms.draw()
        s  = self.inflate(-2,-2)
        pg.draw.rect(self.scr,MenuSystem.frame_left,self,1)
        pg.draw.lines(self.scr,MenuSystem.frame_right,0,(s.topright,s.bottomright,s.bottomleft),1)
        return [self]+r


class TextBox:
    def __init__(self, rect, width=10):
        self.selected = False
        self.font_size = 18
        self.font = pygame.font.SysFont('Arial', self.font_size)
        self.str_list = []
        self.width = width
        self.color = (100,100,100)
        self.rect = rect
        self.string = ''.join(self.str_list)
        
    def char_add(self, event):
        '''modify string list based on event.key'''
        if event.key == pygame.K_BACKSPACE:
            if self.str_list:
                self.str_list.pop()
        elif event.key == pygame.K_RETURN:
            return ''.join(self.str_list)
        elif event.key in [pygame.K_TAB, pygame.K_KP_ENTER]:#unwanted keys
            return False
        elif event.key == pygame.K_DELETE:
            self.str_list = []
            return False
        else:
            char = event.unicode
            if char: #stop emtpy space for shift key adding to list
                self.str_list.append(char)

    def update(self, scr):

        
        if self.selected:
            width = 2
        else:
            width = self.width
        
        s = ''.join(self.str_list)
        if len(s) > 0:
            for n, l in enumerate(s):
                if self.font.size(s[n:])[0] < self.rect.width:
                    label = self.font.render(s[n:], 1, self.color)
                    break
        else:
            label = self.font.render(s, 1, self.color)
        
        self.string = ''.join(self.str_list)
        pygame.draw.rect(scr, self.color, self.rect, width)
        scr.blit(label, self.rect)

class Button:
    def __init__(self, text, rect):
        self.text = text
        self.is_hover = False
        self.default_color = (100,100,100)
        self.hover_color = (255,255,255)
        self.font_color = (0,0,0)
        self.rect = rect
        
    def label(self):
        '''button label font'''
        font = pygame.font.Font(None, 20)
        return font.render(self.text, 1, self.font_color)
        
    def color(self):
        '''change color when hovering'''
        if self.is_hover:
            return self.hover_color
        else:
            return self.default_color
            
    def update(self, screen):
        pygame.draw.rect(screen, self.color(), self.rect)
        screen.blit(self.label(), self.rect)
        
        #change color if mouse over button
        self.check_hover(pygame.mouse.get_pos())
        
    def check_hover(self, mouse):
        '''adjust is_hover value based on mouse over button - to change hover color'''
        if self.rect.collidepoint(mouse):
            self.is_hover = True 
        else:
            self.is_hover = False


        
# ************* TEST ***************************
if __name__ == "__main__":
    scr = pg.display.set_mode((1080,600))
    font = pg.font.Font(pg.font.match_font('mono',1),15)
    scr.fill(-1100)
    textboxes = [
            TextBox(pygame.Rect(60,325, 50,25), 3),
            #TextBox(pygame.Rect(100,500, 300,25), 1)
            TextBox(pygame.Rect(120,325, 50, 25), 3),
            TextBox(pygame.Rect(180, 325, 50, 25), 3),
            TextBox(pygame.Rect(240, 325, 50, 25), 3),
            TextBox(pygame.Rect(300, 325, 50, 25), 3),
            TextBox(pygame.Rect(360, 325, 50, 25), 3),
            TextBox(pygame.Rect(420, 325, 50, 25), 3),
            TextBox(pygame.Rect(480, 325, 50, 25), 3),
            TextBox(pygame.Rect(540, 325, 50, 25), 3),
            TextBox(pygame.Rect(600, 325, 50, 25), 3),
            TextBox(pygame.Rect(660, 325, 50, 25), 3),
            TextBox(pygame.Rect(720, 325, 50, 25), 3),
            TextBox(pygame.Rect(780, 325, 50, 25), 3),
            TextBox(pygame.Rect(840, 325, 50, 25), 3),
            TextBox(pygame.Rect(900, 325, 50, 25), 3),
            TextBox(pygame.Rect(960, 325, 50, 25), 3),
            TextBox(pygame.Rect(60, 400, 50, 25), 3),
            TextBox(pygame.Rect(120, 400, 50, 25), 3),
            TextBox(pygame.Rect(180, 400, 50, 25), 3),
            TextBox(pygame.Rect(240, 400, 50, 25), 3),
            TextBox(pygame.Rect(300, 400, 50, 25), 3),
            TextBox(pygame.Rect(360, 400, 50, 25), 3),
            TextBox(pygame.Rect(420, 400, 50, 25), 3),
            TextBox(pygame.Rect(480, 400, 50, 25), 3),
            TextBox(pygame.Rect(540, 400, 50, 25), 3),
            TextBox(pygame.Rect(600, 400, 50, 25), 3),
            TextBox(pygame.Rect(660, 400, 50, 25), 3),
            TextBox(pygame.Rect(720, 400, 50, 25), 3),
            TextBox(pygame.Rect(780, 400, 50, 25), 3),
            TextBox(pygame.Rect(840, 400, 50, 25), 3),
            TextBox(pygame.Rect(900, 400, 50, 25), 3),
            TextBox(pygame.Rect(960, 400, 50, 25), 3)
            

    ]
    btn = [
            Button('Step 1', pygame.Rect(60,350, 50, 25)),
            Button('Step 2', pygame.Rect(120,350, 50, 25)),
            Button('Step 3', pygame.Rect(180,350, 50, 25)),
            Button('Step 4', pygame.Rect(240,350, 50, 25)),
            Button('Step 5', pygame.Rect(300,350, 50, 25)),
            Button('Step 6', pygame.Rect(360,350, 50, 25)),
            Button('Step 7', pygame.Rect(420,350, 50, 25)),
            Button('Step 8', pygame.Rect(480,350, 50, 25)),
            Button('Step 9', pygame.Rect(540,350, 50, 25)),
            Button('Step 10', pygame.Rect(600,350, 50, 25)),
            Button('Step 11', pygame.Rect(660,350, 50, 25)),
            Button('Step 12', pygame.Rect(720,350, 50, 25)),
            Button('Step 13', pygame.Rect(780,350, 50, 25)),
            Button('Step 14', pygame.Rect(840,350, 50, 25)),
            Button('Step 15', pygame.Rect(900,350, 50, 25)),
            Button('Step 16', pygame.Rect(960,350, 50, 25)),
            Button('Step 17', pygame.Rect(60, 425, 50, 25)),
            Button('Step 18', pygame.Rect(120, 425, 50, 25)),
            Button('Step 19', pygame.Rect(180, 425, 50, 25)),
            Button('Step 20', pygame.Rect(240, 425, 50, 25)),
            Button('Step 21', pygame.Rect(300, 425, 50, 25)),
            Button('Step 22', pygame.Rect(360, 425, 50, 25)),
            Button('Step 23', pygame.Rect(420, 425, 50, 25)),
            Button('Step 24', pygame.Rect(480, 425, 50, 25)),
            Button('Step 25', pygame.Rect(540, 425, 50, 25)),
            Button('Step 26', pygame.Rect(600, 425, 50, 25)),
            Button('Step 27', pygame.Rect(660, 425, 50, 25)),
            Button('Step 28', pygame.Rect(720, 425, 50, 25)),
            Button('Step 29', pygame.Rect(780, 425, 50, 25)),
            Button('Step 30', pygame.Rect(840, 425, 50, 25)),
            Button('Step 31', pygame.Rect(900, 425, 50, 25)),
            Button('Step 32', pygame.Rect(960, 425, 50, 25)),
            Button('Play', pygame.Rect(60, 500, 50, 25)),
            Button('Tempo', pygame.Rect(180,500, 50, 25))
        ]
        

    for box in textboxes:
            box.update(scr)
    for butt in btn:
            butt.update(scr)
            pygame.display.flip()

    pg.display.flip()
    
    # create the container
    ms       = MenuSystem()
    
    # create the (sub)menus
    # Menu(items,label=None,excudes=())
    # items is an iterable of str/Menu objects
    # excudes are indices of non-reactives items
 
    main     = Menu(("notes","C","C#","D","D#","E","F","F#","G","G#","A", "A#", "B"),'',(0,))
    
    
    while 1:
        ev = pg.event.wait()
        if ev.type == pg.MOUSEBUTTONDOWN and not ms:
            
            # initializes the container with the main menu
            # MenuSystem.set(Menu,position,font)
            # position = (x,y)
            # font = pygame.font object
            ms.set(main,ev.pos,font)
            
            # MenuSystem.screen()
            # draws the menus and returns a list of rects(one for each menu displayed or deleted)
            pg.display.update(ms.screen())
        
        # updates
        # MenuSystem.update(pygame.event object)
        # returns True if there has been change
        if ms.update(ev):
            
            pg.display.update(ms.screen())
            
        # MenuSystem.OUTPUT = None
        # when you select an item
        # MenuSystem.OUTPUT contains the numeric path ...
        # [1,2,3] means submenu 1 of main menu, submenu 2 of submenu 1, item 3 of submenu 2
        if ms.OUTPUT:
            print(ms.OUTPUT,main.items(ms.OUTPUT)) # Menu.items(numeric path) returns the path changed to label
            if ms.OUTPUT == [3]: break
            if ms.OUTPUT[:2] == [2,2]: pg.display.update(pg.draw.rect(scr,pg.Color(main.items(ms.OUTPUT)[-1]),scr.get_rect(),10))
