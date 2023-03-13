#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math


def tran_int(x):
    return int(x + 0.5)


def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if x0 == x1:
        if y0 > y1:
            y0, y1 = y1, y0
        for y in range(y0, y1 + 1):
            result.append((x0, y))  #斜率不存在

    elif y0 == y1:
        if x0 > x1:
            x0, x1 = x1, x0
        for x in range(x0, x1 + 1):
            result.append((x, y0))  #斜率为0

    elif algorithm == 'Naive':
        if x0 > x1:
            x0, y0, x1, y1 = x1, y1, x0, y0
        k = (y1 - y0) / (x1 - x0)
        for x in range(x0, x1 + 1):
            result.append((x, tran_int(y0 + k * (x - x0))))

    elif algorithm == 'DDA':
        k = (y1 - y0) / (x1 - x0)
        if abs(k) < 1:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0  #保证从左到右画线
            for x in range(x0, x1 + 1):
                result.append((x, tran_int(y0)))
                y0 += k
        else:
            if y0 > y1:
                x0, y0, x1, y1 = x1, y1, x0, y0  #保证从上到下画线
            for y in range(y0, y1 + 1):
                result.append((tran_int(x0), y))
                x0 += 1 / k

    elif algorithm == 'Bresenham':
        result = draw_Bresenham(x0, y0, x1, y1)

    return result


def draw_Bre_pre(x0, x1, y0, y1, flag):
    #画斜率绝对值在0-1之间的线段，x为单位步长
    #注意，这里的xy分别是长边和短边，即斜率dx/dy绝对值小于1
    #flag用于判断是否xy倒转
    result = []
    if x0 > x1:
        x0, y0, x1, y1 = x1, y1, x0, y0  #保证从左到右画线
    dx = x1 - x0
    dy = y1 - y0
    step_y = 1  #y每次的增量，如果斜率为负则需要减少
    if y0 > y1:
        step_y = -1
        dy = -dy
    p = 2 * dy - dx
    for x in range(x0, x1 + 1):
        if flag == 0:  #根据是否翻转决定坐标
            result.append((x, y0))
        else:
            result.append((y0, x))
        if p > 0:
            y0 += step_y
            p = p + 2 * dy - 2 * dx
        else:
            p = p + 2 * dy
    return result


def draw_Bresenham(x0, y0, x1, y1):
    k = (y1 - y0) / (x1 - x0)
    if abs(k) < 1:
        return draw_Bre_pre(x0, x1, y0, y1, 0)
    else:  #斜率大于1要以y为单位步长
        return draw_Bre_pre(y0, y1, x0, x1, 1)


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result


def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []

    xc = tran_int((x0 + x1) / 2)
    yc = tran_int((y0 + y1) / 2)  #中心点坐标

    rx = abs(x1 - x0) // 2
    ry = abs(y1 - y0) // 2  #长短半轴
    flag = 0

    if rx < ry:
        rx, ry = ry, rx
        flag = 1

    #画一象限的椭圆
    #注意rx和ry是长短半轴，flag用于判定是否翻转
    x = 0
    y = tran_int(ry)  #第一个点
    p = ry**2 - rx**2 * ry + rx**2 / 4  #初始判定值

    while ry**2 * x < rx**2 * y:
        if flag == 0:  #根据是否翻转决定坐标
            result.extend([(xc + x, yc + y), (xc - x, yc + y),
                           (xc + x, yc - y), (xc - x, yc - y)])
        else:
            result.extend([(xc + y, yc + x), (xc - y, yc + x),
                           (xc + y, yc - x), (xc - y, yc - x)])
        if p >= 0:
            p += 2 * ry**2 * x - 2 * rx**2 * y + 2 * rx * rx + 3 * ry**2
            x += 1
            y += -1
        else:
            p += 2 * ry**2 * x + 3 * ry**2
            x += 1

    p = ry**2 * (x + 0.5)**2 + rx**2 * (y - 1)**2 - rx**2 * ry**2
    while True:
        if flag == 0:  #根据是否翻转决定坐标
            result.extend([(xc + x, yc + y), (xc - x, yc + y),
                           (xc + x, yc - y), (xc - x, yc - y)])
        else:
            result.extend([(xc + y, yc + x), (xc + y, yc - x),
                           (xc - y, yc + x), (xc - y, yc - x)])
        if y == 0: break  #画完退出
        if p <= 0:
            p += 2 * ry**2 * x - 2 * rx**2 * y + 2 * ry**2 + 3 * rx**2
            x += 1
            y += -1
        else:
            p += -2 * rx**2 * y + 3 * rx**2
            y += -1

    return result


def Bspline(i, k, u):
    if k == 1:
        if i <= u and u < i + 1:
            result = 1.0
        else:
            result = 0.0
    else:
        result = ((u - i) / (k - 1)) * Bspline(i, k - 1, u) + (
            (i + k - u) / (k - 1)) * Bspline(i + 1, k - 1, u)
        #实际上约掉了/len(p_line)，比如u-ui=u/len-i/len
        #因为只有k层所以没必要递推
    return result


