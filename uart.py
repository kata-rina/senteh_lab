#!/usr/bin/python3

import serial, struct, csv, time, threading, datetime, re

serial_com=0
global files_opened
files_opened=0
packets=bytearray([])

strings=[[],[],[],[],[],[],[]]
time_control=[0, 0, 0, 0, 0, 0, 0]
#----------------------------------------------------------------------------------
def getFile(sensor):

    global gnico_writer
    global lm35_writer
    global ds_writer
    global ntc_writer
    global ntc_max_writer
    global termopar_writer
    global tmp_writer

    writer={
            1:lm35_writer,
            2:ds_writer,
            3:tmp_writer,
            4:gnico_writer,
            5:termopar_writer,
            6:ntc_max_writer,
            7:ntc_writer
            }
    return writer.get(sensor)

#----------------------------------------------------------------------------------
#funkcija za izračun 8bitnog crc iz dobivenih podataka
def crc_racun(podatak1,podatak2,opkod2):
    maska=(0x1 << 8)
    pom=0x01
    j=0
    devider=0x1D5
    ostatak=0
    shift=0

    if opkod2[5]==0:
       podatak1=podatak1[::-1]
       podatak2=podatak2[::-1]
    for i in range(4):                                                          #podaci moraju biti tipa int
        podatak1[i]=int(format(podatak1[i],'032b'),2)
        podatak2[i]=int(format(podatak2[i],'032b'),2)
    podatak1=((podatak1[0]<<24)|(podatak1[1]<<16)|(podatak1[2]<<8)|(podatak1[3]))   #posloži podatke za izračun
    podatak2=((podatak2[0]<<24)|(podatak2[1]<<16)|(podatak2[2]<<8)|(podatak2[3]))
    ostatak=(podatak1>>23)
    i=0
    for i in range(64):
        if(maska & ostatak):
            ostatak=(ostatak ^ devider)
        ostatak=(ostatak << 1)

        if(i<23):
            shift=(podatak1 >> (22-i))
            shift=(shift & pom)
            ostatak=(ostatak|shift)
        elif(i>=23 and i<55):
            shift=(podatak2 >> (31-j))
            shift=(shift & pom)
            ostatak=(ostatak | shift)
            j+=1

    ostatak=(ostatak >> 1)
    ostatak=format(ostatak,'08b')
    return ostatak

#------------------------------------------------------------------------------------
# funkcija za konfiguraciju serijskog prikjučka
# ako se pošalje krivi serijski priključak funkcija vraća vrijednost nula
def set_configuration(portname,baudrate):
    global serial_object

    try:
        serial_object=serial.Serial(portname, baudrate)        #definiranje veze sa serijsku komunikaciju
        serial_com=1
    except serial.SerialException:
        serial_com=0
        return 0

#------------------------------------------------------------------------------------
def open_files(path):
    global files_opened
    files_opened = 1
    time = str(datetime.datetime.now())
    time = time[0:19]
    time = re.sub(" ", "_", time)
    time = re.sub(":", "_", time)

    filename1 = path + "gnico_" + time + ".csv"
    filename2 = path+ "tmp_" + time + ".csv"
    filename3 = path + "lm35_" + time + ".csv"
    filename4 = path + "ds_" + time + ".csv"
    filename5 = path + "ntc_max_" + time + ".csv"
    filename6 = path + "ntc_" + time + ".csv"
    filename7 = path + "termopar_" + time + ".csv"

    global gnico
    gnico = open(filename1, 'a+', newline='')
    global tmp
    tmp = open(filename2, 'a+', newline='')
    global lm35
    lm35 = open(filename3, 'a+', newline='')
    global ds
    ds = open(filename4, 'a+', newline='')
    global ntc_max
    ntc_max = open(filename5, 'a+', newline='')
    global ntc
    ntc = open(filename6, 'a+', newline='')
    global termopar
    termopar = open(filename7, 'a+', newline='')

    global gnico_writer
    gnico_writer = csv.writer(gnico)
    global tmp_writer
    tmp_writer = csv.writer(tmp)
    global lm35_writer
    lm35_writer = csv.writer(lm35)
    global ds_writer
    ds_writer = csv.writer(ds)
    global ntc_max_writer
    ntc_max_writer = csv.writer(ntc_max)
    global ntc_writer
    ntc_writer= csv.writer(ntc)
    global termopar_writer
    termopar_writer = csv.writer(termopar)

