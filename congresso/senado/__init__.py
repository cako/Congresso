# -*- coding: utf8 -*-

import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime as dt

LEGINIS = [1826, 1830, 1834, 1838, 1843, 1845, 1848, 1850, 1853, 1857, 1861,
           1864, 1867, 1869, 1872, 1877, 1878, 1882, 1885, 1886, 1890, 1891,
           1894, 1897, 1900, 1903, 1906, 1909, 1912, 1915, 1918, 1921, 1924,
           1927, 1930, 1933, 1934, 1946, 1951, 1955, 1959, 1963, 1967, 1971,
           1975, 1979, 1983, 1987, 1991, 1995, 1999, 2003, 2007, 2011, 2015]
LEGFINS = [1829, 1833, 1837, 1841, 1844, 1847, 1849, 1852, 1856, 1860, 1863,
           1866, 1868, 1872, 1875, 1878, 1881, 1884, 1885, 1889, 1891, 1893,
           1896, 1899, 1902, 1905, 1908, 1911, 1915, 1917, 1920, 1923, 1926,
           1929, 1930, 1934, 1937, 1951, 1955, 1959, 1963, 1967, 1970, 1974,
           1978, 1983, 1987, 1991, 1995, 1999, 2003, 2007, 2010, 2015, 2019]

class Fetcher:
    """
    Define uma classe genérica Fetcher. Faz interface com o recursos
    http://legis.senado.gov.br/dadosabertos/{}
    dos seus métodos.
    """

    def __init__(self, fetch, baseurl, baselocal, write=False, delxml=True):
        self._baseurl = baseurl
        self._baselocal = os.path.abspath(os.path.expanduser(baselocal))
        self._fetch = fetch
        self._fetched = False
        self._delxml=delxml
        self.xml = None
        self._write = write
        self.info = {}

    def _get_xml_remote(self):
        """
        Obtem arquivo XML que contem a informação remotamente.

        Retorna
        -------
        * -2: Falha na obtenção dos dados remotos
        *  0: Sucesso

        Altera
        ------
        * self.xml: caso bem sucedido, preenche-a com o root do XML
        """
        try:
            r = requests.get(self._baseurl.format(self._fetch))
        except requests.ConnectionError:
            return -2
        if r.status_code != requests.codes.ok:
            return -2
        tree = ET.ElementTree(ET.fromstring(r.content))
        self.xml = tree
        return 0

    def _get_xml_local(self):
        """
        Obtem arquivo XML que contem a informação localmente.

        Retorna
        -------
        * -1: Falha na obtenção dos dados locais
        *  0: Sucesso

        Altera
        -------
        * self.xml: caso bem sucedido, preenche-a com o root do XML
        """
        try:
            tree = ET.parse(os.path.join(self._baselocal,
                                         str(self._fetch)+'.xml'))
        except (NameError, IOError):
            return -1
        self.xml = tree
        return 0

    def _get_xml(self, remote=None):
        """
        Obtem arquivo XML que contem informação sobre o parlamentar.

        Entra
        -----
        * remote: especifica se os dados serão obtidos local (False) ou
                  remotamente (True), respectivamente. Em case de None, será
                  primeiro feita uma busca local, seguida por uma remota

        Retorna
        -------
        * -2: falha na obtenção dos dados remotos
        * -1: falha na obtenção dos dados locais
        *  0: Sucesso

        Altera
        ------
        * self.xml: caso bem sucedido, preenche-a com o root do XML
        """
        err = None
        if not remote:  # igual a: remote is False or remote is None:
            err = self._get_xml_local()
        if remote or err != 0:
            err = self._get_xml_remote()
        return err

    def _parse_xml(self):
        """
        Analisa o conteúdo de self.xml e constrói self.info.

        Retorna
        -------
        - -3: self.xml não existe
        -  0: Sucesso
        -  1: parlamentar não existe

        Altera
        -------
        - self.info: caso bem sucedido, preenche-a com os dados obtidos do XML
        """

        if self.xml is None:
            return -3

        # Verifica se parlamentar existe
        try:
            root = self.xml.getroot()[1][0]
        except IndexError:
            return 1

        # Processa dados
        for campo in root:
            self.info[campo.tag] = campo.text
        return 0

    def get_info(self, remote=None):
        """
        Obtem informações. Em caso de obtenção de dados remotos, faz interface
        com o recurso self._baseurl

        Entra
        -----
        * remote: especifica se os dados serão obtidos local (False) ou
                  remotamente (True), respectivamente. Em case de None, será
                  primeiro feita uma busca local, seguida por uma remota
        * save: caso o método deja remoto, é possível salvá-lo através desta
                flag. O método nunca overwrite.

        Retorna
        ---------
        * -2: Falha na obtenção dos dados remotos
        * -1: Falha na obtenção dos dados locais
        *  0: Sucesso
        *  1: Parlamentar não existe
        *  2: Falha ao salvar (alterou com sucesso self.xml e self.info)
        *  3: Dados já foram buscados

        Altera
        -------
        * self.xml:  caso bem sucedido, preenche-a com o root do XML
        * self.info: caso bem sucedido, preenche-a com os dados obtidos do XML
        """
        # Obtem dados: altera self.xml
        if self._fetched:
            return 3
        self._fetched = True

        err = self._get_xml(remote)
        if err != 0:
            return err

        # Analisa dados do parlamentar: altera self.info
        err = self._parse_xml()
        if err != 0:
            return err

        # Salva
        if self._write:
            datapath = os.path.join(self._baselocal, str(self._fetch)+'.xml')
            if os.path.isfile(datapath):
                return 2
            try:
                self.xml.write(datapath)
            except IOError:
                return 2
        if self._delxml:
            del self.xml
        return 0


