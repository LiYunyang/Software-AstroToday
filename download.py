import re
import urllib2
import time
import datetime
import os
from PIL import Image
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from html.parser import HTMLParser


def scrap():
    url = 'https://arxiv.org/list/astro-ph/new?skip=0&show=2000'
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    content = response.read()
    print 'connected to arXiv'
    tik = time.time()
    pattern1 = re.compile('<h2>(.*?)</dl>\n<h3>', re.S)
    match = re.search(pattern1, content)
    content_range = match.group(0)
    pattern2 = re.compile('<dt><a name=(.*?)</dd>', re.S)
    items = re.findall(pattern2, content_range)
    arxiv_list = list()
    for idx, _ in enumerate(items):
        p = re.compile('<a href="(/pdf/\d{4}\.\d{5}).*?" title="Download PDF">pdf</a>.*?<span class="descriptor">Title:</span>(.*?)\n.*?<span class="descriptor">Authors:</span>(.*?)</div>.*?<span class="primary-subject">(.*?)\(.*?<p class="mathjax">(.*?)</p>', re.S)
        elements = re.findall(p, _)
        if not elements:
            continue
        pdf, title, name_content, catagory, abstract = elements[0]
        author_info = re.findall('<a href="(.*?)">(.*?)</a>', name_content)
        abstract_sect = re.findall('(.*?)\n', abstract)
        for i, _ in enumerate(abstract_sect):
            abstract_sect[i] += ' '
        abstract = ''.join(abstract_sect)
        to_remove = re.findall('<.*?>', abstract)
        for _ in to_remove:
            abstract = abstract.replace(_, '')
        arxiv_list.append({'pdf': pdf, 'title': title, 'class': catagory, 'author': author_info, 'abstract': abstract})
    tok = time.time()
    print tok - tik
    return arxiv_list


def de_symbol(text, symbol):
    text = text.replace('&lt;', r'<')
    text = text.replace('&gt;', r'>')
    text = text.replace('] ', ' ')
    text = text.replace('[', ' ')
    text = text.replace('\\rm', 'TOBErm')
    text = text.replace('\\it', 'TOBEit')
    text = text.replace('\\tt', 'TOBEtt')
    text = text.replace('\\text', 'TOBEtext')
    text = text.replace('\,', ' ')
    text = text.replace('\~', '~')
    text = text.replace('&#', 'ANDSHARP')
    if symbol.find('\\'):
        symbol = '\\' + ''.join(symbol.split('\\'))

    for sym in symbol:

        if sym == '\\':

            l = text.split(sym)
            if len(l) > 1:
                text = reduce(lambda x, y: x + r'\textbackslash{}' + y, l)
            else:
                text = l[0]

        elif sym == '^':
            l = text.split(sym)
            if len(l) > 1:
                text = reduce(lambda x, y: x + r'\textasciicircum{}' + y, l)
            else:
                text = l[0]

        else:
            l = text.split(sym)
            if len(l) > 1:
                text = reduce(lambda x, y: x + '\\' + sym + y, l)
            else:
                text = l[0]
    text = text.replace('TOBErm', '\\rm')
    text = text.replace('TOBEit', '\\it')
    text = text.replace('TOBEtt', '\\tt')
    text = text.replace('TOBEtext', '\\text')
    text = text.replace('~', ' $\sim$ ')
    text = text.replace('ANDSHARP', '&#')
    return text


