import random as r
import time
import os
from datetime import datetime
import math
import threading
global isWindows
import googlemaps
import webbrowser
isWindows = False

try:
    from win32api import STD_INPUT_HANDLE
    from win32console import GetStdHandle, KEY_EVENT, ENABLE_ECHO_INPUT, ENABLE_LINE_INPUT, ENABLE_PROCESSED_INPUT
    isWindows = True   
except ImportError as e:
    import sys
    import select
    import termios

class KeyPoller():
    def __enter__(self):
        global isWindows
        if isWindows:
            self.readHandle = GetStdHandle(STD_INPUT_HANDLE)
            self.readHandle.SetConsoleMode(ENABLE_LINE_INPUT|ENABLE_ECHO_INPUT|ENABLE_PROCESSED_INPUT)

            self.curEventLength = 0
            self.curKeysLength = 0

            self.capturedChars = []
        else:
            # Save the terminal settings
            self.fd = sys.stdin.fileno()
            self.new_term = termios.tcgetattr(self.fd)
            self.old_term = termios.tcgetattr(self.fd)

            # New terminal setting unbuffered
            self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

        return self

    def __exit__(self, type, value, traceback):
        if isWindows:
            pass
        else:
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    def poll(self):
        if isWindows:
            if not len(self.capturedChars) == 0:
                return self.capturedChars.pop(0)

            eventsPeek = self.readHandle.PeekConsoleInput(10000)

            if len(eventsPeek) == 0:
                return None

            if not len(eventsPeek) == self.curEventLength:
                for curEvent in eventsPeek[self.curEventLength:]:
                    if curEvent.EventType == KEY_EVENT:
                        if ord(curEvent.Char) == 0 or not curEvent.KeyDown:
                            pass
                        else:
                            curChar = str(curEvent.Char)
                            self.capturedChars.append(curChar)
                self.curEventLength = len(eventsPeek)

            if not len(self.capturedChars) == 0:
                return self.capturedChars.pop(0)
            else:
                return None
        else:
            dr,dw,de = select.select([sys.stdin], [], [], 10.0)
            if dr == []:
                return None
            else:
                return sys.stdin.read(1)

def statusBar(pomRem, pomtot, inverse = False): # This function creates a status bar.
    global wid
    ratio = pomRem/pomtot
    if inverse:
        ratio = 1 - ratio
    prefill, postfill, white, bR, bL = '(', ')', ' ', 'o-{', '}-o'# the character used to inidices the bar is being filled
    tSize = wid - len(bL) - len(bR) # the size of the status bar.
    numNotches, numDig = int(tSize * ratio), f"{ratio*100:2.0f}%"
    numNotches = numNotches - len(numDig) if numNotches >= len(numDig) else 0
    prenotches = int(numNotches/2)
    postnotches = numNotches - prenotches # This notches business calculates the fill of the status bar.
    numWhite = tSize - numNotches - len(numDig) # The whitespace of the status bar. 
    s = "~"*wid+"\n" + f"{bR:s}{prefill*prenotches:s}{numDig:s}{postfill*postnotches:s}{white*numWhite:s}{bL:s}\n" + "~"*wid
    print(s)

def getPomsInWeek(disp=False, mins = False):
    global pomWindow,time_left_today, mpd, BTHOUR, BTMIN, bed_time, workRemPoms, bed_time_t, TRST,TRWT,TRFT, sleep, ppd, possible, WB, wid
    sep = ' '
    curr_time_t = time.time()
    time_rem_t = bed_time_t - curr_time_t
    currTS = time.localtime(time.time())
    
    if time_rem_t <= 0.0:
        #reset the bed_time_t
        x=datetime.today()
        bed_time=x.replace(day=x.day+1, hour=BTHOUR, minute=BTMIN , second=0, microsecond=0)
        bed_time_t = time.mktime(bed_time.timetuple())
        TRST = sleep
        todaysWorkRate = (WB % ppd)/WB # ratio of time in the week that i should spend working today.
        TRWT = todaysWorkRate * workRemPoms * pomWindow#For fixing TRWT

    days_rem, hrs_rem, mins_rem, secs_rem = 6.0 - currTS.tm_wday, 23 - abs(BTHOUR - currTS.tm_hour), 59 - abs(BTMIN - currTS.tm_min), 60 - bed_time.second - currTS.tm_sec
    tot_minutes_rem =  (mpd * days_rem) + (60.0 * hrs_rem) + mins_rem + (secs_rem/60.0)
    time_left_today = (60.0 * hrs_rem) + mins_rem + (secs_rem/60.0)
    pomsAvailable = tot_minutes_rem / pomWindow
    
    if disp:
        lwid = math.floor((wid-3)/2)
        rwid = wid - lwid
        print("{0:^{1}s}{2:^{3}.0f}".format("Weekly Balance", lwid, pomsAvailable, rwid) )
        print("{0:^{1}s}{2:^{3}.0f}".format("Pending", lwid, workRemPoms, rwid) )

    if mins:
        return tot_minutes_rem 
    return pomsAvailable