#------------------------------------------------------------------------------------
#slanje zahtjeva za podatak s određenog senzora
def sendRequest(senzor):
    serial_object.write(senzor.encode('utf-8'))


#-------------------------------------------------------------------------------------
#slanje zahtjeva za namještanje temperature
#   argument: a=duty cycle, b= način rada (grijanje, hlađenje ili all off)
def send_duty_cycle(a,b):
    a_to_int = int(a)
    duty_cycle = format(a_to_int, '05d')
    coeff = b + duty_cycle

    n = serial_object.write(coeff.encode('utf-8'))

#-------------------------------------------------------------------------------------
#slanje temperature na stm
# def send_temperature(temp):
#     n=serial_object.write(temp.encode('utf-8'))

#--------------------------------------------------------------------------------------
# funkcija koja čita zapakirane podatke sa svih senzora
# funkcija raspakirava pakete podataka i sprema ih u csv datoteku
# def readData():
#     opkod=0
#     podatak1=0
#     podatak2=0
#     crc=0
#     podaci=[]
#     pod1=[]
#     pod2=[]
#
#     while True:
#
#         broj=serial_object.in_waiting                                           #iz buffera pročitaj broj primljenih bajtova
#         if broj==0:                                                             #ako nemamo ništa za pročitati izađi van
#             return
#         paket=serial_object.read(broj)                                          #inače pročitaj sve dobivene podatke
#         for i in range(broj):                                                   #iteriraj kroz bajtove i nalazi pakete
#             error=0
#             crc_yes=0
#             # n=serial_object.in_waiting
#             # paket.append(serial_object.read(n))
#             # broj+=n
#             if paket[i]==65:
#                 if paket[i+1]==66:                                              #nakon što smo našli početak paketa provjeravaj
#                     opkod=int(format(paket[i+2], '08b'))                        #operacijski kod i podatke
#                     #provjera je li ispravan operacijski kod
#                     if (not((0x70 & opkod)==0x70) or (opkod & 0x70)):
#                         brojac=int(format(paket[i+3], '08b'), 2)
#                         opkod2=(format(paket[i+2], '08b'))
#                         senzor=int(opkod2[1:4],2)
#
#
#                         for a in range(8):
#                             try:
#                                 podaci.append(paket[i+a+4])
#                             except IndexError:
#                                 error=1
#                                 continue
#                         if (error==1):
#                             error=0
#                             time_control[senzor-1]+=1.0
#                             temperatura=-1
#                             strings[senzor-1].append(temperatura)
#                             continue
#
#                         podatak1=podaci[0:4]
#                         podatak2=podaci[4:8]
#                         if (opkod & 0x04):                                      #ako je MSB okreni podatke
#                             podatak2=podatak2[::-1]
#                             podatak1=podatak1[::-1]
#                         pod1=float(format((struct.unpack('<f', struct.pack('4B', *podatak1))[0]), '.4f'))
#                         pod2=float(format((struct.unpack('<f', struct.pack('4B', *podatak2))[0]), '.4f'))
#
#                         if not(opkod & 0x08):
#                             temperatura=pod2
#                             vrijeme=pod1
#                         else:
#                             temperatura=pod1
#                             vrijeme=pod2
#
#                         if (time_control[senzor-1]!=vrijeme):
#                             temperatura=0
#                             strings[senzor-1].append(temperatura)
#
#                         time_control[senzor-1]+=1.0
#
#                         if (opkod & 0x02):          #ako ima crc izračunaj crc i postavi zastavicu
#                             crc=format(paket[i+12], '08b')
#                             mojcrc=crc_racun(podatak1,podatak2,opkod2)
#
#                             if(crc != mojcrc):
#                                 print('crc ne valja')
#                                 temperatura=0
#                                 strings[senzor-1].append(temperatura)
#                                 continue
#
#                             crc_yes=1
#
#                         if (opkod & 0x01): #ako ima oznake za kraj
#                             if crc_yes:     #ako ima crc
#                                 if ((paket[i+13]!=89) or (paket[i+14]!=90)): #ako nije dobra oznaka za kraj preskoči
#                                         continue
#
#                                 else:
#                                     # file=getFile(senzor)
#                                     strings[senzor-1].append(temperatura)
#                                     # file.writerow([vrijeme,temperatura])
#                                     podaci=[]
#
#                             elif ((paket[i+12]!=89) or (paket[i+13]!=90)): #ako ima oznake za kraj a nema crc-a i ako nije dobar znak za kraj
#                                 continue
#
#                             else:
#                                 strings[senzor-1].append(temperatura)
#                                 podaci=[]
#
#                         else:
#                             strings[senzor-1].append(temperatura)
#                             podaci=[]

