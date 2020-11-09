# Geração Automática de Questões para Português Brasileiro

A Geração de Questões (GQ) é dada pela extração factual e a conversão de sentenças em perguntas. Através do Reconhecimento de Entidades Nomeadas (NER) é realizada a identificação de estruturas semânticas do texto para coleta de informações em cada sentença. As estruturas encontradas são verificadas de acordo com a [extração de relações factuais](https://github.com/marcosspalenza/PTBR_RelationExtraction). Avançando da identificação das estruturas, o sistema avalia as estruturas factuais e as entidades nomeadas de acordo com as regras de conversão pré-estabelecidas. As regras variam de acordo com a classe da entidade, a gramática da sentença e o tipo de estrutura factual ao qual ela se enquadra.


## Requisitos
Os testes foram realizados com [Python 3.6](https://python.org) e os frameworks utilizados são apresentados abaixo:

- [SpaCy](https://spacy.io) v2.2.3



## Input
O documento de entrada é no formato _anotado_ por um _sistema NER_, assim como o exemplo abaixo:

>
>O novo continente ( __<EM ID=_Cap4-229_ CATEG=_LOCAL_>América</EM>__ ) continha características étnicas , lingüísticas e culturais tão variadas quanto as dos povos que habitavam a __<EM ID=_Cap4-230_ CATEG=_LOCAL_>Europa</EM>__ naquele período .
>

## Reconhecimento
O processo de extração inicia com a verificação gramatical, identificando substantivos da sentença, __NOUN__ e __PROPN__. Simultâneamente, a coleta dos verbos da frase, identificados como __VERB__, indicam a posição dos substantivos na estrutura factual.

### Análise de Dependência
Com os termos coletados, a análise de dependência inicia a identificação factual com relação aos sintágmas nominais, relacionando as principais entidades com os demais elementos da frase em _nsubj_ e _nsubj:pass_. Essa formulação visa a criação de triplas. As triplas são a identificação das componentes factuais e a relação entre elas. Assim, as triplas são compostas por dois segmentos e uma relação. Portanto, os segmentos __COMP1__ e __COMP2__ são conectados por uma relação __REL__, formando a tripla COMP1 - REL - COMP2. 

Basicamente, temos no primeiro momento uma tripla formada pela conexão verbal da frase com os substantivos através do reconhecimento de uma relação simples. Há a necessidade de refinar as componentes e as relações para estruturas de dependência coerentes. No momento, as estruturas adjacentes aceitas como parte da componente principal são _flat:name_, _case_, _nmod_, _obj_, _appos_, _amod_, _advmod_, _acl:relcl_, _obl_, _conj_ e _xcomp_. Os limites da componente são estabelecidos pela recorrência destes modelos de dependência no entorno do núcleo do sintágma nominal. Os limites das componentes não transpõe as pontuações da frase (_punct_).

### NER
O NER é associado então para identificar se o mesmo se enquadra nas triplas formadas ou é um componente adicional. A aplicação das regras sobrepõe as duas estruturas, entidades nomeadas e triplas relacionais, para identificação dos núcleos de informação e a formação de questões. A formação de questões então é realizada através de regras de manipulação destas componentes na frase.

As regras são formulas posicionais das componentes. O código abaixo é um exemplo de uma regra simples de transformação:
 
	if model == "PESSOA"
		if name in a1:
			question = a1.replace(name, " quem ")+" "+rel+" "+a2+"?"

O tipo de questão é para uma entidade _PESSOA_. O nome está na componente 1 da tripla (_A1, REL, A2_) e a formação da questão é realizada diretamente substituindo a entidade nomeada __PESSOA__ por __"Quem"__ em _A1_.

## Referências
PIROVANI, Juliana; SPALENZA, Marcos; OLIVEIRA, Elias. Geração Automática de Questões a partir do Reconhecimento de Entidades Nomeadas em Textos Didáticos. __Simpósio Brasileiro de Informática na Educação - SBIE__. p. 1147. 2017. [PDF](https://br-ie.org/pub/index.php/sbie/article/view/7643)