#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import math
import cg_algorithms as alg
from typing import Optional
from PyQt5.QtWidgets import (QApplication, QMainWindow, qApp, QGraphicsScene,
                             QGraphicsView, QGraphicsItem, QListWidget,
                             QHBoxLayout, QWidget, QStyleOptionGraphicsItem,
                             QLabel, QFileDialog, QColorDialog, QPushButton,
                             QMenu, QAction, QProxyStyle, QStyle, QStatusBar,
                             QSizePolicy, QMessageBox, QSpinBox, QDialog,
                             QFormLayout)
from PyQt5.QtGui import QPainter, QMouseEvent, QColor, QImage, QPainter,\
 QIcon, QPixmap,QKeySequence
from PyQt5.QtCore import QRectF, Qt, QSize
import ctypes

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

height = 550
width = 650
icon_size = 40
DEBUG = 0


class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = '0'
        self.temp_item = None

        self.color = QColor(0, 0, 0)
        self.pre_x = 0  #用于平移旋转，记录上一个点
        self.pre_y = 0
        self.center_x = 0
        self.center_y = 0  #旋转中心
        self.max_x = 0
        self.max_y = 0
        self.min_x = 0
        self.min_y = 0  #用于裁剪
        self.pre_list = []

    def clear(self):
        self.scene().clear()
        self.list_widget.clear()
        self.updateScene([self.sceneRect()])
        self.temp_id = self.main_window.get_id()

    def save(self, filename):
        rect = self.scene().sceneRect()
        pixmap = QImage(rect.height(), rect.width(),
                        QImage.Format_ARGB32_Premultiplied)
        painter = QPainter(pixmap)
        rectf = QRectF(0, 0, pixmap.rect().height(), pixmap.rect().width())
        self.scene().render(painter, rectf, rect)
        pixmap.save(filename[0])

    def start_draw_line(self, algorithm):
        self.status = 'line'
        self.temp_algorithm = algorithm

    def start_draw_polygon(self, algorithm):
        self.status = 'polygon'
        self.temp_algorithm = algorithm

    def start_draw_ellipse(self):
        self.status = 'ellipse'

    def start_draw_curve(self, algorithm):
        self.status = 'curve'
        self.temp_algorithm = algorithm

    def start_translate(self):
        self.status = 'translate'

    def start_rotate(self):
        self.status = 'rotate'

    def start_scale(self):
        self.status = 'scale'

    def start_clip(self, algorithm):
        self.status = 'clip'
        self.temp_algorithm = algorithm

    def finish_draw(self):
        self.temp_id = self.main_window.get_id()
        self.temp_item = None

    def finish_poly_curve(self):
        if self.status == 'polygon' and self.temp_item is not None:
            x, y = self.temp_item.p_list[0]  #回到开始的点
            self.temp_item.p_list.append([x, y])
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
            self.setMouseTracking(False)  #关闭追踪
        if self.status == 'curve' and self.temp_item is not None:
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
            self.setMouseTracking(False)  #关闭追踪

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''
        self.updateScene([self.sceneRect()])

    def find_selected(self, x, y):
        for i in range(0, len(self.item_dict)):
            rect = self.item_dict[i].boundingRect()
            if rect.contains(x, y) == True:
                self.selected_id = i

    def selection_changed(self, selected):
        self.finish_poly_curve()
        self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        if selected != '':
            self.selected_id = selected
            self.item_dict[selected].selected = True
            self.item_dict[selected].update()
        #       self.status = ''
        self.updateScene([self.sceneRect()])

    def center(self, k):
        x = 0
        y = 0
        num = max(1, len(self.item_dict[k].p_list))
        for i in self.item_dict[k].p_list:
            x += i[0]
            y += i[1]
        x /= num
        y /= num
        return (x, y)

    def angle(self, now_x, now_y):
        Cos = (self.pre_x * now_x + self.pre_y * now_y) / (
            math.sqrt(self.pre_x**2 + self.pre_y**2) *
            math.sqrt(now_x**2 + now_y**2))
        Sin = (self.pre_y * now_x - self.pre_x * now_y) / (
            math.sqrt(self.pre_x**2 + self.pre_y**2) *
            math.sqrt(now_x**2 + now_y**2))
        #   print("cos = %f  Sin = %f" % (Cos, Sin))
        if Cos > 1:
            Cos = 1.0

    #        print("fix")
        if Sin >= 0:
            angle = math.degrees(math.acos(Cos))
        else:
            angle = math.degrees(-math.acos(Cos))
        return angle

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.LeftButton:
            return  #只允许左键点击
        if DEBUG:
            print("press")
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item = MyItem(self.temp_id, self.status,
                                    [[x, y], [x, y]], self.color,
                                    self.temp_algorithm)
            self.scene().addItem(self.temp_item)
            #self.scene()为QGraphicsScene类
        elif self.status == 'polygon':
            if self.temp_item is None:  #第一个点
                self.setMouseTracking(True)  #开启追踪
                self.temp_item = MyItem(self.temp_id, self.status,
                                        [[x, y], [x, y]], self.color,
                                        self.temp_algorithm)
                self.scene().addItem(self.temp_item)
        elif self.status == 'ellipse':
            self.temp_item = MyItem(self.temp_id, self.status,
                                    [[x, y], [x, y]], self.color,
                                    self.temp_algorithm)
            self.scene().addItem(self.temp_item)
        elif self.status == 'curve':
            if self.temp_item is None:  #第一个点
                self.setMouseTracking(True)  #开启追踪
                self.temp_item = MyItem(self.temp_id, self.status,
                                        [[x, y], [x, y]], self.color,
                                        self.temp_algorithm)
                self.scene().addItem(self.temp_item)
        elif self.status == 'translate':
            self.pre_x = x
            self.pre_y = y
        elif self.status == 'rotate':
            if self.selected_id != '' and (x != self.center_x
                                           or y != self.center_y):

                self.center_x, self.center_y = self.center(self.selected_id)
                self.pre_x = x - self.center_x
                self.pre_y = y - self.center_y
                self.pre_list = []
                for x0, y0 in self.item_dict[self.selected_id].p_list:
                    self.pre_list.append([x0, y0])
                self.temp_item = MyItem(
                    self.temp_id, 'polygon',
                    [[int(self.center_x) - 1,
                      int(self.center_y) - 1],
                     [int(self.center_x) + 1,
                      int(self.center_y) - 1],
                     [int(self.center_x) + 1,
                      int(self.center_y) + 1],
                     [int(self.center_x) - 1,
                      int(self.center_y) + 1],
                     [int(self.center_x) - 1,
                      int(self.center_y) - 1]], QColor(0, 255, 0), 'DDA')
                #绿色的中心点
                self.scene().addItem(self.temp_item)
        elif self.status == 'scale':
            if self.selected_id != '' and (x != self.center_x
                                           or y != self.center_y):
                self.center_x, self.center_y = self.center(self.selected_id)
                self.pre_x = x - self.center_x
                self.pre_y = y - self.center_y
                self.pre_list = []
                for x0, y0 in self.item_dict[self.selected_id].p_list:
                    self.pre_list.append([x0, y0])
                self.temp_item = MyItem(
                    self.temp_id, 'polygon',
                    [[int(self.center_x) - 1,
                      int(self.center_y) - 1],
                     [int(self.center_x) + 1,
                      int(self.center_y) - 1],
                     [int(self.center_x) + 1,
                      int(self.center_y) + 1],
                     [int(self.center_x) - 1,
                      int(self.center_y) + 1],
                     [int(self.center_x) - 1,
                      int(self.center_y) - 1]], QColor(0, 255, 0), 'DDA')
                #绿色的中心点
                self.scene().addItem(self.temp_item)
        elif self.status == 'clip':
            if self.selected_id != '' and self.item_dict[
                    self.selected_id].item_type == 'line':
                self.pre_x = x
                self.pre_y = y
                self.temp_item = MyItem(self.temp_id,
                                        self.status, [[x, y], [x, y]],
                                        QColor(0, 0, 255), self.temp_algorithm)
                #蓝色的裁剪框
                self.scene().addItem(self.temp_item)

        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        #注意：只有在鼠标按下时才会追踪，除非开启持续追踪
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item.p_list[1] = [x, y]
        if self.status == 'polygon':
            if self.temp_item is not None:
                self.temp_item.p_list[-1] = [x, y]  #多边形最后一个点在变化
        if self.status == 'ellipse':
            self.temp_item.p_list[1] = [x, y]
        if self.status == 'curve':
            if self.temp_item is not None:
                self.temp_item.p_list[-1] = [x, y]  #多边形最后一个点在变化
        if self.status == 'translate':
            if self.selected_id != '':
                self.item_dict[self.selected_id].p_list = alg.translate(
                    self.item_dict[self.selected_id].p_list, x - self.pre_x,
                    y - self.pre_y)
                self.pre_x = x
                self.pre_y = y
        if self.status == 'rotate':
            if self.selected_id != '' and (x != self.center_x
                                           or y != self.center_y):
                now_x = x - self.center_x
                now_y = y - self.center_y
                Angle = self.angle(now_x, now_y)
                #             print(angle)
                self.item_dict[self.selected_id].p_list = alg.rotate(
                    self.pre_list, self.center_x, self.center_y, -Angle)
        if self.status == 'scale':
            if self.selected_id != '':
                now_x = x - self.center_x
                now_y = y - self.center_y
                new_len = math.sqrt(now_x**2 + now_y**2)
                pre_len = math.sqrt(self.pre_x**2 + self.pre_y**2)
                #           print(new_len, pre_len)
                self.item_dict[self.selected_id].p_list = alg.scale(
                    self.pre_list, self.center_x, self.center_y,
                    1.0 * new_len / pre_len)
        if self.status == 'clip':
            if self.selected_id != '' and self.item_dict[
                    self.selected_id].item_type == 'line':
                self.temp_item.p_list[-1] = [x, y]

        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if DEBUG:
            print("release")
        if event.button() != Qt.LeftButton:
            return
        if self.status == 'line':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        if self.status == 'polygon':  #放开只表示结束了一段
            if self.temp_item is not None:
                pos = self.mapToScene(event.localPos().toPoint())
                x = int(pos.x())
                y = int(pos.y())
                self.temp_item.p_list.append([x, y])
        if self.status == 'ellipse':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        if self.status == 'curve':  #放开只表示结束了一段
            if self.temp_item is not None:
                pos = self.mapToScene(event.localPos().toPoint())
                x = int(pos.x())
                y = int(pos.y())
                self.temp_item.p_list.append([x, y])
        if self.status == 'translate':
            pass
        if self.status == 'rotate':
            if self.selected_id != '':
                self.scene().removeItem(self.temp_item)
                self.updateScene([self.sceneRect()])
        if self.status == 'scale':
            if self.selected_id != '':
                self.scene().removeItem(self.temp_item)
                self.updateScene([self.sceneRect()])
        if self.status == 'clip':
            if self.selected_id != '' and self.item_dict[
                    self.selected_id].item_type == 'line':
                pos = self.mapToScene(event.localPos().toPoint())
                x = int(pos.x())
                y = int(pos.y())
                now = alg.clip(self.item_dict[self.selected_id].p_list,
                               min(self.pre_x, x), min(self.pre_y, y),
                               max(self.pre_x, x), max(self.pre_y, y),
                               self.temp_algorithm)
                self.item_dict[self.selected_id].p_list = now  #更新线段
                self.scene().removeItem(self.temp_item)
                self.updateScene([self.sceneRect()])

        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.LeftButton:
            return
        if DEBUG:
            print("doubleclick")
        self.finish_poly_curve()
        self.updateScene([self.sceneRect()])
        super().mouseDoubleClickEvent(event)