def getStatus(PF):### CODE FOR STATUS SELECTION:
    ''' FREE : [0.0, 0.0], Proactive : (0.0, 1.5], Ahead : (1.5, 3.0], 
    On Schedule : (3.0, 4.0], Behind : (4.0, 4.5], DANGER (4.5, 10.0) '''
    global wid
    sep = ' '
    statuses = {0:'Free',2.0:'Very Ahead',4.0:'Ahead',6.0:'On Schedule',8.0:'Behind', 10.0:'DANGER'}
    Keys = list(statuses.keys())
    sKeys = [abs( float(str(key)) - (PF*10) )for key in statuses.keys()]
    small, j = 100, 0
    for i in range(len(sKeys)):
        small = small if small < sKeys[i] else sKeys[i]
        j = j if small < sKeys[i] else i
    status = statuses[Keys[j]]
    if j == 0:
        j = 1 if PF != 0 else 0
    lwid = math.floor((wid-3)/2)
    rwid = int(wid - lwid)
    print("{0:^{1}}{2:^{3}s}".format("Status", lwid, status, rwid) )

def recommendedPoms(kaizenD, todaysPoms):
    global pomodorros, pomsRem
    new_pomodorros = []
    list_of_tups = [ (p,pomsRem[p]) for p in pomodorros]
    new_list = []
    while(len(list_of_tups) > 0):
        i = 0
        maxSoFar = 0 #max so far
        for tup in list_of_tups:#Selection Sort
            if tup[1] > maxSoFar:
                maxSoFar = tup[1]
                maxTup = list_of_tups[i]
            i+=1
        list_of_tups.remove(maxTup)
        new_list.append(maxTup)
        new_pomodorros.append(maxTup[0])
    pomodorros = new_pomodorros
    D = {}
    for tup in new_list:
        if tup[0] == 'Misc.':
            continue
        if todaysPoms > 0:
            name = tup[0]
            rPoms = kaizenD[name]# if todaysPoms != 1 else 1 #recommended poms
            if todaysPoms - rPoms < 0:
                rPoms = todaysPoms
            todaysPoms -= rPoms
            D[name] = rPoms
        else:
            break
    return D

def pomRecommendation(twmr, dr, twr, rdwr, ppd,log = False): #Kaizen
    global pomodorros, pomsRem, pomWindow, TRWT, fullchart_on
    kaizenD = {}
    todaysPoms = math.floor(TRWT/pomWindow)
    for pom in pomodorros:
        pomRemaining = pomsRem[pom]
        avgDailyContrbtn = math.ceil(pomRemaining / (dr + 1) )
        kaizenD[pom] = avgDailyContrbtn
        if log:
            print(f"{pom:^16s}: {kaizenD[pom]:5d}")
    kaizenSum = sum (kaizenD.values())
    if kaizenSum != 0:
        twFactor = todaysPoms / float(kaizenSum) #today's work factor
    else:
        twFactor = 0 
    if twFactor != 1:
        for pom in pomodorros:
            pomRemaining = pomsRem[pom]
            if dr > 0:
                kaizenD[pom] = math.ceil(pomRemaining / dr * twFactor)
            else:
                kaizenD[pom] = pomsRem[pom]
        recPoms = recommendedPoms(kaizenD, todaysPoms)
        for pom in pomodorros:
            if pom in recPoms:
                kaizenD[pom] = recPoms[pom]
            else:
                kaizenD[pom] = 0
            if log:
                print(f"{pom:^16s}: {kaizenD[pom]:5d}")
    #print("-"*30)
        if not fullchart_on:
            rtn = {}
            for pom in kaizenD: 
                if kaizenD[pom] != 0:
                    rtn[pom] = kaizenD[pom]
            return rtn
    #return rtn # return kaizenD here instead of rtn to view the entire list of tasks.
    return kaizenD

def printDate():
    global wid
    now = datetime.now()
    date_and_time = now.strftime("%A, %B %d, %Y %I:%M:%S %p")
    date_and_time = "{0:^{1}}".format(date_and_time, wid)
    print(date_and_time)

