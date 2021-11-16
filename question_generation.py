import re
import os
import sys
import nltk
import spacy
from argparse import ArgumentParser # arguments manager
# from graphviz import Digraph

"""
Identify NER marks within each sentence

"""
# Model Harem Tags
def find_names_HAREM(nent):
    names = []
    pattern = "<EM(.+?)>(.+?)</EM>"
    rgx = re.compile(pattern)
    # identifiers = re.compile('"(.+?)"')
    identifiers = re.compile("'(.+?)'")
    match = [ ((identifiers.findall(x[0]),x[1])) for x in rgx.findall(nent)]
    for idx, x in enumerate(rgx.findall(nent)):
        names.append((x[1],match[idx][0][1]))
    return names


# Model CoNLL B-I-O
def find_names_CoNLL(nent):
    names = []
    for sn in nent:
        ent = sn.split(" ")
        if len(ent) > 1 and ent[1] != "O":
            if "B-" in ent[1]:
                names.append((ent[0], ent[1]))
            elif "I-" in ent[1]:
                last_name, last_cat = names[-1]
                names[-1] = ((last_name+" "+ent[0], last_cat))
            else:
                print("Exception : "+str(ent)+"\n") # exception
    return names

"""
Extract relations using triplets: Arg1 + REL + Arg2
"""
def find_triplets(sentence):
    nlp = spacy.load("pt_core_news_sm")
    doc = nlp(sentence)
    # graph = Digraph('G', filename='sentence.gv', format='png', node_attr={'shape': 'plaintext'})
    triplets = []
    for d in doc:
        triple = []
        main_pos = ["NOUN", "PROPN", "VERB"]
        if (d.dep_ == "nsubj" or d.dep_ == "nsubj:pass") and d.pos_ in main_pos:
            if d.head.pos_ == "VERB" and d.head.pos_ in main_pos:
                triple.append(d)
                triple.append(d.head)
                d2 = [d_ for d_ in doc if d_.head.i == d.head.i and d_ != d.head and d_ not in triple]
                if d2 != [] and triple != [] and d2[0].pos_ in main_pos:
                    triple.append(d2[0])


            elif d.head.pos_ in main_pos:
                triple.append(d)
                triple.append(d.head)
                d2 = [d_ for d_ in doc if d_.head.i == d.head.i and d_ != d.head and d_ not in triple and d_.pos_ == "VERB"]
                if d2 != [] and triple != []:
                    triple.append(d2[0])

        triple = [x for _, x in sorted(zip([t.i for t in triple], triple))]
        text = [tkn.text for tkn in triple]
        if len(triple) == 3:
            dependency = ["flat:name", "case", "nmod", "obj", "appos", "amod", "advmod", "acl:relcl", "obl", "conj", "xcomp"]
            t_ids = [(t.i, t.i+1) for t in triple]
            for tid, t in enumerate(triple):
                c1 = [d_ for d_ in doc if d_.head == t and d_ not in triple  and d_.dep_ in dependency]
                c2 = c1
                while c2 != []:
                    c2 = ([d_ for d_ in doc if d_ not in c1  and d_.head in c1 and d_.dep_ in dependency])
                    c1 = c1 + c2

                complements = c1
                if complements != []:
                    complements.append(t)
                    limits = (min([c.i for c in complements]), max([c.i for c in complements])+1)

                    ini, end = limits
                    if tid < 2 and end > t_ids[tid+1][0]:
                        end = t_ids[tid+1][0]
                    if tid > 0 and ini <= t_ids[tid-1][1]:
                        ini = t_ids[tid-1][1]

                    while doc[ini].dep_ == "punct": ini = ini+1

                    limits = (ini, end)
                    t_ids[tid] = limits

                    text[tid] = " ".join([doc[wi].text for wi in range(limits[0], limits[1])])

            triplets.append(text)
    return triplets

"""
Extract the segment indices on match (sentence location)
"""
def find_matching(mylist, pattern):
    match = []
    for i in range(len(mylist)):
        if mylist[i:i+len(pattern)] == pattern:
            match.append((i, i+len(pattern)))
    if match != []:
        return match[0]
    else:
        return None

