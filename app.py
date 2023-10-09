#6.12:
# entrada de dados - new UID e Experimento (validaca entrada dados, alteracao pergunta)
# 2) If there is an alternative with 100% chance, it should be the first alternative to be input into the system.
# 3) If there are more than on alternative with 100% chance, the order does not matter since item 2 is satisfied.
# 4) If there is an alternative composed by 2 statements joined with "AND" (conjunction) and each statement has its
# financial value with its respective probability then the statement with the greatest probability should be input the first into the system.
# Example of an alternative like that: 95% chance of losing US$10000 AND 5% chance of losing US$100.

import streamlit as st
import pandas as pd
from PIL import Image
from riskSeekingForLossesIdentification import isRiskSeekingForLossesChoice
from peewee import PostgresqlDatabase
from database_connector import decision, create_tables, valuebeholderhaspreferencevaluebearer, psychologicalvalueascription, database_proxy, do_insertions, problem, alternatives, ref, bias, show_all_decisions_tobemade_query_for_agent, show_all_problems_and_alternatives_query, show_decisions_query, Users, show_all_problems_and_decision_query, agent_decision
from time import time
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

#layout
st.set_page_config(layout="wide")

#For the System:
COD_VALUE_LOSS = 1
COD_VALUE_GAIN = 2
COD_AGENT1 = 1
COD_REF_RISK_SEEKING = 1 #TODO: Replace with value in record
COD_BIAS_RISK_SEEKING = 1 #TODO: Replace with value in record

#
COD_PROBLEM_1 = 1
MIN_ANSWER_SIZE = 1

def create_user(username, cod_sexo, cod_age, email, password):
    # Verifique se o usuário já existe
    existing_user = Users.get_or_none(Users.username == username)
    if existing_user:
        st.error("Nome de usuário já existe.")
        return
    
    # Crie um novo usuário
    Users.create(
        username=username,
        cod_sexo=cod_sexo,
        cod_age=cod_age,
        email=email,
        password=password,
        # Outros campos do usuário aqui
    )
    
    st.success("Usuário cadastrado com sucesso!")

def register():
    st.title("Cadastro de Usuário")
    username = st.text_input("Nome de Usuário")
    cod_sexo = st.selectbox('Sexo', ['M', 'F'])
    cod_age = st.number_input("Idade", min_value=1, step=1)
    email = st.text_input("E-mail")
    password = st.text_input("Senha", type="password")
    if st.button("Cadastrar"):
        create_user(username, cod_sexo, cod_age, email, password)


# Página de login
def login():
    st.title("Login")
    username = st.text_input("Nome de Usuário")
    password = st.text_input("Senha", type="password")
    if st.button("Salvar"):
        # Verifique se as credenciais estão corretas no banco de dados
        user = Users.get_or_none(Users.username == username)
        if user and user.password == password:
            st.success("Login bem-sucedido!")
        else:
            st.error("Credenciais inválidas.")

def analisar():
    # Obtém todas as linhas da tabela agent_decision
    decisions = agent_decision.select()

    # Itera pelas linhas e aplica a função isRiskSeekingForLossesChoice
    for decision in decisions:
        coproblem = decision.cod_problem
        codchoice = decision.cod_choice

        # Aplica a função isRiskSeekingForLossesChoice
        is_risk_seeking = isRiskSeekingForLossesChoice(coproblem, codchoice)

        # Preenche a coluna bias_detected com 1 se for True, senão 0
        decision.bias_detected = 1 if is_risk_seeking else 0

        # Salva a alteração no banco de dados
        decision.save()


from PIL import Image, ImageFont, ImageDraw
import textwrap

def findWord(line, word):
    pos = line.find(word)
    return pos

def replace_word(line, old_word, new_word):
    # for line in f:
    cont = 0
    pos = findWord(line, old_word)
    while pos >= 0:
        cont = cont + 1
        line = line[:pos] + new_word + line[pos + len(old_word):]
        pos = findWord(line, old_word)
    return line

def draw_multiple_line_text(image, text, font, text_color, text_start_left, text_start_height, width_box):
    '''
    From unutbu on [python PIL draw multiline text on image](https://stackoverflow.com/a/7698300/395857)
    '''
    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size
    y_text = text_start_height
    lines = textwrap.wrap(text, width=width_box)
    for line in lines:
        line_width, line_height = font.getsize(line)
        draw.text((text_start_left, y_text), line, font=font, fill=text_color)
        y_text += line_height

