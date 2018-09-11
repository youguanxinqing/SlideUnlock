# -*- coding: utf-8 -*-

"""
@Version : Python3.6
@Time    : 2018/9/10 19:33
@File    : slider_unlock.py
@SoftWare: PyCharm 
@Author  : Guan
@Contact : youguanxinqing@163.com
@Desc    :
=================================
    破解滑动解锁
=================================
"""
import time
from PIL import Image
from io import BytesIO
from random import randint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException


def get_a_node(cssSelector, type):
    """获得节点"""
    opts = {
        "unclick": "EC.presence_of_element_located",
        "click": "EC.element_to_be_clickable",
    }
    needfunc = eval(opts.get(type))
    node = wait.until(needfunc((By.CSS_SELECTOR, cssSelector)))
    return node

def crop_img(pos):
    """截图"""
    screentshot = BytesIO(browser.get_screenshot_as_png())
    img = Image.open(screentshot).crop(pos)
    return img

def get_img_posistion(node):
    """获取图片的位置"""
    location = node.location
    # print(location)
    size = node.size

    # 构建图片的左，上，右，下坐标
    left, top, right, buttom = ( location["x"], location["y"],
                                 location["x"] + size["width"],
                                 location["y"] + size["height"] )

    return (left, top, right, buttom)

def get_two_imgs():
    """获取完整与缺块图片"""
    imgNode = get_a_node(".gt_box", "unclick")
    pos = get_img_posistion(imgNode)
    # 完整图片
    imgwhole = crop_img(pos)

    # 点击滑块，获取缺块图片
    get_a_node("div.gt_slider_knob.gt_show", "unclick").click()
    # 截图之前，先隐藏滑块
    try:
        browser.execute_script(
                "var node = document.getElementsByClassName('gt_slice gt_show');"
                "node[0].style.display='none'")
    except WebDriverException:
        browser.execute_script(
                "var node = document.getElementsByClassName('gt_bg gt_show');"
                "node[0].style.display='block'")
    time.sleep(3)
    # 缺块图片
    imgpart = crop_img(pos)

    # 截完图片后恢复滑块
    try:
        browser.execute_script(
                "var node = document.getElementsByClassName('gt_slice gt_show');"
                "node[0].style.display='block'")
    except WebDriverException:
        browser.execute_script(
                "var node = document.getElementsByClassName('gt_bg gt_show');"
                "node[0].style.display='block'")

    return (imgwhole, imgpart)

def is_pixel_equal(imgwhole, imgpart, x, y):
    """比较像素点是否相同
    允许范围内返回true,反之false"""
    pixel = imgwhole.load()[x, y]
    pixe2 = imgpart.load()[x, y]
    allowOffset = 60
    if abs(pixel[0]-pixe2[0]) < allowOffset \
            and abs(pixel[1]-pixe2[1]) < allowOffset \
            and abs(pixel[2]-pixe2[2]) < allowOffset:

        return True
    else:
        return False

def get_move_distance(imgwhole, imgpart):
    """比较两张图片
    返回移动距离"""
    for i in range(imgwhole.size[0]):
        for j in range(imgwhole.size[1]):
            flag = is_pixel_equal(imgwhole, imgpart, i, j)
            if not flag:
                return i

def get_move_track(offset):
    """获得移动轨迹"""
    current = 0
    point = (3/4)*offset
    v = 0
    t = 0.2
    moves = []
    while current < offset:
        if current < point:
            a = 3
        else:
            a = -5

        v0 = v
        v = v0 + a*t
        # 高中物理移动距离公式
        x = v0*t + (1/2)*a*t**2
        current += x
        moves.append(round(x))
    return moves

def move_spider(moves):
    """移动滑块"""
    slider = get_a_node(".gt_slider_knob.gt_show", "click")
    ActionChains(browser).click_and_hold(slider).perform()
    for x in moves:
        ActionChains(browser).move_by_offset(x, randint(-1, 1)).perform()

    time.sleep(1)
    ActionChains(browser).release().perform()

def main():
    browser.get("http://www.sgs.gov.cn/notice")
    keyword = get_a_node("#keyword", "unclick")
    keyword.send_keys("百度")
    btnSearch = get_a_node("#buttonSearch", "click")
    btnSearch.click()

    imgwhole, imgpart = get_two_imgs()
    offset = get_move_distance(imgwhole, imgpart)
    moves = get_move_track(offset-10)
    move_spider(moves)

if __name__ == "__main__":
    browser = webdriver.Chrome()
    browser.maximize_window()
    wait = WebDriverWait(browser, 10)

    main()