class Senador(Fetcher):
    """
    Define a classe Senador.
    """
    _baseurl = 'http://legis.senado.gov.br/dadosabertos/senador/{}/historico'

    def __init__(self, cod, baselocal=None, fetch=False, write=False,
                 delxml=True):
        if not baselocal:
            curdir = os.path.dirname(os.path.abspath("__file__"))
            baselocal = os.path.join(curdir, 'data', 'senador')
        self.cod = int(cod)
        super().__init__(self.cod, self._baseurl, baselocal, write, delxml)
        self.nome = self.dn = self.UF = self.sexo = self.M = self.F = None
        self.partidos = []
        self.materias = []
        if fetch:
            self.get_info()

    @property
    def sexo(self):
        return self.__sexo

    @sexo.setter
    def sexo(self, sexo):
        self.__sexo = sexo
        if sexo is not None:
            self.M = sexo.lower()[0] == 'm'
            self.F = sexo.lower()[0] == 'f'

    def __lt__(self, other):
        return self.dn < other.dn

    def __repr__(self):
        return 'senado.Senador({})'.format(self.cod)

    def __str__(self):
        if self.nome:
            return 'Senador {}, no. {}'.format(self.nome, self.cod)
        else:
            return 'Senador no. {}'.format(self.cod)

    def _parse_xml(self):
        if self.xml is None:
            return -3

        # Verifica se parlamentar existe
        try:
            parlamentar = self.xml.getroot()[1][0]
        except IndexError:
            return 1

        # Processa dados do parlamentar
        atrs = ('nome', 'sexo', 'UF')
        atrs_xml = ('NomeParlamentar', 'Sexo', 'SiglaUfNatural')

        atrs_md = ('_uf', '_legini', '_legfim', '_anoini', '_anofim', '_tit',
                  '_url')
        atrs_md_xml = ('SiglaUF', 'LegislaturaInicio', 'LegislaturaFim',
                      'AnoInicio', 'AnoFim', 'TitularSuplente',
                      'PaginaNoMandato')

        atrs_mt = ('tipo', 'num', 'ano', 'ementa')
        atrs_mt_xml = ('SiglaMateria', 'NumeroMateria', 'AnoMateria', 'Ementa')

        for campo in parlamentar:
            tag = campo.tag
            txt = campo.text
            if tag == 'NomeCompleto':
                if self.nome is None:
                    self.nome = txt
            elif tag == 'DataNascimento':
                self.dn = dt.strptime(txt, '%Y-%m-%d')
            elif tag == 'Partidos':
                for part in campo:
                    try:
                        self.partidos.append(part.find('SiglaPartido').text)
                    except AttributeError:
                        try:
                            self.partidos.append(part[0].text)
                        except (IndexError, AttributeError):
                            pass
            elif tag == 'Mandatos':
                self.mandatos = []
                for mandato in campo:
                    for atr in atrs:
                        setattr(self, atr, None)
                    for cp in mandato:
                        try:
                            setattr(self, atrs_md[atrs_md_xml.index(cp.tag)], cp.text)
                        except ValueError:
                            pass
                    self.mandatos.append(Mandato(self._uf, self._legini,
                                                 self._legfim, self._anoini,
                                                 self._anofim, self._tit,
                                                 self._url))
                for atr in atrs_md:
                    delattr(self, atr)
                self.mandatos.sort()
            elif tag == 'MateriasDeAutoria': # ou 'Relatorias'
                for mat in campo:
                    m = Materia(mat[0].text) # Codigo
                    for camp in mat[1:]:
                        try:
                            setattr(m, atrs_mt[atrs_mt_xml.index(camp.tag)], camp.text)
                        except ValueError:
                            pass
                    # Fix baselocal!
                    self.materias.append(m)
                self.materias.sort()
            #elif campo.tag == 'MembroComissao':
                #self.info['MembroComissao'] = []
                #for col in campo:
                    #self.info['MembroComissao'].append( (col.find('SiglaColegiado').text,
                                                         #col.find('SiglaCasa').text) )
            #elif campo.tag == 'Cargos':
                #self.info['Cargos'] = []
                #for col in campo:
                    #self.info['Cargos'].append(col.find('SiglaColegiado').text)
            #elif campo.tag == 'Votacoes':
                #self.info['Votacoes'] = []
                #for vot in campo:
                    #cod = vot.find('CodigoMateria')
                    #try:
                        #cod = int(cod.text)
                    #except AttributeError:
                        #cod = -1
                    #voto = vot.find('VotoParlamentar')
                    #voto = voto.text
                    #self.info['Votacoes'].append( (cod, voto) )
            else:
                try:
                    setattr(self, atrs[atrs_xml.index(tag)], txt)
                except ValueError:
                    self.info[tag] = txt
        return 0
    _parse_xml.__doc__ = Fetcher._parse_xml.__doc__


