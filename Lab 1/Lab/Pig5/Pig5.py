import time
import Pyro4
import random
import threading
import timeit
import datetime
from collections import OrderedDict
from os.path import abspath, exists
import os
current_file_path = __file__
current_file_dir = os.path.dirname(__file__)


#Pyro4.config.SERIALIZER = 'pickle'
#Pyro4.config.NS_PORT = 5000

physical_list_lock  =  threading.Lock()
initiator_lock = threading.Lock()
take_shelter_lock = threading.Lock()
@Pyro4.expose
class Pig5:
    def __init__(self, pigID, myHost, myPort, my_peers, physical_position):
        self.pigID = pigID#pigID is "peer1"
        self.myHost = myHost
        self.myPort = myPort
        self.my_peers = my_peers#list of peers
        self.physical_position = physical_position#list
        #self.physical_peers = physical_peers
        
        
        self.domain = "pig.bird."
        self.pigID = self.domain+pigID #pigID is "pig.bird.peer1"
        self.peers = []
        for k in self.my_peers:
            k = self.domain + k
            self.peers.append(k)   
        self.nameServer = Pyro4.locateNS()#**************Instead of locating, look in piazza
        print "Registering pig with pigID: ", self.pigID
        daemon =  self.registerPeer(myHost, myPort)

        
        
        threading.Thread(target = daemon.requestLoop).start()
        
        #self.connectToneighbors_pURI()
        self.neighbors_pURI = {}
        self.pig_positions = {}
        self.hitFlag = False
        self.static_neighbors_pURI = {}
        self.score = 6
        
        #print "Calling initiator function from ", self.pigID)
        #threading.Thread(target = self.initiator(), kwargs={'position':position, 'hopcount': hopcount}).start()#*******can call from main()?


#*************************        registerPeer(myHost, myPort)        ***********************    
        
    def registerPeer(self, myHost, myPort):
        daemon=Pyro4.Daemon(port = myPort, host=myHost)
        self.pURI = daemon.register(self)
        #self.nameServer.unregister(self.pigID, self.pURI)
        
        """try:
        # 'test' is the name by which our object will be known to the outside world
            self.nameServer.remove(self.pigID)
        
        except NamingError:
            pass"""
        
        self.nameServer.register(self.pigID, self.pURI)
        return daemon
        
        


#*************************        connectToneighbors_pURI()        ***********************    

    def connectToneighbors_pURI(self):
        #print "NS items", self.nameServer.list(prefix="pig.bird").items()
        for pigID, pURI in self.nameServer.list(prefix="pig.bird").items():
            if(pigID != self.pigID and pigID in self.peers):
                self.neighbors_pURI[pigID]  = Pyro4.Proxy(pURI)
        #print "My peer neighbors_pURI are: ", self.neighbors_pURI




#*************************        get_physical_positions()        ***********************    

    def get_physical_positions(self):#returns 
        other_file_path = os.path.join(current_file_dir, "..", "config.txt")
        
        f = open(other_file_path, 'rw')
        
        
        for line in f:
            line = line.strip()
            line = line.rstrip('\n')
            line = line.split("=")
            self.pig_positions[line[0]] = line[1]
            
        f.close()
        return self.pig_positions#Dictionary = {"pig.bird.peer1":"1,1",....}
        
        
        
#*************************        get_static_neighbors_pURI()        ***********************    
     
     
    def get_static_neighbors_pURI(self):
        
        other_file_path = os.path.join(current_file_dir, "..", "phy_neigh_static.txt")

        
        with open(other_file_path, 'r') as f:
            f.seek(0)
            self.static_neighbors_pURI = {}
            lines  = f.readlines()# lines is a list
            for line in lines:
                line.rstrip('\n')
                co = line.split("=")
                do = co[1].split(";")
                n_ = []
                for d in do:
                    n_.append(d)
                self.static_neighbors_pURI[co[0]] = n_   
        #print "static_neighbors_pURI", self.static_neighbors_pURI
        
        return self.static_neighbors_pURI#Dictionary = {"0,0":["0,1","1,0"], ....}
          
          
               
               
