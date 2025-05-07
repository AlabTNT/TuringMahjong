from flask import Flask, request, redirect, jsonify, render_template, send_file, url_for, flash
from flet import Page, Row, Column, MainAxisAlignment, Checkbox, icon, ElevatedButton, Text, TextField, Icon, Image, Card, Container
import flet as ft
import flask as fk
import tkinter as tk
from os import path,remove
import os
import sys
from json import load, dump
from datetime import datetime
from hashlib import md5
from time import sleep, time
import threading
from random import randint, choice, shuffle
import random as rand
import subprocess
from typing import Any, Union, Dict, List, Callable
import re
from copy import deepcopy

__version__="1.2.0"



def __itt_date__(itrr:list|dict):
    itr=deepcopy(itrr)
    if type(itr)==list:
        for i in itr:
            if type(i)==datetime:
                i=i.strftime("%Y-%m-%d/%H:%M:%S")
            elif type(i) in [list, dict]:
                __itt_date__(i)
    elif type(itr)==dict:
        for i in itr:
            if type(itr[i])==datetime:
                itr[i]=itr[i].strftime("%Y-%m-%d/%H:%M:%S")
            elif type(itr[i]) in [list, dict]:
                __itt_date__(itr[i])
    return itr

def __unitt_date__(itrr:list|dict):
    itr=deepcopy(itrr)
    if type(itr)==list:
        for i in itr:
            if type(i)==str:
                if "/" in i:
                    i=handle_time(i)
            elif type(i) in [list, dict]:
                __unitt_date__(i)
    elif type(itr)==dict:
        for i in itr:
            if type(itr[i])==str:
                if "/" in itr[i]:
                    itr[i]=handle_time(itr[i])
            elif type(itr[i]) in [list, dict]:
                __unitt_date__(itr[i])
    return itr

def read_raw_json(target) -> list|dict:
    with open(target,'r',encoding='utf-8',errors='replace') as f:
        return load(f)
    
def read_raw_data(target) -> list|dict:
    with open(f"./data/{target}.json",'r',encoding='utf-8',errors='replace') as f:
        return load(f)

def write_raw_json(target,data):
    with open(target,'w',encoding='utf-8',errors='replace') as f:
        dump(data,f)

def write_raw_data(target,data):
    with open(f"./data/{target}.json",'w',encoding='utf-8',errors='replace') as f:
        dump(data,f)

def read_json(target) -> list|dict:
    return __unitt_date__(read_raw_json(target))

def read_data(target) -> list|dict:
    return __unitt_date__(read_raw_data(target))
    

def write_json(target,data):
    d=__itt_date__(data)
    with open(target,'w',encoding='utf-8',errors='replace') as f:
        dump(d,f)
    
def write_data(target,data):
    d=__itt_date__(data)
    with open(f"./data/{target}.json",'w',encoding='utf-8',errors='replace') as f:
        dump(d,f)

def rhash(data)->str:
    return md5(str(data).encode()).hexdigest()

def wlog(data:str, types:str="Info")->str:
    t=datetime.now()
    day=t.strftime("oflog.%Y-%m-%d.log")
    t=t.strftime("%m-%d %H:%M:%S")
    if not path.exists("log"):
        os.mkdir("log")
    with open(f"log/{day}",'a',encoding='utf-8',errors='replace') as f:
        f.write(f"[{t}][{types}] {data}\n")   
    print(f"[{t}][{types}] {data}\n")
    
def handle_time(timestring:str) -> datetime:
    try:
        timestring=timestring.replace("：",":").replace("\\","/")
        if "/" in timestring:
            #有时间的
            __t=timestring.split("/")
            date=__t[0].split("-")
            time=__t[1].split(":")
            if len(date)==3: #带年份的
                if len(date[0])==2: #年份没补全的
                    date[0]="20"+date[0]
                if len(date[1])==1: #月份没补0的
                    date[1]="0"+date[1]
                if len(date[2])==1:
                    date[2]="0"+date[2]
            elif len(date)==2:
                date.insert(0,str(datetime.now().year))
                if len(date[1])==1: #月份没补0的
                    date[1]="0"+date[1]
                if len(date[2])==1: #日期没补0的
                    date[2]="0"+date[2]
            else:
                raise
                
            if len(time)==2: #不带秒的
                if time[0]=="23" and time[1]=="59": #
                    time.append("59")
                else:
                    time.append("00")
                if len(time[0])==1:
                    time[0]="0"+time[0]
            elif len(time)==3: #带秒的
                if len(time[0])==1:
                    time[0]="0"+time[0]
            
        else:
            date=timestring.split("-")
            time=["00","00","00"]
            if len(date)==3: #带年份的
                if len(date[0])==2: #年份没补全的
                    date[0]="20"+date[0]
                if len(date[1])==1: #月份没补0的
                    date[1]="0"+date[1]
                if len(date[2])==1:
                    date[2]="0"+date[2]
            elif len(date)==2:
                date.insert(0,str(datetime.now().year))
                if len(date[1])==1: #月份没补0的
                    date[1]="0"+date[1]
                if len(date[2])==1: #日期没补0的
                    date[2]="0"+date[2]
            else:
                raise
        this=datetime.strptime("-".join(date)+"/"+":".join(time),"%Y-%m-%d/%H:%M:%S")
        return this
    except:
        return None