def printPomChart(pomodorros, kaizenD, remWorkPoms):
    global chart_view_on, reset_pomsRem, accum_view_on, pomsAccum, pomLength, fullchart_on, pomsRem, wid
    out_of = sum ( reset_pomsRem.values() )
    if chart_view_on:
        t1,t2,t3 = 'Task', 'Week', 'Today'
        todaysKaizenPoms = sum ( kaizenD.values() )
        header = "{1:_^{0}s}{2:_^{0}s}{3:_^{0}s}".format(math.floor(wid/3), t1,t2,t3)
        print('\n'+header)
        
        if fullchart_on:
            completed = []
            for pom in reset_pomsRem:
                if pom not in pomsRem:
                    done = reset_pomsRem[pom]
                    completed.append(pom)
                    continue

                else:
                    done = (reset_pomsRem[pom] - pomsRem[pom])
                if pom in kaizenD:
                    #print(f"{pom:^16s} | {done:>3d} / {reset_pomsRem[pom]:>2d}  | {kaizenD[pom]:>5d}")
                    mid = f"{done:>3d} / {reset_pomsRem[pom]:>2d}"
                    print( "{1:^{0}s}{2:^{0}s}{3:^{0}d}".format(math.floor(wid/3), pom,mid,kaizenD[pom]) )
                elif done == 0 or pom not in kaizenD:
                    mid = f"{done:>3d} / {reset_pomsRem[pom]:>2d}"
                    #print(f"{pom:^16s} | {done:>3d} / {reset_pomsRem[pom]:>2d}  | {0:>5d}")
                    print( "{1:^{0}s}{2:^{0}s}{3:^{0}d}".format(math.floor(wid/3), pom,mid, 0) )
   
            print("{0:_^{1}}".format('Completed',wid))
            for pom in completed:
                done = reset_pomsRem[pom]
                mid = f"{done:>3d} / {reset_pomsRem[pom]:>2d}"
                print( "{1:^{0}s}{2:^{0}s}{3:^{0}d}".format(math.floor(wid/3), pom,mid, 0) )
            todaysKaizenPoms = sum ( kaizenD.values() )
            mid = f"{(out_of - remWorkPoms):>3d} /{out_of:>2d}"
            footer = "{1:^{0}s}{2:^{0}s}{3:^{0}d}".format(math.floor(wid/3), "Total",mid,todaysKaizenPoms)
            print('-'*wid)
            print(footer)

        else:
            for pom in kaizenD:
                mid = f"{(reset_pomsRem[pom] - pomsRem[pom]):>3d}"
                print( "{1:^{0}s}{2:^{0}s}{3:^{0}d}".format(math.floor(wid/3), pom,mid, kaizenD[pom]) )
            todaysKaizenPoms = sum ( kaizenD.values() )
            mid = f"{(out_of - remWorkPoms):>3d} /{out_of:>2d}"
            footer = "{1:^{0}s}{2:^{0}s}{3:^{0}d}".format(math.floor(wid/3), "Total",mid,todaysKaizenPoms)
            print('-'*wid)
            print(footer)

    if accum_view_on:
        t1,t2, t3 = 'Task', 'Total', 'Time'
        tot_accum = sum( pomsAccum.values() )
        print("{1:_^{0}s}{2:_^{0}s}{3:_^{0}s}".format(math.floor(wid/3), t1, t2, t3))
        #print("-"*wid) 
        for pom in pomsAccum:
            pomsAccumulated = pomsAccum[pom]
            hours, mins = int((pomsAccumulated*pomLength)/60), int((pomsAccumulated*pomLength)%60)
            thours, tmins = int((tot_accum*pomLength)/60), int((tot_accum*pomLength)%60)
            timeAccum = f"{hours:>2d}h {mins:>2d}s"
            print( "{1:^{0}s}{2:^{0}d}{3:^{0}s}".format(math.floor(wid/3), pom,pomsAccumulated, timeAccum) )

        todaysKaizenPoms = f"{thours:>2d}h {tmins:>2d}m"
        footer = "{1:^{0}s}{2:^{0}d}{3:^{0}s}".format(math.floor(wid/3), "Total",tot_accum,todaysKaizenPoms)
        print('-'*wid)
        print(footer)

def displayStats(timeRem, PF, ADFT, ADWT, ADST, money, income, bills, expenses):
    global TRST, TRFT, TRWT, pomsAccum, money_view_on, time_view_on, mainview_on, BTHOUR, BTMIN, bed_time, remday_view_on, wid, bed_time_t, wid
    sep = ' '
    t_string,r_string,f_string = 'Today', 'Remaining Days this Week', 'Financial'

    lwid = math.floor((wid-3)/2)
    rwid = wid - lwid

    if mainview_on:
        print("{0:^{1}s}{2:>{3}.0f}%".format("PF (C / WB)", lwid, PF*100.0, int(rwid/2)+1 ))
    if time_view_on:
        currTS = time.localtime(time.time())
        hrs_rem, mins_rem, secs_rem = 23 - abs(BTHOUR - currTS.tm_hour), 59 - abs(BTMIN - currTS.tm_min), 60 - bed_time.second - currTS.tm_sec
        print('{0:_^{1}s}'.format(t_string, wid))
        #for time_left in [TRFT, TRWT, TRST, ADFT, ADWT, ADST]:

        #print(f"{'Time Left Today':19s} : {sep:6s}{hrs_rem:>2d}h {mins_rem:>2d}m {secs_rem:>2d}s") 
        timeString = '{0:>2d}h {1:>2d}m {2:>2d}s'.format(hrs_rem,mins_rem,secs_rem)
        print("{0:^{1}s}{2:^{3}s}".format('Time Left Today', lwid, timeString, rwid) )
        s, i = ['Free Time Today','Task Time Today','Sleep Time Today'], 0
        for times in [TRFT, TRWT, TRST]:
            timeString = '{0:>2d}h {1:>2d}m {2:>2d}s'.format(int(times/60),int(times%60),int(times*60%60))
            print("{0:^{1}s}{2:^{3}s}".format(s[i], lwid, timeString, rwid) )
            i+=1
        if remday_view_on:
            a, j = ['Free Time', 'Task Time', 'Sleep Time'], 0
            print("{0:_^{1}s}".format(r_string, wid))
            for times in [ADFT, ADWT, ADST]:
                timeString = '{0:>2d}h {1:>2d}m {2:>2d}s'.format(int(times/60),int(times%60),int(times*60%60))
                print("{0:^{1}s}{2:^{3}s}".format(a[j], lwid, timeString, rwid) )
                i+=1
    if money_view_on:
        line = '-' * 12
        labels = ['Earnings', 'Expenses', 'Net Earnings', 'Starting Balance', 'Next Month']
        print("{0:^{1}s}".format(f_string, wid))
        print("~"*wid)
        m1 =  "+ ${0:>13,.2f}".format(income,rwid)
        print("{0:_^{1}s}{2:_>{3}s}".format(labels[0], lwid, m1, rwid-3) )

        m2 =  "- ${0:>13,.2f}".format(expenses,rwid)
        print("{0:_^{1}s}{2:_>{3}s}".format(labels[1], lwid, m2, rwid-3) )
        print("-"*wid)

        m3 =  "${0:>13,.2f}".format(income-expenses,rwid)
        print("{0:_^{1}s}{2:_>{3}s}".format(labels[2], lwid, m3, rwid-3) ) 

        m4 =  "+ ${0:>13,.2f}".format(money,rwid)
        print("{0:_^{1}s}{2:_>{3}s}".format(labels[3], lwid, m4, rwid-3) )

        print("-"*wid)
        m5 =  "+ ${0:>13,.2f}".format(money - expenses + income,rwid)
        print("{0:_^{1}s}{2:_>{3}s}".format(labels[4], lwid, m5, rwid-3) )

