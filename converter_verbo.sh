#!/bin/bash

function verbo3P(){
	verbo=$1
	lemma=`grep -m1 "^$verbo,.*\.V" DicPalavrasSimples.txt | cut -d"." -f1 | cut -d"," -f2`
	v3P=`grep ".*,$lemma.V:J3s" DicPalavrasSimples.txt | cut -d"," -f1`
	echo $v3P
}

verbo=$(verbo3P $1)
echo $verbo