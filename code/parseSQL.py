# -*- coding: utf-8 -*-

##############################################################################
#   NAME:       parseSQL
#   PURPOSE:    Get all table list from SQL file using python
#
#   REVISIONS:
#   Ver        Date           Author           Description
#  -------     ----------     ---------------  ------------------------------------
#   0.1        2014-02-04     EunPyo Hong      1. Created this File.
#
#   NOTES:	  
#
##############################################################################


import re
import glob
import os
import sys, getopt

tableList = []      # 테이블 목록
withTableList = []  # WITH문 테이블 리스트
fileName = ''       # 파일 명
fileList = []       # 파일 리스트(전체 SQL 파일)

OUTPUT_FILE = ''       # 저장할 파일명
INPUT_SQL = ''            # SQL 저장 폴더

# 파일 읽기
def readFile(file):
    global fileName
    
    f = open(file, 'r')
    
    isBeforeFrom = 0
    isLoopContinue = 0  # Parsing 해야 할 SELECT 부분인지 확인
    isComment = 0 # '/* */' 주석 확인
    
    
    try:
        for line in f:
            # 한줄 주석 건너뛰기
            if re.match(' *--', line):
                continue
            
            # '/* */' 주석 처리
            if re.match('.*/\*', line):
                if re.match('.*\*/', line):
                    isComment = 0
                    continue
                else:
                    isComment = 1
            
            # '/* */' 주석 넘어감
            if isComment == 1:
                continue
            
            # SELECT, WITH문 찾으면 ';' 만날때 까지 루프
            if (re.match('^SELECT', line) or re.match('^WITH', line)) and isLoopContinue != 1:
                isLoopContinue = 1
                # WITH문으로 시작하면 WITH 테이블 명은 제외
                if re.match('^WITH', line):
                    line = re.search('WITH[ ]+[A-Z0-9._]*', line).group()
                    line = re.sub('WITH[ ]+', '', line)
                    withTableList.append(line)
            
            # 다중 WITH문 처리
            if re.match('.*,[ |\t]*[A-Za-z0-9\._]*[ ]+AS', line):
                line = line[line.find(',')+ 1 :line.find('AS')].strip()
                withTableList.append(line)
                continue
            
            # ';' 만나면 종료
            if line.find(';') > -1 and isLoopContinue == 1:
                break
            
            # FROM과 JOIN 뒤의 글짜 뽑기
            if ((re.match('[^A-Za-z0-9\.]*FROM', line) or line.find(' JOIN ') > -1 or line.find(' FROM ') > -1) and isLoopContinue == 1) or isBeforeFrom == 1 :
                if isBeforeFrom != 1:
                    # FROM이나 JOIN이후 테이블명이 않나오는 걸 처리
                    temp = re.search('(FROM|JOIN).*', line).group().strip()
                    
                    # FROM이나 JOIN 바로 뒤에 '(' 만나면 건너뜀
                    if re.match('FROM\(', line.lstrip()):
                        isBeforeFrom = 0
                        continue
                    
                    # FROM이나 JOIN 뒤 줄바꿈 있으면 다음줄에 처리
                    if temp == 'FROM' or temp == 'JOIN':
                        isBeforeFrom = 1
                        continue
                else:
                    # FROM이나 JOIN뒤에 '(' 만나면 건너뜀
                    #if line.find('(') > -1:
                    if re.match('^\(', line.lstrip()):
                        isBeforeFrom = 0
                        continue

                
                # '..' 뒤 공백 제거
                line = re.sub('\.\. *', '..', line)
                
                # 'FROM', 'JOIN'문 제거
                if line.find('FROM') > -1 or line.find('JOIN') > -1:
                    line = re.search('(FROM|JOIN)([ ]|\t)+[A-Za-z.0-9_\xa1-\xfe/\[\]]*', line).group()
                    line = re.sub('(FROM|JOIN)([ ]|\t)+', '', line)
                
                # 주석 및 필요 없는 문장 제거
                line = re.search('^[A-Za-z.0-9_\xa1-\xfe/\[\]]*', line.lstrip()).group()

                
                # '..' 있으면 앞부분 제거
                if line.find('..') > -1:
                    line = re.sub('[A-Za-z]+\.\.', '', line)
                    tableList.append(line)
                # '.' 있을 떄 처리
                elif line.find('.') > -1:
                    line = line.split('.')
                    tableList.append(line[len(line)-1])
                # 공백 들어가지 않게 처리
                elif len(line) > 0:
                    tableList.append(line)    

                isBeforeFrom = 0
        
        temp = os.path.basename(file)
        fileName = os.path.splitext(temp)
        
    finally:
        f.close()
    
    return tableList
  
# 파일 쓰기
def writeFile(file, count, tableList):
    f = open(file, 'a')
    
    for i in range(len(tableList)):
        f.write(str(count) + ',' + fileName[0] + ',' + tableList[i] + '\n')
                
    f.close()
    

# 파일 리스트 얻기
def getFileList(INPUT_SQL):
    for dirname, dirnames, filenames in os.walk(INPUT_SQL):
    #디렉토리처리
        # for subdirname in dirnames:
            # name = os.path.join(dirname, subdirname)
            # print name
    #파일처리
        for filename in filenames:
            fileList.append(os.path.join(dirname, filename))

# csv 파일 체크
def checkFile(file):
    if os.path.isfile(file):
        os.remove(file)

# 배열 내 중복 데이터 제거
def removeDup(tableList):
    return {}.fromkeys(tableList).keys() 

def printHelp():
    print "Usage: parseSQL.py -s [SOURCE SQL FOLDER] -t [TARGET FILE NAME]"

#**************************************
#  Main Start
#**************************************

# Arg 처리
try:
    opts, arg = getopt.getopt(sys.argv[1:],"hs:t:",["source=","target="])   # -h는 인수 없고 -s, -t는 뒤에 인수 받음.
    
    # 인수 없을 때 처리
    if len(opts) == 0:
        printHelp()
        sys.exit(2)
except getopt.GetoptError:
   printHelp()
   sys.exit(2)

for opt, arg in opts:
    if opt == '-h':
        printHelp()
        sys.exit()
    elif opt in ("-s", "--source"):
        INPUT_SQL = arg
    elif opt in ("-t", "--target"):
        OUTPUT_FILE = arg

# 파일 확인. 있으면 삭제
checkFile(OUTPUT_FILE)

# SQL 파일 리스트 받아오기
getFileList(INPUT_SQL)

count = 0

# 파일 리스트 받아서 처리
for i in fileList:
    count += 1
    tableList = readFile(i)
    tableList = removeDup(tableList)
    # WITH 테이블 지우기
    tableList = list(set(tableList) - set(withTableList))
    
    writeFile(OUTPUT_FILE, count, tableList)
    tableList = []
    withTableList = []