def Timer(choice,desc=True): 
    global timer_start_time, timer_mins, wid
    mins = timer_mins
    secs = int(mins * 60)
    if not paused:
        startTime = timer_start_time
        currTime = time.time()
    else:
        startTime = 0.0
        currTime = 0.0
    choice = "{0:^{1}}".format(choice, math.floor(wid/2) )
    if desc:
        timePrint = f"{int((secs - currTime + startTime+1)/60/60):02d}:{int((secs - currTime + startTime+1)/60%60):02d}:{int((secs - currTime + startTime+1)%60):02d}"
        print(choice+' : '+f"{timePrint:>18s}")
    else:
        print(choice+':  {:02d}:{:02d}'.format(int((currTime - startTime)/60), int((currTime - startTime)%60)))        

def information_screen(remWorkPoms, targetPoms, sleep, timeRem, PF, ADFT, ADWT, ADST, kaizenD, prompt):
    global pomodorros, money, income, bill, expenses, timer_is_on, curr_pom, mainview_on, thread_view_mode, wid#, rest_is_on
    if thread_view_mode: 
        print("~"*wid+"\nActive Threads:")
        for thread in threading.enumerate():
            try:
                print(thread.getName(), ' : ', thread)
            except AttributeError:
                pass
        print("~"*wid+"\nInput Threads:")
        for thread in UIthreads:
            try:
                print(thread.getName(), ' : ', thread)
            except AttributeError:
                pass
        print("~"*wid+"\nPrinting Threads:")
        for thread in RPthreads:
            try:
                print(thread.getName(), ' : ', thread)
            except AttributeError:
                pass
    print("*"*wid)
    printDate()
    statusBar(remWorkPoms, targetPoms, inverse=True)
    if mainview_on:
        getStatus(PF)
        getPomsInWeek(disp=True)
    displayStats(timeRem, PF, ADFT, ADWT, ADST, money, income, bills, expenses)
    printPomChart(pomodorros, kaizenD, remWorkPoms)
    print("*"*wid)
    print('-'*wid)
    if timer_is_on:# or rest_is_on:
        Timer(curr_pom)
        print("-"*wid)
    print(prompt)
    print("-"*wid)
    print("*"*wid)

def getPF(remWorkPoms, prompt, disp = False):
    global pomWindow, pomsRem, TRWT, TRFT, TRST, ADFT, ADST, ADWT, ppd, sleep, possible, MODE, time_slept, time_left_today, workRemPoms, reset_pomsRem

    remPomsPerDay = ppd - sleep/pomWindow
    workRemMins = remWorkPoms*pomWindow # Minutes of commitments remaining.
    hrsRem, minRem = int(workRemMins/60.0), int(workRemMins%60.0) 
    timeRem = f"{hrsRem:>5d}h {minRem:>2d}m" # time remaining. 
    WB = getPomsInWeek() # Weekly Balance
    daysRemInWeek = int(WB/ppd)
    PF = remWorkPoms/(WB-sleep*daysRemInWeek/pomWindow) # Procrastination Factor. Remaining Work Poms / Weekly Balance
    todaysWorkRate = (WB % ppd)/WB # ratio of time in the week that i should spend working today.
    remDaysWorkRate = 1 - todaysWorkRate # the ratio of time in the week to spend working on the remaining days.
    kaizenD = pomRecommendation(workRemMins, daysRemInWeek, todaysWorkRate, remDaysWorkRate, ppd)
    mpd = ppd * pomWindow
    workRemPoms = remWorkPoms

    if time_left_today <= TRWT:
        possible = False
    if not possible:
        TRWT = todaysWorkRate * workRemMins#For fixing TRWT
        possible = True
    if daysRemInWeek > 0:
        ADWT = int((remWorkPoms*pomWindow-TRWT)/ (daysRemInWeek))
        ADST = sleep
        ADFT =  mpd - ADWT - ADST
    else:
        ADWT = 0.0
        ADST = 0.0
        ADFT =  0.0

    targetPoms = sum(reset_pomsRem.values())
    if disp:
        information_screen(remWorkPoms, targetPoms, sleep, timeRem, PF, ADFT, ADWT, ADST, kaizenD, prompt)
    return PF, kaizenD

