# Feito por Pedro Limeira.
# crawler para detectar gastos de senadores com CEAPS
# Site utilizado http://www.senado.gov.br/transparencia/

import urllib2,urllib,webbrowser,json
from BeautifulSoup import BeautifulSoup

def get_total(val):
  return float(str(val).replace("R$ ","").replace('.','').replace(',','.'))

def get_ranking(gastos_dic):
  ranking = []
  for gasto in gastos_dic.keys():
      ranking.append((float(gastos_dic[gasto]),gasto))
  ranking.sort(reverse=True)
  return ranking
  

SENADO_URL = "http://www.senado.gov.br/transparencia"

resultJSON = open("resultados.json","w")
resultJSONNF = open("resultados_nf.json","w")

gastos = {}
nf_gastos = {}

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
    nf_gastos[i] = {}
    i2 = 0
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
            nf_gastos[i][i2] = {}
            
            params = urllib.urlencode({'COD_ORGAO': senadorCode, 'ANO_EXERCICIO': str(ano['value']), 'NOM_SENADOR': senadorName, 'IND_PESSOAL': '','COD_PROCESSO': '','COD_PERIODO': str(mes['value'])})

            verbaMesValoresPage = urllib2.urlopen(SENADO_URL + "/verba/asp/VerbaMes.asp", params)

            parser = BeautifulSoup(verbaMesValoresPage)

            #A 0 eh a string escrito Total a segunda eh o valor. Nessa linha R$ xx,x
            _total = parser.find('tfoot').findAll('td')[1].find('b').contents[0]
            total = get_total(_total)

            print '     ' + str(ano.contents[0]) + ' ' + str(mes.contents[0]) + ' : ' + str(_total)
            gastos[senadorName] += total
            nf_gastos[i][i2]['nome'] = senadorName
            nf_gastos[i][i2]['ano'] = str(ano.contents[0])
            nf_gastos[i][i2]['mes'] = str(mes.contents[0])
            nf_gastos[i][i2]['valor'] = str(_total)
            nf_gastos[i][i2]['valor_num'] = total
            i2 = i2 + 1
    i = i + 1

resultJSONNF.write(json.JSONEncoder().encode(nf_gastos))

resultJSONNF.close()

