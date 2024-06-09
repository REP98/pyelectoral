#! /usr/bin/env python3
#  -*- coding: utf-8 -*-
"""MODULO PARSE"""
import os
from .Data import ResponseData, UTILS

# TXT
class TXT:
    """Toma Archivos TXT o genera uno para su posterior uso

    Raises:
        FileExistsError: Generado si existe o no un archivo según su acción
    """
    @staticmethod
    def to_txt(data: list, filename: str, dirname: str):
        """Escribe un archivo TXT de los resultados datos

        Args:
            data (list): Lista de Resultados del CNE a escribir
            filename (str): Nombre del Archivo a escribir
            dirname (str): Dirección donde se alamacenara el archivo

        Raises:
            FileExistsError: Si la dirección no es una carpeta Valida
        """
        if not os.path.exists(dirname):
            raise FileExistsError(f"El Directorio {dirname} no existe")
        
        with open(os.path.join(dirname, filename + ".txt"), mode="w", encoding="UTF-8") as file:
            for v in data:
                file.write(f"cedula={v.cedula}, status={str(v.status)}, status_text={v.status_text}, nombre y apellido={v.nombre_apellido}, centro={v.centro}, estado={v.estado}, municipio={v.municipio}, parroquia={v.parroquia}, direccion={v.direccion}\n")
    
    @staticmethod
    def of_txt(filename: str, with_header: bool = True) -> list:
        """Transforma un arcivo TXT a una lista de Cedulas validas para su uso

        EL archivo debe ser:
        
        ```plaintext
        V-12000000
        V-12000000
        V-12000000
        ```
        ó 
        ```plaintext
        Cédulas:
        V-12000000
        E-12000000
        V-12000000
        ```
        
        
        Args:
            filename (str): nombre del archivo
            with_header (bool, optional): Indica si el archivo tiene cabezera en la linea 1. Defaults to True.

        Raises:
            FileNotFoundError: Si el archivo no existe

        Returns:
            list: Lista de Cedulas preparadas para integrar a `pyElectoral.CNE.as_collection`
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(f"El Archivo {filename} no existe")
        
        data: list = []
        
        with open(filename, mode="r", encoding="UTF-8") as file:
            lineas = file.readlines()
            
            if with_header:
                lineas: list = lineas[1:]
                
            for linea in lineas:
                data.append(UTILS.format_dni_to_str(linea.strip()))
                
        return data
# CSV
import csv
from dataclasses import astuple

class File_CSV:
    """Lee o Genera un CSV"""
    @staticmethod
    def write(data: list, filename: str, dirname: str) -> None:
        """Escrive un  CSV

        Args:
            data (list): lista de datos a escribir
            filename (str): Nombre del Archivo CSV
            dirname (str): Dirección del archivo

        Raises:
            FileExistsError: Si el Directorio no existe
        """
        if not os.path.exists(dirname):
            raise FileExistsError(f"El directorio {dirname} no existe.")
        
        if isinstance(data[0], ResponseData):
            da = []
            for d in data:
                da.append(astuple(d))
            data = da
            
        headers = ["Cédula", "Cod.", "Nombre y Apellido", "Centro", "Estado", "Municipio", "Parroquia", "Dirección"]
        
        with open(os.path.join(dirname, filename + ".csv"), mode="w", encoding="UTF-8", newline="") as file:
            fw = csv.writer(file)
            fw.writerow(headers)
            fw.writerows(data)
    @staticmethod
    def read(filename: str, delimiter: str = ",") -> list:
        """Lee un CSV para su uso y conversion a List
        
        El CSV:
        cedula
        V-12000000
        V-00000000
        
        Tambien puede ser:
        nacionalidad,cedula
        V,12000000
        V,00000000  

        Args:
            filename (str): Nombre del CSV
            delimiter (str, optional): Delimitador del CSV. Defaults to ",".

        Raises:
            FileNotFoundError: Si el Archivo no existe

        Returns:
            list: Lista del CSV
        """
        data = []
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Archivo {filename} no encontrado")
        
        with open(filename, mode="r", encoding="UTF-8") as file:
            reader = csv.DictReader(file, delimiter= delimiter)
            for col in reader:
                if len(col) > 1:
                    k: tuple = tuple(col.keys())
                    data.append(f"{col[k[0]]}-{str(''.join(d for d in str(col[k[1]]) if d.isdigit()))}")
                else:
                    k: str = tuple(col.keys())[0]
                    data.append(UTILS.format_dni_to_str(col[k]))
        return data

# XLSL

class Excel:
    """Manejador de archivos Excel
    
        Dependencies:
            openpyxl: Necesario para Su ejecución
        
        Raises:
            ImportError: Si `openpyxl` no existe
    """
    def __init__(self):
        """ Inicializador de la clase
        """
        try:
            import openpyxl # type: ignore
            self.wb = openpyxl.Workbook
            self.lwb = openpyxl.load_workbook
        except ImportError:
            raise ImportError("El paquete openpyxl no esta disponible para la clase Excel")
    
    def write(self, data: list, filename: str, dirname: str) -> None:
        """Escribe un Excel de una lista de Respuesta de Datos del CNE

        Args:
            data (list): lista de datos de respuesta del CNE
            filename (str): Nombre del Archivo
            dirname (str): Directorio donde almacenar el archivo

        Raises:
            FileExistsError: Si el directorio no existe

        """
        if not os.path.exists(dirname):
            raise FileExistsError(f"La dirección {dirname} no existe")

        wb = self.wb()
        sheet = wb.active
        sheet.title = "hoja"
        sheet.append(("Cédula", "Cod.", "Nombre y Apellido", "Centro", "Estado", "Municipio", "Parroquia", "Dirección"))
        for d in data:
            res = astuple(d)
            sheet.append(res)
        wb.save(os.path.join(dirname, filename + ".xlsx"))


    def read(self,filename: str) -> list:
        """Lee un archivo XLSX 
    
        El Excel puede contener:
        nacionalidad,cedula
        V 12000000
        V 12000000
        
        ó
        
        cedulas:
        cedulas
        V-12000000
        V12000000

        Args:
            filename (str): Ruta y Nombre del Archivo

        Raises:
            FileNotFoundError: Si el Archivo no existe

        Returns:
            list: Lista de Datos Obtenidos del XLSX
        
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(f"El archivo {filename} no existe")
        
        wb = self.lwb(filename, data_only=True) 
        sheet = wb.active
        header_row = sheet[1]
        data_list = []

        for row in sheet.iter_rows(min_row=2, max_col=17):
            values: list = [cell.value for cell in row if cell is not None]
            values: list = UTILS.clear_none(values)
                
            if len(values) > 1:
                ci: str = ''.join(c for c in str(values[1]) if c.isdigit())
                data_list.append(f"{values[0]}-{ci}")
            else:
                data_list.append(UTILS.format_dni_to_str(str(values[0])))

        return data_list