def prompt(stage=1, choice = None): # The point of this is to eventually get a choice from the user. every 3 seconds display the infoscreen, and request input.
    global pomodorros, pomsRem, reset_poms, timer_is_on, curr_pom, MODE, paused
    global text_buffer, no_input, UIthread, UIthreads, RPthreads,wid
    def background(stage):
        global text_buffer, no_input#, rest_is_on, answerBuffer, answerCounter, rest_is_on, feedback_on
        while no_input:
            os.system("clear")
            remWorkPoms = sum(pomsRem.values())

            prompt = ">> " + text_buffer
        
            if timer_is_on:# or rest_is_on:
                s2, s3 = 'S: STOP', 'D: DONE'
                if paused:
                    s1 = 'P: RESUME'
                else:
                    s1 = 'P: PAUSE'
                prompt = "{1:<{0}s}|{2:^{0}}|{3:>{0}s}".format(math.floor((wid-2)/3),s1,s2,s3) +'\n' + "*"*wid + '\n' + "-"*wid + '\n' + prompt

            PF, kaizenD = getPF(remWorkPoms, prompt, disp=True)
            time.sleep(0.25)
            deteriorate_time()

    def get_user_input():
        global text_buffer, no_input
        with KeyPoller() as keyPoller:
            counter = 0 
            while no_input:
                c = keyPoller.poll()
                if c is None:
                    if counter > 0: 
                        no_input = False
                        text_buffer = ' '#TIMEOUT
                        break
                    else:
                        counter += 1
                else:
                    u = c.encode()
                    if u == b'\x7f':
                        text_buffer = text_buffer[:-1]
                    elif u  == b'\n':
                        no_input = False
                        break
                    else:
                        text_buffer += c
        #sys.exit(["Goodbye, for now ..."])

    if stage == 1: #Print CLI and collect user input and returns it to MainMenu
        RPthread = threading.Thread(target=background, daemon = True, args=[stage], name="Prompt") # repeated printing thread
        # RPthreads.append(RPthread)
        RPthread.start() # Now RP is running until user enters input.
        UIthread = threading.Thread(target=get_user_input, name="Input", daemon = True)
        #UIthreads.append(UIthread)
        UIthread.start()
        UIthread.join()
        RPthread.join()
     #~~~~~~~~~~~~ ... When the thread finish ...
        rtn = text_buffer
        text_buffer = ''
        no_input = True
        return rtn

    elif stage == 2: # Confirmation
        if choice == 'Sleep':
            return 'y'
        if choice == 'Misc.':
            return 'y'
        if choice in pomodorros:
            return 'y'
        else:
            return 'n'     
    if stage == 3: 
        #RPthread = threading.Thread(target=background, daemon = True, args=[stage], name="Prompt") # repeated printing thread
        # RPthreads.append(RPthread)
        #RPthread.start() # Now RP is running until user enters input.
        UIthread = threading.Thread(target=feedback, name="Input", daemon = True)
        #UIthreads.append(UIthread)
        UIthread.start()
        UIthread.join()
        #RPthread.join()
        #~~~~~~~~~~~~ ... When the thread finish ...
        rtn = text_buffer
        text_buffer = ''
        no_input = True
        return rtn

def deteriorate_time(): # Used by prompt1 to deteriorate TRFT/TRWT.
    # Running => MODE := WORK | Paused
    global TRFT, TRST, TRWT, MODE, ppd, pomWindow, sleep, time_slept
    if MODE == "WORK":
        TRWT =  ((getPomsInWeek()%ppd * pomWindow) - TRST - TRFT) + 1/60.0
    if MODE == 'FREE':    
        TRFT =  ((getPomsInWeek()%ppd * pomWindow) - TRWT - TRST) + 1/60.0
    if MODE == 'SLEEP':
        TRST = sleep - (time.time() - time_slept)/60.0

def stop_timer():
    global MODE, paused, no_input, timer_is_on
    #timer_is_on = False
    paused = False
    startRest()

def logTask():
    global TaskLogOn
    TaskLogOn = True
    save()

def feedback():
    global prev_pom, pomsAccum, reset_pomsRem, answerBuffer, wid, feedback_view_on
    mark = '*' * wid
    print(mark)
    if prev_pom == 'Misc.':
        while True:
            newName = input('{1:_^{0}s}\n'.format(
                                    wid, 
                                    'New Name'
                                ))
            if newName in reset_pomsRem:
                if newName in pomsAccum:
                    pomsAccum[newName] += 1
                else:
                    pomsAccum[newName] = 1
                prev_pom = newName
                break
            else:
                continue
    answerBuffer['pleasant_score'] = input('{1:_^{0}s}\n{2:_^{0}s}\n'.format( 
                                            wid, 
                                            'How pleasant do you feel?',
                                            '(0:very unpleasant)|(2.5:unpleasant)|(5:neutral)|(7.5:pleasant)|(10:very pleasant)'
                                        ))

    answerBuffer['activated_score'] = input('{1:_^{0}s}\n{2:_^{0}s}\n'.format( 
                                            wid, 
                                            'How activated do you feel?',
                                            '(0:very deactivated)|(2.5:deactivated)|(5:neutral)|(7.5:activated)|(10:very activated)'
                                        ))
    answerBuffer['productive_score'] = input('{1:_^{0}s}\n{2:_^{0}s}\n'.format( 
                                            wid, 
                                            'How productive was that pomodorro?',
                                            '(0:very unproductive)|(2.5:unproductive)|(5:neutral)|(7.5:productive)|(10:very productive)'
                                        ))

    x = (float(answerBuffer['pleasant_score'])-5.0)/5.0
    y = (float(answerBuffer['activated_score'])-5.0)/5.0

    try:
        if x < 0.0 and y < 0.0 or y < 0.0: 
            theta = 270.0 - math.degrees ( math.atan( y/x ))
        elif x < 0.0:
            theta = 180.0 -  math.degrees ( math.atan( y/x ))
        elif y < 0.0:
            theta = 360.0 - math.degrees ( math.atan( y/x ))
        else:
            theta = math.degrees ( math.atan( y/x ))
    except ZeroDivisionError:
        theta = 0

    feelings = { 18: 'happy', 36: 'elated', 54: 'excited', 72: 'alert', 90: 'activated',\
                108: 'tense', 126: 'nervous', 144: 'stressed', 162: 'upset' , 180: 'unpleasant',\
                198: 'sad', 216: 'depressed', 234:'bored', 252: 'sluggish', 270: 'deactivated',\
                288: 'calm', 306:'relaxed', 324:'serene', 342:'content', 0: 'pleasant'}

    Keys = list(feelings.keys())
    sKeys = [abs( feelingdeg - theta ) for feelingdeg in feelings.keys()]
    small, j = 100, 0
    for i in range(len(sKeys)):
        small = small if small < sKeys[i] else sKeys[i]
        j = j if small < sKeys[i] else i
    feeling = feelings[Keys[j]]
    sep = ' '
    answerBuffer['feeling'] = feeling
    unfeeling = feelings[int((180.0 + Keys[j]) % 360.0)]
    answerBuffer['feeling_score'] = input('{1:_^{0}s}\n{2:_^{0}s}\n'.format(
                                            wid, 
                                            f'How {feeling:s} do you feel?', 
                                            f'(0:very {unfeeling:s})|2.5:{unfeeling:s}|(5:neutral)|(7.5:{feeling:s})|(10:very {feeling:s})'
                                        ))
    
    answerBuffer['additionalFeedback'] = input('{1:_^{0}s}'.format(
                                        wid, 
                                        'Additional Comments'
                                    ))
    logTask()
    feedback_view_on = False

