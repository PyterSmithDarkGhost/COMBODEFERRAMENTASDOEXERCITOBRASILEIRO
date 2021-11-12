# DSGTools Op
### Ferramentas para planejamento militar do Exército Brasileiro.
#### DSG - Diretoria de Serviço Geográfico

---
O DSGTools Op é um conjunto de ferramentas produto dos Estágios Básico e Avançado de Geoinformação para Corpo de Tropa, ministrados desde 2015, onde são apresentados os conceitos da geoinformação e as suas potencialidades de utilização prática, por intermédio de um SIG, que visa auxiliar nas atividades de preparo e emprego da tropa.

Durante os cursos de 2016 e 2017, os instrutores receberam uma série de comentários sobre possíveis aplicações do QGIS nas atividades das OM e foi identificada a necessidade de um plugin que reunisse as diversas ferramentas de interesse militar, implementadas de forma a facilitar sua utilização por OM de Corpo de Tropa. Para isso, deveriam ser utilizadas terminologias de uso militar e omitidas configurações específicas (fora do conhecimento básico da geoinformação para Corpo de Tropa).

A materialização desse conjunto de ferramentas foi denominada DSGTools Op, idealizado como uma extensão do plugin DSGTools, mas hoje totalmente independente.

---
### Ferramentas atuais

1. **Cálculo de coordenadas e dimensões** - Calcula automaticamente as coordenadas geográficas e planas de uma camada de pontos. Importante na interação da tropa terrestre com apoio aéreo.
2. **Conversão de unidades angulares** - Dado um campo da tabela de atributos com ângulos em graus, gera um campo com os ângulos em milésimos.
3. **Criação de pontos por coordenadas** - Cria um ponto num arquivo existente, a partir de suas coordenadas.
4. **Relocação de pontos por coordenadas** - Ao selecionar um ponto existente, movê-lo para outra posição a partir das coordenadas da nova posição.
5. **Declinação magnética e convergência meridiana** - Selecionando-se um ponto, linha ou polígono são apresentadas a Declinação Magnética e Convergência Meridiana do dado selecionado.
6. **Determinação do MI (Índice de Nomenclatura) da carta** - Ao clicar em uma região da tela que esteja dentro do Brasil aparecerá qual carta engloba aquela região, nas diversas escalas, sendo possível baixar as cartas na região escolhida.
7. **Perfil do terreno** - Traça um gráfico representativo da variação de elevação do terreno (raster), a partir de uma linha desenhada pelo usuário ou selecionada em uma camada vetorial.
8. **Geocodificação** - A partir de um arquivo CSV contendo endereços (e opcionalmente outros dados), determina a localização geográfica dos mesmos, criando uma camada de pontos atributados com os valores constantes do arquivo. Realiza também o processo inverso: dada uma camada de pontos, determina o endereço de cada um, adicionando um novo atributo com estes valores à camada. Utiliza a Bing Maps API.
9. **Medição durante aquisição vetorial** - Apresenta ao usuário as medidas da feição sendo desenhada (distância parcial/acumulada para linhas, área para polígonos) como uma tooltip junto ao cursor.
10. **Simbologia Militar** - Cria ou carrega banco de dados com simbologia militar prevista no manual MD33-M-02. Visa substituir o calco impresso pelos planos de informação do QGIS. (Ferramenta ainda em desenvolvimento, nem todos os símbolos previstos estão implementados).
11. **Sombreamento do terreno** - A partir da posição, data e hora indicados, a ferramento calcula a posição do Sol e então gera uma representação visual das sombras no terreno devidas ao relevo.
12. **Criação de pontos por azimute/distância** - Permite criar novas feições pontuais em camadas vetoriais de pontos a partir de um ponto predefinido e um azimute e distância a partir do mesmo.
13. **Alcance do armamento** - Gera buffers de alcance de armamento com base em valor definido pelo usuário, valendo-se também de um azimute de tiro e uma angulação de visada/atuação da peça.
14. **Geração de azimutes e distâncias** - Seleciona-se vários pontos, ou uma linha ou um polígono e é gerado um “csv” com as coordenadas do primeiro ponto e o azimute e distância para os demais pontos.
15. **Plano de chamada** - A partir de endereços geocodificados, pontos gerados previamente com ferramenta ‘Geocodificação’, agrupa os pontos através de algoritmos de proximidade espacial, visando subdividir o espaço em regiões de atuação e definir centros de atuação mais justos que distribuam uniformemente as distâncias entre o mesmo e cada ponto.

---
## Créditos
1. **Declinação magnética** - valor obtido por meio do geomag.py por Christopher Weiss cmweiss@gmail.com, https://github.com/cmweiss/geomag.  Utilizando modelo de coeficientes WMM 2020.0 do NOAA.
NCEI Geomagnetic Modeling Team and British Geological Survey. 2019. World Magnetic Model 2020. NOAA National Centers for Environmental Information. doi: 10.25921/11v3-da71, 2020, 01/14/2020.
2. **Perfil do terreno** - adaptação do plugin feito em 2008 por Borys Jurgiel e em 2012 por Borys Jurgiel e Patrice Verchere, https://github.com/etiennesky/profiletool/ .
3. **Criação de pontos por coordenadas** - adaptação do Trace Digitize Action Copyright (C) 2010  Cédric Möri, with stuff from Stefan Ziegler EMAIL: cmoe@geoing.ch. WEB: www.geoing.ch
4. **Sombreamento do terreno** - valores de posição solar obtidos a partir do sunposition.py por Samuel Bear Powell, https://github.com/s-bear/sun-position.

---
Última versão estável no QGIS: 3.20.0
