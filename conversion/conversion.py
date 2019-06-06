#!/usr/bin/python3
import csv, sys, re, matplotlib, math
import matplotlib.pyplot as plt
files=sys.argv[1:]

for i in range(len(files)):
    with open(files[i], newline='') as csvfile:
        raw_data=list(csv.reader(csvfile, delimiter=','))[0]
        data=[int(x,16) for x in raw_data]

    if re.search(r"^ds_",files[i]):
        temp=[x*0.0625 for x in data]
        ds=temp
        time=[x for x in range(len(temp))]

        plt.figure(1)
        matplotlib.style.use('seaborn')
        plt.plot(time,temp,'k')
        plt.xlabel('Vrijeme[s]')
        plt.ylabel('Temperatura[°C]')
        plt.title('Karakteristika senzora DS18B20')
        plt.grid(True)
        continue

    if re.search(r"^lm35", files[i]):
        temp=[x*300/1023 for x in data]
        lm35=temp
        time=[x for x in range(len(temp))]

        plt.figure(2)
        matplotlib.style.use('seaborn')
        plt.plot(time,temp,'k')
        plt.xlabel('Vrijeme[s]')
        plt.ylabel('Temperatura[°C]')
        plt.title('Karakteristika senzora LM35DZ')
        plt.grid(True)
        continue

    if re.search(r"^ntc_2", files[i]):
        voltage=[x*3.3/1023 for x in data]

        R1 = 25000
        R2 = 16000
        VCC = 3.3
        T = 25 + 273.15

        ntc_resistance = [(R1*R2*(VCC - x))/(x*(R1 + R2) - VCC*R2) for x in voltage]
        a = [(1/T) + (1/3900)*math.log(x/10000) for x in ntc_resistance]
        ntc = [(1/x) - 273.15 for x in a]
        # ntc=voltage
        time=[x for x in range(len(voltage))]

        plt.figure(3)
        matplotlib.style.use('seaborn')
        plt.plot(time,ntc,'k')
        plt.xlabel('Vrijeme[s]')
        plt.ylabel('Temperatura[°C]')
        plt.title('Karakteristika senzora NTC')
        plt.grid(True)
        continue

    if re.search(r"^ntc_max", files[i]):
        temp=[x*0.125 for x in data]
        ntc_max=temp
        time=[x for x in range(len(temp))]

        plt.figure(4)
        matplotlib.style.use('seaborn')
        plt.plot(time,temp,'k')
        plt.xlabel('Vrijeme[s]')
        plt.ylabel('Temperatura[°C]')
        plt.title('Karakteristika senzora NTC+MAX')
        plt.grid(True)
        continue

    if re.search(r"^termopar", files[i]):
        temp=[(x>>3)*0.25 for x in data]
        thermocouple=temp
        time=[x for x in range(len(temp))]

        plt.figure(5)
        matplotlib.style.use('seaborn')
        plt.plot(time,temp,'k')
        plt.xlabel('Vrijeme[s]')
        plt.ylabel('Temperatura[°C]')
        plt.title('Karakteristika senzora Termopar + MAX')
        plt.grid(True)
        continue

    if re.search(r"^tmp", files[i]):
        temp=[(x>>4)*0.0625 for x in data]
        tmp=temp
        time=[x for x in range(len(temp))]

        plt.figure(6)
        matplotlib.style.use('seaborn')
        plt.plot(time,temp,'k')
        plt.xlabel('Vrijeme[s]')
        plt.ylabel('Temperatura[°C]')
        plt.title('Karakteristika senzora TMP101')
        plt.grid(True)
        continue

    if re.search(r"^gnico", files[i]):
        voltage=[(x*3.3)/1023 for x in data]
        gnico=voltage

        VCC = 5
        R1 = 61.1 * pow(10, 3)
        R2 = 56 * pow(10, 3)
        R3 = 732
        R4 = 39 * pow(10, 3)

        X = VCC * (1 + R4 * (1/R2 + 1/R3) )
        Y = -VCC * R4 / R2

        RTD = [0 for x in range(len(voltage))]
        RTD = [( R1 * voltage - Y * R1 )/(X + Y - voltage) for voltage in voltage]
        # brojnik=[56000*x for x in voltage]
        # nazivnik=[(15.8*5 - x) for x in voltage]
        # otpor=[0 for x in range(len(brojnik))]
        ad=[0 for x in range(len(voltage))]
        a = -412.6
        b = 140.41
        c = 0.00764
        d = -6.25*pow(10,-17)
        e = (-1.25)*pow(10, -24)

        for i in range(len(voltage)):
            # otpor[i]=brojnik[i]/nazivnik[i]
            ad[i]=( a + b*pow(1+c*RTD[i], 0.5) + d*pow(RTD[i], 5) + e*pow(RTD[i],7))

        time=[x for x in range(len(voltage))]
        gnico=ad
        plt.figure(7)
        matplotlib.style.use('seaborn')
        plt.plot(time, gnico,'k')
        plt.xlabel('Vrijeme[s]')
        plt.ylabel('Temperatura[V]')
        plt.title('Karakteristika senzora G-NICO')
        plt.grid(True)
        continue

# fig, ax = plt.subplots()
# ax.plot(time, gnico, 'k--', label='DS18B20')
# ax.plot(time, thermocouple, 'k:', label='Termopar')
# legend = ax.legend(loc='upper left', shadow=True, fontsize='x-small')
#
# legend.get_frame().set_facecolor('C0')

plt.show()