def stop_rest():
    global curr_pom, MODE, feedback_on, timer_is_on, timerThread#, #rest_is_on, timerThread, timer_is_on
    global fullchart_on, remday_view_on, money_view_on, accum_view_on, mainview_on, chart_view_on, time_view_on
    global feedback_view_on
    timerThread.cancel()
    feedback_view_on=True
    timer_is_on = False


    prev_pom = 'Rest'
    #timerThread = threading.Timer(timer_)
    MODE = 'FREE'

def startRest():
    global timer_mins, timer_start_time, pomRest, curr_pom, timerThread, prev_pom#rest_is_on, feedback_on, timerThread
    if curr_pom == 'Sleep':
        return
    prev_pom = curr_pom
    curr_pom = 'Rest'
    timer_start_time = time.time()
    timer_mins = pomRest
    #timer_mins = float(1/60)
    timerThread = threading.Timer(timer_mins * 60, stop_rest)
    timerThread.setName(curr_pom)
    timerThread.start()

def beginPom(choice):
    global pomodorros, pomsRem, pomsAccum, MODE, TRST, curr_pom 
    global time_slept, timer_is_on, timer_start_time, timer_mins, timerThread, sleep
    global fullchart_on, remday_view_on, money_view_on, accum_view_on, mainview_on, accum_view_on, mainview_on, chart_view_on, time_view_on
    if choice == "Sleep":
        if TRST > 0:
            mins = sleep
            time_slept = time.time()
            curr_pom = choice
            timer_mins = mins
            timer_start_time = time.time()
            timer_is_on = True
            timerThread = threading.Timer(timer_mins * 60.0, stop_timer)
            timerThread.setName(curr_pom)
            timerThread.start()
            MODE = "SLEEP"

    else:
        if choice != 'Misc.' and pomsRem[choice]:
            pomsRem[choice] -= 1
            if choice in pomsAccum:
                pomsAccum[choice] += 1
            else:
                pomsAccum[choice] = 1
            if not pomsRem[choice]:
                pomodorros.remove(choice)
                del pomsRem[choice]
        else:
            if choice == 'Misc.':
                pass

        mins = pomLength
        curr_pom = choice
        timer_mins = mins
        timer_start_time = time.time()
        timer_is_on = True
        #timer_mins = 3 * float(1/60)
        timerThread = threading.Timer(timer_mins * 60.0, stop_timer)
        timerThread.setName(curr_pom)
        timerThread.start()
        MODE = "WORK"            

        fullchart_on = False
        remday_view_on = False
        money_view_on = False
        accum_view_on = False
        mainview_on = False
        chart_view_on = False
        time_view_on = False