#*************************        bird_approaching(position, hopcount, senders, senders_take_shelter, landing_time)        ***********************    
               
        
    def bird_approaching(self, position, hopcount, senders, senders_take_shelter, landing_time):#position is a list
        print self.pigID, ": Received bird_approaching message at ", datetime.datetime.now().time().strftime('%H:%M:%S')
        print self.pigID, ": Hopcount", hopcount
        self.pig_positions = self.get_physical_positions()#we are appending in this function. so, locked
        #print "pig_positions", self.pig_positions
        
        #Take evasive action here and then decrementing and sending
        #If the position is yours, get static physical neighbor coordinates of your current position.
            #If any one of your static neighboring positions is not present in pig_positions,change your position to that and write to config.txt
                #If hopcount > 0, decrement hopcount, append your pigID in senders, call send_bird_approaching on your peer pigs
            #Else, you are going to be hit and call take_shelter(pigID) and in takeshelter(pigID), send that.
            
        #print "self.physical_position", self.physical_position
        #print "position", position
        #if (self.physical_position[0] == position[0] && self.physical_position[1] == position[1]):
        #if len(set(self.physical_position) & set(position)) != 0:
    
        if self.physical_position[0] == position[0] and \
           self.physical_position[1] == position[1]:
           
            print self.pigID, ": Target position is mine"
            #kk = True
            #print "kk", kk
            physical_list_lock.acquire()
            #if landing_time - 2 * hopcount == 0:
                #You are hit
                
                #self.was_hit(self.pigID, True)
            #else:
                #Check if your neighboring positions are empty
                    #If empty, move and update
                    #If not, you are hit
            self.static_neighbors_pURI = self.get_static_neighbors_pURI()
            str_neigh1 = str(position[0])
            str_neigh2 = str(position[1])
            str_neigh = str_neigh1 + ',' + str_neigh2   
        
            
            my_physical_neigh = self.static_neighbors_pURI[str_neigh]
            for p in my_physical_neigh:
                #str_temp = str(p[0]) + ',' + str(p[1])
                if p not in self.pig_positions.values():#p is empty
                    physical_list_lock.acquire()
                    self.physical_position = p
                    other_file_path = os.path.join(current_file_dir, "..", "config.txt")
                    
                    with open(other_file_path, 'r+') as f:
                        lines = f.readlines()
                        for k in lines:
                            k.strip('\n')
        
                        for i, line in enumerate(lines):
                            if self.pigID in line:
                                spline = line.split(" = ")
                                spline.remove(spline[1])
                                line = str(spline[0])
            
                                line = line + " = " + p + '\n'
                                lines[i] = line
            

                                
                        f.seek(0)                    
                        for line in lines:
                            f.write(line)  
                    
                    print self.pigID, ": I changed my position to ", self.physical_position        
                    cflag = 1
                    """#Decrement hopcount and Send this to your peer pigs
                        hopcount = int(hopcount)
                        if hopcount > 0:
                            hopcount = hopcount - 1
                            senders.append(self.pigID)
                            physical_list_lock.release()            

                            self.send_bird_approaching(position, hopcount, senders)"""
                    physical_list_lock.release()
                    break
                else:
                    cflag = 0
            print "cflag", cflag   
            if cflag == 0:# If you don't find any empty neighboring positions
                    #You are going to be hit and send take_shelter message and set hitFlag to True
                print self.pigID, ": I am going to be hit"
                self.was_hit(self.pigID, True)
                
                    #Find your neighboring positions - my_physical_neigh
                pig_dict = dict((key, value) for key, value in self.pig_positions.iteritems() if key.startswith("pig"))
                for p in my_physical_neigh:#If there are pigs in your neighboring positions, set pigID to that pigID and send this message
                    if p in pig_dict.values():
                        for key in pig_dict.keys():
                            if pig_dict[key] == p:
                                pigID = key#Neighboring pig's ID
                                #Extract pURI's and call take_shelter on them
                                senders_take_shelter.append(self.pigID)
                                for pigID, pURI in self.neighbors_pURI.items():                                        
                                    pURI.take_shelter(pigID, senders_take_shelter)
                
                        
        #Check if the position is your neighboring position
        #If so, check if you any other empty neighboring position
            #If so, move there. And update in config.txt
            #If you can't, you are going to be hit by a stone or a pig after it is hit            
        else: # 'position' is not yours
            physical_list_lock.acquire()
            count = 0
            self.static_neighbors_pURI = self.get_static_neighbors_pURI()
            #print "self.static_neighbors_pURI", self.static_neighbors_pURI
            str_neigh1 = str(self.physical_position[0])
            str_neigh2 = str(self.physical_position[1])
            str_neigh = str_neigh1 + ',' + str_neigh2       
            #print "str_neigh", str_neigh
            
            my_physical_neigh = self.static_neighbors_pURI[str_neigh]
            #print "my_physical_neigh", my_physical_neigh
            str_temp = str(position[0]) + ',' + str(position[1])
            #print "str_temp", str_temp
            cflag = 1
            if str_temp in my_physical_neigh:#The 'position' is my neighboring position
                print self.pigID," : This position is my neighboring position"
                for p in my_physical_neigh:
                    if p != str_temp:
                        if p not in self.pig_positions.values():#empty at p
                            self.physical_position = p
                            other_file_path = os.path.join(current_file_dir, "..", "config.txt")
                            
                            with open(other_file_path, 'r+') as f:
                                lines = f.readlines()
                                for k in lines:
                                    k.strip('\n')
        
                                for i, line in enumerate(lines):
                                    if self.pigID in line:
                                        spline = line.split(" = ")
                                        spline.remove(spline[1])
                                        line = str(spline[0])
            
                                        line = line + " = " + p + '\n'
                                        lines[i] = line
            

                                
                                f.seek(0)                    
                                for line in lines:
                                    f.write(line)
                                print self.pigID, ": I changed my position to ", self.physical_position
                            
                            cflag = 1
                            break
                        
                        else:
                            cflag = 0
                    
                if cflag == 0:
                #There is a chance that you are going to be rolled over by the hitting pig
                #You are hit
                #Send bird_approaching to your neighbors_pURI
                #Decrement hopcount and Send this to your peer pigs
                    hopcount = int(hopcount)
                    if hopcount > 0:
                        print self.pigID, ": Hopcount before decrementing", hopcount
                        hopcount = hopcount - 1
                        senders.append(self.pigID)
                        physical_list_lock.release()            

                        self.send_bird_approaching(position, hopcount, senders, senders_take_shelter, landing_time)
                    self.was_hit(self.pigID, True)
            else:#Not in my neighboring positions also
                hopcount = int(hopcount)
                print self.pigID, ": Hopcount before decrementing", hopcount
                if hopcount > 0:
                    hopcount = hopcount - 1
                    senders.append(self.pigID)
                    physical_list_lock.release()            

                    self.send_bird_approaching(position, hopcount, senders, senders_take_shelter, landing_time)               
            
      
      
            