# JSON

import json 
from dataclasses import asdict

class Jfile:
    """Manejador de Archivos JSON"""
    @staticmethod
    def write(data: list, filename: str, dirname) -> None:
        """Permite generar un archivo .json
        
        Args:
            data (list): Lista de datos de resultados del CNE
            filename (str): Nombre el archivo a generar sin extención
            dirname (str): Ruta donde guardar el archivo

        Raises:
            FileExistsError: Si el directorio no existe
        """
        if not os.path.exists(dirname):
            raise FileExistsError(f"La dirección {dirname} no existe")
        da: list = [asdict(row) for row in data]
        with open(os.path.join(dirname, filename + ".json"), mode='w', encoding="utf-8") as file:
            json.dump(da, file, ensure_ascii=False, indent=4) 


    @staticmethod
    def read(filename: str) -> list:
        """Lee un Json y lo trasforma en dict
        
        Args:
            filename (str): Ruta y nombre del Json a Leer

        Raises:
            FileNotFoundError: Si el archivo no existe

        Returns:
            list: Lista de datos obtenidos
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(f"El archivo {filename} no existe")
        
        data: list = []
        with open(filename, mode="r", encoding="UTF-8") as json_file:
            data = json.load(json_file)

        if data and len(data) > 0:
            result: list = []
            for n in data:
                ci = str(''.join(c for c in str(n['cedula']) if c.isdigit()))
                result.append(f"{n['nacionalidad'].upper()}-{ci}")
            return result
        return data


# Generado Python
class PyFile:
    """Generador de Archivos Python"""
    @staticmethod
    def write(data: list, filename: str, dirname: str) -> None:
        """Genera un Archivo python valido para su posterior uso

        Args:
            data (list): Lista de datos ResponseData obtenidos del CNE
            filename (str): Nombre del Archivo .py sin extensión
            dirname (str): Directorio donde generar el modulo Python

        Raises:
            FileExistsError: Si el directorio No existe
        """
        if not os.path.exists(dirname):
            raise FileExistsError(f"La dirección {dirname} no existe")
        
        filepath: str = os.path.join(dirname, filename + ".py")
        with open(filepath, mode="w", encoding="utf-8") as file:
            file.write(f"#! /usr/bin/env python3\n#  -*- coding: utf-8 -*-\n")
            file.write(f"# GENERADO POR PyElector\n\n")
            file.write(f"from pyElectoral import ResponseData\n\n")
            file.write(f"DATA: list = [\n")
            for i in data:
                file.write(f"   {str(i)}, \n")
            file.write(f"]\n")