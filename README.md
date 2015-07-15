horesase
========

# 惚れさせプロト1

IDを入力すると、惚れさせ男子の名言を表示します。

データベースは以下を利用しています。
- 惚れさせ男子データベース
- https://github.com/june29/horesase-boys


## misawa-matcher実行環境 - Ubuntu 14.04, python3.4(64bit)
### pythonのバージョンについて
`python3`でpython3.xを起動。
pipは`pip3`でpython3.xのpipが実行できる。

### 各種アプリのインストール
mecabの辞書は必ずutf8を入れること。
デフォルトはeuc-jpで、UnicodeDecodeErrorrを吐いて死ぬ。
↓でおｋ。
```sh
sudo apt-get install python3.4
sudo apt-get install python3-pip
sudo apt-get install mecab
sudo apt-get install mecab-ipadic-utf8
sudo apt-get install libmecab-dev
```

### pythonライブラリのインストール
```sh
sudo pip3 install nltk
sudo pip3 install tweepy
sudo pip3 install pyyaml
```

### mecab-pythonのインストール
```sh
sudo pip3 install mecab-python3
```
上記で無理なら、

```sh
wget https://mecab.googlecode.com/files/mecab-python-0.996.tar.gz
tar -zxvf mecab-python-0.996.tar.gz
cd mecab-python-0.996
```
でsetup.pyを
```python
def cmd2(str):  
    return string.split (cmd1(str))  
```
から↓に修正。
```python
def cmd2(str):  
    return cmd1(str).split()  
```
修正後、
```sh
sudo pip3 install -e .
```

## misawa-matcher実行環境 - Amazon Linux, python3.4(64bit)
### mecab, ipadicのインストール
```sh
`# mecab本体のインストール`
wget https://mecab.googlecode.com/files/mecab-0.996.tar.gz
tar zxvf mecab-0.996.tar.gz
cd mecab-0.996
./configure --with-charset=utf-8
make
sudo make install
sudo bash -c 'echo "/usr/local/lib" >> /etc/ld.so.conf.d/usr-local.conf'

`# 設定の読み直し`
sudo ldconfig

`# ipadicのインストール`
wget https://mecab.googlecode.com/files/mecab-ipadic-2.7.0-20070801.tar.gz
tar zxvf mecab-ipadic-2.7.0-20070801.tar.gz
cd mecab-ipadic-2.7.0-20070801
./configure --with-charset=utf-8
make
sudo make install
```
### pythonライブラリのインストール
pip3は適宜絶対パスで実行するとトラブルが少ない
```sh
which pip3
sudo /usr/local/bin/pip3 install `package name`
```

### mecab-pythonのインストール
setup.pyで下記の変更
```python
def cmd2(str):  
    return string.split (cmd1(str))  
```
に加え、`mecab-config`を絶対パスに置換
(`which mecab-config`などで調べる)
e.g) mecab-config -> /usr/local/bin/mecab-config

## misawa-matcher実行環境 - windows8.1, python3.4(64bit)
[この記事](http://qiita.com/ykchat/items/97dd7be100bfa837b7c4)が参考になる。
python64bitの場合、mecabのビルドが必要。

### pythonのバージョンについて
windowsのpythonはpy.exeで簡単にバージョンが切り替えられる。
```dos
REM python2系が起動
py -2 "file name"
REM python3系が起動
py -3 "file name"
```
デフォルトで起動するバージョンは環境変数`PY_PYTHON`で指定可能。
pipは各バージョンのインストールディレクトリにあり、
絶対パスで実行かインストールディレクトリに移動して実行すればおｋ。

### MeCabビルド
visual studioは2008でなくとも大丈夫（vs2012でもイケた）。
vsのインストールディレクトリのbatを叩き、ビルドする。
vs2012の場合は以下。
```bat
C:\Program Files (x86)\Microsoft Visual Studio 11.0\VC\bin\x86_amd64\vcvarsx86_amd64.bat
nmake -f Makefile.msvc.in
```

ただし、makefileは適宜修正する。
特に辞書のバージョン番号を埋め込む必要があるので注意。
```Makefile
LDFLAGS = /nologo /OPT:REF /OPT:ICF /LTCG /NXCOMPAT /DYNAMICBASE /MACHINE:X64 ADVAPI32.LIB
DEFS =  -D_CRT_SECURE_NO_DEPRECATE -DMECAB_USE_THREAD \
        -DDLL_EXPORT -DHAVE_GETENV -DHAVE_WINDOWS_H -DDIC_VERSION=102 \
```

### mecab-pythonのビルド
こちらもvs2012でイケる。
その前にsetup.pyで、
```python
def cmd2(str):
    return string.split (cmd1(str))
```
を次に変更する
```python
def cmd2(str):
    return cmd1(str).split()
```
参考: http://anond.hatelabo.jp/20121113070853

からの、
```bat
C:\Program Files (x86)\Microsoft Visual Studio 11.0\VC\bin\x86_amd64\vcvarsx86_amd64.bat
py -3 setup.py bdist_wininst
```
作成したlibmecab.dllをpython34/Lib/site-packages以下にコピペ。
またMeCabインストール時、辞書はutf-8にしないとUnicodeDecodeErrorrを吐くので注意。
が、辞書をutf-8にするとコマンドラインで文字化けするジレンマ。現状nkfをかますか、ファイルに出力するしかない。

### pythonライブラリのインストール
windowsは[インストーラ](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pip)があり、exeを叩けば勝手に入る。
しかもMKLでビルドされているので高速。numpyやscipyはここから入れると良い。
ビルドが必要なモノ以外はpipでも普通に入る。


## misawa-matcherの実行方法
linux:`python3 matcher_main.py 'sentence'`  
windows:`py -3 matcher_main.py 'sentence'`
mac: `python matcher_main.py 'sentence'`

事前にjsonを解析した結果を'meigenWords.bin'に保存している。
初回実行時など'meigenWords.bin'がない場合、
jsonをダウンロードして解析を実行するため時間がかかる。

## TODO
* import時間の問題
  - nltkのロードに3秒程度要する
* LDAの導入・ドラム問題の解消
  - 現状一致するワードが一切ない場合、ドラムのミサワ（初期値）が表示
  - LDAで解消するか、場合によってはランダム表示で切り抜けるか
