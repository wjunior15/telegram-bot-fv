import telebot
import math
from msedge.selenium_tools import Edge, EdgeOptions
from selenium.webdriver.common.keys import Keys
import time
 
options = EdgeOptions()
options.use_chromium = True
 
caminho_chave = r"...\chave_API_bot_Telegram.txt"
chave_api_file = open(caminho_chave, "r")
chave_api = chave_api_file.read()
 
bot = telebot.TeleBot(chave_api)
 
##Variáveis Globais do Bot
geracao = None
 
placas = None
 
cidade = None
 
variavel_incorreta = None
 
opcao = None
 
js_code = """
var linha_minima = document.getElementsByTagName('tr')[15].getElementsByTagName('td');
 
lenFor = linha_minima.length;
 
for(var i=1; i<lenFor; i++){
    if(i == 1){
        var menor = linha_minima[1].innerText;
    }else{
        if(linha_minima[i].innerText < menor){
            menor = linha_minima[i].innerText;
        };
    };
};
 
return menor
"""
 
##Funções auxiliares do bot
 
def calcula_num_placas(geracao, placas):
    n_placas = geracao / (placas * 120)
    return n_placas
 
def busca_temp_cidade(cidade):
    pass
 
def verifica_kwh(mensagem):
    global geracao
    texto = mensagem.text.lower()
    
    if "kwh" in texto and opcao == 1:
        geracao = float(texto.replace('kwh','').replace(' ','').replace(',','.')) * 1000
        return True
    else:
        return False
 
def verifica_kwp(mensagem):
    global placas
    texto = mensagem.text.lower()
    
    if "kwp" in texto and geracao and opcao == 1:
        placas = float(texto.replace('kwp','').replace(' ','').replace(',','.')) * 1000
        return True
    else:
        return False
    
def verifica_cidade(mensagem):
    global placas
    global geracao
    global cidade
    global opcao
    
    if placas and geracao and cidade == None and opcao == 1:
        cidade = mensagem.text
        return True
    else:
        return False
    
def busca_temperatura(cidade):
    global js_code
    
    driver = Edge(options = options)
    driver.get("https://pt.climate-data.org/america-do-sul/brasil-114/")
 
    time.sleep(5)
    
    #concorda cookies
    driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div[2]/div[2]/button[1]').click()
    
    driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div[3]/div/button[1]').click()
    
    ##Realiza Busca
    driver.find_element_by_xpath('/html/body/div[2]/div[1]/div[2]/div[2]/div/div/form/span').click()
    driver.find_element_by_xpath('/html/body/div[2]/div[1]/div[2]/div[2]/div/div/form/input').send_keys(cidade)
    driver.find_element_by_xpath('/html/body/div[2]/div[1]/div[2]/div[2]/div/div/form/input').send_keys(Keys.ENTER)
    
    #seleciona primeira opcao
    driver.find_element_by_class_name('data').click()
    
    #varrer opções
    menor = driver.execute_script(js_code)
    
    driver.quit()
    
    return menor    
 
 
##Funções de mensagens do bot
@bot.message_handler(commands = ['reset'])
def reseta_atendimento(mensagem):
    global placas
    global geracao
    global cidade
    global variavel_incorreta
    global opcao
    
    geracao = None
    placas = None
    cidade = None
    variavel_incorreta = None
    opcao = None
    
    texto = """       
    Escolha uma das opções abaixo, clicando na opção:
        /opcao1 Verificar quantidade de placas;
        /opcao2 Verificar geração do cliente;
        /opcao3 Contatar o suporte;
        
        /reset para recomeçar o atendimento."""
    
    bot.send_message(mensagem.chat.id, texto)
    
    
    
@bot.message_handler(commands = ['OK'])
def realiza_calculos(mensagem):
    global placas
    global geracao
    global cidade
    global opcao
    bot.send_message(mensagem.chat.id, "Estamos calculando")
    
    n_placas = calcula_num_placas(geracao, placas)
    
    bot.send_message(mensagem.chat.id, "Será(ão) necessário(s) {} placa(s) do modelo indicado.".format(math.ceil(n_placas)))
    
    temp_minima = busca_temperatura(cidade)
    
    bot.send_message(mensagem.chat.id, "A temperatura minima anual na cidade escolhida foi de {}°C".format(temp_minima))
    
    placas = None
    cidade = None
    geracao = None
    opcao = None
    
@bot.message_handler(commands = ['INCORRETO'])
def dado_incorreto(mensagem):
    global variavel_incorreta
    variavel_incorreta = True
    bot.send_message(mensagem.chat.id, "Vamos resolver")
 
@bot.message_handler(func=verifica_cidade)
def obtem_cidade(mensagem):
    global placas
    global geracao
    global cidade
    bot.send_message(mensagem.chat.id, "Recebemos a cidade, confira as informações:\nGeração esperada: {} kWh\nPotência das placas: {} kWp\nCidade da usina: {}\n/OK ou /INCORRETO".format(geracao/1000, placas/1000, cidade))
    
 
@bot.message_handler(func=verifica_kwh)
def obtem_khw(mensagem):
    bot.send_message(mensagem.chat.id, "Recebemos a Energia, digite a potência da placa (Não esqueça da unidade kWp):")
    
@bot.message_handler(func=verifica_kwp)
def obtem_kwp(mensagem):
    bot.send_message(mensagem.chat.id, "Recebemos potência da placa, digite a cidade onde será instalada a usina:")
    
@bot.message_handler(commands = ['opcao1'])
def opcao1(mensagem):
    
    global opcao
    opcao = 1
    
    bot.send_message(mensagem.chat.id, "Digite a energia necessária (Não esqueça da unidade kWh):")
 
@bot.message_handler(commands = ['opcao2'])
def opcao2(mensagem):
    bot.send_message(mensagem.chat.id, "Você clicou na opção 2")
 
@bot.message_handler(commands = ['opcao3'])
def opcao3(mensagem):
    bot.send_message(mensagem.chat.id, "Você clicou na opção 3")
 
def verificar(mensagem):
    return True
 
#criando um decorator:
@bot.message_handler(func=verificar)
def responder(mensagem):
    
    texto = """       
    Escolha uma das opções abaixo, clicando na opção:
        /opcao1 Verificar quantidade de placas;
        /opcao2 Verificar geração do cliente;
        /opcao3 Contatar o suporte;
        
        /reset para recomeçar o atendimento."""
    
    bot.send_message(mensagem.chat.id, texto)
 
bot.polling()