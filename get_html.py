import re
import requests


def get_content():
    url = "https://arxiv.org/list/astro-ph/new?skip=0&show=2000"
    r = requests.get(url)
    content = r.content
    print 'retrieved'
    pattern = re.compile('<h3>New submissions for (.*?)</h3>(.*?)<h3>Cross-lists for (.*)</h3>(.*?)<h3>', re.S)
    match = re.findall(pattern, content)
    new_sub_date = match[0][0].split(' ')
    new_sub_cont = match[0][1]
    crs_lis_date = match[0][2].split(' ')
    crs_lis_cont = match[0][3]
    return new_sub_date, new_sub_cont, crs_lis_date, crs_lis_cont


def extract_data(content):
    pattern = re.compile('<dt>(.*?)</dt>\n<dd>(.*?)</dd>', re.S)
    dl_list = re.findall(pattern, content)
    p1 = re.compile('">\[(\d*?)\]</a>.*?href="/pdf/(\d*?\.\d*?)"', re.S)
    p2 = re.compile('Title:</span>\s*?(\S.*?)\n</div>.*?Authors:</span>\s*?(\S.*?)</div>.*?"primary-subject">(.*?)</div>.*?"mathjax">(.*?)</p>', re.S)
    p3 = re.compile('<a href="(.*?)">(.*?)</a>', re.S)
    p4 = re.compile('Comments:</span>\s*?(\S.*?)\n</div>')
    p5 = re.compile('\((.*?-.*?)\)')
    out_data = list()
    for idx, _ in enumerate(dl_list):
        match = re.findall(p1, _[0])
        id, arxiv_id = match[0]
        match = re.findall(p2, _[1])
        title, author_block, subject_block, abstract = match[0]
        abstract = abstract.replace('\n', ' ')
        authors = re.findall(p3, author_block)
        subjects = re.findall(p5, subject_block)
        for i, __ in enumerate(subjects):
            subjects[i] = subjects[i].replace('astro-ph.', '')
            subjects[i] = subjects[i].replace('physics.', '')
        try:
            match = re.findall(p4, _[1])
            comments = match[0]
        except:
            comments = None
        out_data.append([id, arxiv_id, title, authors, subjects, abstract, comments])
    return out_data


def write_html(new_sub_date, new_sub_data, crs_lis_date, crs_lis_data):
    f = open("Astrotoday.html", 'w')
    header = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="author" content="Yunyang Li">
    <meta name="description" content="personal research website">
    <link rel="stylesheet" type="text/css" href="all.css">
    <link rel="stylesheet" href="font/fontawesome-all.css">
    <link rel="stylesheet" href="font/css/academicons.css">
    <script src="items.js"></script>
    <script src="all.js"></script>
    <script src="at.js"></script>
    <script type="text/x-mathjax-config">
        MathJax.Hub.Config({tex2jax: {inlineMath: [['$$','$$'], ['$','$']]}});
    </script>
    <script type="text/javascript" async
            src='https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.2/MathJax.js?config=TeX-MML-AM_CHTML'>
    </script>
    <script src="https://ajax.aspnetcdn.com/ajax/jQuery/jquery-3.3.1.min.js">
    </script>
    <title>Yunyang Li | Astro Today</title>