class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """

    def __init__(self,
                 item_id: str,
                 item_type: str,
                 p_list: list,
                 color,
                 algorithm: str = '',
                 parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id  # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list  # 图元参数
        self.color = color  #画笔颜色
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False

    #QGraphicsItem的虚函数，由QGraphicsView调用updateScene()实现
    def paint(self,
              painter: QPainter,
              option: QStyleOptionGraphicsItem,
              widget: Optional[QWidget] = ...) -> None:

        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
            painter.setPen(self.color)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())

        elif self.item_type == 'polygon':
            item_pixels = []
            for i in range(1, len(self.p_list)):
                line = alg.draw_line([self.p_list[i - 1], self.p_list[i]],
                                     self.algorithm)
                item_pixels += line
            painter.setPen(self.color)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())

        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
            painter.setPen(self.color)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())

        elif self.item_type == 'curve':
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
            painter.setPen(self.color)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())

        elif self.item_type == 'clip':
            painter.setPen(QColor(0, 0, 255))  #绿色裁剪框
            painter.drawRect(self.boundingRect())

    def boundingRect(self) -> QRectF:
        if self.item_type == 'line':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'polygon' or self.item_type == 'clip':
            x1 = y1 = 0
            x0 = width
            y0 = height
            for x, y in self.p_list:
                x0 = min(x0, x)
                y0 = min(y0, y)
                x1 = max(x1, x)
                y1 = max(y1, y)
            x1 -= x0
            y1 -= y0
            return QRectF(x0 - 2, y0 - 2, x1 + 4, y1 + 4)

        elif self.item_type == 'ellipse':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 2, y - 2, w + 4, h + 4)
        elif self.item_type == 'curve':
            x1 = y1 = 0
            x0 = height
            y0 = width
            for x, y in self.p_list:
                x0 = min(x0, x)
                y0 = min(y0, y)
                x1 = max(x1, x)
                y1 = max(y1, y)
            x1 -= x0
            y1 -= y0
            return QRectF(x0 - 2, y0 - 2, x1 + 4, y1 + 4)


class MainWindow(QMainWindow):
    """
    主窗口类
    """

    def __init__(self):
        super().__init__()
        self.item_cnt = 1

        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(150)

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, width, height)  #绘画范围
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(width, height)  #画布窗口大小
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget

        # 设置菜单栏
        menubar = self.menuBar()
        menubar.setMinimumHeight(icon_size)  #菜单栏高度

        set_pen_act = menubar.addAction('')
        set_pen_act.setIcon(
            QIcon(QPixmap("resource/pen.png").scaled(icon_size, icon_size)))
        #设置画笔

        save_canvas_act = menubar.addAction('')
        save_canvas_act.setIcon(
            QIcon(QPixmap("resource/save.png").scaled(icon_size, icon_size)))
        #保存画布

        reset_canvas_act = menubar.addAction('')
        reset_canvas_act.setIcon(
            QIcon(QPixmap("resource/reset.png").scaled(icon_size, icon_size)))
        #重置画布
        '''
        reset_canvas_act = QAction(
            QIcon(QPixmap("resource/reset.png").scaled(icon_size, icon_size)),
            '')
        menubar.addAction(reset_canvas_act)#错误写法，不会显示图标
        '''

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        line_menu = menubar.addMenu(
            QIcon(QPixmap("resource/line.png").scaled(icon_size, icon_size)),
            '')  #线段
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')

        polygon_menu = menubar.addMenu(
            QIcon(
                QPixmap("resource/polygon.png").scaled(icon_size, icon_size)),
            '')  #多边形
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')

        ellipse_act = menubar.addAction('')
        ellipse_act.setIcon(
            QIcon(
                QPixmap("resource/ellipse.png").scaled(icon_size, icon_size)))
        #椭圆

        curve_menu = menubar.addMenu(
            QIcon(QPixmap("resource/curve.png").scaled(icon_size, icon_size)),
            '')  #曲线
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')

        translate_act = menubar.addAction('')
        translate_act.setIcon(
            QIcon(
                QPixmap("resource/translate.png").scaled(icon_size,
                                                         icon_size)))
        #平移

        rotate_act = menubar.addAction('')
        rotate_act.setIcon(
            QIcon(QPixmap("resource/rotate.png").scaled(icon_size, icon_size)))
        #旋转

        scale_act = menubar.addAction('')
        scale_act.setIcon(
            QIcon(QPixmap("resource/scale.png").scaled(icon_size, icon_size)))
        #缩放

        clip_menu = menubar.addMenu(
            QIcon(QPixmap("resource/clip.png").scaled(icon_size, icon_size)),
            '')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')
        #裁剪

        exit_act = menubar.addAction('')
        exit_act.setIcon(
            QIcon(QPixmap("resource/exit.png").scaled(icon_size, icon_size)))
        #退出

        # 连接信号和槽函数
        set_pen_act.triggered.connect(self.set_pen_action)
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        save_canvas_act.triggered.connect(self.save_canvas_action)
        self.list_widget.currentTextChanged.connect(
            self.canvas_widget.selection_changed)
        line_naive_act.triggered.connect(self.line_naive_action)
        line_dda_act.triggered.connect(self.line_dda_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)
        polygon_dda_act.triggered.connect(self.polygon_dda_action)
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)
        ellipse_act.triggered.connect(self.ellipse_action)
        curve_bezier_act.triggered.connect(self.curve_bezier_action)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)
        translate_act.triggered.connect(self.translate_action)
        rotate_act.triggered.connect(self.rotate_action)
        scale_act.triggered.connect(self.scale_action)
        clip_cohen_sutherland_act.triggered.connect(
            self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)
        exit_act.triggered.connect(self.exit_action)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(width, height)
        self.setWindowTitle('CG Demo')

    def get_id(self):
        _id = str(self.item_cnt)
        self.item_cnt += 1
        return _id

    def set_pen_action(self):
        self.canvas_widget.finish_poly_curve()
        self.statusBar().showMessage('设置画笔')
        color = QColorDialog().getColor()
        self.canvas_widget.color = color

    def reset_canvas_action(self):
        self.statusBar().showMessage('重置画布')
        self.canvas_widget.finish_poly_curve()

        dialog = QDialog()
        dialog.setWindowTitle('重置画布信息')
        dialog.setWindowModality(Qt.WindowModal)
        dialog.resize(300, 110)

        btn1 = QPushButton(dialog)
        btn1.setText('确定')
        btn1.move(50, 70)
        btn1.clicked.connect(dialog.accept)

        btn2 = QPushButton(dialog)
        btn2.setText('取消')
        btn2.move(175, 70)
        btn2.clicked.connect(dialog.reject)

        width_box = QSpinBox()
        width_box.setRange(100, 1100)
        width_box.setValue(650)

        height_box = QSpinBox()
        height_box.setRange(100, 1100)
        height_box.setValue(550)

        formlayout = QFormLayout(dialog)
        formlayout.addRow(QLabel('宽'), width_box)
        formlayout.addRow(QLabel('高'), height_box)

        if dialog.exec() == 1:
            new_width = width_box.value()
            new_height = height_box.value()
            self.scene.setSceneRect(0, 0, new_width, new_height)  #绘画范围
            self.canvas_widget.setFixedSize(new_width, new_height)  #画布窗口大小
            #   self.list_widget.setFixedWidth(150)

            self.item_cnt = 0
            self.canvas_widget.clear_selection()
            self.canvas_widget.clear()
            self.list_widget.clearSelection()

    def save_canvas_action(self):
        self.canvas_widget.finish_poly_curve()
        self.statusBar().showMessage('保存画布')
        filename = QFileDialog.getSaveFileName(self, '选择存储位置', 'utitled',
                                               'Images (*.bmp)')
        if filename[0]:
            pix = self.canvas_widget.grab(
                self.canvas_widget.sceneRect().toRect())
            pix.save(filename[0])

    def line_naive_action(self):
        self.canvas_widget.finish_poly_curve()
        self.canvas_widget.start_draw_line('Naive')
        self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_dda_action(self):
        self.canvas_widget.finish_poly_curve()
        self.canvas_widget.start_draw_line('DDA')
        self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_bresenham_action(self):
        self.canvas_widget.finish_poly_curve()
        self.canvas_widget.start_draw_line('Bresenham')
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_dda_action(self):
        self.canvas_widget.finish_poly_curve()
        self.canvas_widget.start_draw_polygon('DDA')
        self.statusBar().showMessage('DDA算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_bresenham_action(self):
        self.canvas_widget.finish_poly_curve()
        self.canvas_widget.start_draw_polygon('Bresenham')
        self.statusBar().showMessage('Bresenham算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def ellipse_action(self):
        self.canvas_widget.finish_poly_curve()
        self.canvas_widget.start_draw_ellipse()
        self.statusBar().showMessage('绘制椭圆')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_bezier_action(self):
        self.canvas_widget.finish_poly_curve()
        self.canvas_widget.start_draw_curve('Bezier')
        self.statusBar().showMessage('绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_b_spline_action(self):
        self.canvas_widget.finish_poly_curve()
        self.canvas_widget.start_draw_curve('B-spline')
        self.statusBar().showMessage('绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def translate_action(self):
        self.canvas_widget.finish_poly_curve()
        self.statusBar().showMessage('平移')
        self.canvas_widget.start_translate()

    def rotate_action(self):
        self.canvas_widget.finish_poly_curve()
        self.canvas_widget.start_rotate()
        self.statusBar().showMessage('旋转')

    def scale_action(self):
        self.canvas_widget.finish_poly_curve()
        self.canvas_widget.start_scale()
        self.statusBar().showMessage('缩放')

    def clip_cohen_sutherland_action(self):
        self.canvas_widget.finish_poly_curve()
        self.canvas_widget.start_clip('Cohen-Sutherland')
        self.statusBar().showMessage('裁剪')

    def clip_liang_barsky_action(self):
        self.canvas_widget.finish_poly_curve()
        self.canvas_widget.start_clip('Liang-Barsky')
        self.statusBar().showMessage('裁剪')

    def exit_action(self):
        self.canvas_widget.finish_poly_curve()
        reply = QMessageBox.question(
            self, '', '是否保存当前草稿？',
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.save_canvas_action()
            qApp.quit()
        elif reply == QMessageBox.No:
            qApp.quit()


class MyProxyStyle(QProxyStyle):
    pass

    def pixelMetric(self, QStyle_PixelMetric, option=None, widget=None):

        if QStyle_PixelMetric == QStyle.PM_SmallIconSize:
            return icon_size
        else:
            return QProxyStyle.pixelMetric(self, QStyle_PixelMetric, option,
                                           widget)


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    mw = MainWindow()

    myStyle = MyProxyStyle(
        'Windows')  # The proxy style should be based on an existing style,
    # like 'Windows', 'Motif', 'Plastique', 'Fusion', ...
    app.setStyle(myStyle)

    mw.setWindowIcon(QIcon("resource/icon.png"))
    mw.show()
    sys.exit(app.exec_())