#*************************        take_shelter(pigID)        ***********************    
    def take_shelter(self, pigID, senders_take_shelter):
        if self.pigID == pigID:
            #Take evasive action
            self.static_neighbors_pURI = self.get_static_neighbors_pURI()
            str_neigh1 = str(self.physical_position[0])
            str_neigh2 = str(self.physical_position[1])
            str_neigh = str_neigh1 + ',' + str_neigh2       
        
            
            my_physical_neigh = self.static_neighbors_pURI[str_neigh]
            for p in my_physical_neigh:
                if p not in senders_take_shelter:
                    if p not in self.pig_positions.values():
                        self.physical_position = p
                        take_shelter_lock.acquire()
                        other_file_path = os.path.join(current_file_dir, "..", "config.txt")
                        with open(other_file_path, 'r+') as f:
                            lines = f.readlines()
                            for k in lines:
                                k.strip('\n')
                            for i, line in enumerate(lines):
                                if self.pigID in line:
                                    spline = line.split("=")
                                    spline.remove(spline[1])
                                    line = str(spline[0])
            
                                    line = line + " = " + p + '\n'
                                    lines[i] = line
                            f.seek(0)
                            for line in lines:
                                f.write(line) 
                        take_shelter_lock.release()

                        cflag = 1
                        break
                        
                    else:
                        cflag = 0
                    
            if cflag == 0:
                #You are going to be hit and set hitFlag to True
                print "Pig ", self.pigID, " hit by pig rolling over"
                self.was_hit(self.pigID, True)
                
        else:
            #Send to your peer neighbors_pURI
            senders_take_shelter.append(self.pigID)
            for ppigID, pURI in self.neighbors_pURI.items():
                if ppigID not in senders_take_shelter:
                    threading.Thread(target = pURI.take_shelter, kwargs={'pigID':pigID, 'senders_take_shelter': senders_take_shelters}).start()
            
            
            
            
    
#*************************        send_bird_approaching(position, hopcount, senders)        ***********************    
        
    def send_bird_approaching(self, position, hopcount, senders, senders_take_shelter, landing_time):
        print "Sending bird_approaching message with hopcount", hopcount, " and position ", position, " to my peer pigs"
        time.sleep(2)
        for pigID, pURI in self.neighbors_pURI.items():
            if pigID not in senders:
                
                threading.Thread(target = pURI.bird_approaching, kwargs={'position':position, 'hopcount': hopcount, 'senders':senders, 'senders_take_shelter':senders_take_shelter,'landing_time':landing_time}).start()
                #time.sleep(2)
        
