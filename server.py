import json
from urllib.parse import unquote
from collections import Counter

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import pandas
from pandas import read_excel

app = FastAPI()




def get_df(file_name, locale="rus"):
  sheet_name = "form_result_list"
  if locale == "eng":
    sheet_name += "_eng"
  df = read_excel(file_name, sheet_name = sheet_name)
  df.drop(df.columns[18], axis=1, inplace=True)
  if locale == "eng":
      df.columns =  [  'Дата', 'Возраст', 'Пол', 'Образование',
        'Семейное положение', 'Есть ли дети',
        'Путешествуют ли с вами дети', 'Доход',
        'Регион', 'Транспорт',
        'Вы приезжали в Мурманскую область с целью (выбрать главную цель)',
        'Длительность поездки',
        'С кем Вы путешествуете?',
        'Размещение',
        'Устроил ли Вас уровень комфорта',
        'Как часто Вы бываете у нас',
        'Сколько денег потратили на 1 чел сутки',
        'Понравилось ли Вам у нас',
        'Что Вам больше всего понравилось и запомнилось в Мурманской области?',
        'Что вам не понравилось?',
        'Что для вас важно?',
        'Где Вы узнали об отдыхе в Мурманской области',
        'Какими соц.сетями пользуетесь?',
        'Какую из достопримечательностей Мурманской области Вы считаете ее главным символом?',
        'Пользовались ли Вы во время пребывания услугами гидов, экскурсоводов',
        'Обращались ли Вы за консультацией в туристический информационный центр?',
        'Время года',
        'Есть ли у Вас пожелания представителям турбизнеса области?']
  else:
      df.columns = [  'Дата', 'Возраст', 'Пол', 'Образование',
        'Семейное положение', 'Есть ли дети',
        'Путешествуют ли с вами дети', 'Доход',
        'Регион', 'Транспорт',
        'Вы приезжали в Мурманскую область с целью (выбрать главную цель)',
        'Длительность поездки',
        'С кем Вы путешествуете?',
        'Размещение',
        'Устроил ли Вас уровень комфорта',
        'Как часто Вы бываете у нас',
        'Сколько денег потратили на 1 чел сутки',
        'Понравилось ли Вам у нас',
        'Что Вам больше всего понравилось и запомнилось в Мурманской области?',
        'Что вам не понравилось?',
        'Что для вас важно?',
        'Где Вы узнали об отдыхе в Мурманской области',
        'Какими соц.сетями пользуетесь?',
        'Какую из достопримечательностей Мурманской области Вы считаете ее главным символом?',
        'Пользовались ли Вы во время пребывания услугами гидов, экскурсоводов',
        'Обращались ли Вы за консультацией в туристический информационный центр?',
        'Время года',
        'Хотели бы Вы еще раз вернуться в Мурманскую область и порекомендовать ее своим друзьям?',
        'Есть ли у Вас пожелания представителям турбизнеса области?']
  df.dropna(axis=0, how='all')
  return df.copy()

df_rus = get_df("datafile_rus.xls")
df_eng = get_df("datafile_eng.xls", locale="eng")

def count_other(data):
  # in place
  count = 0
  keys = list(data.keys())
  for key in keys:
    if not key.startswith("["):
      count += data.pop(key)
  if count:
    data["[Другое]"] = count

def apply_filter(df, params):
  result = df.copy()
  for k, v in params.items():
    result = result[result[k] == v]
  return result


def apply_filter(df, params):
  result = df.copy()
  for k, v in params.items():
    result = result[result[k] == v]
  return result

def get_datalist(columns, locale, params=None):
  df = df_rus if locale == "rus" else df_eng

  if params:
    filterd_df = apply_filter(df, params)
  else:
    filterd_df = df
  datalist = []

  datalist = []
  for col in columns:
    data = Counter(dict(filterd_df[col].value_counts()))
    count_other(data)
    datalist.append({"name": col, "data": data, "keys": ["-",*list(data.keys())]})
  return datalist

class NumpyIntSerializer(json.JSONEncoder):
  def default(self, u):
      if u.__class__.__name__ == "int64":
        return int(u)
      return u.__dict__


def unquote_query_params(params):
  par = {}
  for k, v in params.items():
    par[unquote(k)] = unquote(v)
  return par

naive_cache = {}


def get_unqiue_key(params):
  params_keys = list(params.keys())
  params_keys = sorted(params_keys)
  unqiue_key = ""
  for key in params_keys:
    unqiue_key += params[key]

  return unqiue_key


portrait_columns = ["Пол", "Возраст", "Доход", "Семейное положение", "Есть ли дети", "Путешествуют ли с вами дети", "Время года", "Длительность поездки"]
portrait_filters = ["Время года", "Пол", "Возраст", "Семейное положение", "Есть ли дети",]

import pprint

@app.get("/portrait/{language}")
async def root(r: Request, language: str):
  params = unquote_query_params(r.query_params)
  datalist = get_datalist(portrait_columns, language, params)
  pprint.pprint(datalist)
  response = NumpyIntSerializer().encode(datalist)


  return JSONResponse(content=json.loads(response), headers={"Access-Control-Allow-Origin": "*"})

satisfaction_columns = ["Время года", 'Сколько денег потратили на 1 чел сутки','Регион', 'Транспорт', 'Размещение', 'Устроил ли Вас уровень комфорта', 'Как часто Вы бываете у нас', 'Какими соц.сетями пользуетесь?', 'Что для вас важно?', 'Понравилось ли Вам у нас', 'Что вам не понравилось?', "Длительность поездки"]
satisfaction_filters = ["Время года", 'Транспорт', "Длительность поездки",'Регион', 'Понравилось ли Вам у нас',]

@app.get("/satisfaction/{language}")
async def root(r: Request, language: str):
  params = unquote_query_params(r.query_params)

  response = NumpyIntSerializer().encode(get_datalist(satisfaction_columns, language, params))


  return JSONResponse(content=json.loads(response), headers={"Access-Control-Allow-Origin": "*"})