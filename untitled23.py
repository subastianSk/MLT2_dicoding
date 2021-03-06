# -*- coding: utf-8 -*-
"""Untitled23.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XKpJxSJNpDMJEIKvwz75WLEfeyEVfHAk

# **Sistem Rekomendasi Filter Aplikasi Bagi Pengguna di Play Store**

## **Pendahuluan**
Pada proyek kedua ini akan dibuat sistem rekomendasi filter aplikasi untuk pengguna di Play Store menggunakan content-based filtering. 
Untuk memudahkan posisi gunakan menu Table of Contents di kanan atas Google Colab

### **1. Mengimpor pustaka/modul python yang dibutuhkan**
"""

# Memasang modul plotly & scikit-learn terbaru
!pip install -U plotly
!pip install -U scikit-learn
!pip install kaggle

# Untuk pengolahan data
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.impute import KNNImputer

# Untuk visualisasi data
import plotly.express as px
from plotly.offline import iplot
import missingno as msno

# Untuk pembuatan sistem rekomendasi 
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity

# Untuk evaluasi sistem rekomendasi
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score

"""### **2. Mempersiapkan Dataset**

2.1 Menyiapkan kredensial akun Kaggle
"""

# upload api kaggle json
from google.colab import files
files.upload() #upload kaggle.json

# Make a directory named “.kaggle”
!mkdir ~/.kaggle

#Copy the “kaggle.json” into this new directory
!cp kaggle.json ~/.kaggle/

! chmod 600 ~/.kaggle/kaggle.json

"""2.2 Mengunduh dan Menyiapkan Dataset"""

# Mengunduh dataset menggunakan Kaggle CLI
!kaggle datasets download -d lava18/google-play-store-apps

# Mengekstrak berkas zip ke direktori aktif saat ini
!unzip /content/google-play-store-apps.zip

"""## **3. Pemahaman Data (Data Understanding)**

3.1 Memuat Data pada sebuah Dataframe menggunakan pandas
"""

# Memuat data pada dataframe di variable df dari file googleplaystore.csv
df = pd.read_csv("/content/googleplaystore.csv")

# Pratinjau dataset
df.tail(3)

"""3.2 Uraian variabel pada dataset yang bakal di eksekusi"""

# Menghitung jumlah data kosong pada setiap kolom
df.isna().sum()

# Memvisualisasikan data kosong pada setiap kolom
sorted_null = msno.nullity_sort(df, sort='ascending') 
figures = msno.matrix(sorted_null, color=(1, 0.43, 0.43))

"""## **4. Persiapan Data (Data Preparation) dan Visualisasi Data**

### 4.1 Pembersihan data pada setiap kolom
4.1.1 Kolom Rating
"""

# Melihat data unik pada kolom rating
df['Rating'].unique()

# Mencari data rating yang nilainya lebih dari 5
df[df['Rating']>5]

# Melakukan penghapusan baris pada index 10472
df.drop(df.index[10472], axis=0, inplace=True)

# Mencari kembali data rating yang nilainya lebih dari 5
if(len(df[df['Rating']>5]) == 0):
  print("Data rating dengan nilai > 5 sudah dihapus")
else:
  print("Data rating dengan nilai > 5 belum dihapus")

# Inisiasi objek KNNImputer dengan nilai tentangga = 5 (sesuai setelan awal)
# Dimana 5 merepresentasikan rentang rating
imputer = KNNImputer()

# Melakukan imputasi pada nilai NaN
df['Rating'] = imputer.fit_transform(df[['Rating']]).ravel()
# Membulatkan nilai hasil imputasi dengan 1 koma
df['Rating'] = df['Rating'].round(decimals=1)

# Mencari data rating yang nilainya kosong

if(df['Rating'].isna().sum() == 0):
  print("Data rating dengan nilai NaN sudah diimputasi")
else:
  print("Data rating dengan nilai NaN belum diimputasi")

"""4.1.2 Kolom Komentar Reviews"""

# Mengubah tipe data kolom reviews menjadi integer
df["Reviews"] = df["Reviews"].astype(int)
df.info()

"""4.1.3 Kolom Size"""

# Melihat data unik pada kolom Size
df['Size'].unique()

