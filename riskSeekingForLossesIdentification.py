#Error Identification
##TODO: return the customized msg if is risk_seeking_for_losses

import streamlit as st
from database_connector import alternatives


def isProbabilityHighAndLess100(x):
    if x>50 and x<100:
        return True
    else:
        return False

def isProbability100(x):
    if x==100:
        return True
    else:
        return False

def isNegativeValue(x):
    if x<0:
        return True
    else:
        return False

def isNegativeOrZeroValue(x):
    if x<=0:
        return True
    else:
        return False

def isAbsValuea2GreaterAbsValuea1(a2, a1):
    if abs(a1)<abs(a2):
        return True
    else:
        return False

def isEV1GreaterEV2(ev1, ev2):
    if ev1>=ev2:
        return True
    else:
        return False

def calculaEv(valor1, p1, valor2, p2):
    return valor1*p1/100+valor2*p2/100

def isRiskSeekingForLossesChoice(coproblem, codchoice):
    #Esse metodo recebe o coproblem e o codchoice da alternativa selecionada como decisao final
    #codchoice so pode ter os valores 1 ou 2

    #Pega os dados de codchoice 1:
    choice_1 = alternatives.get(
        alternatives.cod_choice == 0,
        alternatives.cod_problem == coproblem
    )
    #descalternative1 = choice_1.desc_alternative
    finantialvaluea1 = choice_1.financial_valuea
    probabilitya1 = choice_1.probabilitya

    finantialvalueb1 = choice_1.financial_valueb
    probabilityb1 = choice_1.probabilityb

    #Pega os dados de codchoice 2:
    #Pega os dados de codchoice 2:
    choice_2 = alternatives.get(
        alternatives.cod_choice == 1,
        alternatives.cod_problem == coproblem
    )
    #descalternative2 = choice_2.desc_alternative
    finantialvaluea2 = choice_2.financial_valuea
    probabilitya2 = choice_2.probabilitya

    finantialvalueb2 = choice_2.financial_valueb
    probabilityb2 = choice_2.probabilityb


    return codchoice==1 and isProbability100(probabilitya1) and isNegativeValue(finantialvaluea1) and isProbabilityHighAndLess100(probabilitya2) \
           and isNegativeValue(finantialvaluea2) and isNegativeOrZeroValue(finantialvalueb2) and \
           isAbsValuea2GreaterAbsValuea1(finantialvaluea2, finantialvaluea1) and \
           isEV1GreaterEV2(calculaEv(finantialvaluea1,probabilitya1, finantialvalueb1,probabilityb1), calculaEv(finantialvaluea2,probabilitya2, finantialvalueb2,probabilityb2))
