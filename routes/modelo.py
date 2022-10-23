from fastapi import APIRouter, File, UploadFile
import pickle
import pandas as pd
from starlette.responses import JSONResponse
import sys
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

modelo = APIRouter()

@modelo.post("/identificador")
def read_something(code: str):
    with open('./files/modelo_entrenado.pkl', 'rb') as f:
        modelo = pickle.load(f)
    #Lectura de archivos
    df_clientes = pd.read_csv("./files/Clientes_Descriptivo.txt", sep="	")
    df_transacciones = pd.read_csv("./files/Transacciones_Clientes.txt", sep="	")
    df_giros = pd.read_csv("./files/Catalogo_Giros.txt", sep="	")
    df_prueba=df_clientes.merge(df_transacciones, on="NU_CTE_COD", how="left")
    df_datos=df_prueba.merge(df_giros, on="NU_AFILIACION", how="right")
    #Se obtiene el historial de esa persona
    df_datos=df_datos.loc[df_datos.loc[:, 'NU_CTE_COD'] == code]
    # Eliminando variables que no están relacionadas al objetivo
    df_datos.drop(columns=["CD_ESTADO","CD_POSTAL","CD_GIRO","IM_TRANSACCION","TIPO_TARJETA","NU_AFILIACION"], axis = 1, inplace=True)
    #Obtener Mes de la operacion
    df_datos["MES"]=df_datos['FH_CORTE'].apply(lambda x: x[3:5])
    df_datos.drop(columns=["FH_CORTE","FH_OPERACION"], axis = 1, inplace=True)
    #Se crea una nueva variable, para saber si ha perdido la huella o no
    #En el estudio se observó que la edad mínima en la que se desvanece la huella dactilar es a los 63 años en el caso de las mujeres, y a los 66, en los hombres
    df_datos["SIN_HUELLA"]=((df_datos["CD_SEXO"]=="F") & (df_datos["EDAD"]>=63)) | ((df_datos["CD_SEXO"]=="M") & (df_datos["EDAD"]>=66))
    df_datos["SIN_HUELLA"]=df_datos["SIN_HUELLA"].map({False: 0, True: 1})
    df_datos["SIN_HUELLA"].unique()
    #Se elimina la columna de la edad y sexo
    df_datos.drop(columns=["EDAD","CD_SEXO"], axis = 1, inplace=True)

    #Creación de nuevas columnas
    df_datos['FARMACIA']=0
    df_datos['HOSPITALES']=0
    df_datos['MEDICOS Y DENTISTAS']=0
    df_datos['OTROS']=0

    farmacia=df_datos.loc[df_datos["NB_GIRO"]=="FARMACIAS"]
    farmacia2=farmacia.groupby(["NU_CTE_COD"]).count()
    hospitales=df_datos.loc[df_datos["NB_GIRO"]=="HOSPITALES"]
    hospitales2=hospitales.groupby(["NU_CTE_COD"]).count()
    medicos=df_datos.loc[df_datos["NB_GIRO"]=="MEDICOS Y DENTISTAS"]
    medicos2=medicos.groupby(["NU_CTE_COD"]).count()
    otros=df_datos.loc[df_datos["NB_GIRO"]=="OTROS"]
    otros2=otros.groupby(["NU_CTE_COD"]).count()

    ids=df_datos['NU_CTE_COD'].unique()
    for i in ids:
        try:
            df_datos['FARMACIA'].loc[df_datos.loc[:, 'NU_CTE_COD'] == i]=farmacia2.loc[i][0]
        except KeyError:
            pass
        try:
            df_datos['HOSPITALES'].loc[df_datos.loc[:, 'NU_CTE_COD'] == i]=hospitales2.loc[i][0]
        except KeyError:
            pass
        try:
            df_datos['MEDICOS Y DENTISTAS'].loc[df_datos.loc[:, 'NU_CTE_COD'] == i]=medicos2.loc[i][0]
        except KeyError:
            pass
        try:
            df_datos['OTROS'].loc[df_datos.loc[:, 'NU_CTE_COD'] == i]=otros2.loc[i][0]
        except KeyError:
            pass
    
    #Se elimina las columnas
    df_datos.drop(columns=["NB_GIRO","NB_SUBGIRO","MES","NU_CTE_COD"], axis = 1, inplace=True)
    #Predicción del modelo
    df = pd.DataFrame(df_datos.iloc[0]).transpose()
    resultado=modelo.predict(df)
    if resultado[0]==0:
        result=False
    else:
        result=True
    return JSONResponse(content={"response":result})