# Mengganti nilai pada kolom size
# Menyesuaikan nilai Megabyte
df['Size']= df['Size'].str.replace('M','000')
# Menyesuaikan nilai Kilobyte
df['Size'] = df['Size'].str.replace('k','')
# Mengganti nilai Varies with device menjadi 0
df['Size'] = df['Size'].replace("Varies with device",'0')
# Mengganti tipe data kolom size
df['Size'] = df['Size'].astype('float')

# Mengkonversi seluruh nilai size pada megabyte
for item in df['Size']:
  # Penyesuaian nilai untuk aplikasi dengan ukuran yang kecil
  if item < 10:
      df['Size'] = df['Size'].replace(item, item*1000)
df['Size'] = df['Size']/10000

# Pratinjau hasil
df['Size'].head(5)

"""
4.1.4 Kolom Installs"""

# Melihat data unik pada kolom Installs
df['Installs'].unique()

# Menghapus simbol + dan ,
df['Installs'] = df['Installs'].str.replace('+', '')
df['Installs'] = df['Installs'].str.replace(',', '')
# Mengubah tipe data kolom Installs
df['Installs'] = df['Installs'].astype('int')

# Melihat data unik pada kolom Installs
df['Installs'].unique()

"""4.1.5 Kolom Type"""

# Melihat jumlah data kosong pada kolom Type
df['Type'].isna().sum()

# Mencari data Type = NaN
df[df['Type'].isna()]

# Menghapus data NaN
for index in df[df['Type'].isna()].index:
  df.drop(index, axis=0, inplace=True)

# Mencari kembali data rating yang nilainya lebih dari 5
if(df['Type'].isna().sum() == 0):
  print("Data Type dengan nilai NaN sudah dihapus")
else:
  print("Data Type dengan nilai NaN belum dihapus")

# Melihat data unik pada kolom Installs
df['Price'].unique()

# Menghapus simbol $ 
df['Price'] = df['Price'].str.replace('$', '')
# Mengubah tipe data kolom Price
df['Price'] = df['Price'].astype('float')

# Mengecek informasi dataframe
df.info()

"""4.1.7 Kolom Last Updated Di Play Store"""

# Mengubah tipe data kolom last updated
df['Last Updated'] = pd.to_datetime(df['Last Updated'])
# Melihat hasil perubahan tipe data
df.head(3)

"""4.1.8 Kolom Current Versi"""

# Melihat jumlah data kosong pada kolom Current Ver
df['Current Ver'].isna().sum()

# Mencari data yang nilai Current Ver = NaN
df[df['Current Ver'].isna()]

# Menghapus data NaN
for index in df[df['Current Ver'].isna()].index:
  df.drop(index, axis=0, inplace=True)

"""4.1.9 Kolom Android Versi"""

# Melihat jumlah data kosong pada kolom Android Ver
df['Android Ver'].isna().sum()

# Mencari data yang nilai Android Ver = NaN
df[df['Android Ver'].isna()]

# Menghapus data NaN
for index in df[df['Android Ver'].isna()].index:
  df.drop(index, axis=0, inplace=True)

"""4.2 Pembersihan data duplikasi"""

# Melihat jumlah data duplikasi
df.duplicated().sum()

# Menghapus data duplikasi
df.drop_duplicates(inplace=True)

# Hasil data setelah dibersihkan
df.head(5)

"""# **4.3 Visualisasi Data**"""

# Fungsi untuk plot distribusi data pada suatu kolom numerik
def plot_distribution(column:str, title:str):
  figures = px.histogram(data_frame=df,
                        x=column,
                        color='Type',
                        template='plotly_white',
                        marginal='box',
                        color_discrete_sequence=["#FF7171","#9FD8DF"],
                        barmode='overlay',
                        histfunc='count')

  figures.update_layout(font_family='Open Sans',
                        title=dict(text=title,
                                  x=0.5,
                                  font=dict(color="#333",size=20)),
                        hoverlabel=dict(bgcolor='white'))

  figures.update_xaxes(
      automargin=True
  )

  iplot(figures)

