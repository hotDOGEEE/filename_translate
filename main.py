import pathlib
import requests
import re
import argparse
import os
from stardict import DictCsv

re_hiragana = re.compile(u"[\u3040-\u309f]+")
re_katakana = re.compile(u"[\u30a0-\u30ff]+")
re_en = re.compile(r'[A-Za-z]')
ban_str = r'\/:*?"<>|'


csvname = os.path.join(os.path.dirname(__file__), 'ecdict.csv')
dc = DictCsv(csvname)


def translate(query):

    def local_trans():
        check_rst = dc.query(query)["translation"]
        rst = check_rst.find(",")
        return check_rst[3:rst]

    def youdao():
        rh = re.findall(re_hiragana, query)
        rk = re.findall(re_katakana, query)
        ren = re.findall(re_en, query)
        if rh or rk or ren:
            url = 'http://fanyi.youdao.com/translate'
            data = {
                "i": query,  # 待翻译的字符串
                "from": "ja",
                "to": "zh-CHS",
                "smartresult": "dict",
                "client": "fanyideskweb",
                "doctype": "json",
                "version": "2.1",
                "keyfrom": "fanyi.web",
                "action": "FY_BY_REALTIME"
            }
            res = requests.post(url, data=data).json()
            return res['translateResult'][0][0]['tgt']
        else:
            return query
    try:
        return local_trans()
    except:
        try:
            return youdao()
        except Exception as e:
            print(e, "免费接口用完了")
            return query


def language_confirm(file_name:str):
    def _en_dispose():
        replace_name = str()
        fn = file_name.split("_")
        f_postfix = fn[-1]
        fn = fn[:-1]
        for w in fn:
            trans_w = translate(w)
            replace_name += trans_w +"_"
        replace_name = replace_name[:-1]
        full_name = replace_name + f_postfix
        return full_name

    def _jp_dispose():
        replace_name = str()
        ig_index = file_name.find("□")
        f_postfix = file_name[ig_index:]
        fn = file_name[:ig_index]
        words = fn.split("_")
        for w in words:
            if "◇" in w:
                spec = w.split("◇")
                s0 = translate(spec[0])
                s1 = translate(spec[1])
                joint = s0 + "◇" + s1
                replace_name += joint
            else:
                replace_name += translate(w) + "_"
        full_name = replace_name + f_postfix
        for b in ban_str:
            if b in full_name:
                full_name = full_name.replace(b, "")
        return full_name
    rh = re.findall(re_hiragana, file_name)
    rk = re.findall(re_katakana, file_name)
    if rh or rk:
        return _jp_dispose()
    else:
        return _en_dispose()


def main(path):
    source_path = pathlib.Path(path)
    for dir in source_path.rglob(""):
        files = [x for x in dir.iterdir() if x.is_file()]
        for f in files:
            rename_data = language_confirm(f.name)
            f.rename(dir / rename_data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="传入翻译文件夹路径")
    parser.add_argument("--path", type=str, default=r"D:\tools\ic_file\ICChat Files\huxu\files\test_rename")
    args = parser.parse_args()
    main(args.path)