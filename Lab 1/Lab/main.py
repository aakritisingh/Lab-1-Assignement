from Pig1.Pig1 import Pig1
from Pig2.Pig2 import Pig2
from Pig3.Pig3 import Pig3
from Pig4.Pig4 import Pig4
from Pig5.Pig5 import Pig5
from Pig6.Pig6 import Pig6
import numpy as np
import sys
import time
import datetime
from os.path import abspath, exists
import os
import random
current_file_path = __file__
current_file_dir = os.path.dirname(__file__)


def get_physical_positions():#returns
    pig_positions = {}
    other_file_path = os.path.join(current_file_dir, "config.txt")
    with open(other_file_path, 'rw') as f:
        f.seek(0)
        lines  = f.readlines()# lines is a list
        print lines
        for l in lines:
            l = l.rstrip('\n')
            l = l.split(" = ")
            pig_positions[l[0]] = l[1]
        
        #f.close()
    return pig_positions#Dictionary = {"pig.bird.pig 1":"1,1",....}    
            
            
            
                        
                        
        
def initiator(position, hopcount):
        print "In initiator"
        #print "Acquiring lock")
        #initiator_lock.acquire()
        temp_pig_positions = get_physical_positions()
        #print "temp_pig_positions", temp_pig_positions
        temp_pig_positions.update((x, np.sqrt(int(y[0]) ** 2 + int(y[2]) ** 2)) for x, y in temp_pig_positions.items())
        init_pig = min(temp_pig_positions, key = lambda k: temp_pig_positions[k])
        #print "Releasing lock")
        #initiator_lock.release()
        return init_pig
        

"""if init_pig == self.pigID:
            print "I am the initiating pig ", self.pigID)
            senders = []
            senders_take_shelter = []
            print "Calling bird_approaching message at time ", datetime.datetime.now().time())
            self.bird_approaching(position, hopcount, senders, senders_take_shelter, 6)
            time.sleep(6)
            status_all_senders = []
            self.status_all(status_all_senders, status_all_replies)
            print
            status_senders = []
            self.status(pigID, status_senders) """      

def call_bird_approaching(pigObjs, pigObj, position, hopcount, senders, senders_take_shelter, landing_time):
    
    print "Calling bird_approaching message at time ", datetime.datetime.now().time().strftime('%H:%M:%S')
    pigObj.bird_approaching(position, hopcount, senders, senders_take_shelter, landing_time)
    time.sleep(7)
    
    print "Calling status_all at time ", datetime.datetime.now().time().strftime('%H:%M:%S')
    status_all_senders = []
    status_all_replies = []
    pigObj.status_all(status_all_senders, status_all_replies)
    
    
    print "Calling status(pigID) at time ", datetime.datetime.now().time().strftime('%H:%M:%S')
    status_senders = []
    pigID = random.choice(pigObjs).pigID
    pigObj.status(pigID, status_senders)   


 
 
def main():
    pigObjs = []

    #p1 = Pig(pigID, myIP, myPort, pig s, physical_position)
    
    print "Creating Pig objects at time ", datetime.datetime.now().time().strftime('%H:%M:%S')
    
    p1 = Pig1("pig1", 'localhost', 4011, ['pig2', 'pig6'], [1,1])
    pigObjs.append(p1)

    p2 = Pig2("pig2", 'localhost', 4012, ['pig1', 'pig4'], [1, 3])
    pigObjs.append(p2)

    p3 = Pig3("pig3", 'localhost', 4013, ['pig6'], [2, 3])
    pigObjs.append(p3)

    p4 = Pig4("pig4", 'localhost', 4014, ['pig2', 'pig5'], [3, 3])
    pigObjs.append(p4)

    p5 = Pig5("pig5", 'localhost', 4015, ['pig4', 'pig6'], [3, 1])
    pigObjs.append(p5)

    p6 = Pig6("pig6", 'localhost', 4016, ['pig1', 'pig3', 'pig5'], [2, 0])
    pigObjs.append(p6)
    
    #print "pigObjs", pigObjs
    print "Connecting to neighbors"
    
    for i in pigObjs:
        i.connectToneighbors_pURI()
        
    print "Calling initiator"  
    init_pig = initiator([2,3], 6)
    print "*********Starting*********"
    print "Pig that is initiating is :", init_pig
    
    senders = []
    senders_take_shelter = []
    
    #j = 0
    """while j < 3:
        print "Sleeping for 5 seconds in while in main, current time is ", datetime.datetime.now().time())
        time.sleep(5)
        print "After sleeping for 5 seconds in while in main, current time is ", datetime.datetime.now().time())
        print "Calling call_bird_approaching")
        j = j + 1
        for i in pigObjs:
            if i.pigID == init_pig:
                call_bird_approaching(i, [2,3], 6, senders, senders_take_shelter, 7)"""
                
    for i in pigObjs:
        #print "i.pigID", i.pigID
        if i.pigID == init_pig:
            print "Starting Episode 1 at ", datetime.datetime.now().time().strftime('%H:%M:%S')
            print "------------------"
            #print "Calling call_bird_approaching at ", datetime.datetime.now().time().strftime('%H:%M:%S')
            call_bird_approaching(pigObjs, i, [2,3], 6, senders, senders_take_shelter, 7)
            
    print "Out of episode 1 at time ", datetime.datetime.now().time().strftime('%H:%M:%S')
    
    print "Sleeping for 10 seconds"
    time.sleep(20)
    print "After sleep"
    
    
    for i in pigObjs:
        if i.pigID == init_pig:
            print "Starting Episode 2 at ", datetime.datetime.now().time().strftime('%H:%M:%S')
            print "------------------"

            #print "Calling call_bird_approaching at ", datetime.datetime.now().time().strftime('%H:%M:%S')
            call_bird_approaching(pigObjs, i, [1,3], 3, senders, senders_take_shelter, 7)
    print "Out of episode 2 at time ", datetime.datetime.now().time().strftime('%H:%M:%S')
    
    print "Sleeping for 10 seconds"       
    time.sleep(10)
    
    
    for i in pigObjs:
        if i.pigID == init_pig:
            print "Starting Episode 3 at ", datetime.datetime.now().time().strftime('%H:%M:%S')
            print "------------------"

            #print "Calling call_bird_approaching at ", datetime.datetime.now().time()
            call_bird_approaching(pigObjs, i, [4,3], 5, senders, senders_take_shelter, 7)
    print "Out of episode 3 at time ", datetime.datetime.now().time().strftime('%H:%M:%S')   

if __name__ == "__main__":
    main()









