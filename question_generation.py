import os
import spacy
from nltk.tree import Tree
import re

SENTS = ["Na verdade, é melhor compreender a história das ideias, principalmente ideias que emergiram da lógica matemática, uma disciplina obscura e cultual que primeiro se desenvolveu no século dezenove.",
          "Como um cientista da computação comentou: “Se, em 1901, um talentoso e simpático estranho fosse chamado a pesquisar as ciências e nomeasse o ramo que seria o menos frutífero para o século seguinte, sua escolha poderia muito bem ser estabelecida na lógica matemática.” E ainda, isto teria provido a fundação para um campo que teria mais impacto no mundo moderno que qualquer outro.",
          "A tese de Shannon surgiu quando Bush recomendou que ele tentasse descobrir tal teoria. “A matemática pode ser definida como o tópico no qual nós nunca raramente lido fora dos departamentos de filosofia.",
          "Boole é muitas vezes descrito como um matemático, mas ele viu a si mesmo como um filósofo, seguindo os passos de Aristóteles.",
          "Tentar improvisar no trabalho lógico de Aristóteles foi um movimento intelectual ousado."]

NER = ["""Na verdade , é melhor compreender a história das ideias , principalmente ideias que emergiram da lógica matemática , uma disciplina obscura e cultual que primeiro se desenvolveu <EM ID="Artigo1-3" CATEG="TEMPO">no século dezenove</EM> .""",
          """Como um cientista da computação comentou : “Se , <EM ID="Artigo1-7" CATEG="TEMPO">em 1901</EM> , um talentoso e simpático estranho fosse chamado a pesquisar as ciências e nomeasse o ramo que seria o menos frutífero para o século seguinte , sua escolha poderia muito bem ser estabelecida na lógica matemática .” E ainda , isto teria provido a fundação para um campo que teria mais impacto no mundo moderno que qualquer outro .""",
          """A tese de Shannon surgiu quando <EM ID="Artigo1-48" CATEG="PESSOA">Bush</EM> recomendou que ele tentasse descobrir tal teoria . “A matemática pode ser definida como o tópico no qual nós nunca raramente lido fora dos departamentos de filosofia .""",
          """Boole é muitas vezes descrito como um matemático , mas ele viu a si mesmo como um filósofo , seguindo os passos de <EM ID="Artigo1-72" CATEG="PESSOA">Aristóteles</EM> .""",
          """Tentar improvisar no trabalho lógico de <EM ID="Artigo1-81" CATEG="PESSOA">Aristóteles</EM> foi um movimento intelectual ousado ."""]

def person_ner(stks, loc, pre, pos):
    for l0, l1 in loc:
        if pre != [] and pos != []:
            # pre verbs and pos verbs exists
            print(" ".join(stks[:l0])+" quem "+" ".join(stks[l1:-1])+"?")
        elif pos != []:
            # just pre verbs
            vidx, v = pre[-1]
            if type(vidx) == tuple:
                vidx = vidx[0]
            print("Quem"+" ".join(stks[:vidx]))

        elif pre != []:
            # just pos verbs
            vidx, v = pos[0]
            if type(vidx) == tuple:
                vidx = vidx[0]
            print("Quem"+" ".join(stks[vidx:]))

        else:
            # no verbs
            print(" ".join(stks[:l0])+" quem "+" ".join(stks[l1:-1])+"?")

def time_ner(stks, loc, pre, pos):
    for l0, l1 in loc:
        if "," in stks:
            sign = [widx for widx, word in enumerate(stks) if "," in word]
            if len(sign) == 1:
                if sign[0] > l0:
                    print("Quando "+" ".join(stks[:l0]))
                if sign[0] > l1:
                    print("Quando "+" ".join(stks[l1:]))
            """else:
                if sign[0] > l0:
                    print("Quando "+" ".join(stks[:l0]))
                if sign[-1] > l1:
                    print("Quando "+" ".join(stks[:l0]))
                if sign[0] > l1:
                    print("Quando "+" ".join(stks[l1:]))
            """
        else:
            print("Quando "+" ".join(stks[:l0]))

#def abstraction_ner(stks, loc, pre, pos):
#    for l0, l1 in loc:
        
            
def verbal_locutions(verbs, words):
    verbal_connections = []
    for vid, v_ in enumerate(verbs):
        if vid != 0 and verbs[vid-1][0] == verbs[vid][0]-1:
            if type(verbal_connections[-1][0]) == tuple:
                verbal_connections[-1] = ( verbal_connections[-1][0]+(verbs[vid][0], ), verbal_connections[-1][1]+(verbs[vid][1], ) )
            else:
                verbal_connections[-1] = tuple(zip(verbal_connections[-1], verbs[vid]))
            continue
        verbal_connections.append(verbs[vid])
    return verbal_connections

def main():
    nlp = spacy.load("pt")
    for s, n in zip(SENTS, NER):
        pattern = "<EM(.+?)>(.+?)</EM>"
        rgx=re.compile(pattern)
        identifiers = re.compile('"(.+?)"')

        match = [ ((identifiers.findall(x[0]),x[1])) for x in rgx.findall(n)]

        if match == []:
            print("\n_________________\n")
            continue
        else:
            print(match)

            doc = nlp(s)
            words = [(w_.text , w_.tag_, w_.dep_) for w_ in doc]
            loc = []
            for typeof, name in match:
                pre = []
                pos = []
                for l0, l1 in loc:
                    for vidx, v_ in verbs:
                        if type(vidx) == int:
                            if vidx < l0:
                                pre.append((vidx, v_))
                            if vidx > l1:
                                pos.append((vidx, v_))
                verbs = []
                ntks = name.split()
                stks = [(w_.text) for w_ in doc]
                loc = [(i, i+len(ntks)) for i in range(len(stks)) if stks[i:i+len(ntks)] == ntks]
                verbs = [(wid, w_.text) for wid, w_ in enumerate(doc) if "|V|" in w_.tag_.upper()]
                verbs = verbal_locutions(verbs, words)
                if typeof[1].upper() == "PESSOA":
                    person_ner(stks, loc, pre, pos)
                if typeof[1].upper() == "TEMPO":
                    time_ner(stks, loc, pre, pos)
                if typeof[1].upper() == "ABSTRACCAO":
                    abstraction_ner(stks, loc, pre, pos)
                #if typeof[1].upper() == "TEMPO":
                  
                  
            print("\n_________________\n")
    #                 if pos == []:
    #                     print(pre, pos)
    #                     verb_ref = pre[-1]
    #                     if type(verb_ref[0]) == int:
    #                         print("quando "+ verb_ref[1]+" ".join(stks[:verb_ref[0]]))
    #                     else:
    #                         print("quando "+ " ".join(verb_ref[1])+" ".join(stks[:verb_ref[0][0]]))

if __name__ == '__main__':
    main()