# -*- coding:utf-8 -*-

import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime, date, timedelta
from const_opm import API_DAILY, API_FORE, APPID, LANG, UNITS
from manu import manu, record


db = SQLAlchemy()
his_list = []


class OpmDaily(db.Model):
    __tablename__ = 'weather_origin'
    __table_args__ = (db.UniqueConstraint('location', 'timestamp'), None)

    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(80))
    timestamp = db.Column(db.Integer)
    weather = db.Column(db.String(10))
    icon = db.Column(db.String(5))
    temp_max_c = db.Column(db.Float)
    temp_min_c = db.Column(db.Float)
    wind_deg = db.Column(db.Float)
    humidity = db.Column(db.Integer)
    pressure = db.Column(db.Float)
    dt = db.Column(db.String(12))
    wind_str = db.Column(db.String(10))


    def __init__(self, location, timestamp, weather, icon, temp_max_c, temp_min_c, wind_deg, humidity, pressure, dt, wind_str):
        self.location = location
        self.timestamp = timestamp
        self.weather = weather
        self.icon = icon
        self.temp_max_c = temp_max_c
        self.temp_min_c = temp_min_c
        self.wind_deg = wind_deg
        self.humidity = humidity
        self.pressure = pressure
        self.dt = dt
        self.wind_str = wind_str

    def __repr__(self):
        return "{0},{1},{2},{3},{4},{5},{6},{7},{8}".format(self.location, self.dt,
                                                        self.weather,
                                                        self.icon,
                                                        self.temp_max_c,
                                                        self.temp_min_c,
                                                        self.wind_str,
                                                        self.humidity,
                                                        self.pressure)


def fetch_opm(location):
    """Get response from opm 16days daily forecast."""
    payload = dict(q=location, APPID=APPID, lang=LANG, units='metric')
    r = requests.get(API_DAILY, params=payload, timeout=20)
    return r


def deg_compass(num):
    val = int((num/22.5) + .5)
    arr = ["N","NNE","NE","ENE","E","ESE", "SE", "SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
    cn = dict(N='北', NNE='北',
              NE='东北', ENE='东北',
              E='东', ESE='东',
              SE='东南', SSE='东南',
              S='南', SSW='南',
              SW='西南', WSW='西南',
              W='西', WNW='西',
              NW='西北', NNW='西北')
    deg = arr[(val % 16)]
#    print(arr[(val % 16)])
#    print(cn[deg])
    return(cn[deg])



def read_db(response, n):
    """Extract the database from the response."""
    data = response.json()

    city = data['city']['name']
#    date = datetime.utcfromtimestamp(data['list'][0]['dt']).strftime('%Y-%m-%d')
    timestamp = data['list'][n]['dt']
    weather = data['list'][n]['weather'][0]['description']
    icon = data['list'][n]['weather'][0]['icon']
    temp_max = data['list'][n]['temp']['max']
    temp_min = data['list'][n]['temp']['min']
    wind_deg = data['list'][n]['deg']
    humidity = data['list'][n]['humidity']
    pressure = data['list'][n]['pressure']
    dt = datetime.utcfromtimestamp(timestamp).strftime("%m-%d")
    wind_str = deg_compass(wind_deg)

    results = (city, timestamp, weather, icon, temp_max, temp_min,
               wind_deg, humidity, pressure, dt, wind_str)
    return results


def insert_db(location):
    """Insert the values into the table weather_origin"""
    r = fetch_opm(location)

    if r.status_code == 200:
        dt_in_db = db.session.query(OpmDaily.timestamp).\
                              filter_by(location='{}'.format(location)).all()
#        print (dt_in_db)
        for i in range(7):
            result = read_db(r, i)
            dt_req = read_db(r, i)[1]
#            print(dt_req)
            if (dt_req,) in dt_in_db:
#                print ("have")
                continue
            record = OpmDaily(location=result[0],
                              timestamp=result[1],
                              weather=result[2],
                              icon=result[3],
                              temp_max_c=result[4],
                              temp_min_c=result[5],
                              wind_deg=result[6],
                              humidity=result[7],
                              pressure=result[8],
                              dt=result[9],
                              wind_str=result[10])
#                print (record)
            db.session.add(record)
        db.session.commit()

    else:
        return (r.status_code, "请查看帮助文档")


def extract_db(location):
    """Extract values from db, turn it into string."""
#    c.execute('''SELECT * from weather_origin where location=? order by dt desc''', (location,))
#    r = c.fetchall()[:7]
#    r_dict = {}

    r = db.session.query(OpmDaily).\
                     filter_by(location='{}'.format(location)).\
                     order_by(desc(OpmDaily.timestamp)).all()[:7]
    r.reverse()

    return r


def delta_db(location):
#    c.execute("SELECT dt from weather_origin where location=? ORDER BY dt DESC", \
#              (location,))
#    dt_r = c.fetchone()

    ts_r = db.session.query(OpmDaily.timestamp).\
                   filter_by(location='{}'.format(location)).\
                   order_by(desc(OpmDaily.dt)).first()
#    print(ts_r[0])
    last_day = datetime.utcfromtimestamp(ts_r[0])
    today = datetime.today()
#    print(type(last_day))
#    print(type(today))
#    print(last_day - today)
    return last_day - today


def modify_weat(location, weather):
    today = datetime.utcnow().strftime("%m-%d")
    weat_list = ["晴","多云","晴间多云","阴","阵雨","雷阵雨","冰雹","小雨","中雨",\
                 "大雨","暴雨","大暴雨","特大暴雨","冻雨","雨夹雪","阵雪","小雪",\
                 "中雪","大雪","暴雪","浮尘","扬沙","沙尘暴","强沙尘暴",'雾',"霾",\
                 "风","大风","飓风","热带风暴","龙卷风","冷","热","雨"]
    if weather in weat_list:
       for row in db.session.query(OpmDaily).\
                             filter(OpmDaily.location=='{}'.format(location)).\
                             filter(OpmDaily.dt=='{}'.format(today)).all():
#        print(row)
#        print(row.weather)
            row.weather = weather
#        print(row)
            db.session.add(row)
#        print(db.session.dirty)
            db.session.commit()
            return ("更新成功")
    else:
        return ("输入格式不正确。「上海 晴」以空格分隔。")


def query_his(location):
    query_list = []
    for row in extract_db(location):
        location=row.location
        dt=row.dt
        weather=row.weather
        temp_max_c=row.temp_max_c
        temp_min_c=row.temp_min_c
        wind_str=row.wind_str
        humidity=row.humidity
        pressure=row.pressure

        text = """{0}，{1}，{2} ~ {3}℃，{4}风\n""".format(dt,
                                                               weather,
                                                               temp_max_c,
                                                               temp_min_c,
                                                               wind_str)
        query_list.append(text)
    result = location, tuple(query_list)
    his_list.append(result)


def main(location):
    loc_in_db = db.session.query(OpmDaily.location).\
                     filter_by(location='{}'.format(location)).all()

    if (location,) in loc_in_db:
        if delta_db(location) > timedelta(days=5):
#            return extract_db(location)
           print('old')
           for row in extract_db(location):
               print(row)
           query_his(location)
           return extract_db(location)
        else:
            print('update')
            insert_db(location)
            for row in extract_db(location):
                print(row)
            query_his(location)
            return extract_db(location)

    else:
        insert_db(location)
        for row in extract_db(location):
            print(row)
        query_his(location)
        return extract_db(location)


if __name__ == "__main__":
    user_enter=input("> ")
    main(user_enter)