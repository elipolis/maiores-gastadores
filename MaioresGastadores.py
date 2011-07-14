# Feito por Pedro Limeira.
# crawler para detectar gastos de senadores com passagem aereas.
# Site utilizado http://www.senado.gov.br/transparencia/

import urllib2,urllib,webbrowser
from BeautifulSoup import BeautifulSoup

def get_total(val):
  return float(str(val).replace("R$ ","").replace('.','').replace(',','.'))

SENADO_URL = "http://www.senado.gov.br/transparencia"

resultPage = open("resultados.html","a")

initHtml = '''
  <html><head><title>Maiores Gastadores</title></head><body>
  <h1 style="text-align: center"><b>Gastos totais de senadores desde o inicio de seus mandatos</b></h1>
  <ul>
'''

resultPage.write(initHtml)

gastos = {}

parser = BeautifulSoup(urllib2.urlopen(SENADO_URL))

senadores = parser.find('select',{'name':'COD_ORGAO'}).findAll('option')[1:]

i = 0
for senador in senadores:
    print '-------'
    senadorCode = str(senador['value'])
    senadorName = str(senador.contents[0])

    params = urllib.urlencode({'COD_ORGAO': senadorCode})
    verbaAnoPage = urllib2.urlopen(SENADO_URL + '/verba/asp/VerbaAno.asp', params)

    parser = BeautifulSoup(verbaAnoPage)

    anos = parser.find('select', {'name':'ANO_EXERCICIO'}).findAll('option')[1:]

    gastos[senadorName] = 0
    print senadorName

    for ano in anos:
        params = urllib.urlencode({'COD_ORGAO': senadorCode, 'ANO_EXERCICIO': str(ano['value'])})
        verbaMesPage = urllib2.urlopen(SENADO_URL + "/verba/asp/VerbaMes.asp", params)

        parser  = BeautifulSoup(verbaMesPage)

        _meses = parser.find('select', {'name':'COD_PERIODO'})
        if _meses == None:
          break

        meses = _meses.findAll('option')[1:]

        for mes in meses:
            params = urllib.urlencode({'COD_ORGAO': senadorCode, 'ANO_EXERCICIO': str(ano['value']), 'NOM_SENADOR': senadorName, 'IND_PESSOAL': '','COD_PROCESSO': '','COD_PERIODO': str(mes['value'])})

            verbaMesValoresPage = urllib2.urlopen(SENADO_URL + "/verba/asp/VerbaMes.asp", params)

            parser = BeautifulSoup(verbaMesValoresPage)

            #A 0 eh a string escrito Total a segunda eh o valor. Nessa linha R$ xx,x
            _total = parser.find('tfoot').findAll('td')[1].find('b').contents[0]
            total = get_total(_total)

            print '     ' + str(mes.contents[0]) + ' : ' + str(_total)
            gastos[senadorName] += total

for gasto in gastos:
  resultPage.write('<li style="border-bottom: 1px solid black; padding: 10px 0 "> ' + str(gasto) + '     R$ ' + str(gastos[gasto]) + '</li>' )

resultPage.write('</ul><footer style="text-align: center">resultado da execucao do script MaioresGastadores.py</footer></body></html>')

webbrowser.open("resultados.html")
