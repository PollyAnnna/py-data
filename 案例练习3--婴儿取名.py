#!/usr/bin/env python
# coding: utf-8

# **在1879年以后，对于YYYY的出生年份，我们创建了一个逗号分隔的文件yobYYYY.txt。
# 每个单独的年度文件中的每条记录都具有“名称、性别、编号”的格式，其中名称为2到15
# 字符，性别是M(男性)或F(女性)，“number”是名称出现的次数。
# 每个文件首先按性别排序，然后按降序排列出现的次数排序。当有
# 并列出现的次数上，按姓名字母顺序排列。这种排序很容易做到
# 确定名称的秩。每个性别的第一个记录为1，每个性别的第二个记录为1
# 第2级，以此类推。
# 为了保护隐私，我们将名单限制在至少出现5次的名字之内。
# https://www.ssa.gov/oact/babynames/limits.html

# In[23]:


import pandas as pd
import numpy as np
pd.options.display.max_rows=10


# In[24]:


get_ipython().system('type -n 10  C:\\Users\\polly\\Downloads\\names\\yob1880.txt  ')


# In[25]:


#先加载其中一个文件
names1880=pd.read_csv(r"C:\Users\polly\Downloads\names\yob1880.txt",names=['name','sex','births'])
names1880


# In[28]:


#用births列的sex分组小计表示该年度的births总计
names1880.groupby('sex')['births'].sum()


# ## 该数据集按年度被分隔成了多个文件，先要将所有数据都组装到一个DataFrame里面，并加上一个year字段

# ### 我的方法：

# In[37]:


years=range(1880,2019)
yns=[]
for year in years:
    yn=pd.read_csv(r"C:\Users\polly\Downloads\names\yob{}.txt".format(year),names=['name','sex','births'])
    yn.index=np.full(len(yn),year)   # shape为len（yn),值全部都是year的数组。np.full(shape,value)
    yns.append(yn)
yns


# In[42]:


all_names=pd.concat(yns)
all_names


# ### 书中的方法：

# In[45]:


years = range(1880, 2019)

pieces = []
columns = ['name', 'sex', 'births']

for year in years:
    path =r'C:\Users\polly\Downloads\names\yob%d.txt' % year
    frame = pd.read_csv(path, names=columns)

    frame['year'] = year
    pieces.append(frame)

#第一，concat默认是按行将多个DataFrame组合到一起的；
#第二，必须指定ignore_index=True，因为我们不希望保留read_csv所返回的原始行号。

all_names2 = pd.concat(pieces, ignore_index=True) 
all_names2


# ## 按性别和年度统计的总出生数:

# In[57]:


sex_births=all_names.pivot_table(index=all_names.index,columns='sex',values='births',aggfunc='sum')
sex_births.index.name='year'
sex_births


# In[59]:


import matplotlib.pyplot as plt


# In[61]:


sex_births.plot(title='Total births by sex and year') #Series和DataFrame都有一个plot方法。默认情况下，它们所生成的是线型图


# ## 插入一个prop列，用于存放每年指定名字的婴儿数相对于当年该性别总出生数的比例

# In[62]:


all_names2


# In[65]:


all_names2['prop']=all_names2['births']/(all_names['births'].sum())   #这样错误，要计算相对于该年、该性别的比例
all_names2


# In[66]:


#要计算相对于该年、该性别的比例，需groupby，再每组内部计算。
def add_prop(group):
    group['prop']=group.births/group.births.sum()
    return group
all_names2=all_names2.groupby(['year','sex']).apply(add_prop)
all_names2


# In[67]:


#做一些有效性检查，比如验证所有分组的prop的总和是否为1：
all_names2.groupby(['year','sex']).prop.sum()


# ## 需要取出该数据的一个子集：每对sex/year组合的前1000个名字:

# In[78]:


def get_top1000(group):
     return group.sort_values(by='births',ascending=False).head(1000)
top1000=all_names2.groupby(['year','sex']).apply(get_top1000) 
top1000


# In[79]:


top1000.reset_index() # index和列有重复，报错！


# In[80]:


top1000.reset_index(inplace=True, drop=True) #drop
top1000


# In[147]:


top1000[top1000.name=='Mary']


# ## 分析命名趋势:

# In[81]:


#首先将前1000个名字分为男女两个部分：
boys=top1000['sex'=='M']
girls=top1000['sex'=='F']


# In[84]:


boys=top1000[top1000.sex=='M']
girls=top1000[top1000.sex=='F']
boys


# ### 我的方法：

# In[126]:


def draw_nm(group,x):
    df=group[group['name'] in x][['year','births','name']]  # group['name'] in x这种写法错误！！
    return df.pivot(index='year',columns='name',values='births')
bnames=['John','Hary']
draw_nm(boys,bnames).plot(subplots=True,title="Number of boy births per year")


# In[138]:


#错误写法：
boys['name'] in bnames


# In[128]:


#正确写法：
boys['name'].isin(bnames)


# In[133]:


def draw_nm(group,x):
    df=group[group['name'].isin(x)][['year','births','name']] 
    return df.pivot(index='year',columns='name',values='births')


# In[137]:


bnames=['John','George']
draw_nm(boys,bnames).plot(subplots=True,title="Number of boy births per year") 
# DF.plot()默认是把index作为x轴，每列的数据画一条线，自行添加图例（每列的列名），y轴为每列的数据


# ### 书上方法：

# In[144]:


total_births = top1000.pivot_table('births', index='year',
                                   columns='name',
                                   aggfunc=sum)  # year+name 有可能会有重复，比如1880年的男的mary和女的mary，所以不能用pivot
subset = total_births[['John', 'Harry', 'Mary', 'Marilyn']]
subset.plot(subplots=True, figsize=(12, 10), grid=False,
            title="Number of births per year")


# In[148]:


import datetime from datetime


# ## 评估命名多样性的增长

# In[149]:


top1000


# In[156]:


table=top1000.pivot_table(index='year',columns='sex',values='prop',aggfunc='sum')
table


# In[157]:


table.plot(title='Sum of table1000.prop by year and sex',
 yticks=np.linspace(0, 1.2, 13), xticks=range(1880, 2020, 10))


# In[ ]:


#另一个办法是计算占总出生人数前50%的不同名字的数量，这个数字不太好计算。我们只考虑2010年男孩的名字：

