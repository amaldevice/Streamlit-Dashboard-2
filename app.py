import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import warnings
warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt
import seaborn as sns
import google.generativeai as genai
import PIL.Image
import io

# Konfigurasi Google Generative AI
genai.configure(api_key="AIzaSyDQfpY0Oo-Qv_V1szhqXKSfAedCKA1czTc")
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# Judul aplikasi
st.title('Tools Automasi Statistik Deskriptif dan Analisis Data Dasar')

# Upload file
uploaded_file = st.file_uploader("Upload file CSV atau Excel", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            separator = st.text_input("Masukkan separator yang digunakan dalam file CSV (misalnya, ',' atau ';')", value=',')
            if separator:  # Pastikan separator telah diisi
                df = pd.read_csv(uploaded_file, sep=separator)
                st.success("File CSV berhasil dibaca!")
            else:
                df = None
                st.warning("Silakan masukkan separator yang digunakan dalam file CSV.")
        elif uploaded_file.name.endswith('.tsv'):
            df = pd.read_csv(uploaded_file, sep='\t')
        elif uploaded_file.name.endswith('.xlsx'):
            excel_file = pd.ExcelFile(uploaded_file)
            sheet_name = st.selectbox("Pilih nama sheet yang akan digunakan:", excel_file.sheet_names)
            if sheet_name:  # Pastikan sheet telah dipilih
                df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                st.success("File Excel berhasil dibaca!")
            else:
                df = None
                st.warning("Silakan pilih nama sheet yang akan digunakan.")
        else:
            st.error("Format file tidak didukung!")
            df = None
    except Exception as e:
        st.error(f"Error membaca file: {e}")
        df = None

    if df is not None:
        # Menampilkan dataframe
        st.subheader('Menampilkan Dataframe Awal :')
        st.write("Ukuran dan Bentuk Data : ", df.shape)
        st.write("Dataframe:")
        st.write(df)

        st.subheader('Pembersihan Data Frame')
        st.write("Melakukan Pembersihan Data Frame!")
        df.dropna(inplace=True)
        st.write("Pembersihan Data Frame Selesai!")
        
        # Checkbox untuk melewati pemilihan kolom tanggal
        skip_date_selection = st.checkbox('Lewati pemilihan kolom tanggal')

        if not skip_date_selection:
            tanggal = st.multiselect('Pilih kolom yang berisi data tanggal:', df.columns)
            if tanggal:  # Hanya lanjutkan jika kolom tanggal telah dipilih
                for tgl in tanggal:
                    df[tgl] = pd.to_datetime(df[tgl])
                
                st.write("Dataframe setelah pemformatan tanggal:")
                st.write(df)
            else:
                st.warning("Silakan pilih kolom yang berisi data tanggal untuk melanjutkan, atau centang 'Lewati pemilihan kolom tanggal'.")
        else:
            st.write("Pemilihan kolom tanggal dilewati.")

        # Lanjutkan dengan operasi lain setelah pemilihan kolom tanggal atau melewatinya
        st.subheader('Operasi Lain Setelah Pemilihan Kolom Tanggal')
        # Tambahkan operasi lain di sini
        st.write("Lanjutkan dengan operasi lain...")
        
        st.write("Dataframe:")
        st.write(df)

        numeric = df.select_dtypes(include=['int', 'float'])
        categorical = df.select_dtypes(include=['object'])
        for x in categorical.columns:
            if categorical[x].nunique() > 10:
                categorical.drop(x, axis=1, inplace=True)
        # Statistik deskriptif
        st.write("Statistik Deskriptif:")
        st.write(df.describe())

        # Visualisasi Korelasi
        st.subheader('Visualisasi Korelasi:')
        plt.figure(figsize=(12, 10))
        sns.heatmap(numeric.corr(), annot=True, cmap='coolwarm')
        st.pyplot(plt)
        plt.clf()  # Membersihkan plot sebelumnya

        # Visualisasi distribusi kolom
        st.subheader('Visualisasi Distribusi Data:')
        st.write("Visualisasi Distribusi Kolom:")
        column = st.selectbox("Pilih kolom untuk visualisasi distribusi:", numeric.columns)
        plt.figure(figsize=(12, 10))
        sns.histplot(numeric[column], kde=True)
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        st.pyplot(plt)
        img_buffer.seek(0)
        plt.clf()  # Membersihkan plot sebelumnya

        # Load the image from the BytesIO object
        img = PIL.Image.open(img_buffer)

        st.write("Interpretasi dari Google Generative AI:")
        try:
            response = model.generate_content([
                """Berdasarkan hasil analisis plot di atas, insight apa yang dapat diperoleh dari pola yang terlihat dan hubungan antar variabel? 
                Berikan rekomendasi tindakan yang dapat diambil serta langkah-langkah selanjutnya berdasarkan temuan tersebut. Buatkan penjelasannya dalam bahasa indonesia""",
                img
            ])
            response.resolve()
            st.write(response.text)
        except Exception as e:
            st.error(f"Error generating content: {e}")
        plt.clf()  # Membersihkan plot sebelumnya


        # Visualisasi countplot
        st.subheader('Visualisasi Countplot :')
        column = st.selectbox("Pilih kolom untuk visualisasi countplot:", categorical.columns)
        plt.figure(figsize=(12, 10))
        ax = sns.countplot(data=categorical, x=column)
        # Menambahkan label di atas setiap bar
        for p in ax.patches:
            ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='baseline', fontsize=12, color='black', xytext=(0, 5), 
                        textcoords='offset points')
        plt.tight_layout()  # Pastikan layout sesuai
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        st.pyplot(plt)
        
        # Mengirim deskripsi plot ke Google Generative AI
        img = PIL.Image.open(img_buffer)

        st.write("Interpretasi dari Google Generative AI:")
        try:
            response = model.generate_content([
                """Berdasarkan hasil analisis plot di atas, insight apa yang dapat diperoleh dari pola yang terlihat dan hubungan antar variabel? 
                Berikan rekomendasi tindakan yang dapat diambil serta langkah-langkah selanjutnya berdasarkan temuan tersebut. Buatkan penjelasannya dalam bahasa indonesia""",
                img
            ])
            response.resolve()
            st.write(response.text)
        except Exception as e:
            st.error(f"Error generating content: {e}")
        plt.clf()

        # Visualisasi countplot Categoric + Categoric
        st.subheader('Visualisasi Categoric :')
        column = st.multiselect("Pilih kolom untuk visualisasi countplot:", categorical.columns)
        # Cek apakah dua kolom telah dipilih
        if len(column) == 2:
            plt.figure(figsize=(12, 10))
            ax = sns.countplot(data=categorical, x=column[0], hue=column[1])

            plt.title(f'Countplot of {column[0]} by {column[1]}', fontsize=16)

            # Menambahkan label axis
            plt.xlabel(column[0], fontsize=14)
            plt.ylabel('Count', fontsize=14)
            
            # Menambahkan label di atas setiap bar
            for p in ax.patches:
                ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), 
                            ha='center', va='baseline', fontsize=12, color='black', xytext=(0, 5), 
                            textcoords='offset points')
            
            plt.tight_layout()  # Pastikan layout sesuai
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png')
            img_buffer.seek(0)
            st.pyplot(plt)
            
            # Mengirim deskripsi plot ke Google Generative AI
            img = PIL.Image.open(img_buffer)
            
            st.write("Interpretasi dari Google Generative AI:")
            try:
                response = model.generate_content([
                    """Berdasarkan hasil analisis plot di atas, insight apa yang dapat diperoleh dari pola yang terlihat dan hubungan antar variabel? 
                    Berikan rekomendasi tindakan yang dapat diambil serta langkah-langkah selanjutnya berdasarkan temuan tersebut. Buatkan penjelasannya dalam bahasa indonesia""",
                    img
                ])
                response.resolve()
                st.write(response.text)
            except Exception as e:
                st.error(f"Error generating content: {e}")
            
            plt.clf()
        else:
            st.warning("Silakan pilih dua kolom untuk visualisasi countplot.")

        # Plot Aggregasi Data Grouping (Categoric + Numeric) 

        st.subheader('Aggregasi Data Categoric + Numeric :')
        column = st.multiselect("Pilih kolom untuk aggregasi data, Kolom pertama sebagai Baris dan Kolom kedua sebagai Kolom Aggregasi:", df.columns)
        st.write('Pilih jenis aggregasi :')
        jenis_aggregasi = st.selectbox('Pilih jenis aggregasi:', ['sum', 'mean', 'median', 'max', 'min', 'count'])

        # Cek apakah dua kolom telah dipilih
        if len(column) == 2:
            group_col = column[0]
            agg_col = column[1]

            # Cek apakah kolom kedua adalah numerik
            if pd.api.types.is_numeric_dtype(df[agg_col]):
                # Grouping data dan menghitung aggregasi berdasarkan pilihan pengguna
                if jenis_aggregasi == 'sum':
                    grouped_data = df.groupby(group_col)[agg_col].sum().reset_index().sort_values(by=agg_col, ascending=False)
                elif jenis_aggregasi == 'mean':
                    grouped_data = df.groupby(group_col)[agg_col].mean().reset_index().sort_values(by=agg_col, ascending=False)
                elif jenis_aggregasi == 'count':
                    grouped_data = df.groupby(group_col)[agg_col].count().reset_index().sort_values(by=agg_col, ascending=False)
                elif jenis_aggregasi == 'min':
                    grouped_data = df.groupby(group_col)[agg_col].min().reset_index()
                elif jenis_aggregasi == 'max':
                    grouped_data = df.groupby(group_col)[agg_col].max().reset_index()
                elif jenis_aggregasi == 'median':
                    grouped_data = df.groupby(group_col)[agg_col].median().reset_index()

                st.write(grouped_data)

                plt.figure(figsize=(12, 10))
                ax = sns.barplot(data=grouped_data, x=group_col, y=agg_col)
                plt.title(f'Aggregasi {jenis_aggregasi} of {agg_col} by {group_col}', fontsize=16)

                # Menambahkan label axis
                plt.xlabel(group_col, fontsize=14)
                plt.ylabel(jenis_aggregasi.capitalize(), fontsize=14)

                # Menambahkan label di atas setiap bar
                for p in ax.patches:
                    ax.annotate(f'{p.get_height():.2f}', (p.get_x() + p.get_width() / 2., p.get_height()), 
                                ha='center', va='baseline', fontsize=12, color='black', xytext=(0, 5), 
                                textcoords='offset points')
                plt.tight_layout()
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png')
                img_buffer.seek(0)
                st.pyplot(plt)
                
                # Mengirim deskripsi plot ke Google Generative AI
                img = PIL.Image.open(img_buffer)

                st.write("Interpretasi dari Google Generative AI:")
                try:
                    response = model.generate_content([
                        """Berdasarkan hasil analisis plot di atas, insight apa yang dapat diperoleh dari pola yang terlihat dan hubungan antar variabel? 
                        Berikan rekomendasi tindakan yang dapat diambil serta langkah-langkah selanjutnya berdasarkan temuan tersebut. Buatkan penjelasannya dalam bahasa indonesia""",
                        img
                    ])
                    response.resolve()
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Error generating content: {e}")
                plt.clf()
            else:
                st.error("Kolom kedua harus berupa kolom numerik untuk aggregasi.")
        else:
            st.warning("Silakan pilih dua kolom untuk aggregasi data.")
