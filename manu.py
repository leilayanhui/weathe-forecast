# -*- coding:utf-8 -*-

weather = {}
his_list = []


def make_dict():
    filename = 'weather_info.txt'
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            k, v = line.strip().split(',')
            weather[k] = v
        return weather


def query(city):
    '''查询天气情况'''
    weather_data = make_dict()
    if city in weather_data:
        result = city + ", " + weather_data[city] + '\n'
        his_list.append(result)
        return result
    else:
        return "抱歉，找不到该城市。\n"


def manu():
    '''使用程序的帮助说明'''
    return """
    • 输入城市名拼音「shanghai」，回车或点击「查询」获得天气情况；
    • 输入城市名，空格，天晴情况「shanghai 晴」，可修改该城市当天天气情况；
    • 点击「帮助」获得帮助信息；
    • 点击「历史」获得历史查询信息。
"""



def record(his_list):
    '''生成查询记录'''
    if len(his_list) != 0:
        print ("\n-------------- 历史查询 --------------\n")
        for i in set(his_list):
            print (i)
        print ("-" * 38 + "\n")
    else:
        print ("无查询记录\n")


def main():
    while True:
        city = input("输入城市或「帮助」: ")
        if city == "h" or city == "help" or "帮助" in city:
            print (manu())

        elif city == "history" or city == "历史":
            record()

        elif city == "quit" or city == "q" or city == "exit":
            break

        else:
            print (query(city))

if __name__ == '__main__':
    main()