class Mandato:
    """
    Define um Mandato de um senador, com atributos descrevendo qual UF
    representou início, fim e se o Senador foi Titular ou Suplente
    """
    def __init__(self, UF, legini, legfim, anoini, anofim, tit=None, url=None):
        self.UF = UF
        self.legini, self.legfim = int(legini), int(legfim)
        self.anoini, self.anofim = int(anoini), int(anofim)
        self.T, self.S = None, None
        if tit is not None:
            if tit.lower()[0] != 't': # Titular
                self.T = False
                self.S = True
            else:
                self.S = False
                self.T = True
        self._tit = tit
        self.url = url

    def __lt__(self, other):
        return self.legini < other.legini

    def __repr__(self):
        rep = 'senado.Mandato({}, {}, {}, {}, {}, {})'
        return rep.format(self.UF, self.legini, self.legfim, self.anoini,
                          self.anofim, self._tit, self.url)


class Materia(Fetcher):
    """
    Define uma Matéria e seus atributos. Faz interface com o recurso
        http://legis.senado.leg.br/dadosabertos/materia/{cod}
    através do método get_info()
    """
    _baseurl = 'http://legis.senado.leg.br/dadosabertos/materia/{}'

    def __init__(self, cod, baselocal=None, fetch=False, write=False,
                 delxml=True):
        if not baselocal:
            curdir = os.path.dirname(os.path.abspath("__file__"))
            baselocal = os.path.join(curdir, 'data', 'materia')
        self.cod = int(cod)
        super().__init__(self.cod, self._baseurl, baselocal, write, delxml)
        self.ano = self.tipo = self.T = self.casa = self.num = self.data = None
        self.autores = []
        self.ementa = None
        if fetch:
            self.get_info()

    def __lt__(self, other):
        if self.data:
            return self.data < other.data
        elif self.ano:
            return self.ano < other.ano
        else:
            return False

    def __repr__(self):
        return 'senado.Materia({})'.format(self.cod)

    def _parse_xml(self):
        if self.xml is None:
            return -3

        # Verifica se parlamentar existe
        try:
            root = self.xml.getroot()[1]
        except IndexError:
            return 1

        # Processa dados do parlamentar
        for campo in root:
            if campo.tag == 'IdentificacaoMateria':
                for cp in campo:
                    tag = cp.tag
                    txt = cp.text
                    if tag == 'AnoMateria':
                        self.ano = int(txt)
                    elif tag == 'IndicadorTramitando':
                        self.T = True if txt.lower() == 'sim' else False
                    elif tag == 'NumeroMateria':
                        self.num = txt
                    elif tag == 'SiglaCasaIdentificacaoMateria':
                        self.casa = txt
                    elif tag == 'SiglaSubtipoMateria':
                        self.tipo = txt
            elif campo.tag == 'DadosBasicosMateria':
                for cp in campo:
                    tag = cp.tag
                    txt = cp.text
                    if tag == 'DataApresentacao':
                        self.data = dt.strptime(txt, '%Y-%m-%d')
            elif campo.tag == 'Autoria':
                for autor in campo:
                    for cp in autor:
                        if cp.tag == 'IdentificacaoParlamentar':
                            for c in cp:
                                if c.tag == 'CodigoParlamentar':
                                    cod = int(c.text)
                                elif c.tag == 'NomeParlamentar':
                                    nome = c.text
                                elif c.tag == 'SexoParlamentar':
                                    sexo = c.text
                                elif c.tag == 'UfParlamentar':
                                    uf = c.text
                    sen = Senador(cod)
                    sen.nome, sen.sexo, sen.UF = nome, sexo, uf
                    self.autores.append(sen)
    _parse_xml.__doc__ = Fetcher._parse_xml.__doc__

