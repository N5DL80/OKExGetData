# -*- coding: UTF-8 -*-
import os
import sys
import time
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
    server_start = date_time.utcfromtimestamp(unix - 115200)  # 减32小时得到格林尼治时间
    server_end = date_time.utcfromtimestamp(unix - 28800)     # 减8小时得到格林尼治时间

    # 格式化为服务器认可的ISO8601时间格式
    server_start_time = server_start.isoformat(timespec='milliseconds') + 'Z'
    server_end_time = server_end.isoformat(timespec='milliseconds') + 'Z'

    return server_start_time, server_end_time


def get_moduel_path(file_path):

    # 判断是否使用pyinstaller打包程序
    if hasattr(sys, 'frozen'):
        module_path = os.path.dirname(sys.executable)  # 获取打包项目地址
    else:
        module_path = os.path.dirname(__file__)  # 获取项目地址

    file_path = module_path + '/' + file_path   # 合成存储路径（项目地址 + 指定目录 + 文件名称）
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


def mkdir(file_path):
    # 去除首位空格
    file_path = file_path.strip()
    # 去除尾部 \ 符号
    file_path = file_path.rstrip("\\")
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    is_exists = os.path.exists(file_path)
    # 判断结果
    if not is_exists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(file_path)
        # print(path + ' 创建成功')
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        # print(path + ' 目录已存在')
        return False


def input_file(list_info, file_path):
    file = open(file_path, 'a', encoding='UTF-8')  # r只读，w可写，a追加
    for line in list_info:
        # 把server的格林威治时间转换成北京时间
        line[0] = utc0_to_utc8(line[0])
        file.write(",".join(line) + '\n')
    file.close()


def get_file(file_path):
    # 获取最后一条记录的时间戳
    min_time = np.loadtxt(file_path, dtype=str, delimiter=',')
    # 还原为server识别的ISO8601时间模式
    file_server_time = utc8_to_utc0(min_time[-1, 0])
    return file_server_time


def file_line_num(file_path):
    count = -1
    for count, line in enumerate(open(file_path, 'r')):
        pass
    count += 1
    return count


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
    kline = spot_api.get_kline(symbol_, start_time, end_time, period_)      # 获取数据
    if len(kline) > 0:
        return kline
    else:
        return ''


if __name__ == '__main__':

    # 创建一个全局计时器，记录程序运行的开始时间
    all_time = time.time()

    api_key = ''
    seceret_key = ''
    passphrase = ''

    # symbol = input('输入要保存的货币对名称：')
    symbols = ['BTC-USDT', 'OKB-USDT', 'ETH-USDT', 'ETC-USDT', 'LTC-USDT']
    period = 60     # K线图的时间周期
    # 必须是 [60 180 300 900 1800 3600 7200 14400 21600 43200 86400 604800]中的任一值，否则请求将被拒绝。
    # 这些值分别对应的是[1min 3min 5min 15min 30min 1hour 2hour 4hour 6hour 12hour 1day 1week]的时间段。

    # 计算数据开始和结束的时间
    start, end = server_time()
    print('\n获取数据的时间周期为:')
    print('----------------------------------')
    print('起始时间：', start)
    print('结束时间：', end)

    for symbol in symbols:

        # 数据长度计数器
        data_line = 0
        # 创建一个局部的计时器
        jb_time = time.time()

        # 计算数据开始和结束的时间
        start, end = server_time()
        print('----------------------------------')
        print('请求写入%s数据（一次最多200条）' % symbol)
        # 合成相对存储路径
        path = 'OKExData/现货数据/' + symbol + '/'

        # 创建与交易品种名称一致的文件夹
        mkdir(path)

        # 合成文件相对路径和文件名，调用合成文件完整的存储路径函数
        filePath = get_moduel_path(
            path + str(get_day_date() - datetime.timedelta(days=1)) + ' ' + symbol + ' 1min K线数据.txt')

        while True:

            if lock_file(filePath):
                # 如果文件存在，并且不是空文件
                end = get_file(filePath)  # 获取文件中最后一行记录的时间戳

                # 以最后记录的时间再向前200个单位获取K线数据（OKEx服务器默认一次请求最多获取200个数据，且限制每2秒5次请求）
                k_line_info = get_k_line_info(api_key, seceret_key, passphrase, symbol, start, end, period)

                # 计算请求数据的长度
                num = len(k_line_info)

                if num == 0:
                    pass
                else:
                    # 追加写入数据
                    input_file(k_line_info, filePath)

                    # 开始计数
                    data_line += num
                    print('已写入：%d条, 本次写入合计：%d条数据' % (num, data_line))

            else:
                # 文件不存在或是一个空文件
                # 以当前日期零点再向前200个单位获取K线数据（OKEx服务器默认一次请求最多获取200个数据，且限制每2秒5次请求）
                k_line_info = get_k_line_info(api_key, seceret_key, passphrase, symbol, start, end, period)

                # 计算请求数据的长度
                num = len(k_line_info)

                if num == 0:
                    pass
                else:
                    # 新建文件并写入数据
                    input_file(k_line_info, filePath)

                    # 开始计数
                    data_line += num

                    print('已写入：%d条, 本次写入合计：%d条数据' % (num, data_line))

            if num < 200:
                print('\nOKEx服务器已经没有可更新的数据啦！')
                print('\n合计已存储数据：%s条' % file_line_num(filePath))
                print('\n本次耗时：', round(time.time() - jb_time, 2), '秒')
                break

    print('==================================')
    print('完成!\n\n共计耗时：', round(time.time() - all_time, 2), '秒')