#-----------------------------------------------------------------------------------------------------

#funkcija koja na kraju prekida komunikaciju i zatvara datoteku u koju smo spremali podatke
def end_communication():

    global gnico
    global termopar
    global ntc_max
    global ntc
    global tmp
    global lm35
    global ds
    global files_opened

    if (serial_com==1):
        serial_com==0
        serial_object.close()


    if (files_opened==1):
        for i in range(7):
            time_control[i]=0
            sensor=i+1
            file=getFile(sensor)
            file.writerow(data for data in strings[i])
            strings[i]=[]

        files_opened=0
        gnico.close()
        termopar.close()
        ntc_max.close()
        ntc.close()
        tmp.close()
        lm35.close()
        ds.close()

#--------------------------------------------------------------------------------------------
def close_files():

    global gnico
    global termopar
    global ntc_max
    global ntc
    global tmp
    global lm35
    global ds
    global files_opened

    if (files_opened==1):

        for i in range(7):
            time_control[i]=0
            sensor=i+1
            file=getFile(sensor)
            in_file=strings[i]
            file.writerow([data for data in strings[i]])
            strings[i]=[]

        files_opened=0
        gnico.close()
        termopar.close()
        ntc_max.close()
        ntc.close()
        tmp.close()
        lm35.close()
        ds.close()


#------------------------------------------------------------------------------------------------------
#thread za periodičko čitanje sa serijske veze
#očitavanje se vrši svaku sekundu
class TimerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._is_running=True

        self.paused = True
        self.state = threading.Condition()

    def run(self):
        self.resume()
        # next_call=time.time()

        while True:
            next_call=time.time()
            with self.state:
                if self.paused:
                    self.state.wait()

            read_bytes()
            next_call+=1
            time.sleep(1)
            # time.sleep(next_call-time.time())

    def pause(self):  #pauziraj i čekaj za signal za ponovno pokretanje
        with self.state:
            self.paused = True

    def resume(self): #nastavi raditi
        with self.state:
            self.paused = False
            self.state.notify()

    def stop(self):
        self._is_running=False
        self.join()

#---------------------------------------------------------------------------------------
def read_bytes():

    broj=serial_object.in_waiting                                           #iz buffera pročitaj broj primljenih bajtova
    if broj==0:                                                             #ako nemamo ništa za pročitati izađi van
        return

    packets.extend(bytearray(serial_object.read(broj)))                                          #inače pročitaj sve dobivene podatke
#-------------------------------------------------------------------------------------

