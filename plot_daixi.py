#!/usr/bin/python
# -*- coding:utf-8 -*-

r=0

from tkinter import filedialog,Tk
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MultipleLocator,FormatStrFormatter

#读取数据路径
Tk().withdraw()
filetypes0 = [('text files','.txt')]
filepath0 = filedialog.askopenfilename(initialdir=os.getcwd(),
                                        title='Select files:',
                                        filetypes=filetypes0)

#读取数据
source_data=np.array([]).reshape(0,2)
f=open(filepath0,'r',encoding='utf-8')
line=f.readline()
while line:
    line=f.readline()
    line=line[2:-1]
    if line=='Elements':
        break

line=f.readline()
while line:
    k_str=line.split('k=')[-1].split()[0]
    if '(' in k_str:
        k_str=k_str.split('(')[0]
    k_data=float(k_str)
    line=f.readline()
    if 'i' in line:
        line=line.replace('i','j')
    freq_data=abs(complex(line))
    source_data=np.concatenate((source_data,np.array([[k_data,freq_data]])))
    line=f.readline()

f.close()
source_data=source_data[source_data[:,0].argsort()]

#整理数据
xdata=list(set(source_data[:,0]))
xdata.sort()
m=0
for i in xdata:
    max=len(np.where(source_data[:,0]==i)[0])
    if m<max:
        m=max
m=m+1
r=round(r)
if r<1 or r>m-1:
    r=m-1

data=np.array([]).reshape(0,m)
for i in xdata:
    data0=np.insert(np.sort(source_data[source_data[:,0]==i,1]),0,i)
    if len(data0)<m:
        data0=np.concatenate((data0,np.full([1,m-len(data0)],np.nan)))
    data=np.concatenate((data,data0.reshape(1,m)))

#写入数据
filepath1= os.path.split(filepath0)[0]+'/'
filename0='.'.join(os.path.split(filepath0)[1].split('.')[:-1])
data_w = pd.DataFrame(data)
writer = pd.ExcelWriter(filepath1+filename0+'.xlsx')
data_w.to_excel(writer,filename0,header=False,index=False,encoding='utf-8')
writer.save()
writer.close()

#计算带隙位置
dx0=np.array([[0,np.nan]])
for i in range(1,r+1):
    dx0[-1,1]=data[:,i].min()
    dx0=np.concatenate((dx0,np.array([[data[:,i].max(),np.nan]])))
dx0=dx0[:-1,:]

for i in range(r):
    if dx0[r-1-i,1]-dx0[r-1-i,0]<0.1:
        dx0=np.delete(dx0,r-1-i,axis=0)

#分离间断数据
axx1=[r'$\Gamma$','X','M',r'$\Gamma$','R','X|R','M','$X_1$']

data0=[]
data1=[]
if data[-1,0]<=5:
    data0=data[data[:,0]<5,:]
    axx1[5]='X'
elif data[0,0]>=5:
    data1=data
    axx1[5]='R'
else:
    data0=data[data[:,0]<5,:]
    data1=data[data[:,0]>=5,:]
if 1 in data[:,0] and data0[-1,0]>4:
    data0=np.concatenate((data0,data0[data0[:,0]==1,:]))
    data0[-1,0]=5

#绘图
fig1 = plt.figure(1)
ax = plt.subplot(111)

for i in range(1,r+1):
    if len(data0)>1:
        plt.plot(data0[:,0],data0[:,i],'b')
    if len(data1)>1:
        plt.plot(data1[:,0],data1[:,i],'b')

xrange=[int(round(data[0,0])),int(round(data[-1,0]))]
plt.xlim(xrange)
plt.ylim(bottom=0)

axx0=range(xrange[0],xrange[1]+1)
plt.xticks(axx0,axx1[xrange[0]:xrange[1]+1])


'''
ymajorLocator = MultipleLocator(2000)
ymajorFormatter = FormatStrFormatter('%d')

ax.yaxis.set_major_locator(ymajorLocator)
ax.yaxis.set_major_formatter(ymajorFormatter)

yminorLocator = MultipleLocator(1000)
ax.yaxis.set_minor_locator(yminorLocator)
'''

ax.tick_params(direction='in')
ax.xaxis.grid(True, which='major')
ax.yaxis.grid(False,which='both')
ymax=plt.axis()[-1]

plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False
##plt.xlabel('K')
plt.ylabel('Frequency(Hz)')


ax1=plt.twinx()
for i in range(len(dx0[:,0])):
    rect = plt.Rectangle((xrange[0],dx0[i,0]),xrange[1],dx0[i,1]-dx0[i,0],color='silver',alpha=1)
    ax1.add_patch(rect)
plt.ylim([0,ymax])

ax1.set_yticks(dx0.reshape(1,-1)[0])
ax1.tick_params(direction='in')

fig1.show()
fig1.savefig(filepath1+filename0+'.png',dpi=640)
