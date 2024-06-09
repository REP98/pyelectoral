#! /usr/bin/env python3
#  -*- coding: utf-8 -*-
"""MODULO DATA"""   
import re
from dataclasses import dataclass
from enum import Enum, verify, UNIQUE

@verify(UNIQUE)
class STATUS(Enum):
    """STATUS Colección de estados de la consulta CNE
    """
    NOT_REGISTERED = 900
    NOT_EXISTS = 950
    REGISTERED = 100
    DECEASED = 120
    DISABLED = 130
    NO_RESPONSE = 500
    EXTRANGERO = 170
    
    @classmethod
    def get_text(self, value: int) -> str:
        """Genera una version de Texto del Estado

        Args:
            value (int): Estatus actual

        Returns:
            str: Significado del Estatus
        """
        return {
            self.NOT_REGISTERED.value: "Cédula no inscrita",
            self.REGISTERED.value: "Inscrito",
            self.DECEASED.value: "Fallecido",
            self.DISABLED.value: "Inhabilitado",
            self.EXTRANGERO.value: "Fuera del País",
            self.NOT_EXISTS.value: "Cédula No existe"
        }.get(value, "Sin Respuesta")
        
    @classmethod
    def __str__(self):
        return self.get_text(self.value)

@dataclass
class ResponseData:
    """Datos de Respuesta del CNE
    
    Esta Clase se usa para almacenar las respuestas y resultados del la clase CNE, a fin de poder validar y usar según convenga
    """
    cedula: str
    status: int = 500
    nombre_apellido: str = None
    centro: str = None
    estado: str = None
    municipio: str = None
    parroquia: str = None
    direccion: str = None
    
    def __post_init__(self):
        if isinstance(self.status, STATUS):
            self.status = self.status.value
        if self.cedula:
            self.cedula = self.cedula.upper()
        if self.nombre_apellido:
            self.nombre_apellido = self.nombre_apellido.title()
        if self.centro:
            self.centro = self.centro.title()
        if self.direccion:
            self.direccion = self.direccion.title()
        if self.estado:
            self.estado = self.estado.title()
        if self.municipio:
            self.municipio = self.municipio.title()
        if self.parroquia:
            self.parroquia = self.parroquia.title()
            
    @property
    def status_text(self):
        """Texto del Estado actual"""
        return STATUS.get_text(self.status)

class UTILS:
    """UTILIDADES de PyElector
    """
    @staticmethod
    def format_dni(dni: str|int) -> dict:
        """Transforma la cedula en un diccionario valido
        
        Ejemplo:
        --------
        >>> UTILS.format_dni("V-12000000")
            {'nacionalidad': 'V', 'cedula': '12000000'}
        >>> UTILS.format_dni(12000000)
            {'nacionalidad': 'V', 'cedula': '12000000'}
        >>> UTILS.format_dni("E-12.000.000")
            {'nacionalidad': 'V', 'cedula': '12000000'}

        Args:
            dni (str | int): la cédula a formatear

        Returns:
            dict: un dicionario con la nacionalidad y la cédula formateada
        """
        data = {}
        
        if isinstance(dni, int):            
            data: dict[str, str] = { "nacionalidad": "V", "cedula": str(dni) }
            
        elif isinstance(dni, str):
            if "-" in dni:
                return UTILS.separate_dni(dni)
            
            dni = ''.join(char for char in dni if char.isalnum())
            
            if not "v" in dni.lower() and not "e" in dni.lower():
                data['cedula'] = str(dni)
                data["nacionalidad"] = "V"
            else:
                data['cedula'] = dni[1:]
                
            if "e" in dni.lower():
                data["nacionalidad"] = "E"
            else:
                data["nacionalidad"] = "V"
                
        return data
    
    @staticmethod
    def separate_dni(dni: str) -> dict:
        """Separador de Cédulas por guión

        Args:
            dni (str): cedula a separar

        Returns:
            dict: diccionario de nacionalidad y cédulas separadas
        """
        s: list = re.split(r'-', dni)
        return {
            "nacionalidad": str(s[0]).upper(),
            "cedula": int(''.join(d for d in str(s[1]) if d.isdigit()))
        }
        
    @staticmethod
    def format_dni_to_str(dnis: str | int) -> str:
        d: dict = UTILS.format_dni(dnis)
        return f"{d["nacionalidad"]}-{str(d['cedula'])}"
    
    @staticmethod
    def clear_none(data: list) -> list:
        newdata = []
        for d in data:
            if d:
                newdata.append(d)
        return newdata