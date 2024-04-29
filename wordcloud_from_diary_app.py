import streamlit as st
import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from wordcloud import WordCloud
from janome.tokenizer import Tokenizer
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
#ローカル
# credentials = Credentials.from_service_account_file("venv/hiramatsudiaryproject-af40bbe80284.json", scopes=scope)
#デプロイ用
credentials = Credentials.from_service_account_info( st.secrets["gcp_service_account"], scopes=[ "https://www.googleapis.com/auth/spreadsheets", ],)

gc = gspread.authorize(credentials)

# スプレッドシートIDを変数に格納する。
SPREADSHEET_KEY = st.secrets["SPREADSHEET_KEY"]
# SPREADSHEET_KEY = "1L65r8Dx8GZpn2qMyCU3V7hg2rZqfFZGMWcOm3j6qJ-0"
# スプレッドシート（ブック）を開く
workbook = gc.open_by_key(SPREADSHEET_KEY)
# シートを開く
sheet = workbook.worksheet('シート1')
data = sheet.get_all_values()
# Pandas DataFrameに変換
df = pd.DataFrame(data)
# 一行目をカラム名にする
df.columns = df.iloc[0]
# 一行目を削除する
df = df[1:]
#テキストから名詞のみを抜き出す関数
def nouns_maker(text):
    tokenizer = Tokenizer()
    noun_list = []
    for token in tokenizer.tokenize(text):
        p = token.part_of_speech.split(",")
        if p[0] == "名詞":
            noun_list.append(token.surface)
    nouns = " ".join(noun_list)
    return nouns

st.title('「頑張った」の図')
st.header("WordCloud from Efficacy!")
with st.form("my_form", clear_on_submit=False):
    line_id = st.text_input('diaryappのユーザーIDを入力して下さい。')
    # スペースや改行があれば削除
    line_id = ''.join(line_id.split())
    submitted = st.form_submit_button("日記を出力")
if submitted:
    try:
        df = df[df.iloc[:, 6] == line_id ]
        # 2列目の値を取得して連結
        concatenated_string = ''.join(df["efficacy"])
        # st.text(concatenated_string)
        wc = WordCloud(width=740, height=520, font_path="ipaexg.ttf", min_font_size=15, max_font_size=110,
                       colormap="Greens")
        wc.generate(nouns_maker(concatenated_string))
        wc.to_file('result.png')
        st.image("result.png")
    except IndexError:
        st.subheader("エラーです。")
        st.text("ユーザーIDを確認してください。  \nLINEのdiaryappの画面で「ユーザーID」と入力すると出てくるよ。")

