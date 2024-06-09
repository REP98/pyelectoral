#! /usr/bin/env python3
#  -*- coding: utf-8 -*-
"""MODULO CNE"""
import requests
import re
from bs4 import BeautifulSoup
from dataclasses import asdict
from .Data import ResponseData, STATUS


class CNE:  
    """Consulta Cédulas del CNE Venezuela

    Args:
        other_url (str, optional): URL del CNE para consultar, (Utils cuando hay elecciones). Defaults to None.
    """ 
    
    URL = "http://www.cne.gob.ve/web/registro_electoral/ce.php" # URL BASE DEL CNE
    
    payload = {
        "nacionalidad": "",
        "cedula": ""
    }
    
    _dictionary: dict = {
        "NOT_RESPONSE": "Servidor No Responde",
        "OBJECTION": "Esta cédula de identidad presenta una objeción por lo que no podrá ejercer su derecho al voto",
        "OBJECTION_PATTERS": r"Objeción:(.*?)Descripción",
        "NOT_REGISTER": "Esta cédula de identidad no se encuentra inscrito en el Registro Electoral",
        "NOT_EXISTS": "Esta cédula de identidad no se encuentra inscrita en el Registro Electoral"
    }
    
    def __init__(self, other_url: str = None):
        """Inicializa las consultas de cédulas del CNE Venezuela

        Args:
            other_url (str, optional): URL del CNE para consultar, (Utils cuando hay elecciones). Defaults to None.
        """
        if other_url:
            self.URL = other_url
    
    def set_dict(self, data) -> None:
        self._dictionary.update(data)
        
    def get_dict(self) -> dict:
        return self._dictionary
    
    @property
    def result(self) -> ResponseData:
        return self._result
    
    def as_dict(self) -> dict:
        return asdict(self._result)
    
    def query(self, nat: str, dni: str|int) -> ResponseData:
        """Consulta del CNE

        Args:
            nat (str): Nacionalidad por defecto es "V"
            dni (str | int): Cédula de Identidad a consultar

        Returns:
            ResponseData: Retoran una clase `ResponseData` con los datos optenidos
        """
        nat = self._format_nationaly(nat)
        self.payload['nacionalidad'] = nat
        self.payload['cedula'] = dni
        self._result = ResponseData(f"{nat}-{str(dni)}", STATUS.NO_RESPONSE)
        
        try:
            r = requests.get(self.URL, params=self.payload)
        except:
           raise ConnectionError(self.err(0))
       
        if r.status_code == 200:
            content = self._parse_html(r.content)
            s = self._valid_content(content)
            if s:
                self._result = ResponseData(f"{nat}-{str(dni)}", s)
            else:
                self._result = self._parse_text(content)
            
        return self._result
        
    def _valid_content(self, content: str) -> int|bool:
        if self._dictionary['NOT_REGISTER'] in content:
            return STATUS.NOT_REGISTERED
        elif self._dictionary['NOT_EXISTS'] in content:
            return STATUS.NOT_EXISTS
        elif self._dictionary['OBJECTION'] in content:
            matchs = re.search(self._dictionary['OBJECTION_PATTERS'], content)
            if matchs:
                c: str = matchs.group(1).strip()
                o = re.sub(r"\(\d\)+","", c).title().strip()
                if o == "Fallecido":
                    return STATUS.DECEASED
                else:
                    return STATUS.DISABLED
        return False
                
        
    def _format_nationaly(self, nat: str) -> str:
        if nat:
            nat = nat.upper()
            if nat == "E":
                return "E"
        return "V"
    
    def _parse_html(self, content: str) -> str:
        soup = BeautifulSoup(content, 'html.parser')
        return self._clear_text(soup.get_text())
        
    def _clear_text(self, text : str) -> str:
        if text:
            text = text.replace("\n", " ")
            text = " ".join(text.split())
        return text

    def _parse_text(self, content: str) -> ResponseData:
        patterns = ['Cédula:', 'Nombre:', 'Estado:', 'Municipio:', 'Parroquia:', 'Centro:', 'Dirección:', 'Registro Electoral', 'Impresión de Consulta de Datos', 'SERVICIO ELECTORAL', 'Registro ElectoralCorte']
        for pattern in patterns:
            content = content.replace(pattern, '|')
        
        content = content.strip()
        response = [re.sub(r'\s+', ' ', val.strip()) for val in content.split('|')]
        return ResponseData(
            response[1],
            STATUS.REGISTERED,
            response[2],
            response[6],
            response[3],
            response[4],
            response[5],
            response[7]
        )

    def err(self, err_code: int) -> str:
        return {
            0: f"[PYELECTORAL] No se puede establecer conexión con el servidor CNE.org [{self.payload['nacionalidad']}-{self.payload['cedula']}]",
            1: "[PYELECTORAL] Datos Invalidos",
            2: "[PYELECTORAL] Los parametros de la consulta no pueden estar vacios"
        }.get(err_code, "")
        
class as_collection:
    """Consulta una lista de cedulas del CNE
    Args:
        data (list): Lista de cedulas en formato ['V-00000000']
        outher_uri: (str) URL Opcional. Defaults None
        with_tqdm (bool) Indica se se añade una barra de progreso en terminal. Tenga en cuenta que debe tener instalado tqdm. Defaults to False
    """
    def __init__(self, data: list, outher_uri : str = None, with_tqdm : bool = False):
        """Inicializa la consulta de cedulas de la lista

        Args:
            data (list): lista de cédulas
            outher_uri (str, optional): URL opcional. Defaults to None.
            with_tqdm (bool) Indica se se añade una barra de progreso en terminal, Defaults to False
        """
        self.errors: list = []
        self.results: list = []
        self._cne = CNE(other_url=outher_uri)
        self._process(data, with_tqdm)
            
    def _process(self, data: list, with_tqdm=False) -> None:
        if data == []:
            raise Exception(self._cne.err(2))
        
        if with_tqdm:
            try:
                from tqdm import tqdm
                for i in tqdm(data, desc="PyElector Progress: ", ascii=True, colour="#E53935"):
                    try:
                        nal, dni = i.split("-")
                        resultconsult = self._cne.query(nal, int(dni))
                        self.results.append(resultconsult)
                    except ConnectionError:
                        raise
                    except:
                        self.errors.append(i)                
            except ImportError:
                raise
        else:
            for i in data:
                try:
                    nal, dni = i.split("-")
                    resultconsult = self._cne.query(nal, int(dni))
                    self.results.append(resultconsult)
                except ConnectionError:
                    raise
                except:
                    self.errors.append(i)
                
    def all(self) -> list:
        """Retorna todos los resultados de la busquedad

        Returns:
            List[ResponseData]: Lista de Datos de respuestas
        """
        return self.results
    
    def get(self, ix : int) -> ResponseData|bool:
        """Obtiene un resultado por su indice

        Args:
            ix (int): EL indice

        Returns:
            ResponseData: Respuesta del Indice o False si no hay resultados
        """
        if 0 <= ix < len(self.results):
            return self.results[ix]
        return False