def personaliza_image(int_cod_agent, int_cod_problem, finantialvaluea1, probabilitya1,finantialvalueb1, probabilityb1, finantialvaluea2,probabilitya2,finantialvalueb2, probabilityb2, alternativa_ganho, alternativa_perda, desc_bias, desc_ref):
    str_cod_agent = str(int_cod_agent)
    str_cod_problem = str(int_cod_problem)

    #Escreve na imagem de forma personalizada ao problema em questão e retorna o nome da nova imagem
    #TODO: Receber como parametro: texto de Bias e Ref e fazer o Replace de alternativa_ganho e alternativa_perda
    #TODO: Receber como parametro: alternativa_ganho e alternativa_perda
    #alternativa_ganho = "B"
    #alternativa_perda = "A"
    #, alternativa_ganho, alternativa_perda, desc_bias, desc_ref
    #text_loss_aversion_bias = "Uma perda certa é muito dolorosa (alternativa alternativa_perda).O decisor tem AVERSÃO À PERDA: uma perda dói mais do que o ganho equivalente dá prazer"
    text_loss_aversion_bias = desc_bias
    #text_reference_point = "O decisor busca evitar a perda certa na alternativa alternativa_perda e tem a esperança de não perder nada na alternativa alternativa_ganho.O seu PONTO DE REFERÊNCIA foi 'NÃO PERDER NADA', pois isso é um GANHO em relação à alternativa alternativa_perda"
    text_reference_point = desc_ref

    #print("text_loss_aversion_bias Antes: "+ text_loss_aversion_bias)
    text_loss_aversion_bias = replace_word(text_loss_aversion_bias, "alternativa_perda", alternativa_perda)
    text_loss_aversion_bias = replace_word(text_loss_aversion_bias, "alternativa_ganho", alternativa_ganho)
    #print("text_loss_aversion_bias Depois: "+ text_loss_aversion_bias)

    #print("text_reference_point Antes: "+ text_reference_point)
    text_reference_point = replace_word(text_reference_point, "alternativa_perda", alternativa_perda)
    text_reference_point = replace_word(text_reference_point, "alternativa_ganho", alternativa_ganho)
    #print("text_loss_aversion_bias Depois: "+ text_reference_point)

    list_text1 = text_loss_aversion_bias.split(".")
    text1 = list_text1[0]
    text1b = list_text1[1]

    list_text2 = text_reference_point.split(".")
    text2 = list_text2[0]
    text2b = list_text2[1]


    my_image = Image.open("risk_seeking_for_high_prob_of_loss.png")
    # Call draw Method to add 2D graphics in an image
    imgDraw = ImageDraw.Draw(my_image)


    #Titulo
    font = ImageFont.truetype("arial.ttf", 40, encoding="unic")
    imgDraw.text((1705, 64), alternativa_ganho, fill=(0, 0, 0), font=font) #preto

    #Left
    font = ImageFont.truetype("arial.ttf", 36, encoding="unic")
    imgDraw.text((375, 165), alternativa_perda, fill=(0, 0, 0), font=font) #preto

    font = ImageFont.truetype("arial.ttf", 32, encoding="unic")
    imgDraw.text((120, 230), "Alta perda com certeza", fill=(0, 0, 0), font=font) #preto
    font = ImageFont.truetype("arial.ttf", 28, encoding="unic")
    imgDraw.text((150, 280), "100% de chance de perder", fill=(0, 0, 0), font=font) #preto
    #imgDraw.text((210, 320), "R$ 200.000", fill=(0, 0, 0), font=font) #preto
    #imgDraw.text((210, 320), "R$ "+ str(abs(finantialvaluea1)), fill=(0, 0, 0), font=font) #preto
    imgDraw.text((210, 320), "R$ "+ formato_financeiro_brasileiro(abs(finantialvaluea1)), fill=(0, 0, 0), font=font) #preto



    #Right
    font = ImageFont.truetype("arial.ttf", 36, encoding="unic")
    imgDraw.text((1590, 166), alternativa_ganho, fill=(0, 0, 0), font=font) #preto

    font = ImageFont.truetype("arial.ttf", 32, encoding="unic")
    imgDraw.text((1230, 230), "Alta probabilidade de perda maior", fill=(0, 0, 0), font=font) #preto
    font = ImageFont.truetype("arial.ttf", 28, encoding="unic")

    #imgDraw.text((1280, 280), "90% de chance de perder", fill=(0, 0, 0), font=font) #preto
    imgDraw.text((1280, 280), str(probabilitya2) +"% de chance de perder", fill=(0, 0, 0), font=font) #preto
    #imgDraw.text((1340, 320), "R$ 250 mil e", fill=(0, 0, 0), font=font) #preto
    #imgDraw.text((1340, 320), "R$ "+ str(abs(finantialvaluea2)) + " e", fill=(0, 0, 0), font=font) #preto
    imgDraw.text((1340, 320), "R$ "+ formato_financeiro_brasileiro(abs(finantialvaluea2)) + " e", fill=(0, 0, 0), font=font) #preto

    #imgDraw.text((1280, 370), "10% de não perder nada", fill=(0, 0, 0), font=font) #preto
    # TODO: finantialvalueb2
    imgDraw.text((1280, 370), str(probabilityb2) +"% de não perder nada", fill=(0, 0, 0), font=font) #preto

    font = ImageFont.truetype("arial.ttf", 36, encoding="unic")
    #text1 = "Uma perda certa é muito dolorosa (alternativa A)"
    text_color = (0, 0, 255) #azul
    text_start_height = 550
    text_start_left = 60
    caixa_largura = 30
    draw_multiple_line_text(my_image, text1, font, text_color, text_start_left, text_start_height, caixa_largura)

    #text1b = "O decisor tem AVERSÃO À PERDA: uma perda dói mais do que o ganho equivalente dá prazer"
    text_color = (0, 0, 255) #azul
    text_start_height = 650
    text_start_left = 60
    caixa_largura = 26
    draw_multiple_line_text(my_image, text1b, font, text_color, text_start_left, text_start_height, caixa_largura)

    #text2 = "O decisor busca evitar a perda certa na alternativa A e tem a esperança de não perder nada na alternativa B"
    text_start_height = 550
    text_start_left = 620
    text_color = (0, 0, 0) #preto
    caixa_largura = 36
    draw_multiple_line_text(my_image, text2, font, text_color, text_start_left, text_start_height, caixa_largura)

    #text2b = "O seu PONTO DE REFERÊNCIA foi 'NÃO PERDER NADA', pois isso é um GANHO em relação à alternativa A"
    text_start_height = 850
    text_start_left = 620
    text_color = (0, 0, 255) #azul
    caixa_largura = 30
    draw_multiple_line_text(my_image, text2b, font, text_color, text_start_left, text_start_height, caixa_largura)

    #text3="O decisor dá um peso menor na probabilidade alta de perder ainda mais na alternativa B"
    imgDraw.text((1577, 615), alternativa_ganho, fill=(0, 0, 0), font=font) #preto

    # #if st.session_state['cod_agent'] is None:
    # if st.session_state.get('cod_agent') is None:
    #     nome_imagem = 'alerta_personalizado_'+str(COD_AGENT1)+'.png'
    # else:
    #     nome_imagem = 'alerta_personalizado_'+str(st.session_state["cod_agent"])+'.png'
    # #nome_imagem = 'alerta_personalizado_1.png'

    nome_imagem = 'alerta_personalizado_'+str_cod_agent+'_'+ str_cod_problem +'.png'

    my_image.save(nome_imagem)
    # Display edited image
    #my_image.show()
    return nome_imagem