def save(file=None):
    global pomsRem, pomsAccum, TRFT, TRWT, TRST, money, income, bills, expenses, answerBuffer, curr_pom, TaskLogOn, gmaps
    if not file:
        file = 'data/savefile.txt'
    TaskLog = open('data/TaskLog.txt', 'a')
    savePoms = open(file,'w')
    saveFins = open('data/fin.txt', 'w')
    saveTims = open('data/dailytimes.txt','w')
    saveAccums = open('data/accum.txt', 'w')
    finTups = [('Money',money), ('Income', income), ('Bills', bills), ('Expenses', expenses)]
    timeTups = [('TRFT', TRFT), ('TRWT', TRWT), ('TRST', TRST)]
    pomTups = [ (keyPom, pomsRem[keyPom]) for keyPom in pomsRem ]
    accumTups = [ (keyPom, pomsAccum[keyPom]) for keyPom in pomsAccum ]

    for pomTup in pomTups:
        savePoms.write(pomTup[0]+'\n')
        savePoms.write(str(pomTup[1])+'\n')
    for finTup in finTups:
        saveFins.write(finTup[0]+'\n')
        saveFins.write(str(finTup[1])+'\n')
    for timeTup in timeTups:
        saveTims.write(timeTup[0]+'\n')
        saveTims.write(str(timeTup[1])+'\n')
    for accumTup in accumTups:
        saveAccums.write(accumTup[0]+'\n')
        saveAccums.write(str(accumTup[1])+'\n')
    #print('Successfully Saved.')
    if TaskLogOn:
        geolocation = gmaps.geolocate()
        accuracy = geolocation['accuracy']
        latlong = geolocation['location']
        reverse_geocode = gmaps.reverse_geocode(latlong)
        address = reverse_geocode[0]['formatted_address']
        placeID = reverse_geocode[0]['place_id']
        placeData = gmaps.place(placeID)['result']
        pname = placeData['name']
        locationTypes = str(placeData['types'])
        site = placeData['url']
        now = datetime.now()
        date_and_time = now.strftime("%A, %B %d, %Y %I:%M:%S %p")
        TL = '''{:s}, {:s}\
                \nProductive Score: {:s}\
                \nActivated Score : {:s}\
                \nPleasant Score  : {:s}\
                \nEmotion: {:s}\
                \nEmotion Score : {:s}\
                \nAdditional Feedback : {:s}\
                \nAddress: {:s}\
                \n\tAccuracy: {:f}\
                \n\tPlaceID: {:s}\
                \n\tPlace Name: {:s}\
                \n\tLocation Types: {:s}\
                \n\tUrl: {:s}\n\n'''.format(
                    prev_pom, date_and_time, answerBuffer['productive_score'], answerBuffer['activated_score'], answerBuffer['pleasant_score'], answerBuffer['feeling'], answerBuffer['feeling_score'], answerBuffer['additionalFeedback'], address, accuracy, placeID, pname, locationTypes, site)
        
        TaskLog.write(TL)
        TaskLogOn = False

    answerBuffer = {'productive_score':0, 'pleasant_score':0, 'activated_score':0, 'feeling':None, 'feeling_score':0, 'additionalFeedback':''}

    savePoms.close()
    saveFins.close()
    saveTims.close()
    saveAccums.close()
    TaskLog.close()

    curr_pom = ''

def load(file=None):
    global pomodorros, pomsRem, money, income, TRFT, TRWT, TRST
    if not file:
        loadPoms = open('data/savefile.txt','r')
    else:
        loadPoms = open(file,'r')
    lines = loadPoms.readlines()
    pomodorros = [ lines[i].strip('\n') for i in range(len(lines)) if i%2 == 0]
    pomsRem = {}
    if file == 'data/fin.txt':
        for i in range(len(pomodorros)):
            pomsRem[pomodorros[i]] = float(lines[2*i+1])
        loadPoms.close()
        return pomsRem['Money'], pomsRem['Income'], pomsRem['Bills'], pomsRem['Expenses']
    if file == 'data/dailytimes.txt':
        for i in range(len(pomodorros)):
            pomsRem[pomodorros[i]] = float(lines[2*i+1])
        loadPoms.close()
        return pomsRem['TRFT'], pomsRem['TRWT'], pomsRem['TRST']
    if file == 'data/accum.txt':
        for i in range(len(pomodorros)):
            pomsRem[pomodorros[i]] = int(lines[2*i+1])
        loadPoms.close()
        return pomsRem
    else:     
        for i in range(len(pomodorros)):
            pomsRem[pomodorros[i]] = int(lines[2*i+1])
        loadPoms.close()
        return pomodorros, pomsRem

def Modify_Money():
    global income, money, bills, expenses, money_view_on
    if money_view_on:
        mode = input('\'-\' : expenses or \'+\' : income:\n')
        if mode == '+':
            delta = float(input('Net change to income:\t$'))
            income += delta
        if mode == '-':
            delta = float(input('Net change to expenses:\t$'))
            expenses += delta