# Fungsi untuk plot bar data pada suatu kolom numerik
def plot_bar(column:str, title:str):
  figures = px.bar(data_frame=df,
                  x="Category",
                  y=column, 
                  color="Type", 
                  barmode="group",
                  template='plotly_white',
                  color_discrete_sequence=["#FF7171","#9FD8DF"])

  figures.update_layout(font_family='Open Sans',
                        title=dict(text=title,
                                  x=0.5,
                                  font=dict(color="#333",size=20)),
                        hoverlabel=dict(bgcolor='white'))

  figures.update_xaxes(
      automargin=True
  )

  iplot(figures)

# Fungsi untuk plot pie data pada suatu kolom numerik
def plot_category(column:str, title:str):
  figures = px.sunburst(df,
                      path=["Type","Content Rating",column],
                      color="Installs", 
                      color_continuous_scale=["#9FD8DF","#FF7171"])

  figures.update_layout(font_family='Open Sans',
                        title=dict(text=title,
                                   x=0.5,
                                   font=dict(color="#333",size=20)),
                        title_y=0.96)

  figures.update_traces(hovertemplate="Labels = %{label}<br>Count = %{value}<br>Installed = %{color:.0f} <extra></extra>")

  figures.update_xaxes(
      automargin=True
  )

  iplot(figures)

"""4.3.1 Fitur Numerik"""

# Menampilkan visualisasi data
for column in ["Rating","Size"]:
    plot_distribution(column=column, title=f"Distribusi fitur numerik pada kolom {column}")

# Menampilkan visualisasi data
for column in ["Reviews","Price"]:
    plot_bar(column=column, title=f"Distribusi label {column} dengan label kategori<br>Berdasarkan tipe aplikasi")

"""4.3.2 Fitur Kategori"""

# Menampilkan visualisasi data
for column in ["Category","Genres"]:
    plot_category(column=column, title=f"Distribusi label {column}, Rating Aplikasi dan Tipe Aplikasi<br>Berdasarkan jumlah pengunduh")

# Klik area dalam chart untuk melihat persebaran data yang lebih lengkap

"""4.4 Restrukturisasi Data

4.4.1 Menghapus kolom yang tidak diperlukan
"""

# Menghapus kolom Current Ver
df.drop('Current Ver',inplace=True,axis=1)
df.head()

# Menghapus kolom Last Updated
df.drop('Last Updated',inplace=True,axis=1)
df.head()

# Menyimpan nama-nama aplikasi pada dataframe baru
df_app_name = pd.DataFrame({'App':df['App']})
df_app_name.head()

# Menggunakan kolom aplikasi sebagai index
df.set_index('App',inplace=True)
df.head()

"""4.4.2 Konversi label kategori menjadi one-hot encoding"""

# Memilih semua kolom dengan tipe data object
column_object = df.dtypes[df.dtypes == 'object'].keys()
column_object

# Mengkonversi data kategori ke one-hot encoding
one_hot_label = pd.get_dummies(df[column_object])
one_hot_label.head(3)

# Menghapus kolom dengan tipe data object
df.drop(column_object,axis=1,inplace=True)
df.head()

# Menyatukan one hot encoding dengan seluruh data
df = pd.concat([df,one_hot_label],axis=1)
df.head()

"""4.4.2 Standarisasi label numerik"""

# Memilih semua kolom dengan tipe data integer
column_int = df.dtypes[df.dtypes == 'int64'].keys()
column_int

# Memilih semua kolom dengan tipe data float
column_float = df.dtypes[df.dtypes == 'float64'].keys()
column_float

# Menyatukan semua kolom dengan tipe data numerik
column_numeric = list(column_int) + list(column_float)
column_numeric

# Inisiasi minmaxscaler
scaler = MinMaxScaler()

# Melakukan standarisasi data
scaled = scaler.fit_transform(df[column_numeric])

# Mengganti data numerik dengan data yang sudah
# di standarisasi
i=0
for column in column_numeric:
    df[column] = scaled[:,i]
    i += 1

# Melihat hasil standarisasi data
df.head()

# Menginspeksi data
df.describe()

"""# **5. Pembuatan Sistem Rekomendasi Content Based Filtering**
**5.1 Dengan model K-Nearest Neighbor**
"""

# Membuat sistem rekomendasi dengan model K-Nearest Neighbor
# Inisiasi model 
model = NearestNeighbors(metric='euclidean')

# Melakukan fitting model terhadap data
model.fit(df)

