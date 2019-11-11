import os
import iso8601
import datetime
import numpy as np
import okex.spot_api as spot


def get_day_date():
    return datetime.datetime.now().date()


def server_time():
    date = get_day_date()                                     # 得到当前日期
    date_time = iso8601.parse_date(str(date))                 # 解析日期为iso8601格式
    unix = date_time.timestamp()                              # 转换为Unix格式
    server_end = date_time.utcfromtimestamp(unix - 28800)     # 减8小时得到格林尼治时间
    server_start = date_time.utcfromtimestamp(unix - 115200)  # 减32小时得到格林尼治时间

    # 格式化为服务器认可的ISO8601时间格式
    server_start_time = server_start.isoformat(timespec='milliseconds') + 'Z'
    server_end_time = server_end.isoformat(timespec='milliseconds') + 'Z'

    return server_start_time, server_end_time


def get_moduel_path(file_name):
    module_path = os.path.dirname(__file__)             # 获取项目地址
    file_path = module_path + '/OKExData/' + file_name  # 合成存储路径（项目地址 + 指定目录 + 文件名称）
    return file_path


def lock_file(file_path):

    if os.path.isfile(file_path):    # 检查文件是否存则
        # 检查文件是否为空
        if os.path.getsize(file_path) == 0:
            # 如果文件为空
            return False
        else:
            # 如果文件非空
            return True
    else:
        # 如果不存在
        return False


def input_file(list_info, file_path):
    file = open(file_path, 'a', encoding='UTF-8')  # r只读，w可写，a追加
    for line in list_info:
        # 把server的格林威治时间转换成北京时间
        line[0] = utc0_to_utc8(line[0])
        file.write(",".join(line) + '\n')
    file.close()
    print('已写入%d条数据' % len(list_info))
    return len(list_info)


def get_file(file_path):
    # 获取最后一条记录的时间戳
    min_time = np.loadtxt(file_path, dtype=str, delimiter=',')
    # 还原为server识别的ISO8601时间模式
    file_server_time = utc8_to_utc0(min_time[-1, 0])
    return file_server_time


def utc0_to_utc8(iso8601_time):
    utc0 = iso8601.parse_date(iso8601_time)  # 解析ISO8601时间格式为datetime时间格式
    unix = utc0.timestamp()                  # datetime时间格式转换成Unix时间格式
    utc8 = utc0.fromtimestamp(unix)          # 再把Unix时间格式转换成北京时间的datetime时间格式
    return str(utc8)


def utc8_to_utc0(utc8_time):
    utc8 = iso8601.parse_date(utc8_time)
    unix = utc8.timestamp()
    utc0 = utc8.utcfromtimestamp(unix - 28800)
    server_time_ = utc0.isoformat(timespec='milliseconds') + 'Z'
    return str(server_time_)


def get_k_line_info(api_key_, seceret_key_, passphrase_, symbol_, start_time, end_time, period_):  # 单次请求最多获取200条数据
    spot_api = spot.SpotAPI(api_key_, seceret_key_, passphrase_, True)      # 请求连接
    kline = spot_api.get_kline(symbol_, start_time, end_time, period_)       # 获取数据
    if len(kline) > 0:
        return kline
    else:
        return ''


if __name__ == '__main__':

    api_key = ''
    seceret_key = ''
    passphrase = ''

    # symbol = input('输入要保存的货币对名称：')
    symbols = ['BTC-USDT', 'OKB-USDT', 'ETH-USDT', 'ETC-USDT', 'LTC-USDT']
    period = 60     # K线图的时间周期
    # 必须是 [60 180 300 900 1800 3600 7200 14400 21600 43200 86400 604800]中的任一值，否则请求将被拒绝。
    # 这些值分别对应的是[1min 3min 5min 15min 30min 1hour 2hour 4hour 6hour 12hour 1day 1week]的时间段。

    for symbol in symbols:
        start, end = server_time()
        # 自动输入文件名称，调用合成文件存储路径函数
        filePath = get_moduel_path(str(get_day_date() - datetime.timedelta(days=1)) + ' ' + symbol + ' 1min K线数据.txt')
        while True:
            if lock_file(filePath):
                # 如果文件存在，并且不是空文件
                end = get_file(filePath)  # 获取文件中最后一行记录的时间戳
                # 以最后记录的时间再向前200个单位获取K线数据（OKEx服务器默认一次请求最多获取200个数据，且限制每2秒5次请求）
                k_line_info = get_k_line_info(api_key, seceret_key, passphrase, symbol, start, end, period)

                # 追加写入数据
                num = input_file(k_line_info, filePath)
            else:
                # 文件不存在或是一个空文件

                # 以当前日期零点再向前200个单位获取K线数据（OKEx服务器默认一次请求最多获取200个数据，且限制每2秒5次请求）
                k_line_info = get_k_line_info(api_key, seceret_key, passphrase, symbol, start, end, period)

                print('获取数据的时间周期为:')
                print('起始时间：', start)
                print('结束时间：', end)
                # 新建文件并写入或在空文件中写入数据
                num = input_file(k_line_info, filePath)

            if num < 200:
                print( symbol + '今日行情数据已经存储')
                break

    print('全部行情数据下载完成')