class Legislatura(Fetcher):
    """
    Define uma Legislatura e seus atributos. Faz interface com o recurso
http://legis.senado.gov.br/dadosabertos/senador/lista/legislatura/{legislatura}
    através do método self.get_info()
    """
    _baseurl = ('http://legis.senado.gov.br/dadosabertos/senador/lista/'
                'legislatura/{}')

    def __init__(self, legislatura, baselocal=None, fetch=False, write=False,
                 delxml=True):
        if not baselocal:
            curdir = os.path.dirname(os.path.abspath("__file__"))
            baselocal = os.path.join(curdir, 'data', 'senador', 'lista',
                                     'legislatura')
        super().__init__(legislatura, self._baseurl, baselocal, write, delxml)

        self.leg = int(legislatura)
        self.anoini = LEGINIS[self.leg-1]
        self.anofim = LEGFINS[self.leg-1]
        self.senadores = []

        if fetch:
            self.get_info()

    def __lt__(self, other):
        return self.leg < other.leg

    def __repr__(self):
        return 'senado.Legislatura({})'.format(self.leg)

    def _parse_xml(self):
        if self.xml is None:
            return -3

        # Verifica se parlamentar existe
        try:
            parlamentares = self.xml.getroot()[1][0]
        except IndexError:
            return 1

        # Processa dados do parlamentar
        atrs = ('nome', 'sexo', '_uf', '_legini', '_legfim', '_anoini', '_anofim')
        atrs_xml = ('NomeParlamentar', 'SexoParlamentar', 'SiglaUF',
                    'LegislaturaInicio', 'LegislaturaFim', 'AnoInicio',
                    'AnoFim')
        for par in parlamentares:
            try:
                cod = int(par.get('id'))
            except TypeError:
                continue
            # Sobe dois diretórios
            baselocal = os.path.split(os.path.split(self._baselocal)[0])[0]
            sen = Senador(cod, baselocal=baselocal)
            for campo in par[1:]:
                tag = campo.tag
                txt = campo.text
                if tag == 'NomeCompleto':
                    if sen.nome is None:
                        sen.nome = txt
                elif tag == 'Partidos':
                    sen.partidos = []
                    for part in campo:
                        try:
                            sen.partidos.append(part.find('SiglaPartido').text)
                        except AttributeError:
                            try:
                                sen.partidos.append(part[0].text)
                            except (IndexError, AttributeError):
                                pass
                else:
                    try:
                        setattr(sen, atrs[atrs_xml.index(tag)], txt)
                    except ValueError:
                        sen.info[tag] = txt
            sen.mandatos = [Mandato(sen._uf, sen._legini, sen._legfim,
                                    sen._anoini, sen._anofim)]
            for atr in atrs[2:]:
                delattr(sen, atr)
            self.senadores.append(sen)
        return 0
    _parse_xml.__doc__ = Fetcher._parse_xml.__doc__