</head>
<body>
<div class="main" id="main">
    <div id="fixed_cover">
        <div id="title">
            <h1>ASTRO TODAY</h1>
            <p> Discoveries and ideas upon the sky and in the field everyday</p>
        </div>
        <div id="bars">
            <div class="clear_float"> <hr class="thin_hr"/> </div>
            <div class="bars" >
                <a href="index.html">
                    <div class="tag_box">
                        <div> HOME </div>
                    </div>
                </a>
                <a href="Vitae.html">
                    <div class="tag_box">
                        <div> VITAE </div>
                    </div>
                </a>
                <a href="Research.html">
                    <div class="tag_box">
                        <div> RESEARCH</div>
                    </div>
                </a>
                <a href="Publications.html">
                    <div class="tag_box">
                        <div> PUBLICATIONS </div>
                    </div>
                </a>
                <a href="Astrotoday.html">
                    <div class="tag_box">
                        <div> ASTROTODAY </div>
                    </div>
                </a>
                <a href="links.html">
                    <div class="tag_box">
                        <div> LINKS </div>
                    </div>
                </a>
            </div>
            <div class="clear_float"> <hr class="thin_hr short_hr"/> </div>
        </div>
        <span id="top"></span>
    </div>
    <div class="fix_all_content">
        <div class="content">
            <div class="at_controller">
                    <button id="refresh_button" title='refresh'>
                        <i class="fa fas fa-redo-alt"></i>
                    </button>
                    <button id="all_button" title='smart fold' onclick="all_collapseFunction()">
                        <i class="fa fas fa-indent"></i>
                    </button>
                
            </div>
    """
    bottom = """
            <div id="top_button">
                <a href="#top" target="_self">
                    <i class="fa fa-angle-double-up"></i>
                </a>
            </div>
            <div class="clear_float"> <hr/> </div>
            <div id="footer" class="clear_float">
                <i class="fa fa-copyright"></i>
                <p>Yunyang Li | Johns Hopkins Univeristy</p>
            </div>
        </div>
    </div>