def formato_financeiro_brasileiro(valor):
    valor_formatado = "{:,.0f}".format(valor).replace(",", ".")
    return str(valor_formatado)


def complementa_proposicao(finantialvaluea1, contexto):
    texto = ""
    if finantialvaluea1<0:

        #texto = " de perder R\$"+str(abs(finantialvaluea1))
        texto = " de perder R\$ "+formato_financeiro_brasileiro(abs(finantialvaluea1))
        ##texto = " de perder R$"+str(locale.currency(abs(finantialvaluea1), grouping=True))


    elif finantialvaluea1>0:
        #texto = " de ganhar R\$"+str(abs(finantialvaluea1))
        texto = " de ganhar R\$ "+formato_financeiro_brasileiro(abs(finantialvaluea1))
        ##texto = " de ganhar R$"+str(locale.currency(abs(finantialvaluea1), grouping=True))

    else: #valor financeiro é zero
        if contexto=="ganho":
            texto = " de não ganhar nada"
        elif contexto=="perda":
            texto = " de não perder nada"
        else:
            texto = " de não perder nada"

    return texto

def reescreve_proposicao(finantialvaluea1, probabilitya1, finantialvalueb1,probabilityb1):

    if (finantialvaluea1<0 or finantialvaluea1==0) and (finantialvalueb1<0 or finantialvalueb1==0):
        contexto="perda" #ganho ou nada
    elif (finantialvaluea1>0 or finantialvaluea1==0) and (finantialvalueb1>0 or finantialvalueb1==0):
        contexto="ganho" #ou nada
    else:
        contexto="tantofaz" #ou nada

    texto =""
    texto+=str(probabilitya1)+"% de chance"
    texto+= complementa_proposicao(finantialvaluea1, contexto)

    if(probabilityb1>0):
        texto +=" E "
        texto+=str(probabilityb1)+"% de chance"
        texto+= complementa_proposicao(finantialvalueb1, contexto)

    return texto

def decodeValueGain(x):
    if x == 1:
        x = 'LOSS'
    else:
        x = 'GAIN'
    return x

def check_biases_cod_choice_main_decision(cod_problem, cod_agent, cod_choice, desc_decison ):

    is_riskseekingforlosses = isRiskSeekingForLossesChoice(cod_problem, cod_choice)

    msg_retorno = ""

    # Realiza o instert de Value ValueBeholderHasPreferenceValueBearer para Alternative 1
    valuebeholderhaspreferencevaluebearer.create(
        cod_agent=cod_agent,
        cod_problem=cod_problem,
        cod_choice=0,
        ispreferredbearer = cod_choice == 0,
        isriskseekingforlosses=is_riskseekingforlosses
    )
    # Realiza o instert de Value ValueBeholderHasPreferenceValueBearer para Alternative 2
    valuebeholderhaspreferencevaluebearer.create(
        cod_problem=cod_problem,
        cod_choice=1,
        ispreferredbearer = cod_choice == 1,
        isriskseekingforlosses=is_riskseekingforlosses
    )

    # Se o método isRiskSeekingForLossesChoice retornou True realiza o insert de PsychologicalValueAscription
    if is_riskseekingforlosses:
        psychologicalvalueascription.create(
            cod_agent=cod_agent,
            cod_problem=cod_problem,
            cod_choice=1,
            cod_value=COD_VALUE_LOSS, # 1 LOSS
            cod_bias_calculated=1, # Loss Aversion
            cod_ref_calculated=1 # Hope of losing nothing
        )
        psychologicalvalueascription.create(
            cod_agent=cod_agent,
            cod_problem=cod_problem,
            cod_choice=2,
            cod_value=COD_VALUE_GAIN, # 2 GAIN
            cod_bias_calculated=1, # Loss Aversion
            cod_ref_calculated=1 # Hope of losing nothing
        )

        msg_retorno = "The system identified you may be Risk Seeking for Losses. Your decision may be critical, in this context that involves high financial losses, if you are not aware how you may be influenced to seek risk."

    # Realiza o insert de Decision
    decision.create(
        cod_agent=cod_agent,
        cod_problem=cod_problem,
        cod_choice=cod_choice,
        desc_decison=desc_decison
    )
    return msg_retorno