# Membuat fungsi untuk mendapatkan rekomendasi
# Dengan model KNN
def getRecommendedApps_model(appname:str, recommend_apps:int=5):
  print(f'Apabila pengguna menyukai aplikasi {appname[0]}\n5 aplikasi berikut ini juga mungkin akan disukai :')
  # Mencari aplikasi terdekat dengan aplikasi yang disukai pengguna
  distances, neighbors = model.kneighbors(df.loc[appname],n_neighbors=recommend_apps)
  # Memasukkan aplikasi yang sama pada sebuah list
  similar_app = []
  for appname in df_app_name.loc[neighbors[0][:]].values:
    similar_app.append(appname[0])
  # Memasukan skornya (jarak) pada sebuah list
  similar_distance = []
  for distance in distances[0]:
    similar_distance.append(f"{round(100-distance, 2)}%")
  # Mengembalikan sebuah dataframe berupa rekomendasi terhadap aplikasinya
  return pd.DataFrame(data = {"Nama Aplikasi" : similar_app, "Tingkat Kesamaan" : similar_distance})

# Memberikan rekomendasi terhadap aplikasi yang
# Serupa dengan Natural recipes for your beauty
getRecommendedApps_model(df_app_name.loc[100])

"""5.2 Dengan Cosine Similarity"""

# Menghitung cosine similarity dari dataframe
cosine_sim = cosine_similarity(df)

# Menyimpan hasil perhitungan pada dataframe
cosine_sim_df = pd.DataFrame(cosine_sim, index=df_app_name['App'], columns=df_app_name['App'])
cosine_sim_df.head(3)

# Membuat fungsi untuk mendapatkan rekomendasi
# Dengan Cosine Similarity
def getRecommendedApps_cosine(appname:str, recommended_apps:int=5):
  print(f'Apabila pengguna menyukai aplikasi {appname[0]}\n5 aplikasi berikut ini juga mungkin akan disukai :')
  # Mencari nilai unik pada aplikasi yang disukai pengguna di baris dataframe cosine sim
  # Nilai unik (arr) dikembalikan dalam bentuk yang berurutan dari kecil ke besar 
  arr, ind = np.unique(cosine_sim_df.loc[appname[0]], return_index=True)
  # Memasukkan nama aplikasi yang serupa dari index kedua terakhir sampai index n terakhir
  similar_app = []
  for index in ind[-(recommended_apps+1):-1]:
    similar_app.append(df_app_name.loc[index][0])
  # Memasukkan skor cosine dari aplikasi yang serupa mulai dari index kedua terakhir sampai index n terakhir
  cosine_score = []
  for score in arr[-(recommended_apps+1):-1]:
    cosine_score.append(score)
  # Mengembalikan sebuah dataframe berupa rekomendasi terhadap aplikasinya
  return pd.DataFrame(data = {"Nama Aplikasi" : similar_app, "Cosine Similarity" : cosine_score}).sort_values(by='Cosine Similarity',ascending=False)

# Memberikan rekomendasi terhadap aplikasi yang
# Serupa dengan Natural recipes for your beauty
getRecommendedApps_cosine(df_app_name.loc[100])

"""6. Evaluasi Model K-Nearest Neighbor

6.1 Skor Calinski Harabasz
"""

calinski_harabasz_score(df, df_app_name)

# 6.2 Skor Davies Bouldin

davies_bouldin_score(df, df_app_name)

"""Penutupan
Model untuk memberikan rekomendasi aplikasi untuk pengguna di Google Play Store telah selesai dibuat. Setelah diujikan, model ini bekerja cukup baik dalam memberikan 5 rekomendasi teratas terhadap aplikasi yang disukai/diunduh pengguna. Namun demikian, masih ada beberapa kekurangan dari model yang dibuat seperti yang terlihat pada skor Calinski Harabasz dan Davies Bouldin. Untuk memperbaikinya dapat digunakan algoritma untuk membuat model rekomendasi yang lain seperti menggunakan deep learning lalu dibandingkan performanya dengan model KNN saat ini.

Referensi
Dokumentasi Scikit-learn : https://scikit-learn.org/stable/modules/classes.html
Dokumentasi Plotly : https://plotly.com/python/
Lainnya :
https://www.kaggle.com/ludovicocuoghi/]
https://www.kaggle.com/nandalald/android-app-recommendation
"""