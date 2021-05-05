#!/usr/bin/env python
import re
import os
import zipfile
from collections import Counter    

global term_id
term_id = 0
global doc_id
doc_id = 0

global docID_map
docID_map = {}
global termID_map
termID_map = {}
global terminfo_map
terminfo_map = {}

global postingList
postingList = {}


# Regular expressions to extract data from the corpus
doc_regex = re.compile("<DOC>.*?</DOC>", re.DOTALL)
docno_regex = re.compile("<DOCNO>.*?</DOCNO>")
text_regex = re.compile("<TEXT>.*?</TEXT>", re.DOTALL)


with zipfile.ZipFile("ap89_collection_small.zip", 'r') as zip_ref:
    zip_ref.extractall()
   
# Retrieve the names of all files to be indexed in folder ./ap89_collection_small of the current directory
for dir_path, dir_names, file_names in os.walk("ap89_collection_small"):
    allfiles = [os.path.join(dir_path, filename).replace("\\", "/") for filename in file_names if (filename != "readme" and filename != ".DS_Store")]
    
for file in allfiles:
    with open(file, 'r', encoding='ISO-8859-1') as f:
        filedata = f.read()
        result = re.findall(doc_regex, filedata)  # Match the <DOC> tags and fetch documents

        for document in result[0:]:
            # Retrieve contents of DOCNO tag
            docno = re.findall(docno_regex, document)[0].replace("<DOCNO>", "").replace("</DOCNO>", "").strip()
            # Retrieve contents of TEXT tag
            text = "".join(re.findall(text_regex, document))\
                      .replace("<TEXT>", "").replace("</TEXT>", "")\
                      .replace("\n", " ")

            #print(text)

            #convert text to lowercase
            text = text.lower()
            #print(text)
            
            #remove punctuation
            punctuation = '''!()-[]{};:'"`\.,<>/?@#$%^&*_~'''
            for character in text:
                if character in punctuation:
                    text = text.replace(character, "")
        
            #print(text)

            #tokenize and remove stopwords
            tokenized_text = []
            pattern = re.compile("[\w']+")
            tokenized_text = pattern.findall(text)
            #print(tokenized_text)
            stopwords = []
            with open('stopwords.txt', 'r') as file:
                 for word in file:
                    remove = re.compile('\\n')
                    word = remove.sub('', word)
                    stopwords.append(word)
                    #print(stopwords)
            
            for word in stopwords:
                while(word in tokenized_text):
                    tokenized_text.remove(word)
            #print(tokenized_text)


            # step 3 - build index
            #generate term_id, doc_id, and find position of each term
           
            #increase doc number count
            doc_id += 1
            #add to map
            docID_map[doc_id] = docno

            #write docid/docno to file
            f = open(r"docids.txt", "a+")
            f.write(f'{doc_id}\t{docno}\n')
            f.close()
           
           #reset position for each document
            pos = 0           

            for word in tokenized_text:
                #increment per word
                #check for duplicates
                pos +=1
                #get # of occurrences of word in text
                docfreq = tokenized_text.count(word)
                #print(docfreq)

                if word not in termID_map:
                    term_id += 1
                    #print(termID_map)
                    #update map
                    termID_map[word] = term_id
                   
                    #write to file
                    #holds all unique ids 
                    f = open(r"termids.txt", "a+")
                    termid_list = f.readlines()    
                    f.write(f'{term_id}\t{word}\n')
                    f.close()
                    #write to file
                    f = open(r"term_index.txt", "a+")
                    f.write(f'{term_id}\t{doc_id}:{pos}\n')
                    f.close()
                    
                    postingList[word] = []
                    tuple = (doc_id, docfreq, pos) 

                    if termID_map[word] not in postingList:
                        postingList[word].append(tuple)
                    
                        terminfo_map[term_id]=(postingList[word])
                    print(terminfo_map)
                   # print(postingList)

                else:
                    #if duplicate, find term_id
                    temp_termID = termID_map[word]                    
                    #append to end of each unique term_id
                    with open(r"term_index.txt", "r+") as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            if line.startswith(f'{temp_termID}'):
                                lines[i] = lines[i].strip() + f'\t{doc_id}:{pos}\n'
                        f.seek(0)
                        for line in lines:
                            f.write(line)
                    f.close()
                
                        
                    tuple = (word, temp_termID, pos)
                    if termID_map[word] not in postingList:
                        postingList[word].append(tuple) 
                        terminfo_map[term_id]=(postingList[word])

                    #print(postingList)        
            
            #print(tuple_list)  
            print(f"doc {doc_id} complete")                             

#get terminfo ?               
with open("term_index.txt", "r+") as f:
    lines = f.readlines()
    line_offset = []
    offset = 0
    for line in lines:
        line_offset.append(offset)
    offset += len(line)
file.seek(0)

file.seek(line_offset[n])