def math_text_process(text):
    if text == '':
        return ''
    text = text.replace('&lt;', r'<')
    text = text.replace('&gt;', r'>')
    text = text.replace(r'\textrm', r'\mathrm')
    text = text.replace(r'\textit', r'\TEXTIT')
    text = text.replace(r'\text', r'\mathrm')
    text = text.replace(r'\TEXTIT', r'\textit')
    text = text.replace(r'\lambda', r'TOBELAMBDA')
    text = text.replace(r'\gamma', r'TOBEGAMMA')
    text = text.replace(r'\langle', r'TOBELANGLE')
    text = text.replace(r'\la', r'\lesssim')
    text = text.replace(r'\ga', r'\gtrsim')
    text = text.replace(r'TOBELANGLE', r'\langle')
    text = text.replace(r'TOBELAMBDA', r'\lambda')
    text = text.replace(r'TOBEGAMMA', r'\gamma')
    text = text.replace(r'\msun', r'M_{\odot}')
    text = text.replace(r'\Msun', r'M_{\odot}')
    text = text.replace(r'\Rsun', r'\mathrm{R_\odot}')
    text = text.replace(r'\Rjup', r'\mathrm{R_{jup}}')
    text = text.replace(r'\Mjup', r'\mathrm{M_{jup}}')
    text = text.replace(r'\Pjup', r'\mathrm{P_{jup}}')
    text = text.replace(r'\pjup', r'\mathrm{p_{jup}}')
    text = text.replace(r'\solar', r'\odot')
    text = text.replace(r'\sun', r'\odot')
    text = text.replace(r'\arcdeg', r'^{\circ}')
    text = text.replace(r'\degrees', r'^{\circ}')
    text = text.replace(r'\degree', r'^{\circ}')
    text = text.replace(r'\cm', r'\mathrm{cm}')
    text = text.replace(r'\rsh', r'r_sh')
    text = text.replace(r'\rg', r'r_g')
    text = text.replace(r'\rm', r'\mathrm')
    text = text.replace(r'\kpc', r'\mathrm{kpc}')

    text = text.replace(r'\max', r'\mathrm{max}')
    text = text.replace(r'\min', r'\mathrm{min}')
    text = text.replace(r'\upmu', r'\mathrm{\mu}')
    text = text.replace(r'\GeV', r'\mathrm{GeV}')
    text = text.replace(r'\MeV', r'\mathrm{MeV}')
    text = text.replace(r'\eV', r'\mathrm{eV}')
    text = text.replace(r'\yinit', r'Y_\mathrm{init}')
    text = text.replace(r'\zinit', r'Z_\mathrm{init}')
    text = text.replace(r'\yini', r'Y_\mathrm{ini}')
    text = text.replace(r'\zini', r'Z_\mathrm{ini}')
    text = text.replace(r'\ell', r'l')
    match = re.findall(r'(\\*&.*?;)', text)
    for _ in match:
        text = text.replace(_, ' ')
    return '$%s$' % text


def consider_math(text):
    ravel = text.split('$')
    for idx, _ in enumerate(ravel):
        if idx % 2 == 0:
            ravel[idx] = str(h.unescape(de_symbol(_, '#%^&_\\')).encode('utf-8'))
        else:
            ravel[idx] = math_text_process(_)

    return ''.join(ravel)


def hand_write(imgtitle, imgexpl, rgb, arxiv_item):
    with open('arxivdaily.tex', 'w') as new:
        with open('code/model.tex' , 'r') as model:
            for idx, line in enumerate(model):
                new.writelines(line)
                if '%insert_mix_rgb%\n' == line:
                    new.writelines(r'\definecolor{mix}{RGB}{%d, %d, %d}' %(rgb[0], rgb[1], rgb[2]))
                if '%insert_img_title%\n' == line:
                    new.writelines('%s\\' % imgtitle)
                if '%insert_img_expl%\n' == line:
                    new.writelines('%s' % imgexpl)
                if '%insert_text%\n' == line:
                    for id, _ in enumerate(arxiv_item):
                        # new.writelines('\section{\\normalsize \href{https://arxiv.org%s}{%s}}\n' % (_['pdf'], consider_math(_['title'])))
                        new.writelines('\section{\\normalsize %s}\n' % consider_math(_['title']))
                        new.writelines(r'\small \href{https://arxiv.org%s}{arXiv:%s}~~~' % (_['pdf'], _['pdf'][5:]))
                        new.writelines(r'\small \textcolor{teal}{%s} \\ \\' % _['class'])
                        for i, name in enumerate(_['author']):
                            if i != len(_['author']) - 1:
                                new.writelines('\\small \href{https://arxiv.org%s}{' % name[0])
                                new.writelines(str(h.unescape(name[1]).encode('utf-8')))
                                new.writelines('},~~~~')
                            else:
                                new.writelines(r'\small \href{https://arxiv.org%s}{' % name[0])
                                new.writelines(str(h.unescape(name[1]).encode('utf-8')))
                                new.writelines(r'} \\ \\')

                        # new.writelines(r'\small \textcolor{teal}{arXiv:%s} \\ \\' % _['pdf'][5:])
                        new.writelines(consider_math(_['abstract']))
                        new.writelines('\n')
                    new.writelines(r'\\ \\ \small \textcolor{teal}{End Of File}')


