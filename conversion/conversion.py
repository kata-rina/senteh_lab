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

        ntc_resistance = [(R1*R2*(VCC - x))/(x*(R1 + R2) - VCC*R2) for x in voltage]
        a = [(1/25) + (1/3900)*math.log(x/10000) for x in ntc_resistance]
        ntc = [1/x for x in a]
        # ntc=voltage
        time=[x for x in range(len(voltage))]

        plt.figure(3)
        matplotlib.style.use('seaborn')
        plt.plot(time,ntc_resistance,'k')
        plt.xlabel('Vrijeme[s]')
        plt.ylabel('Napon[V]')
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
        brojnik=[56000*x for x in voltage]
        nazivnik=[(15.8*5 - x) for x in voltage]
        otpor=[0 for x in range(len(brojnik))]
        ad=[0 for x in range(len(brojnik))]
        a=-412.6
        b=140.41
        c=0.00764
        d=-6.25*pow(10,-17)
        e=(-1.25)*pow(10, -24)
        for i in range(len(brojnik)):
            otpor[i]=brojnik[i]/nazivnik[i]
            ad[i]=(a+b*pow(1+c*otpor[i], 0.5)+d*pow(otpor[i],5)+e*pow(otpor[i],7))

        time=[x for x in range(len(voltage))]
        gnico=ad
        plt.figure(7)
        matplotlib.style.use('seaborn')
        plt.plot(time,ad,'k')
        plt.xlabel('Vrijeme[s]')
        plt.ylabel('Napon[V]')
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