#https://docs.streamlit.io/library/api-reference/performance/st.experimental_singleton
@st.cache_resource
def init_connection():
    print("Inicializando conexão com o banco - ", end="")
    database = PostgresqlDatabase(
        st.secrets["postgres"]["dbname"],
        user=st.secrets["postgres"]["user"],
        host=st.secrets["postgres"]["host"],
        password=st.secrets["postgres"]["password"],
        port=st.secrets["postgres"]["port"],
    )
    
    database_proxy.initialize(database)
    print("OK")
    print("Criando tabelas - ", end="")
    create_tables()
    print("OK")
    do_insertions()

init_connection()


#if ('prototipo' in st.experimental_get_query_params()) or ('id_problem' in st.experimental_get_query_params() or  ('sis_sessao_page_risco' in st.session_state) ) :
#http://177.71.194.138/?prototipo=2222
# #Multiapp
# #https://discuss.streamlit.io/t/page-redirect/19263/4
#https://github.com/mrtrycatch/streamlitCrud/blob/main/main.py


Page_cadastro = st.sidebar.selectbox(
    'Ferramenta ABI (Doutorado de Eduardo Ramos)', ['Perfil', 'Cadastro de Problemas', 'Detecção Geral', 'Lista de Decisões a Tomar', 'Decisões Tomadas', 'Lista de todos os Problemas'], 0)

if 'sis_sessao_page_risco' in st.session_state:
    #Exibe o alerta de risco no sistema
    #Entao  sis_sessao_page_risco == 'Exibe Alerta Risco na Decisao'

    #st.experimental_set_query_params(prototipo="2222")

    #Pega valores da sessão:
    if 'sis_cod_problem' in st.session_state:
        sis_cod_problem = st.session_state['sis_cod_problem']

    if 'sis_cod_agent' in st.session_state:
        sis_cod_agent = st.session_state['sis_cod_agent']

    if 'sis_cod_main_decision' in st.session_state:
        sis_cod_main_decision = st.session_state['sis_cod_main_decision']

        #Remove da sessao:
    st.session_state.pop('sis_sessao_page_risco')
    st.session_state.pop('sis_cod_problem')
    st.session_state.pop('sis_cod_agent')
    st.session_state.pop('sis_cod_main_decision')

    #Ed 1: Inicio
    #Mostra a imagem personalizada de alerta
    #Mostra o problema e pede para tomar a Decisao:

    #idProblema = COD_PROBLEM_1
    idProblema = sis_cod_problem

    st.subheader("Módulo de Decisão: ALERTA")

    #st.title("Decidir")

    #st.title("ALERTA na Tomada de Decisão")
    #TODO: colocar msg de alerta

    #Pega os dados de problema:
    problem = problem.get(
        problem.cod_problem == idProblema
    )
    desc_problema = problem.desc_problem

    #Pega os dados de codchoice 1:
    choice_1 = alternatives.get(
        alternatives.cod_choice == 1,
        alternatives.cod_problem == idProblema
    )
    descalternative1 = choice_1.desc_alternative
    finantialvaluea1 = choice_1.financial_valuea
    probabilitya1 = choice_1.probabilitya

    finantialvalueb1 = choice_1.financial_valueb
    probabilityb1 = choice_1.probabilityb

    #Pega os dados de codchoice 2:
    choice_2 = alternatives.get(
        alternatives.cod_choice == 2,
        alternatives.cod_problem == idProblema
    )
    descalternative2 = choice_2.desc_alternative
    finantialvaluea2 = choice_2.financial_valuea
    probabilitya2 = choice_2.probabilitya

    finantialvalueb2 = choice_2.financial_valueb
    probabilityb2 = choice_2.probabilityb

    #Pega os dados de desc_bias:
    bias = bias.get(bias.cod_bias == COD_BIAS_RISK_SEEKING)
    desc_bias = bias.desc_bias

    #Pega os dados de desc_ref:
    ref = ref.get(ref.cod_ref == COD_REF_RISK_SEEKING)
    desc_ref = ref.desc_ref

    input_button_submit = False

    with st.form(key="consulta_decision_final"):

        # Mostra o Alerta
        #Mostra Imagem de alerta 1: Início
        # Verifica se tem Risk Seeking
        is_riskseekingforlosses = isRiskSeekingForLossesChoice(idProblema, sis_cod_main_decision)

        if is_riskseekingforlosses:
            #Houve Risk Seeking e ja salvou no BD
            #Pega os dados de alternativa_ganho e alternativa_perda:
            temp_cod_agent = 0
            #if st.session_state.get('cod_agent') is not None:
            if sis_cod_agent>0:
                #temp_cod_agent = st.session_state["cod_agent"]
                temp_cod_agent = sis_cod_agent

            if(temp_cod_agent != 0):
                #Alternativa 1:
                psychologicalValueAscription = psychologicalvalueascription.get(psychologicalvalueascription.cod_agent == temp_cod_agent,
                                                                                psychologicalvalueascription.cod_choice == 1,
                                                                                psychologicalvalueascription.cod_problem == idProblema)

            alternativa_ganho = 0
            alternativa_perda = 0
            if psychologicalValueAscription.cod_value == COD_VALUE_GAIN:
                alternativa_ganho = 1 #Alternativa 1 é GANHO
                alternativa_perda = 2 #Alternativa 2 é PERDA
            else:
                alternativa_ganho = 2 #Alternativa 2 é GANHO
                alternativa_perda = 1 #Alternativa 1 é PERDA

            #st.warning(msg)
            st.image("alertagrande_ler_com_atencao_risk_seeking_for_high_prob_of_loss.png")

        #Mostra Imagem de alerta 1: Fim

        ##### Decisao TOMADA: #####
        st.subheader("**Esse alerta refere-se à escolha da alternativa "+str(sis_cod_main_decision)+" no problema abaixo:**")

        input_desc_decison = ""
        input_cod_problem = idProblema
        st.write(desc_problema)

        input_desc_decison = ""

        col1, col2 = st.columns(2)
        #original = Image.open(image)
        col1.header("Alternativa 1")
        col1.write("1) "+descalternative1)
        col1.write("Ou seja: "+reescreve_proposicao(finantialvaluea1, probabilitya1, finantialvalueb1,probabilityb1))

        col2.header("**Alternativa 2**")
        col2.write("2) "+descalternative2)
        col2.write("Ou seja: "+reescreve_proposicao(finantialvaluea2, probabilitya2, finantialvalueb2,probabilityb2))

        if is_riskseekingforlosses:
            image_personalizada = Image.open(personaliza_image(temp_cod_agent, idProblema, finantialvaluea1, probabilitya1,finantialvalueb1, probabilityb1, finantialvaluea2,probabilitya2,finantialvalueb2, probabilityb2, str(alternativa_ganho), str(alternativa_perda), desc_bias, desc_ref))
            st.image(image_personalizada)

        input_button_submit = st.form_submit_button("Próximo")

    if input_button_submit:
        #TODO: se está aqui é porque teve vies Risk Seeking for Losses

        #TODO: Atualizar para nova imagem personalizada
        #image = Image.open("buscar_risco.png")
        #st.image(image)
        #st.success("Decision saved with success!")

        #st.experimental_set_query_params(prototipo="2222")

        # Atualiza a página
        st.experimental_rerun()