def programEngine():
    def MainMenu():
        global pomsAccum, timer_is_on, curr_pom, timerThread, timer_mins, timer_start_time, paused
        global MODE, money_view_on, chart_view_on, time_view_on, accum_view_on, mainview_on, fullchart_on, feedback_view_on
        global no_input, text_buffer, remday_view_on, TRST#, feedback_on, rest_is_on, answerCounter, answerBuffer
        while True:
            if not  feedback_view_on:
                user_input = prompt(1)
                if user_input == '0':
                    fullchart_on = False
                    remday_view_on = False
                    money_view_on = False
                    accum_view_on = False
                    mainview_on = False
                    chart_view_on = False
                    time_view_on = False
                    continue
                if user_input == '1':
                    fullchart_on = False
                    remday_view_on = False
                    money_view_on = False
                    accum_view_on = False
                    mainview_on = True
                    chart_view_on = True
                    time_view_on = True
                    continue
                elif user_input == '2': # Full Tasks View
                    fullchart_on = True
                    remday_view_on = False
                    money_view_on = False
                    accum_view_on = False
                    mainview_on = False
                    chart_view_on = True
                    time_view_on = False
                    continue
                elif user_input == '3':
                    fullchart_on = False
                    remday_view_on = True
                    money_view_on = False
                    accum_view_on = False
                    mainview_on = True
                    chart_view_on = False
                    time_view_on = True
                    continue
                elif user_input == '4':
                    fullchart_on = False
                    remday_view_on = False
                    money_view_on = True
                    accum_view_on = False
                    mainview_on = True
                    chart_view_on = False
                    time_view_on = False     
                    continue
                elif user_input == '$' and money_view_on:
                    Modify_Money()
                    continue
                elif user_input == '5':
                    fullchart_on = False
                    remday_view_on = False
                    money_view_on = False
                    accum_view_on = True
                    mainview_on = True
                    chart_view_on = False
                    time_view_on = False
                    continue
                if not timer_is_on:
                    if user_input == 'random': 
                        user_input = r.choice(pomodorros) 
                        confirm = prompt(2, user_input)
                        if confirm == 'y': 
                            curr_pom = user_input
                            beginPom(user_input)
                        elif confirm == 'n': 
                            continue
                    elif user_input == 'Q':
                        print('MMthread ending...')
                        break
                    else:
                        confirm = prompt(2, user_input)
                        if confirm == 'y': 
                            beginPom(user_input)
                elif timer_is_on:
                    if user_input == 'P':
                        if not paused:
                            timerThread.cancel()
                            paused = True
                            timer_mins = timer_mins - (time.time() - timer_start_time)/60
                            if MODE != 'FREE':
                                MODE = 'FREE'
                        elif paused:
                            timer_start_time = time.time()
                            timerThread = threading.Timer(timer_mins*60.0, stop_timer)#, name=curr_pom)
                            timerThread.start()
                            paused = False
                            if MODE != 'WORK':
                                MODE = 'WORK'

                    elif user_input == 'S':
                        if curr_pom == 'Rest':
                            stop_rest()
                        else:
                            timerThread.cancel()
                            timer_is_on = False
                            paused = False
                            timer_start_time = 0.0
                            timer_mins = 0.0
                            MODE = 'FREE'
                        if curr_pom == 'Sleep':
                            timerThread.cancel()
                            timer_is_on = False
                            paused = False
                            timer_start_time = 0.0
                            timer_mins = 0.0
                            MODE = 'FREE'
                            continue
                        elif curr_pom != 'Misc.' and pomsAccum[curr_pom] > 1:
                            pomsAccum[curr_pom] -= 1
                        elif curr_pom != 'Misc.' and pomsAccum[curr_pom] >= 1:
                            del pomsAccum[curr_pom]
                        if curr_pom in pomsRem:
                            pomsRem[curr_pom] += 1
                            print(pomsRem[curr_pom])
                        else:
                            pomsRem[curr_pom] = 1
                        curr_pom = None
                    
                    elif user_input == 'D':
                        if curr_pom == 'Rest':
                            stop_rest()
                        elif curr_pom == 'Sleep':
                            timerThread.cancel()
                            timer_is_on = False
                            paused = False
                            timer_start_time = 0.0
                            timer_mins = 0.0
                            MODE = 'FREE'
                            TRST = 0.0
                        else:
                            timerThread.cancel()
                            stop_timer()
            else:
                prompt(3)

        save()

    MMthread = threading.Thread(name="MMthread",target=MainMenu,args=[]) #repeating main menu thread
    print("MMthread starting...")
    MMthread.run()
    print("Pthread ending...")

if __name__ == '__main__':
    gmaps = googlemaps.Client(key='AIzaSyC2hdmHd-7Q72tsx5uYZkrEh6Ig8QbVi_I')

    # Task Parameters
    mpd = 24 * 60.0
    pomLength = 25 #minutes
    pomRest = 5 #minutes
    pomWindow = pomLength + pomRest #minutes
    ppd = 24 * 60.0 / pomWindow # pomodorros per day
    sleep = 7 * 60 #sleep minutes per night
    money = 0
    income = 0
    wid = 60

    predMoney = 0
    MODE = "FREE" #FREE, WORK, SLEEP
    TRFT, TRWT, TRST = 0.0 , 0.0 , 0.0
    # TEXT
    no_input = True
    text_buffer = ''
    # Timer
    PROACTIVE = False #True when ADWT is negative.
    possible = False
    timer_is_on = False
    paused = False
    curr_pom = None
    prev_pom = None
    timer_start_time = 0
    timer_mins = 0
    workRemPoms = 0.0
    # View Switches
    money_view_on  = False
    chart_view_on = True
    time_view_on = True
    accum_view_on = False
    mainview_on = True
    remday_view_on = False
    thread_view_mode = False
    fullchart_on = False
    feedback_view_on = False
    #Daily Reset
    #feedback_on = False
    answerBuffer = {'productive_score':0, 'pleasant_score':0, 'activated_score':0, 'feeling':None, 'feeling_score':0, 'additionalFeedback':''}

    x=datetime.today()
    BTHOUR, BTMIN = 0, 0
    bed_time=x.replace(day=x.day+1, hour=BTHOUR, minute=BTMIN , second=0, microsecond=0)
    bed_time_t = time.mktime(bed_time.timetuple())
    #Weekly Reset
    # ... COMING SOON ...
    #Thread Stuff
    time_slept = 0
    time_left_today = 0.0 #minutes
    timerThread = threading.Timer(1,None)
    UIthreads, RPthreads = [], [] 
    #File Loading
    TaskLogOn = False
    dir_root = 'data/'
    reset_poms, reset_pomsRem = load(dir_root+'default-save.txt')
    money, income, bills, expenses = load(dir_root+'fin.txt')
    TRFT, TRWT, TRST = load(dir_root+'dailytimes.txt')
    pomsAccum = load(dir_root+'accum.txt')
    pomodorros, pomsRem = load()
    #Launch Program
    pThread = threading.Thread(target=programEngine)
    print("pThread starting...")
    pThread.run()