#*************************        status(pigID, status_senders)        ***********************    
        
    def status(self, pigID, status_senders):
        if self.pigID != pigID:
            #Append yourself to status_senders.
            status_senders.append(self.pigID)#***********************
            #Call send_status(pigID, status_senders)
            self.send_status(pigID, status_senders)
            
        else:
            #This is my pigID
            #Need to reply with flag
            #Call send_status_reply(self, pigID, status_senders, self.hitFlag)
            self.send_status_reply(self.pigID, status_senders, self.hitFlag)#**********************
            
            
            
            
        
#*************************        send_status(pigID, status_senders)        ***********************    
    
    def send_status(self, pigID, status_senders):
        print "Sending status(",pigID,") message to my peers to reach ", pigID, "."
        for pigID, pURI in self.neighbors_pURI.items():
            if pigID not in status_senders:
                threading.Thread(target = pURI.status, kwargs={'pigID':pigID, 'status_senders':status_senders}).start()
                
                
                

#*************************        send_status_reply(pigID, status_senders, hitFlag)        ***********************    

    def send_status_reply(self, pigID, status_senders, hitFlag):
        while len(status_senders) != 0:
            pig_popped = status_senders.pop()
            pURI = self.neighbors_pURI[pig_popped]
            pURI.send_status_reply(pigID, status_senders, hitFlag)
            
        print "Pig ID ", pigID, "'s status is ", hitFlag
        
        
        #while(status_senders != empty)
            #Pop from status_senders
            #Find pURI
            
        #pigID, hitFlag 
        
        
        
        

#*************************        status_all(status_all_senders, status_all_replies)        ***********************    
        
    def status_all(self, status_all_senders, status_all_replies):
        #Send this message to all
        
        #call send_status_all_reply() here 
        status_all_senders.append(self.pigID)
        status_all_replies_pigID = []
        status_all_replies_flag = []
        self.send_status_all_reply(status_all_senders, status_all_replies_pigID, status_all_replies_flag)
        
        
        
        self.send_status_all(status_all_senders, status_all_replies)
        
        
        
        
        
        
#*************************        send_status_all(status_all_senders)        ***********************    
            
    def send_status_all(self, status_all_senders, status_all_replies):
        
        for pigID, pURI in self.neighbors_pURI.items():
            if len(status_all_senders) != 0:
                if pigID not in status_all_senders:
                    print "Sending status_all message to everybody"
                    threading.Thread(target = pURI.status_all, kwargs={'status_all_senders':status_all_senders, 'status_all_replies':status_all_replies}).start()
                
                
                

#*************************        send_status_all_reply(status_all_senders, status_all_replies)        ***********************    
        
    def send_status_all_reply(self, status_all_senders, status_all_replies_pigID, status_all_replies_flag):
        #if len(status_all_senders) != 0:
            
        status_all_replies_pigID.append(self.pigID)
        status_all_replies_flag.append(self.hitFlag)
        print "status_all_senders", status_all_senders
        print "status_all_replies_pigID", status_all_replies_pigID
        print "status_all_replies_flag", status_all_replies_flag
        
        
        pig_popped = status_all_senders.pop()
        if self.pigID != pig_popped:
            pURI = self.neighbors_pURI[pig_popped]
            pURI.send_status_all_reply(status_all_senders, status_all_replies_pigID, status_all_replies_flag)
        #Calculate score from status_all_replies
        if len(status_all_replies_pigID) == 6:
            
            self.score = sum(1 for condition in status_all_replies_flag if condition)
            print "Score is (number of birds not hit) is ", self.score
        
        
        

#*************************        was_hit(pigID, trueFlag)        ***********************    
        
    def was_hit(self, pigID, trueFlag):    
        hitFlag = trueFlag
        
        
        
        
#*************************        broadcast_for_phyCoord(senders, self.pigID)        ***********************        
    
    def broadcast_for_phyCoord(self, senders, pigID):
        self.senders[self.pigID] = self.physical_position
        for pigID, pURI in self.neighbors_pURI.items():
            if(pigID != self.pigID and pigID in self.peers):
                self.neighbors_pURI_URI[pigID]  = Pyro4.Proxy(pURI)
                