#Ed 1: Fim

elif Page_cadastro == 'Lista de Decisões a Tomar' or ('id_problem' in st.experimental_get_query_params()):

    query = show_all_decisions_tobemade_query_for_agent(COD_AGENT1)
    #print(query.namedtuples)
    df = pd.DataFrame(query.namedtuples())
    #df
    #https://github.com/mrtrycatch/streamlitCrud/blob/6f4f162585685355a7191302d9b3e278454e039f/Pages/Cliente/List.py
    params = st.experimental_get_query_params()
    #EDuardo
    st.write(params)
    #st.write(st.get_url())
    #import get_report_ctx
    #from streamlit.report_thread import get_report_ctx
    #from streamlit.server.server import Server

    # Get the current report context
    #ctx = st.report_thread.get_report_ctx()

    # # Get the session ID and widget ID
    # session_id = ctx.session_id
    # widget_id = ctx.widget_id
    #
    # # Get the current URL
    # session_id = get_report_ctx().session_id
    # server = Server.get_current()
    # url = server.get_session_info(session_id).session_request.url

    #import get_report_ctx
    # from streamlit.report_thread import get_report_ctx
    # from streamlit.server.server import Server
    #
    # # Get the current report context
    # ctx = st.report_thread.get_report_ctx()
    #
    # # Get the session ID
    # session_id = ctx.session_id
    #
    # # Get the session info and retrieve the URL
    # server = st.server.server.Server.get_current()
    # session_info = server.get_session_info(session_id)
    # url = session_info.session.request.headers.get("referer", "/")




    # # Get the session ID and widget ID
    # session_id = st.report_thread.get_report_ctx().session_id
    # widget_id = st.report_thread.get_report_ctx().widget_id
    #
    # # Get the session info and retrieve the URL
    # session_info = st.session_state.session_info
    # url = session_info.session.request.headers.get("referer", "/")


    # from streamlit.report_thread import get_report_ctx
    #
    # # Get the current report context
    # ctx = get_report_ctx()
    #
    # # Get the session ID
    # session_id = ctx.session_id
    #
    # # Get the session info and retrieve the URL
    # from streamlit.server.server import Server
    # server = Server.get_current()
    # session_info = server.get_session_info(session_id)
    # url = session_info.session.request.headers.get("referer", "/")

    ## Print the URL
    #print(url)
    if params.get("id_problem") == None:
        st.subheader("Módulo de Decisão: Lista de decisões a tomar")
        colms = st.columns((1, 9, 2))
        campos = ['Nº', 'Problema', 'Ação']
        for col, campo_nome in zip(colms, campos):
        #for x, item in enumerate(ClienteController.SelecionarTodos()):
        #for x, item in enumerate(show_all_decisions_tobemade_query(1)):
        #for x, item in enumerate(df):
        #for item in df.iterrows():
        #See https://towardsdatascience.com/efficiently-iterating-over-rows-in-a-pandas-dataframe-7dd5f9992c01
            for item in df.itertuples():
                #st.write(item) #TODO: Retirar isso
                col1, col2, col3 = st.columns((1, 9, 2))
                col1.write(item.cod_problem)
                col2.write(item.desc_problem)
                #button_space_excluir = col5.empty()
                #on_click_excluir = button_space_excluir.button(
                #    'Excluir', 'btnExcluir' + str(item.id))
                button_space_decidir = col3.empty()
                st.success(item.cod_problem)
                on_click_decidir = button_space_decidir.button(
                    'Decidir', 'btnDecidir' + str(item.cod_problem))
        
                # if on_click_excluir:
                #     ClienteController.Excluir(item.id)
                #     button_space_excluir.button(
                #         'Excluído', 'btnExcluir' + str(item.id))
                #     st.experimental_rerun()
                if on_click_decidir:
                    st.success("Sucesso")
                    st.experimental_set_query_params(id_problem=[item.cod_problem])
                    st.experimental_rerun()

    else:
        #Consulta o problema
        #Mostra o problema e pede para tomar a Decisao:

