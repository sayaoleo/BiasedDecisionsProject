
#https://docs.peewee-orm.com/en/latest/peewee/query_examples.html
#https://docs.peewee-orm.com/en/latest/peewee/relationships.html
#import join as JOIN
from peewee import DatabaseProxy, Model, IntegerField, SQL, AutoField, CharField, CompositeKey, BooleanField, JOIN, DoubleField
#from peewee import JOIN
#JOIN['LEFT_OUTER'] = 'LEFT OUTER'
import streamlit as st

SCHEMA_NAME = st.secrets["postgres"]['schema_name']
database_proxy = DatabaseProxy()

class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database_proxy

class Users(BaseModel):
    username = CharField(max_length=255)
    cod_sexo = CharField(max_length=50)
    cod_age = CharField(max_length=50)
    password = CharField(max_length=255)
    email = CharField(max_length=255)
    class Meta:
        table_name = 'Users'
        schema = SCHEMA_NAME
        
class agent_decision(BaseModel):
    cod_agent = CharField()
    cod_choice = IntegerField()
    cod_problem = IntegerField()
    desc_decision = CharField(null=True, max_length=2000)
    financial_valuea = DoubleField() #V6.2
    financial_valueb = DoubleField() #V6.2
    probabilitya =  DoubleField() #V6.2
    probabilityb =  DoubleField(null=True) #V6.2
    payoff = IntegerField()
    forgone = IntegerField()
    rt = IntegerField()
    button = CharField()
    feedback = IntegerField()
    bias_detected = IntegerField()
    class Meta:
        table_name = 'agent_decision'
        schema = SCHEMA_NAME

class agent(BaseModel):
    anos_experiencia_prof = IntegerField()
    anos_experiencia_prof_com_poder_decisao = IntegerField(
        constraints=[SQL("DEFAULT 0")])
    cod_agent = AutoField()
    cod_cargo = IntegerField()
    cod_funcao = IntegerField()
    cod_sexo = IntegerField()
    cod_tem_poder_decisao = IntegerField()
    nota_conhecimento_decisao = IntegerField()

    cod_tomou_decisao_gokill = IntegerField()
    cod_cargo_outro =  CharField(null=True, max_length=1000)
    cod_funcao_outro = CharField(null=True, max_length=1000)
    cod_negocio_empresa = IntegerField()
    cod_negocio_empresa_outro = CharField(null=True, max_length=1000)
    cod_porte_empresa = IntegerField()

    class Meta:
        table_name = 'agent'
        schema = SCHEMA_NAME

class alternatives(BaseModel):
    cod_problem = IntegerField()
    desc_alternative = CharField(max_length=4000)
    #expected_value_calculated = IntegerField(null=True) #V6.2
    financial_valuea = IntegerField() #V6.2
    financial_valueb = IntegerField(null=True) #V6.2
    probabilitya =  IntegerField() #V6.2
    probabilityb =  IntegerField(null=True) #V6.2
    option = CharField(max_length=10)

    class Meta:
        schema = SCHEMA_NAME
        table_name = 'alternatives'
        indexes = (
            (('option', 'cod_problem'), True),
        )
        primary_key = CompositeKey('option', 'cod_problem')


class decision(BaseModel):
    cod_agent = IntegerField()
    cod_choice = IntegerField()
    cod_problem = IntegerField()
    desc_decison = CharField(null=True, max_length=2000)
    payoff = IntegerField()
    forgone = IntegerField()
    rt = IntegerField()
    button = CharField()
    feedback = IntegerField()

    class Meta:
        schema = SCHEMA_NAME
        table_name = 'decision'

class bias(BaseModel):
    cod_bias = AutoField()
    desc_bias = CharField(null=True, max_length=1000)


    class Meta:
        table_name = 'bias'
        schema = SCHEMA_NAME


class psychologicalvalueascription(BaseModel):
    cod_agent = IntegerField()
    cod_choice = IntegerField()
    cod_bias_calculated = IntegerField(null=True)
    cod_problem = IntegerField()
    cod_ref_calculated = IntegerField(null=True)
    cod_value = IntegerField(null=True)

    class Meta:
        schema = SCHEMA_NAME
        table_name = 'psychologicalvalueascription'
        indexes = (
            (('cod_agent', 'cod_problem', 'cod_choice'), True),
        )
        primary_key = CompositeKey('cod_agent', 'cod_choice', 'cod_problem')


