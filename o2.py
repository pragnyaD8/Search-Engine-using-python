from nltk import word_tokenize
from nltk.stem import PorterStemmer
import string
from bs4 import BeautifulSoup
with open("stopwordlist.txt") as f:
    text= f.read()
    stopwords=text.split()
# print(forward_index)
def forward_extract(info):
    info = info.split('\n')
    forward_index = {}
    for e in info:
        if e!="":
            key = e.split("      ")[0]
            x = e.split("      ")[1]
            newdict = {}
            for each in x.split(";"):
                y = each.split(" ")
                new_list = []
                for e in y:
                    if e!= "":
                        new_list.append(e)
                newdict[new_list[0]] = new_list[1]
            forward_index[key] = newdict

    return forward_index
def inverted_extract(info):
    info = info.split("\n")
    inverted_index = {}
    for e in info:
        if e!="":
            key = e.split("      ")[0]
            x = e.split("      ")[1]
            newdict = {}
            for each in x.split(";"):
                y = each.split(": ")
                new_list = []
                # print(y)
                for e in y:
                    if e!= "":
                        new_list.append(e)
                newdict[new_list[0]] = new_list[1]
            inverted_index[key] = newdict
    return inverted_index

def splitString(inputstr):
    outputstring = []
    for e in inputstr:
        check = ""
        for eachletter in e:
            if eachletter in string.punctuation:
                check = eachletter
        if check=="":
            if e not in string.punctuation and IntegerCheck(e)==0:
                outputstring.append(e)
        else:
            for each_split in e.split(check):
                if IntegerCheck(each_split)==0 and each_split!="":
                    outputstring.append(each_split)
    return outputstring

def IntegerCheck(stri):
    try:
        check = int(stri)
        flag = 1
    except Exception as e:
        flag = 0
        
    if flag == 1:
        return 1
    return 0

def sortDict(ele):
    for i, char in enumerate(ele):
        if isinstance(char, int):
            break
    return ele[:i], int(''.join(map(str, ele[i:])))
with open("topics.txt" 'r') as f:
        queries= f.read().split('</top>\n')
def parsequery(info):
    for e in info:
        x = str(e)
        if x != "\n":

            q_data = str(x)
    q_data = q_data.split("\n")
    title = ""
    for e in q_data:
        if "<title>" in each:
            title = e.split("<title>")[1]
    title = title.strip()
    count=0
    for e in q_data:
        if "<desc>" in e:
            i = count + 1
        if "<narr>" in e:
            j=count -1
        count+=1
    desc = "".join(q_data[i:j])
    count = 0
    for each in q_data:
        if "<narr>" in each:
            i= count+1
        if '</narr>' in each:
            j = count
        count+=1
    narr = "".join(q_data[i:j])

    return title,desc,narr
import math
def parsetopic(info):
    for each in info:
        x = str(each)
        if x != "\n":

            q_data = str(x)
    q_data = q_data.split("\n")
    topic_id = ""
    for each in q_data:
        if "<num>" in each:
            topic_num = each.split("<num>")[1]
    topic_id = topic_num.strip()
    # print(topic_num)
    topic_id = topic_id.split("Number: ")[1].strip()
    return str(topic_id)
def preformfunction(new_query,idf_values,inverted_index,forward_index):
    preprocess_query = performanceAnalysis(new_query)
    query_term_freqs = {}
    for term in preprocess_query:
        query_term_freqs[term] = query_term_freqs.get(term, 0) + 1
    query_terms = list(set(preprocess_query))
    query_weights = {}

    for term in query_terms:
        tf = query_term_freqs[term]
        if term in idf_values:
            idf = idf_values[term]
            query_weights[term] = tf * idf

    matching_docs = set()
    for term in query_terms:
        if term in inverted_index:
            matching_docs.update(inverted_index[term])


    doc_weight = {}
    for doc_id in matching_docs:
        doc_id = doc_id.lstrip()
        doc_weight[doc_id] = {}
        for term in query_terms:
            doc_id = doc_id.lstrip()
            if term in forward_index[str(doc_id)] and term in idf_values:
                tf = float(forward_index[str(doc_id)][term])
                idf = float(idf_values[term])
                doc_weight[doc_id][term] = tf * idf

    scores = {}
    for doc_id in matching_docs:
        doc_id = doc_id.lstrip()
        dot_product_list = []
        magnitude_q_list = []
        magnitude_doc_list = []
        for term in query_terms:

            if term in doc_weight[doc_id] and term in query_weights:
                dot_product_list.append(query_weights[term] * doc_weight[doc_id].get(term, 0))
                magnitude_q_list.append(query_weights[term]**2)
                magnitude_doc_list.append(doc_weight[doc_id][term]**2)
            
        dot_product = sum(dot_product_list)
        magnitude_query = math.sqrt(sum(magnitude_q_list))
        magnitude_doc = math.sqrt(sum(magnitude_doc_list))
        scores[doc_id] = dot_product / (magnitude_query * magnitude_doc)


    ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_docs = [doc_id for doc_id, score in ranked_docs]
    return_dict = {}
    cnt = 0
    for key,val in ranked_docs:
        return_dict[key] = val
        cnt+=1
        if cnt==3:
            break

    return top_docs,return_dict
