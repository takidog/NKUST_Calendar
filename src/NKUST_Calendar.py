import subprocess
import json
import re
from datetime import datetime
from datetime import timedelta
'''
PDF parser tool.

https://github.com/pdfminer/pdfminer.six
pip3 install pdfminer.six
'''
# from tool import pdf2txt   # from pdfminer.six


class NKUST_Calendar:
    def __init__(self, file, term_year):
        self.res = {}
        self.week_start_days = None
        data = None
        try:
            data = self.raw_calendar_decode(file=file)
        except Exception as e:
            print(e)
            print('error in raw_calendar_decode')
        if data != None:
            self.speculate_calendar(data, tw_year=term_year)

    def raw_calendar_decode(self, file):
        """input a pdf file, and use regex simply split.

        Args:
            file (str): path, e.g. "1.pdf", "/var/www/wow/1.pdf"

        Returns:
            [dict]: {
                data:[list]
            }
        # Why not return list ?
        # maybe in future, it will add more information.
        """
        process = subprocess.Popen(
            ['pdf2txt.py', file], stdout=subprocess.PIPE)
        raw_pdf_text, err = process.communicate()

        raw_pdf_text = raw_pdf_text.decode('utf-8')
        raw_pdf_list = raw_pdf_text.split('\n')
        self.raw_list = raw_pdf_list
        # get office name dict
        for i in raw_pdf_list:
            if i.find('單位簡稱') > -1:
                unit_text = i
                break
        replace_dict = {}
        for unit in unit_text[unit_text.find('單位簡稱: ')+6::].replace(' ', '').split('/'):
            replace_text, office = unit.split('-')
            replace_dict[replace_text] = office

        res = {'data': []}
        for i in raw_pdf_text.split('\n'):

            if re.match('.{0,7}([0-9]{1,2}/[0-9]{1,2})', i) != None and i.find('單位簡稱') == -1:

                for k, v in replace_dict.items():
                    if i.find(k) > -1:
                        break

                res['data'].append({'office': v, 'info': i[i.find('(')::]})

        return res

    def json_make(self, date, info, office):
        """Convert date to weeks , self.week_start_days can't be None 

        Args:
            date (datetime.datetime): date form the raw info , use regex to split. 
            info (str): events info.
            office (str): form whitch office.
        """
        week = 0
        if self.week_start_days != None:
            week = int(((date-self.week_start_days).days)/7)+1

        if week > 18:  # will next term
            if date.month == 1:
                week = '寒'
            elif date.month == 7 or date.month == 6:
                week = '暑'
            else:
                if week not in ['寒', '暑']:
                    week = 0

        if date.month == 8:
            week = '暑'

        if (date.month == 9 or date.month == 2) and week == 0:
            week = '預備週'

        if self.res.get(str(week)) != None:
            self.res[str(week)]['events'].append(info)

            # self.res[date.strftime("%Y%m%d")]['events'].append({'office':office,'events':info}) for feature
        else:
            self.res[str(week)] = {'events': [info]}

    def get_json(self):
        """get json , It will return json format for App ver.3.0.0 or higher

        Returns:
            str : json format.
        """
        replace_char = {
            '0': '不可能出現的周，出現表示該修了QQ',
            '1': '第一週',
            '2': '第二週',
            '3': '第三週',
            '4': '第四週',
            '5': '第五週',
            '6': '第六週',
            '7': '第七週',
            '8': '第八週',
            '9': '第九週',
            '10': '第十週',
            '11': '第十一週',
            '12': '第十二週',
            '13': '第十三週',
            '14': '第十四週',
            '15': '第十五週',
            '16': '第十六週',
            '17': '第十七週',
            '18': '第十八週',
            '暑': '暑',
            '寒': '預備週',
            '預備週': '預備週'
        }
        res_json = []
        for k, v in self.res.items():

            tmp = {'week': replace_char[k], 'events': []}
            for event in v['events']:
                tmp['events'].append(event.replace('\n', ''))
            res_json.append(tmp)
        return json.dumps(res_json, ensure_ascii=False)

    def speculate_calendar(self, data, tw_year=(datetime.now().year-1911)):
        """do more regex, and find the school start day.

        Args:
            data ([dict]): from raw_calendar_decode return value.
            tw_year (int): since KMT lose their "China", come to Taiwan's year. :P
                           now.year - 1911 you will get this value. 
        """
        # same_year_list = ['8','9','10','11','12']  #these months are in the same term years
        next_year_list = ['1', '2', '3', '4', '5', '6', '7']  # year +1
        for i in data['data']:
            year = tw_year+1911
            info = i['info']
            date_info = info[info.find('(')+1:info.find(')')]
            # print(date_info,i['info'])
            if re.match('^[0-9]{1,2}/[0-9]{1,2}', date_info) != None:
                'only match   (01/01 )...events_info...   just single day '
                date_info = re.match(
                    '^[0-9]{1,2}/[0-9]{1,2}', date_info).group(0)
                if date_info[0:date_info.find('/')] in next_year_list:
                    year += 1
                day = datetime.strptime(
                    '%s %s' % (year, date_info), '%Y %m/%d')

                if i['info'].find('開始上課') > -1:
                    diff = timedelta(days=day.isoweekday())
                    self.week_start_days = day-diff
                info = info.replace('-', ' ~ ')

                self.json_make(date=day, info=info, office=i['office'])


if __name__ == "__main__":

    data = NKUST_Calendar('cal108-1.pdf', term_year=108).get_json()
    print(data)