class problem(BaseModel):
    cod_problem = AutoField()
    desc_problem = CharField(max_length=5000) #V6 renomear para desc_problem


    class Meta:
        table_name = 'problem'
        schema = SCHEMA_NAME


class ref(BaseModel):
    cod_ref = AutoField()
    desc_ref = CharField(max_length=1000)

    class Meta:
        table_name = 'ref'
        schema = SCHEMA_NAME


class valuebeholderhaspreferencevaluebearer(BaseModel):
    cod_agent = IntegerField()
    cod_choice = IntegerField()
    cod_problem = IntegerField()
    isriskseekingforlosses = BooleanField(null=True)
    ispreferredbearer = BooleanField(null=True)
    #system_rational_value = CharField(max_length=1000)  #V6.2 system_rational_value = "EV"

    class Meta:
        schema = SCHEMA_NAME
        table_name = 'valuebeholderhaspreferencevaluebearer'
        indexes = (
            (('cod_agent', 'cod_problem', 'cod_choice'), True),
        )
        primary_key = CompositeKey('cod_agent', 'cod_choice', 'cod_problem')

def create_tables():
    database_proxy.create_tables([
        agent_decision,
        agent,
        alternatives,
        decision,
        bias,
        psychologicalvalueascription,
        problem,
        ref,
        valuebeholderhaspreferencevaluebearer,
        Users
    ])

def do_insertions():
    print("Inserindo Problem - ", end="")
    #https://stackoverflow.com/questions/28041429/get-or-create-is-it-a-get-or-a-create
    #http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.get_or_create
    person, created = problem.get_or_create(
        cod_problem=1,
        defaults={
            'desc_problem': 'Considere que você trabalha numa empresa de pequeno porte (EPP) que tem R\$ 150 mil disponível para investimento. A empresa já investiu R\$ 200 mil num projeto para criar um novo produto no mercado. Na data prevista inicialmente para concluir o desenvolvimento do produto, a situação reportada é que o projeto está atrasado e que precisaria de mais R\$ 50 mil para concluir o produto. Você precisa fazer uma recomendação para o tomador de decisão escolhendo uma das duas alternativas abaixo. Não há outras alternativas. Qual alternativa você escolhe?'
        }
    )
    print("OK" if created else "Pré-existente")
    print("Inserindo Alternatives 1, 1 - ", end="")
    acreated = alternatives.get_or_create(
        cod_problem=1, cod_choice=1,
        defaults={
            "probabilitya": 100,
            "financial_valuea":-200000,
            "financial_valueb":0,
            "probabilityb":0,
            #"expected_value_calculated":-200000,
            "desc_alternative": 'Cancelar o projeto e perder os R\$ 200.000 já investidos'
        }
    )
    print("OK" if created else "Pré-existente")
    print("Inserindo Alternatives 1, 2 - ", end="")
    created = alternatives.get_or_create(
        cod_problem=1, cod_choice=2,
        defaults={
            "probabilitya": 90,
            "financial_valuea": -250000,
            "financial_valueb": 0,
            "probabilityb": 10,
            #"expected_value_calculated": -225000,
            "desc_alternative": 'Continuar com o projeto investindo mais R\$ 50.000, mesmo sabendo que tem 90% de chance de perder todo o investimento (R\$ 250.000) e 10% de chance de não perder nada'
        }
    )
    print("OK" if created else "Pré-existente")
    print("Inserindo Bias - ", end="")
    created = bias.get_or_create(
        cod_bias=1,
        defaults={
            #"desc_bias": 'Loss Aversion'
            "desc_bias": 'Uma perda certa é muito dolorosa (alternativa alternativa_perda).O decisor tem AVERSÃO À PERDA: uma perda dói mais do que o ganho equivalente dá prazer'
        }
    )
    print("OK" if created else "Pré-existente")
    print("Inserindo Ref - ", end="")
    created = ref.get_or_create(
        cod_ref=1,
        defaults={
            #"desc_ref": 'Your reference point is to lose nothing because it is a GAIN in relation to the alternative that has a sure loss'
            "desc_ref": 'O decisor busca evitar a perda certa na alternativa alternativa_perda e tem a esperança de não perder nada na alternativa alternativa_ganho.O seu PONTO DE REFERÊNCIA foi NÃO PERDER NADA, pois isso é um GANHO em relação à alternativa alternativa_perda'
        }
    )
    print("OK" if created else "Pré-existente")