def performanceAnalysis(preprocess):
    process_list = []
    process_list = word_tokenize(preprocess)
    process_list = [i for i in process_list if i not in stopwords]
    process_list = splitString(process_list)
    process_list = splitString(process_list)
    process_list = [i for i in process_list if not IntegerCheck(i)]
    process_list = [i.lower() for i in process_list]
    process_list = [i for i in process_list if len(i)!=0]
    stemmer = PorterStemmer()
    process_list = [stemmer.stem(word) for word in process_list]
    return process_list
with open('main.qrels', 'r') as f:
    info= f.read()

# Convert the main.qrels file to a Python dictionary
g_truth = {}
for l in info.split('\n'):
    if l.strip():
        query_id, _, doc_id, relevance_label = l.split()
        x = int(str(doc_id).split("-")[1])
        y = int(str(doc_id).split("-")[0].split("FT")[1])
        relevance_label = int(relevance_label)
        if relevance_label > 0 and y == 911 and x<=5368:
            if query_id not in g_truth:
                g_truth[query_id] = {}
            g_truth[query_id][doc_id] = relevance_label
with open('forward_index.txt', 'r') as f:
    info = f.read()
    forward_index = forward_extract(info)
with open('inverse_index.txt', 'r') as f:
    data = f.read()
    inverted_index = inverted_extract(info)

with open('topics.txt', 'r') as f1:
    soup = BeautifulSoup(f1, "html.parser")
    queries = soup.find_all("top")


N = len(forward_index)  
idf_values = {}
for term in inverted_index:
    df = len(inverted_index[term])  
    idf_values[term] = math.log(N / df)
results_list = []


for query in queries:
    title, description, narrative = parsequery(query)
    topics_id = parsetopic(query)
    new_query = title 
    top_docs,t_ranks = preformfunction(new_query,idf_values,inverted_index,forward_index)
    relevant_docs = [doc_id for doc_id in top_docs if doc_id in g_truth[topics_id]]
    # precision = (len(relevant_docs) / len(top_docs)) * 100
    recall = (len(relevant_docs) / len(g_truth[topics_id])) * 100
    count = 1
    # print(topics_id)
    print(recall, " recall for title as query")
    for key in t_ranks:
        g_str = str(topics_id)+"      "+str(key)+"          "+str(count)+"     "+str(t_ranks[key])
        results_list.append(g_str)
        count+=1
    new_query = title + narrative
    top_docs,t_ranks = preformfunction(new_query,idf_values,inverted_index,forward_index)
    relevant_docs = [doc_id for doc_id in top_docs if doc_id in g_truth[topics_id]]
    for key in t_ranks:
        g_str = str(topics_id)+"      "+str(key)+"          "+str(count)+"     "+str(t_ranks[key])
        results_list.append(g_str)
        count+=1
    # precision = (len(relevant_docs) / len(top_docs)) * 100
    recall = (len(relevant_docs) / len(g_truth[topics_id])) * 100
    print(recall, " recall for title + narrative as query")
    new_query = title + description 
    top_docs,t_ranks = preformfunction(new_query,idf_values,inverted_index,forward_index)
    relevant_docs = [doc_id for doc_id in top_docs if doc_id in g_truth[topics_id]]
    # precision = (len(relevant_docs) / len(top_docs)) * 100
    recall = (len(relevant_docs) / len(g_truth[topics_id])) * 100
    print(recall, " recall for title + description as query")


    for k in t_ranks:
        g_str = str(topics_id)+"      "+str(k)+"          "+str(count)+"     "+str(t_ranks[k])
        results_list.append(g_str)
        count+=1


with open('output.txt', 'w') as file:
    for item in results_list:
        file.write(str(item) + '\n')
    