# -*- coding: utf-8 -*-

# -- Sheet --

####Görev1
##adım 1:flo_data_20K.csv verisini okuyunuz.Dataframe’in kopyasını oluşturunuz

!pip install openpyxl

import numpy as np
import pandas as pd
import datetime as dt
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.float_format', lambda x: '%.4f' %x)



df=pd.read_csv('flo_data_20k.csv')

df=df.copy()
df.head()
df.info()

####adım2:Veri setinde
#a. İlk 10 gözlem,
#b. Değişken isimleri,
#c. Betimsel istatistik,
#d. Boş değer,
#e. Değişken tipleri, incelemesi yapınız


df.head(10)
df.columns
df.describe().T

df.shape

df.isnull().sum()

#Adım 3: Omnichannel müşterilerin hem online'dan hemde offline platformlardan alışveriş yaptığını ifade etmektedir. Her bir müşterinin toplam
#alışveriş sayısı ve harcaması için yeni değişkenler oluşturunuz

df["total_shopping"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df.head()
df["total_shopping"]
df.columns


df["total_value"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]
df["total_value"].head()
df.columns

##Adım 4: Değişken tiplerini inceleyiniz. Tarih ifade eden değişkenlerin tipini date'e çeviriniz

date_columns = df.columns[df.columns.str.contains("date")]

df[date_columns] = df[date_columns].apply(pd.to_datetime)

df.info()

##Adım 5: Alışveriş kanallarındaki müşteri sayısının, toplam alınan ürün sayısının ve toplam harcamaların dağılımına bakınız

df.groupby("order_channel").agg({"total_shopping" :["sum","count"],
                                "total_value" :["sum","mean"]})

####Adım 6: En fazla kazancı getiren ilk 10 müşteriyi sıralayınız

df.sort_values(by="total_value",ascending=False).head(10)

##Adım 7: En fazla siparişi veren ilk 10 müşteriyi sıralayınız

df.sort_values(by="total_shopping",ascending=False).head(10)

###Adım 8: Veri ön hazırlık sürecini fonksiyonlaştırınız
def data_prep(dataframe):
    df["total_shopping"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
    df["total_value"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]

    date_columns = df.columns[df.columns.str.contains("date")]
    df[date_columns] = df[date_columns].apply(pd.to_datetime)
    return df
data_prep(df)



##Görev2:
###: Recency, Frequency ve Monetary tanımlarını yapınız.
##Adım 2: Müşteri özelinde Recency, Frequency ve Monetary metriklerini hesaplayınız.
###Adım 3: Hesapladığınız metrikleri rfm isimli bir değişkene atayınız.
###Adım 4: Oluşturduğunuz metriklerin isimlerini recency, frequency ve monetary olarak değiştiriniz.

today_date = df.last_order_date.max() + pd.DateOffset(day=2)

df["recency"] = (today_date-df["last_order_date"])
df["frequency"] = df["total_shopping"]
df["monetary"] = df["total_value"]
rfm = df[["master_id", "recency", "frequency", "monetary"]]


rfm.dtypes

rfm.head()

rfm = rfm.sort_values(by="master_id",ascending=True)
rfm.head(10)

##Görev 3: RF Skorunun Hesaplanması
##Adım 1: Recency, Frequency ve Monetary metriklerini qcut yardımı ile 1-5 arasında skorlara çeviriniz. 
##Adım 2: Bu skorları recency_score, frequency_score ve monetary_score olarak kaydediniz.
##Adım 3: recency_score ve frequency_score’u tek bir değişken olarak ifade ediniz ve RF_SCORE olarak kaydediniz.

rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])



rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))

rfm.describe().T





###görev4
##Adım 1: Oluşturulan RF skorları için segment tanımlamaları yapınız.
##Adım 2: Aşağıdaki seg_map yardımı ile skorları segmentlere çeviriniz

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}


rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
rfm



##GÖREV5
#Adım 1: Segmentlerin recency, frequnecy ve monetary ortalamalarını inceleyiniz.
#Adım 2: RFM analizi yardımıyla aşağıda verilen 2 case için ilgili profildeki müşterileri bulun ve müşteri id'lerini csv olarak kaydediniz.
#a. FLO bünyesine yeni bir kadın ayakkabı markası dahil ediyor. Dahil ettiği markanın ürün fiyatları genel müşteri
#tercihlerinin üstünde. Bu nedenle markanın tanıtımı ve ürün satışları için ilgilenecek profildeki müşterilerle özel olarak
#iletişime geçmek isteniliyor. Sadık müşterilerinden(champions, loyal_customers) ve kadın kategorisinden alışveriş
#yapan kişiler özel olarak iletişim kurulacak müşteriler. Bu müşterilerin id numaralarını csv dosyasına kaydediniz.
#b. Erkek ve Çocuk ürünlerinde %40'a yakın indirim planlanmaktadır. Bu indirimle ilgili kategorilerle ilgilenen geçmişte
#iyi müşteri olan ama uzun süredir alışveriş yapmayan kaybedilmemesi gereken müşteriler, uykuda olanlar ve yeni
#gelen müşteriler özel olarak hedef alınmak isteniyor. Uygun profildeki müşterilerin id'lerini csv dosyasına kaydediniz

##1

rfm.groupby("segment")["recency","monetary","frequency"].mean()

###2
target_segments_customer_ids = rfm[rfm["segment"].isin(["champions","loyal_customers"])]["master_id"]
cust_ids = df[(df["master_id"].isin(target_segments_customer_ids)) &(df["interested_in_categories_12"].str.contains("KADIN"))]["master_id"]
cust_ids.to_csv("yeni_marka_hedef_müşteri_id.csv", index=False)
cust_ids.shape

rfm.head()


target_segments_customer_ids = rfm[rfm["segment"].isin(["cant_loose","hibernating","new_customers"])]["master_id"]
cust_ids = df[(df["master_id"].isin(target_segments_customer_ids)) & ((df["interested_in_categories_12"].str.contains("ERKEK"))|(df["interested_in_categories_12"].str.contains("COCUK")))]["master_id"]
cust_ids.to_csv("indirim_hedef_müşteri_ids.csv", index=False)
cust_ids.head()



