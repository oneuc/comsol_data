#!/usr/bin/python
# -*- coding:utf-8 -*-

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

#整理数据
m=0
n=1
for i in range(len(source_data[:,0]))[1:]:
    if abs(source_data[i,0]-source_data[i-1,0])<0.01:
        n=n+1
    else:
        if n>m:
            m=n
        n=1
if n>m:
    m=n
m=m+1

data=np.array([]).reshape(0,m)
data_k0=source_data[0,:]
for i in range(len(source_data[:,0]))[1:]:
    if abs(source_data[i,0]-source_data[i-1,0])<0.01:
        data_k0=np.append(data_k0,source_data[i,1])
    else:
        if len(data_k0)<m:
            nan0=np.full([1,m-len(data_k0)],np.nan)
            data_k0=np.concatenate((data_k0.reshape(1,-1),nan0),axis=1)
        data=np.concatenate((data,data_k0.reshape(1,-1)))
        data_k0=source_data[i,:]
if len(data_k0)<m:
    nan0=np.full([1,m-len(data_k0)],np.nan)
    data_k0=np.concatenate((data_k0,nan0),axis=1)
data=np.concatenate((data,data_k0.reshape(1,-1)))
data=data[data[:,0].argsort()]

#计算带隙位置
dx0=np.array([[0,np.nan]])
for i in range(1,m):
    dx0[-1,1]=data[:,i].min()
    dx0=np.concatenate((dx0,np.array([[data[:,i].max(),np.nan]])))
dx0=dx0[:-1,:]

for i in range(m-1):
    if dx0[m-2-i,1]-dx0[m-2-i,0]<0.1:
        dx0=np.delete(dx0,m-2-i,axis=0)

#写入数据
filepath1= os.path.split(filepath0)[0]+'/'
filename0=os.path.split(filepath0)[1].split('.')[0]
data_w = pd.DataFrame(data)
writer = pd.ExcelWriter(filepath1+filename0+'.xlsx')
data_w.to_excel(writer, 'Data',float_format='%f')
writer.save()
writer.close()

#绘图
fig1 = plt.figure(1)
ax = plt.subplot(111)

for i in range(1,data.shape[1]):
    plt.plot(data[:,0],data[:,i])

plt.xlim(0, 7)
plt.ylim(bottom=0)
axx0=range(8)
axx1=[r'$\Gamma$','R','M',r'$\Gamma$','X','M','R','X']
plt.xticks(axx0,axx1)

'''
ymajorLocator = MultipleLocator(2000)
ymajorFormatter = FormatStrFormatter('%d')

ax.yaxis.set_major_locator(ymajorLocator)
ax.yaxis.set_major_formatter(ymajorFormatter)

yminorLocator = MultipleLocator(1000)
ax.yaxis.set_minor_locator(yminorLocator)
'''

ax.xaxis.grid(True, which='major')
ax.yaxis.grid(False,which='both')
ymax=plt.axis()[-1]

plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False
plt.xlabel(u'波矢k')
plt.ylabel(u'频率f(Hz)')


ax1=plt.twinx()
for i in range(len(dx0[:,0])):
    rect = plt.Rectangle((0,dx0[i,0]), 7,dx0[i,1]-dx0[i,0],color='silver',alpha=1)
    ax1.add_patch(rect)
plt.ylim([0,ymax])

ax1.set_yticks(dx0.reshape(1,-1)[0])

fig1.show()
fig1.savefig(filepath1+filename0+'.png',dpi=640)