#teste
        #idProblema = st.experimental_get_query_params()
        idProblema = params
        #Eduardo
        #st.write(idProblema)
        #st.experimental_set_query_params() #Limpa o parametro idProblema
        #Limpa o parametro idProblema
        #query_params = st.experimental_get_query_params()
        #EDUARDO:
        #if 'id_problem' in query_params:
        #    query_params.pop('id_problem')
        #st.experimental_set_query_params() #Limpa o parametro idProblema

        if params.get("id_problem") != None:
            idProblema = int(params.get("id_problem")[0]) # Print and Check if it is ok
            #Eduardo
            st.write(idProblema)

            st.subheader("Módulo de Decisão")
            #TODO: Pega os dados de coproblem e de suas alternativas

            #Pega os dados de problema:
            problem = problem.get(
                problem.cod_problem == idProblema
            )
            desc_problema = problem.desc_problem

            #Pega os dados de codchoice 1:
            choice_1 = alternatives.get(
                alternatives.cod_choice == 1,
                alternatives.cod_problem == idProblema
            )
            descalternative1 = choice_1.desc_alternative
            finantialvaluea1 = choice_1.financial_valuea
            probabilitya1 = choice_1.probabilitya

            finantialvalueb1 = choice_1.financial_valueb
            probabilityb1 = choice_1.probabilityb

            #Pega os dados de codchoice 2:
            choice_2 = alternatives.get(
                alternatives.cod_choice == 2,
                alternatives.cod_problem == idProblema
            )
            descalternative2 = choice_2.desc_alternative
            finantialvaluea2 = choice_2.financial_valuea
            probabilitya2 = choice_2.probabilitya

            finantialvalueb2 = choice_2.financial_valueb
            probabilityb2 = choice_2.probabilityb

            #Pega os dados de desc_bias:
            bias = bias.get(bias.cod_bias == COD_BIAS_RISK_SEEKING)
            desc_bias = bias.desc_bias

            #Pega os dados de desc_ref:
            ref = ref.get(ref.cod_ref == COD_REF_RISK_SEEKING)
            desc_ref = ref.desc_ref

            input_button_submit = False

            with st.form(key="include_decision_final"):
                #with st.empty(style={"background-color": "#E6E6E6"}):

                #Start 1
                #st.form(style={"background-color": "#E6E6E6"})

                #Decisao a ser tomada
                # input_cod_problem = st.number_input(label="Problem code", value=idProblema, disabled=True)
                # input_desc_problem = st.text_input(label="Description of the decision-making problem", value=desc_problema, disabled=True)
                # input_cod_agent = COD_AGENT1
                # input_cod_choice = st.number_input(label="Which alternative code is your Decision?", format="%d", step=1)
                # #input_desc_decison = st.text_input(label="Describe the decision")
                input_desc_decison = ""

                #st.write("Código do problema: "+str(idProblema))
                ##input_cod_problem = st.number_input(label="Problem code", value=idProblema, disabled=True)
                input_cod_problem = idProblema
                ##input_desc_problem = st.text_input(label="Description of the decision-making problem", value=desc_problema, disabled=True)
                st.write(desc_problema)

                #st.write("("+str(idProblema)+") "+desc_problema)

                input_cod_agent = COD_AGENT1

                col1, col2 = st.columns(2)
                #original = Image.open(image)
                col1.header("Alternativa 1")
                col1.write("1) "+descalternative1)
                col1.write("Ou seja: "+reescreve_proposicao(finantialvaluea1, probabilitya1, finantialvalueb1,probabilityb1))

                col2.header("Alternativa 2")
                col2.write("2) "+descalternative2)
                col2.write("Ou seja: "+reescreve_proposicao(finantialvaluea2, probabilitya2, finantialvalueb2,probabilityb2))

                #input_cod_choice = st.number_input(label="Which alternative code is your Decision?", format="%d", step=1)
                input_cod_choice = st.number_input(label="Tome uma decisão e digite abaixo o código da alternativa (1 ou 2) que você escolheu. Em seguida, clique no botão Salvar:", format="%d", step=1)
                #col11, col12 = st.columns((2, 8))
                #input_cod_choice = col11.number_input(label="Tome uma decisão e digite abaixo o código da alternativa (1 ou 2) que você escolheu. Em seguida, clique no botão <Salvar>:", format="%d", step=1)
                input_desc_decison = ""


                input_button_submit = st.form_submit_button("Salvar")

            if input_button_submit:
                #st.experimental_get_query_params() #Limpa o parametro idProblema

                msg = ""

                #Eduardo
                #st.write(input_cod_choice)
                #st.write(resposta = input_cod_choice)

                #Valida Inicio
                try:
                    resposta = input_cod_choice # int(resposta)
                except:
                    resposta = None

                #Eduardo
                st.write(resposta)
                if resposta is None:
                    st.error("Insira um número válido.")
                else:
                    if resposta > 2 or resposta < 1:
                        st.error(
                            'A resposta deve ser igual a 1 ou 2'
                        )

                    else:
                        #Verifica se há Risk Seeking e salva no BD em caso positivo

                        msg = check_biases_cod_choice_main_decision(input_cod_problem, input_cod_agent,input_cod_choice, input_desc_decison )

                        if msg != "":
                            #Houve Risk Seeking e ja salvou no BD
                            #Pega os dados de alternativa_ganho e alternativa_perda:
                            temp_cod_agent = 0
                            # if st.session_state.get('cod_agent') is None:
                            #     #temp_cod_agent =  COD_AGENT1
                            # else:
                            #     temp_cod_agent = st.session_state["cod_agent"]
                            temp_cod_agent = input_cod_agent
                            if(temp_cod_agent != 0):
                                #Alternativa 1:
                                psychologicalValueAscription = psychologicalvalueascription.get(psychologicalvalueascription.cod_agent == temp_cod_agent,
                                                                                                psychologicalvalueascription.cod_choice == 1,
                                                                                                psychologicalvalueascription.cod_problem == idProblema)

                            alternativa_ganho = 0
                            alternativa_perda = 0
                            if psychologicalValueAscription.cod_value == COD_VALUE_GAIN:
                                alternativa_ganho = 1 #Alternativa 1 é GANHO
                                alternativa_perda = 2 #Alternativa 2 é PERDA
                            else:
                                alternativa_ganho = 2 #Alternativa 2 é GANHO
                                alternativa_perda = 1 #Alternativa 1 é PERDA

                            # #st.warning(msg)
                            # st.image("alertagrande_ler_com_atencao_risk_seeking_for_high_prob_of_loss.png")
                            #
                            # #TODO: Excluir abaixo
                            # # st.write("desc_bias: "+desc_bias)
                            # # st.write("desc_ref: "+desc_ref)
                            # # st.write("alternativa_perda: "+str(alternativa_perda))
                            # # st.write("alternativa_ganho: "+str(alternativa_ganho))
                            #

                            #Salva o codigo da decisao e o codigo do problema na sessao
                            #TO AQUI: alterar o codigo abaixo para chamar a pagina que vai dar o alerta, mas mostrando primeiro a imagem:
                            #salvar na sessao de sistema: cod_problem, cod_agent, cod_main_decision

                            # if 'sis_sessao_page_risco' not in st.session_state:
                            #     #Aqui seta a sessao da pagina para onde o sistema sera redirecionado:
                            #     st.session_state['sis_sessao_page_risco'] = 'Exibe Alerta Risco na Decisao'
                            #
                            # if 'sis_cod_problem' not in st.session_state:
                            #     st.session_state['sis_cod_problem'] = idProblema
                            #
                            # if 'sis_cod_agent' not in st.session_state:
                            #     st.session_state['sis_cod_agent'] = input_cod_agent
                            #
                            # if 'sis_cod_main_decision' not in st.session_state:
                            #     st.session_state['sis_cod_main_decision'] = input_cod_choice

                            st.session_state['sis_sessao_page_risco'] = 'Exibe Alerta Risco na Decisao'
                            st.session_state['sis_cod_problem'] = idProblema
                            st.session_state['sis_cod_agent'] = input_cod_agent
                            st.session_state['sis_cod_main_decision'] = input_cod_choice

                            # guardar o nome da proxima pagina do sistema: alerta
                            # Obs: na pagina seguinte, fazer igual ao codigo dentro do if abaixo:
                            # #elif st.session_state['pagina_atual'] == 'bool_recebeu_alerta':
                            #
                            # # if st.session_state.get('cod_agent') is None:
                            # #     #temp_cod_agent =  COD_AGENT1
                            # # else:
                            # #     temp_cod_agent = st.session_state["cod_agent"]
                            #
                            # # image_personalizada = Image.open(personaliza_image(temp_cod_agent, idProblema, finantialvaluea1, probabilitya1,finantialvalueb1, probabilityb1, finantialvaluea2,probabilitya2,finantialvalueb2, probabilityb2, str(alternativa_ganho), str(alternativa_perda), desc_bias, desc_ref))
                            # # st.image(image_personalizada)

                            #EDUARDO:
                            #if 'id_problem' in query_params:
                            #    query_params.pop('id_problem')
                            if 'id_problem' in params:
                                params.pop('id_problem')
                            #st.experimental_set_query_params() #Limpa o parametro idProblema

                            # Atualiza a página
                            st.experimental_rerun() #Ed 14-04-23

                        else: # (msg == "")
                            #st.success("Decision saved with success!")
                            st.success("Decisão salva com sucesso!")
                            #EDUARDO
                            st.experimental_set_query_params() #Limpa o parametro idProblema
                            #st.experimental_set_query_params(prototipo="2222")
                            #st.experimental_rerun()
                    #Fim Start 1

