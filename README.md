# **NKUST_Calendar**

將pdf行事曆轉換成json

## Install

```bash
pip3 install -r requirement.txt
```

*Only test in Python3

## Use

1. 先行下載學校[行事曆](https://www.nkust.edu.tw/p/404-1000-4622.php)pdf檔案



```bash
python3 NKUST_Calender.py cal108-1.pdf 108
```

* args[1]  pdf file path.
* args[2] term year 填入這份行事曆的學期年，帶錯會造成周次計算有差

or 

```python
python3 NKUST_Calender.py

file path : 
>>> cal108-1.pdf
term year (e.g. 107, 108 ) :
>>> 108
```



```
save file ? (y/n) 
```



輸出存檔



##目前經過測試的行事曆檔案 

160007259 / 106188010

cal107-1  / cal107-2 

cal108-1 / cal108-2

= U = 