def bytes_to_data(packet):
    paket=packet
    opkod=0
    podatak1=0
    podatak2=0
    crc=0
    podaci=[]
    pod1=[]
    pod2=[]
    print(len(paket))
    for i in range(len(paket)):                                                   #iteriraj kroz bajtove i nalazi pakete
        error=0
        crc_yes=0
        if paket[i]==65:
            if paket[i+1]==66:                                              #nakon što smo našli početak paketa provjeravaj
                opkod=int(format(paket[i+2], '08b'))                        #operacijski kod i podatke
                #provjera je li ispravan operacijski kod
                if (not((0x70 & opkod)==0x70) or (opkod & 0x70)):
                    brojac=int(format(paket[i+3], '08b'), 2)
                    opkod2=(format(paket[i+2], '08b'))
                    senzor=int(opkod2[1:4],2)

                    for a in range(8):
                        podaci.append(paket[i+a+4])

                    podatak1=podaci[0:4]
                    podatak2=podaci[4:8]

                    if not(opkod & 0x08):
                        if (opkod & 0x04):#ako je MSB
                            temperatura=bytearray(podatak2).hex()
                            # temperatura=float(format((struct.unpack('>f', struct.pack('4B', *podatak2))[0]), '.4f'))
                            vrijeme=(struct.unpack('>I', struct.pack('4B', *podatak1))[0])
                        else:
                            podatak=podatak2[::-1]
                            temperatura=bytearray(podatak).hex()
                            # temperatura=float(format((struct.unpack('<f', struct.pack('4B', *podatak2))[0]), '.4f'))
                            vrijeme=(struct.unpack('<I', struct.pack('4B', *podatak1))[0])

                    else:
                        if (opkod & 0x04):#ako je MSB
                            temperatura=bytearray(podatak1).hex()
                            # temperatura=float(format((struct.unpack('>f', struct.pack('4B', *podatak1))[0]), '.4f'))
                            vrijeme=(struct.unpack('>I', struct.pack('4B', *podatak2))[0])

                        else:
                            podatak=podatak1[::-1]
                            temperatura=bytearray(podatak).hex()
                            # temperatura=float(format((struct.unpack('<f', struct.pack('4B', *podatak1))[0]), '.4f'))
                            vrijeme=(struct.unpack('<I', struct.pack('4B', *podatak2))[0])

                    if (time_control[senzor-1]!=vrijeme):
                        temperatura=-1
                        print('vrijeme krivo', senzor, vrijeme, temperatura, time_control[senzor-1])
                        strings[senzor-1].append(temperatura)

                    # if (time_control[senzor-1]==300):
                    #     time_control[senzor-1]=0
                    # else:
                    time_control[senzor-1]+=1

                    if (opkod & 0x02):          #ako ima crc izračunaj crc i postavi zastavicu
                        crc=format(paket[i+12], '08b')
                        mojcrc=crc_racun(podatak1,podatak2,opkod2)

                        if(crc != mojcrc):
                            print('crc kriv', senzor, vrijeme, mojcrc, crc)
                            temperatura=-2
                            strings[senzor-1].append(temperatura)
                            continue

                        crc_yes=1

                    if (opkod & 0x01): #ako ima oznake za kraj
                        if crc_yes:     #ako ima crc
                            if ((paket[i+13]!=89) or (paket[i+14]!=90)): #ako nije dobra oznaka za kraj preskoči
                                    continue

                            else:
                                if (vrijeme != 0):
                                    strings[senzor-1].append(temperatura)
                                podaci=[]

                        elif ((paket[i+12]!=89) or (paket[i+13]!=90)): #ako ima oznake za kraj a nema crc-a i ako nije dobar znak za kraj
                            continue

                        else:
                            if (vrijeme != 0):
                                strings[senzor-1].append(temperatura)
                            podaci=[]

                    else:
                        if (vrijeme != 0):
                            strings[senzor-1].append(temperatura)
                        podaci=[]