# Página de cadastro

elif Page_cadastro == 'Perfil':
    st.subheader("Seu Perfil")
    if st.button("Cadastro"):
        register()
    if st.button("Login"):
        login()
        
elif Page_cadastro == 'Detecção Geral':
    st.subheader("Todos os Problemas")
    query = show_all_problems_and_decision_query()
    df = pd.DataFrame(query.namedtuples())
    df
    if st.button("Analisar"):
        analisar()

elif Page_cadastro == 'Cadastro de Problemas':
    #st.experimental_get_query_params() #Limpa o parametro idProblema

    #PageListCliente.List()
    #st.title("Input data handler: Problem and its Alternatives")
    st.subheader("Cadastro de Problemas")
    input_button_submit = False
    with st.form(key="include_problem_alternatives"):
        st.write("Pre-requisites:")
        st.write("If there is an alternative with 100% chance, it should be the first alternative to be input into the system.")
        st.write("If there is an alternative composed by 2 statements joined with \"AND\" (conjunction) then the statement with the greatest probability should be input the first into the system.")
        st.write("Example of an alternative like that: 95% chance of losing R\$ 10,000 AND 5% chance of losing R\$ 100")
        st.write("")
        st.write("")

        input_cod_problem = st.number_input(label="Problem code", format="%d", step=1)
        input_desc_problem = st.text_input(label="Describe the decision-making problem")
        #input_name = st.text_input(label="Insira o seu nome")
        #input_age = st.number_input(label="Insira sua idade", format="%d", step=1)
        #input_occupation = st.selectbox(label="Selecione sua profissão", options=listOccupation)

        st.write("")
        st.write("")
        st.write("FIRST Alternative")
        st.write("")
        input_cod_choice1 = st.number_input(label="Alternative code", format="%d", step=1, value=1, disabled=True)
        input_desc_alternative1 = st.text_input(label="Describe the alternative", key="input_desc_alternative1")
        #input_financial_valuea1 = st.text_input(label="Financial value", key="input_financial_valuea1")
        input_financial_valuea1 = st.number_input(label="Financial value", key="input_financial_valuea1")
        #input_probabilitya1 = st.number_input(label="Probability (%)", format="%d", key="input_probabilitya1")
        input_probabilitya1 = st.number_input(label="Probability (%)", key="input_probabilitya1")
        st.write("")
        st.write("AND")
        st.write("")
        #input_financial_valueb1 = st.text_input(label="Financial value", value=0, key="input_financial_valueb1")
        input_financial_valueb1 = st.number_input(label="Financial value", value=0, key="input_financial_valueb1")
        input_probabilityb1 = st.number_input(label="Probability (%)", value=0, key="input_probabilityb1")

        st.write("")
        st.write("")
        st.write("SECOND Alternative")
        st.write("")
        input_cod_choice2 = st.number_input(label="Alternative code", format="%d", step=1, value=2, disabled=True)
        input_desc_alternative2 = st.text_input(label="Describe the alternative", key="input_desc_alternative2")
        input_financial_valuea2 = st.number_input(label="Financial value", key="input_financial_valuea2")
        input_probabilitya2 = st.number_input(label="Probability (%)", key="input_probabilitya2")
        st.write("")
        st.write("AND")
        st.write("")
        input_financial_valueb2 = st.number_input(label="Financial value", value=0, key="input_financial_valueb2")
        input_probabilityb2 = st.number_input(label="Probability (%)", value=0, key="input_probabilityb2")

        input_button_submit = st.form_submit_button("Save")

    if input_button_submit:
        #Valida:
        valida1 = ""
        valida2 = ""
        valida3 = ""
        if input_probabilitya1 !=100:
            if input_probabilityb1 == 100 or input_probabilitya2 == 100 or input_probabilityb2 ==100:
                valida1 = "The alternative with 100% chance should be the first alternative to be input into the system."

        if input_probabilityb1>input_probabilitya1:
            valida2 = "In the FIRST Alternative, the statement with the greatest probability should be input the first into the system"
        if input_probabilityb2>input_probabilitya2:
            valida3 = "In the SECOND Alternative, the statement with the greatest probability should be input the first into the system"

        if valida1!="" or valida2!="" or valida3!="":
            if valida1!="":
                st.error(valida1)
            if valida2!="":
                st.error(valida2)
            if valida3!="":
                st.error(valida3)
        else:
            #ClienteController.Incluir(cliente.Cliente(0, input_name, input_age, input_occupation))
            #Save problem
            problem.create(cod_problem=input_cod_problem,desc_problem=input_desc_problem)
            #Problem.create(cod_problem=input_cod_problem,desc_problem=input_desc_problem) #TODO: alterar para desc_problem
            #Save Alternative 1
            alternatives.create(cod_problem=input_cod_problem, cod_choice=input_cod_choice1,
                                desc_alternative=input_desc_alternative1,
                                financial_valuea=input_financial_valuea1,probabilitya=input_probabilitya1,
                                financial_valueb=input_financial_valueb1,probabilityb=input_probabilityb1
                                )
            # expected_value_calculated=(input_probabilitya1/100)*int(input_financial_valuea1) + (input_probabilityb1/100)*int(input_financial_valueb1)

            #Save Alternative 2
            alternatives.create(cod_problem=input_cod_problem, cod_choice=input_cod_choice2,
                                desc_alternative=input_desc_alternative2,
                                financial_valuea=input_financial_valuea2,probabilitya=input_probabilitya2,
                                financial_valueb=input_financial_valueb2,probabilityb=input_probabilityb2
                                )
            # expected_value_calculated=(input_probabilitya2/100)*int(input_financial_valuea2) + (input_probabilityb2/100)*int(input_financial_valueb2)
            st.success("Problem and Alternatives saved with success!")

elif Page_cadastro == 'Lista de todos os Problemas':
    #st.title("Decisões Tomadas")
    st.subheader("Lista de todos os Problemas")
    #st.write("All the Problems and Alternatives are:")
    query = show_all_problems_and_alternatives_query()
    df = pd.DataFrame(query.namedtuples())
    df

elif Page_cadastro == 'Decisões Tomadas':
    st.subheader("Decisões Tomadas")

    st.write("Lista de todas as decisões tomadas:")
    query = show_decisions_query()
    df = pd.DataFrame(query.namedtuples())
    df

# Exibir respostas para debug
st.session_state