def get_or_create_agent():
    if 'cod_agent' in st.session_state:
        created = agent.get_or_create(
            cod_agent=st.session_state['cod_agent'],
            defaults={
                "anos_experiencia_prof": 0,
                "cod_cargo": 0,
                "cod_funcao": 0,
                "cod_sexo": 0,
                "cod_tem_poder_decisao": 0,
                "nota_conhecimento_decisao": 0,
                "cod_tomou_decisao_gokill": 0,
                "cod_negocio_empresa": 0,
                "cod_porte_empresa": 0 #TODO: tinha virgula aqui. Qual o correto?
            }
        )
        if created:
            print(f"Novo agent - cod_agent: {agent.cod_agent}")
    else:
        agent.create(
            anos_experiencia_prof=0,
            cod_cargo=0,
            cod_funcao=0,
            cod_sexo=0,
            cod_tem_poder_decisao=0,
            nota_conhecimento_decisao=0,
            cod_tomou_decisao_gokill = 0,
            cod_negocio_empresa = 0,
            cod_porte_empresa = 0
        )
        st.session_state["cod_agent"] = agent.cod_agent
        print(f"Novo agent - cod_agent: {agent.cod_agent}")
    return agent

def show_problems_query():
    query = (
        problem.select(
            problem.cod_problem,
            problem.desc_problem #V6 renomear para desc_problem
        )
    )
    return query

def show_the_problem_query(id_problem):
    query = (
        problem.select(
            problem.cod_problem,
            problem.desc_problem #V6 renomear para desc_problem
        ).where(problem.cod_problem == id_problem)
    )
    return query

def show_all_problems_and_alternatives_query():
    query = (
        alternatives.select(
            alternatives.cod_problem,
            alternatives.cod_choice,
            alternatives.desc_alternative,
            alternatives.probabilitya,
            alternatives.financial_valuea,
            alternatives.probabilityb,
            alternatives.financial_valueb
            #, Alternatives.expected_value_calculated
        ).order_by(alternatives.cod_problem.desc(),alternatives.cod_choice )
    )
    return query

def show_all_alternatives_ofthe_problem_query(id_problem):
    query = (
        alternatives.select(
            alternatives.cod_problem,
            alternatives.cod_choice,
            alternatives.desc_alternative,
            alternatives.probabilitya,
            alternatives.financial_valuea,
            alternatives.probabilityb,
            alternatives.financial_valueb
            #, Alternatives.expected_value_calculated
        ).where(alternatives.cod_problem == id_problem)
    )
    return query

def show_decisions_query():
    query = (
        decision.select(
            decision.cod_agent,
            #Agent.nome,
            #Decision.desc_decison, #TODO
            decision.cod_problem,
            decision.cod_choice
        )
    )
    return query

def show_all_decisions_tobemade_query_for_agent(id_agent):
    #https://zetcode.com/python/peewee/
    #https://docs.peewee-orm.com/en/latest/peewee/relationships.html
    #https://docs.peewee-orm.com/en/latest/peewee/api.html
    #https://docs.peewee-orm.com/en/latest/peewee/query_examples.html
    query = (
        problem.select(
            problem.cod_problem,
            problem.desc_problem
            #, Decision.cod_agent,
            # Decision.desc_decision
            # ).where(Problem.cod_problem != Decision.cod_problem and Decision.cod_agent==id_agent)
            # ).where((Problem.cod_problem != Decision.cod_problem & Decision.cod_agent==id_agent))

        ).join(decision, JOIN.LEFT_OUTER, on=(problem.cod_problem == decision.cod_problem))
            #https://stackoverflow.com/questions/19259964/peewee-syntax-for-selecting-on-null-field
            #Not null: Peers.select().where(Peers.deleted.is_null(False))
            .where((decision.cod_agent.is_null()))
            .order_by(problem.cod_problem)

        # ).left_outer_join(Decision,on=(Problem.cod_problem == Decision.cod_problem))
        #     .where((Decision.cod_agent==id_agent) & (Decision.cod_agent== none ))
        #     #.order_by(Decision.cod_problem)

        #).join(Decision, JOIN.LEFT_OUTER)
    )
    return query

def show_all_decisions_made_query_for_agent(id_agent):
    #https://zetcode.com/python/peewee/
    #https://docs.peewee-orm.com/en/latest/peewee/relationships.html
    #https://docs.peewee-orm.com/en/latest/peewee/api.html
    query = (
        problem.select(
            problem.cod_problem,
            problem.desc_problem
        ).join(decision, on=(problem.cod_problem == decision.cod_problem))
            .where((decision.cod_agent==id_agent))
    )
    return query

def show_all_problems_and_decision_query():
    query = agent_decision.select()
    return query