"""
Generate quetions using the NER models
"""
def qgen(name, model, a1, rel, a2, phr):
    print((name, model, a1, rel, a2))
    question = ""
    if "TME" in model: # "TEMPO"
        if name in a1:
            question = a1.replace(name, " qual período ")+" "+rel+" "+a2+"?"
        elif name in rel:
            question = a1+" "+rel.replace(name, " de que período ")+" "+a2+"?"
        elif name in a2:
            question = a1+" "+rel+" "+a2.replace(name, " em que época ")+"?"
        else:
            print("Model not found!")
    elif "PER" in model: # "PESSOA"
        if name in a1:
            question = a1.replace(name, " quem ")+" "+rel+" "+a2+"?"
        elif name in rel:
            question = a1+" "+rel.replace(name, " quem ")+" "+a2+"?"
        elif name in a2:
            question = a1+" "+rel+" "+a2.replace(name, " quem ")+"?"
        else:
            print("Model not found!")
    elif "ORG" in model: # "ORGANIZACAO"
        if name in a1:
            question = a1.replace(name, " qual organização")+" "+rel+" "+a2+"?"
        elif name in rel:
            question = a1+" "+rel.replace(name, " qual organização ")+" "+a2+"?"
        elif name in a2:
            question = a1+" "+rel+" "+a2.replace(name, " qual organização ")+"?"
        else:
            print("Model not found!")
    elif "MISC" in model: # "ABSTRACCAO"
        if name in a1:
            question = a1.replace(name, " o que ")+" "+rel+" "+a2+"?"
        elif name in rel:
            question = a1+" "+rel.replace(name, " que abstração ")+" "+a2+"?"
        elif name in a2:
            question = a1+" "+rel+" "+a2.replace(name, " de qual abstração ")+"?"
        else:
            print("Model not found!")
    elif "PLC" in model: # "LOCAL"
        if name in a1:
            question = a1.replace(name, " que local ")+" "+rel+" "+a2+"?"
        elif name in rel:
            question = a1+" "+rel.replace(name, " de qual lugar ")+" "+a2+"?"
        elif name in a2:
            question = a1+" "+rel+" "+a2.replace(name, " aonde ")+"?"
        else:
            print("Model not found!")
    elif "VAL" in model: # "VALOR"
        if name in a1:
            question = a1.replace(name, " qual valor ")+" "+rel+" "+a2+"?"
        elif name in rel:
            question = a1+" "+rel.replace(name, " de qual valor ")+" "+a2+"?"
        elif name in a2:
            question = a1+" "+rel+" "+a2.replace(name, " qual valor ")+"?"
        else:
            print("Model not found!")
    elif "OBR" in model: # "OBRA"
        if name in a1:
            question = a1.replace(name, " que obra ")+" "+rel+" "+a2+"?"
        elif name in rel:
            question = a1+" "+rel.replace(name, " que obra ")+" "+a2+"?"
        elif name in a2:
            question = a1+" "+rel+" "+a2.replace(name, " qual obra ")+"?"
        else:
            print("Model not found!")
    else:
        print("Model not found!")
    if question != "":
        question = question.strip()
        question = question[0].upper()+question[1:]
        return question
    return None

"""
Load NER pairs (plain / marked) sentences
"""
def load_NER(in_path, out_put):
    documents = []
    for d in os.listdir(in_path):
        names = ""
        phrase = ""
        with open(out_put+d, "r") as rdb:
            names = [s_ for s_ in rdb.read().split("\n") if s_ != ""]
        
        with open(in_path+d, "r") as rdb:
            phrase = " ".join([s_ for s_ in rdb.read().split("\n") if s_ != ""])

        if phrase != "":
            documents.append((names, phrase))
    return documents


def main():
    parser = ArgumentParser(usage="%(prog)s [args] <datasetdir>",  description="Question Generation")
    parser.add_argument("-i", "--input", dest="data_input", default="IBERLEF_IN/", help="Input path name. Default 'input/' .")
    parser.add_argument("-o", "--output", dest="data_output", default="IBERLEF_OUT/", help="Output path name. Default 'output/' .")
    args = parser.parse_args()

    documents = []
    entities = []
    triplets = []

    documents = load_NER(args.data_input, args.data_output)

    out_ = 0
    for nent, phr in documents:
        triplets =  find_triplets(phr)
        entities = find_names_CoNLL(nent)
        if triplets != [] and entities != []:
            try:
                loc_a1, loc_rel, loc_a2 = zip(*[(find_matching(phr, a1), find_matching(phr, rel), find_matching(phr, a2)) for a1, rel, a2 in triplets])
                for e, cle in entities:
                    loc_e = find_matching(phr, e)
                    st, nd = loc_e
                    for a1, a2, a3 in zip(loc_a1, loc_rel, loc_a2):
                        st1, nd1 = a1
                        st2, nd2 = a2
                        st3, nd3 = a3
                        start_tri = 0
                        end_tri = 0
                        argument1 = ""
                        relation = ""
                        argument2 = ""

                        if st1 < st2 and st1 < st3:
                            start_tri = st1
                            argument1 = phr[st1:nd1]
                        elif st2 < st3:
                            start_tri = st2
                            argument1 = phr[st2:nd2]
                        else:
                            start_tri = st3
                            argument1 = phr[st3:nd3]

                        if st1 < st2 and st2 < st3:
                            relation = phr[st2:nd2]
                        elif st1 < st3:
                            relation = phr[st1:nd1]
                        else:
                            relation = phr[st3:nd3]

                        if st3 > st1 and st3 > st2:
                            end_tri = nd3
                            argument2 = phr[st3:nd3]
                        elif st2 > st1:
                            end_tri = nd2
                            argument2 = phr[st2:nd2]
                        else:
                            end_tri = nd1
                            argument2 = phr[st1:nd1]

                    question = qgen(e, cle, argument1, relation, argument2, phr)
                    if question != None:
                        with open("d"+str(out_)+"_questions.txt", "a") as wtr:
                            wtr.write("-"+phr+" \n -"+question+"\n\n")
                out_ =+ 1
            except Exception as e:
                print(e)

if __name__ == "__main__":
    main()