def getCurTime():
    nowTime = time.localtime()
    year = int(nowTime.tm_year)
    month = int(nowTime.tm_mon)
    day = int(nowTime.tm_mday)
    return year, month, day


def get_cover(y=None, m=None, d=None):

    if y is None:
        yesterday = datetime.date.today() - datetime.timedelta(1)
        d = yesterday.day
        m = yesterday.month
        y = yesterday.year - 2000

    url = 'https://apod.nasa.gov/apod/ap%02d%02d%02d.html' % (y, m, d)
    request = urllib2.Request(url)
    print url
    response = urllib2.urlopen(request)
    content = response.read()
    pattern = re.compile(
            '<IMG SRC="(image/\d\d\d\d/.*?)".*?<center>.*?<b> (.*?) </b> <br>.*?<b> Explanation: </b>(.*?)<p> *<center>',
            re.S)
    match = re.findall(pattern, content)
    while match == []:
        y = y-1
        url = 'https://apod.nasa.gov/apod/ap%02d%02d%02d.html'%(y, m, d)
        request = urllib2.Request(url)
        print url
        response = urllib2.urlopen(request)
        content = response.read()
        pattern = re.compile(
                '<IMG SRC="(image/\d\d\d\d/.*?)".*?<center>.*?<b> (.*?) </b> <br>.*?<b> Explanation: </b>(.*?)<p> *<center>',
                re.S)
        match = re.findall(pattern, content)
    imgurl = 'https://apod.nasa.gov/apod/' + match[0][0]
    print imgurl
    imgtitle = match[0][1]
    imgexpl = match[0][2]
    imgexpl = imgexpl.replace('\n', ' ')
    to_remove = re.findall('<.*?>', imgexpl)
    for _ in to_remove:
        imgexpl = imgexpl.replace(_, '')

    if os.path.exists('cover.jpg') is False:
        request = urllib2.Request(imgurl, None)
        response = urllib2.urlopen(request)
        with open('cover.jpg', "wb") as f:
            f.write(response.read())
    else:
        pass

    img = Image.open('cover.jpg')
    imgary = np.array(img)
    ratio = 0.5

    try:
        h, l, rgb = imgary.shape
        r, g, b = 255, 255, 255

    except:
        h, l = imgary.shape
        rgb = None
        r, g, b = 255, 255, 255
    if h > l * ratio:
        box = (0, int((h - ratio * l) / 2), l - 1, int((h + ratio * l) / 2))
    else:
        box = (int((l - h / ratio) / 2), 0, int((l + h / ratio) / 2), h - 1)
    plt.figure(figsize=(20, 20 * ratio))
    if rgb is None:
        plt.imshow(img.crop(box), cmap='gray')
    else:
        plt.imshow(img.crop(box))

    plt.axis('off')
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig('cover.jpg', dpi=200)

    return imgtitle, imgexpl, (r, g, b)


if __name__ == '__main__':
    h = HTMLParser()
    if os.path.exists('arxivdaily.tex'):
        print 'Tex already ready'
    else:
        arxiv_item = scrap()
        imgtitle, imgexpl, rgb = get_cover()
        hand_write(imgtitle, imgexpl, rgb, arxiv_item)