def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    step = 0.001
    n = len(p_list)

    if algorithm == 'Bezier':
        u = step  #参数从0到1
        result.append(p_list[0])  #第一个点不用计算

        while u < 1:
            last = p_list[:]  #记录上一次迭代
            now = []  #记录这一次迭代
            for r in range(1, n):
                now = []
                for i in range(0, n - r):
                    now.append([(1 - u) * last[i][0] + u * last[i + 1][0],
                                (1 - u) * last[i][1] + u * last[i + 1][1]])
                last = now[:]
                #now的长度逐次减少，最后为1
            result.append([tran_int(now[0][0]), tran_int(now[0][1])])
            u += step

    elif algorithm == 'B-spline':
        result.append(p_list[0])
        k = 4  #四阶
        u = 3  #参数para从0到1，u=para*len从0开始到len-1

        while u < n:  #3-len-1
            x = 0.0
            y = 0.0
            for i in range(0, n):
                tmp = Bspline(i, k, u)
                x += p_list[i][0] * tmp
                y += p_list[i][1] * tmp
            result.append([tran_int(x), tran_int(y)])
            u += step
    return result


def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    for i in range(0, len(p_list)):
        p_list[i][0] += dx
        p_list[i][1] += dy
    return p_list


def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    for newx, newy in p_list:
        newx -= x
        newy -= y
        newx, newy = newx * math.cos(math.radians(r)) - newy * math.sin(
            math.radians(r)), newx * math.sin(
                math.radians(r)) + newy * math.cos(math.radians(r))
        newx += x
        newy += y
        result.append([int(newx + 0.5), int(newy + 0.5)])

    return result


def scale(p_list, x, y, r):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param r: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """

    result = []
    for newx, newy in p_list:
        newx = (newx - x) * r + x
        newy = (newy - y) * r + y
        result.append([int(newx + 0.5), int(newy + 0.5)])

    return result


def encode(x_min, y_min, x_max, y_max, x, y):
    result = 0
    if (y > y_max): result = (result << 1) + 1
    else: result <<= 1
    if (y < y_min): result = (result << 1) + 1
    else: result <<= 1
    if (x > x_max): result = result = (result << 1) + 1
    else: result <<= 1
    if (x < x_min): result = result = (result << 1) + 1
    else: result <<= 1
    return result


def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    result = p_list[:]  #可能不需要裁剪
    [x0, y0], [x1, y1] = p_list[0], p_list[1]
    if algorithm == "Cohen-Sutherland":
        while (1):
            #       print("point [%f,%f] [%f,%f]" % (x0, y0, x1, y1))
            encode1 = encode(x_min, y_min, x_max, y_max, x0, y0)
            encode2 = encode(x_min, y_min, x_max, y_max, x1, y1)
            #       print("encode %d %d" % (encode1, encode2))
            if (encode1 & encode2):  #在窗口外
                return [[0, 0], [0, 0]]
            if (encode1 | encode2 == 0):  #在窗口内
                result[0] = [tran_int(x0), tran_int(y0)]
                result[1] = [tran_int(x1), tran_int(y1)]
                return result
            #部分在窗口内
            if (encode1 == 0):  #交换，左边是窗口外的
                x0, y0, x1, y1 = x1, y1, x0, y0
                encode1, encode2 = encode2, encode1
            if (encode1 & 0b0001):  #左
                x = x_min
                y = (x_min - x0) / (x1 - x0) * (y1 - y0) + y0
            elif (encode1 & 0b0010):  #右
                x = x_max
                y = (x_max - x0) / (x1 - x0) * (y1 - y0) + y0
            elif (encode1 & 0b0100):  #下
                y = y_min
                if (x0 == x1): x = x0
                else: x = (y_min - y0) / (y1 - y0) * (x1 - x0) + x0
            elif (encode1 & 0b1000):  #上
                y = y_max
                if (x0 == x1): x = x0
                else: x = (y_max - y0) / (y1 - y0) * (x1 - x0) + x0
            x0, y0 = x, y

    elif algorithm == 'Liang-Barsky':
        dx = x1 - x0
        dy = y1 - y0
        p = [-dx, dx, -dy, dy]
        q = [x0 - x_min, x_max - x0, y0 - y_min, y_max - y0]
        u1, u2 = 0, 1

        for i in range(0, 4):
            if p[i] == 0:
                if q[i] < 0:
                    return [[0, 0], [0, 0]]
            else:
                u = q[i] / p[i]
                if p[i] < 0:
                    u1 = max(u1, u)
                else:
                    u2 = min(u2, u)
        if u1 > u2:
            return [[0, 0], [0, 0]]
        x_0 = round(x0 + u1 * dx)
        y_0 = round(y0 + u1 * dy)
        x_1 = round(x0 + u2 * dx)
        y_1 = round(y0 + u2 * dy)
        res = [[x_0, y_0], [x_1, y_1]]

    return res