</div>
</body>
<script>
    $('#refresh_button').click(function(){
    // alert('Im going to start processing');
    $.ajax({
        type:"post",
        url:"cgi-bin/test.py",
        data: {'param':{"hello":"world", "my":"number"}},
        dataType: "json",
        success: function(response)
        {
            alert(response.message);
            // alert(response.keys);
            // alert(response.data);
        }
    });
    // location.reload();
});
</script>
</html>
    """
    f.write(header)
    pre = """
            <div class="at_block tag_div">
                <div class="at_head">
                    NEW SUBMISSIONS %s.%s
                </div>
    """ % (new_sub_date[2], new_sub_date[1])
    end = """
        </div>
    """
    f.write(pre)
    abs_counter = 0
    aut_counter = 0
    for idx, _ in enumerate(new_sub_data):
        author_block = list()
        subject_block = list()
        abstract = _[5]
        for __ in _[3]:
            for key in aut_keyword:
                authors_new = re.sub(r"(.*?%s.*?)" % key, r'<span class="at_highlight">\1</span>', __[1], flags=re.I)
                if __[1] != authors_new:
                    author_block.append('<a href="https://arxiv.org/%s" target="_blank">%s</a>'%(__[0], authors_new))
                    break
            else:
                author_block.append('<a href="https://arxiv.org/%s" target="_blank">%s</a>' % (__[0], __[1]))
        for __ in _[4]:
            subject_block.append('<span class="at_subject at_%s">%s</span>' % (__, __))
        authors = '; '.join(author_block)
        subjects = ''.join(subject_block)
        for _x_ in abs_keyword_s:
            abstract_new = re.sub(r'\b(%s)\b' % _x_, r'<span class="at_highlight">\1</span>', abstract)
            if abstract_new != abstract:
                abs_counter += 1
                abstract = abstract_new
        for _x_ in abs_keyword_i:
            abstract_new = re.sub(r'\b(%s)\b' % _x_, r'<span class="at_highlight">\1</span>', abstract, flags=re.I)
            abstract_new = re.sub(r'\b(%s)\b' % (_x_ + 's'), r'<span class="at_highlight">\1</span>', abstract_new, flags=re.I)
            if abstract_new != abstract:
                abs_counter += 1
                abstract = abstract_new
        item = """
                            <div class="at_item">
                                <div class="at_header">
                                    <div class="at_num"><span>%d</span><button class="ab_button" type="button" title="fold" onclick="collapseFunction()"><i class='fa fas fa-angle-up'></i></button></div>
                                    <div class="at_title">
                                        <span>%s</span>
                                        <div>
                                        <a href="https://arxiv.org/pdf/%s" target="_blank" title='pdf'>
                                            <code class="id">%s</code>
                                        </a>
                                        %s
                                        </div>
                                    </div>
                                </div>
                                <div class="at_content">
                                    <div class="at_authors">
                                        %s
                                    </div>
                                    <div class="at_abstract">%s</div>
                                </div>
                            </div>
                        """ % (idx + 1, _[2], _[1], _[1], subjects, authors, abstract)
        f.write(item)
    f.write(end)
    pre = """
            <div class="at_block tag_div">
                <div class="at_head">
                    CROSS-LISTS %s.%s 
                </div>
        """ % (crs_lis_date[2], crs_lis_date[1])
    end = """
            </div>
        """
    f.write(pre)
    for idx, _ in enumerate(crs_lis_data):
        author_block = list()
        subject_block = list()
        abstract = _[5]
        for __ in _[3]:
            for key in aut_keyword:
                authors_new = re.sub(r"(.*?%s.*?)" % key, r'<span class="at_highlight">\1</span>', __[1], flags=re.I)
                if __[1] != authors_new:
                    author_block.append('<a href="https://arxiv.org/%s" target="_blank">%s</a>'%(__[0], authors_new))
                    break
            else:
                author_block.append('<a href="https://arxiv.org/%s" target="_blank">%s</a>' % (__[0], __[1]))
        for __ in _[4]:
            subject_block.append('<span class="at_subject at_%s">%s</span>'%(__, __))
        authors = '; '.join(author_block)
        subjects = ''.join(subject_block)
        for _x_ in abs_keyword_s:
            abstract_new = re.sub(r'\b(%s)\b' % _x_, r'<span class="at_highlight">\1</span>', abstract)
            if abstract_new != abstract:
                abs_counter += 1
                abstract = abstract_new
        for _x_ in abs_keyword_i:
            abstract_new = re.sub(r'\b(%s)\b' % _x_, r'<span class="at_highlight">\1</span>', abstract, flags=re.I)
            abstract_new = re.sub(r'\b(%s)\b' % (_x_ + 's'), r'<span class="at_highlight">\1</span>', abstract_new, flags=re.I)
            if abstract_new != abstract:
                abs_counter += 1
                abstract = abstract_new
        item = """
                                    <div class="at_item">
                                        <div class="at_header">
                                            <div class="at_num"><span>%d</span><button class="ab_button" type="button" title="fold" onclick="collapseFunction()"><i class='fa fas fa-angle-up'></i></button></div>
                                            <div class="at_title">
                                                <span>%s</span>
                                                <div>
                                                <a href="https://arxiv.org/pdf/%s" target="_blank" title='pdf'>
                                                    <code class="id">%s</code>
                                                </a>
                                                %s
                                                </div>
                                            </div>
                                        </div>
                                        <div class="at_content">
                                            <div class="at_authors">
                                                %s
                                            </div>
                                            <div class="at_abstract">%s</div>
                                        </div>
                                    </div>
                                """%(idx + 1, _[2], _[1], _[1], subjects, authors, abstract)
        f.write(item)
    f.write(end)
    f.write(bottom)
    f.close()

if __name__ == '__main__':
    abs_keyword_i = ['hot gas', 'hot halo', 'neutron star', 'pulsar', 'distance ladder',
    		         'gravitational wave', 'radio', 'fast radio burst', 'merger',
    		         'cosmic microwave', 'Hubble', 'cosmology', 'missing baryon', 'compact object', "Sunyaev-Zel'dovich",
                    'Sunyaev-Zeldovich', 'magnetar']
    abs_keyword_s = ['HST', 'JWST', 'James Webb', 'LISA' 'eLISA', 'CLASS', 'FRB', 'GW', 'CMB', 'LIGO', 'PSR',
                     'Planck', 'WMAP', 'SZ', 'MSP', 'CCO', 'XDINS', 'SGR', 'AXP']
    aut_keyword = ['Bregman, J', 'Yunyang', 'Loeb', 'batygin']
    abs_keyword_i.sort(key=lambda x: -len(x))
    new_sub_date, new_sub_cont, crs_lis_date, crs_lis_cont = get_content()
    new_sub_data = extract_data(new_sub_cont)
    crs_lis_data = extract_data(crs_lis_cont)
    write_html(new_sub_date, new_sub_data, crs_lis_date, crs_lis_data)


