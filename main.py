import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# Konfigurasi Tampilan Pandas agar terminal rapi
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# --- FUNGSI TAMBAHAN: CLEAR SCREEN ---
def clear_screen():
    """Membersihkan layar terminal (Cross-platform)."""
    os.system('cls' if os.name == 'nt' else 'clear')

class StrokeAnalysisApp:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.df = None
        self.raw_df = None 

    def load_data(self) -> bool:
        print(f"\n[LOADING] Membaca data dari '{self.filepath}'...")
        if not os.path.exists(self.filepath):
            print(f"[ERROR] File tidak ditemukan di: {self.filepath}")
            return False
        
        try:
            self.df = pd.read_csv(self.filepath)
            self.raw_df = self.df.copy()
            print(f"[SUCCESS] Data dimuat! Total baris: {self.df.shape[0]}, Kolom: {self.df.shape[1]}")
            return True
        except Exception as e:
            print(f"[ERROR] Gagal membaca file: {e}")
            return False

    # 1. DATA PREPROCESSING
    def clean_data(self):
        if self.df is None: return
        print("\n--- [DATA CLEANING] ---")
        
        duplicates = self.df.duplicated().sum()
        if duplicates > 0:
            print(f"-> Ditemukan {duplicates} data duplikat. Menghapus...")
            self.df.drop_duplicates(inplace=True)
        else:
            print("-> Tidak ada data duplikat.")

        missing = self.df.isnull().sum()
        if missing.sum() > 0:
            print(f"-> Ditemukan missing values:\n{missing[missing > 0]}")
            for col in self.df.columns:
                if self.df[col].dtype in ['float64', 'int64']:
                    self.df[col].fillna(self.df[col].mean(), inplace=True)
                else:
                    self.df[col].fillna(self.df[col].mode()[0], inplace=True)
            print("-> Missing values telah diisi (Imputasi Mean/Mode).")
        else:
            print("-> Data lengkap (Tidak ada missing values).")
        
        print(f"-> Status Data Sekarang: {self.df.shape}")

    # 2. STATISTICAL SUMMARY
    def show_summary(self):
        if self.df is None: return
        print("\n--- [STATISTIK DESKRIPTIF] ---")
        print("1. Tipe Data Kolom:")
        print(self.df.dtypes)
        print("\n2. Ringkasan Numerik:")
        print(self.df.describe().T)
        print("\n3. Ringkasan Kategorikal:")
        print(self.df.describe(include=['O']).T)

    # 3. ALGORITMA (SEARCH & SORT)
    def search_data(self):
        if self.df is None: return
        print("\n--- [SEARCHING] ---")
        try:
            min_age = float(input("Masukkan batas minimum umur: "))
            stroke_only = input("Tampilkan hanya pasien Stroke? (y/n): ").lower()
            
            query = self.df[self.df['Age'] >= min_age]
            if stroke_only == 'y':
                query = query[query['Stroke'] == 1]
            
            count = len(query)
            print(f"\n[HASIL] Ditemukan {count} pasien.")
            if count > 0:
                print(query.head(10)) 
                if count > 10: print("... (Data lainnya disembunyikan)")
        except ValueError:
            print("[ERROR] Masukkan angka yang valid untuk umur.")

    def sort_data(self):
        if self.df is None: return
        print("\n--- [SORTING] ---")
        
        # --- PERUBAHAN DI SINI: Menu Pilihan Angka ---
        cols_available = ['Age', 'Average_Glucose_Level', 'BMI']
        
        print("Pilih kolom untuk sorting:")
        for i, col_name in enumerate(cols_available, 1):
            print(f"{i}. {col_name}")
            
        try:
            pilihan = int(input(f"Masukkan pilihan (1-{len(cols_available)}): "))
            
            if 1 <= pilihan <= len(cols_available):
                col = cols_available[pilihan - 1] # Ambil nama kolom dari list
            else:
                print("[ERROR] Pilihan angka tidak valid.")
                return

            ascending = input("Urutkan menaik (A) atau menurun (D)? ").lower() == 'a'
            sorted_df = self.df.sort_values(by=col, ascending=ascending)
            
            print(f"\n[HASIL] Top 10 Data berdasarkan '{col}':")
            
            # Menampilkan hasil dengan aman (cek nama kolom 'Sex' atau 'Gender')
            try:
                # Cek apakah kolom 'Sex' ada, jika tidak coba 'Gender', jika tidak ada print default
                if 'Sex' in sorted_df.columns:
                    print(sorted_df[[col, 'Sex', 'Stroke', 'Work_Type']].head(10))
                elif 'Gender' in sorted_df.columns:
                    print(sorted_df[[col, 'Gender', 'Stroke', 'Work_Type']].head(10))
                else:
                    print(sorted_df.head(10))
            except Exception as e:
                print(f"[WARN] Menampilkan kolom default. Error detail: {e}")
                print(sorted_df.head(10))

        except ValueError:
            print("[ERROR] Harap masukkan angka saja.")

    # 4. VISUALISASI DATA
    def visualization_menu(self):
        if self.df is None: return
        
        while True:
            print("\n--- [MENU VISUALISASI] ---")
            print("1. Distribusi Stroke (Pie Chart)")
            print("2. Matriks Korelasi (Heatmap)")
            print("3. Sebaran Umur (Histogram & KDE)")
            print("4. Hubungan Glukosa vs BMI (Scatter)")
            print("0. Kembali ke Menu Utama")
            
            choice = input("Pilih grafik (1-4): ")
            
            plt.figure(figsize=(10, 6))
            sns.set_theme(style="whitegrid")

            if choice == '1':
                self.df['Stroke'].value_counts().plot.pie(autopct='%1.1f%%', colors=['skyblue', 'salmon'])
                plt.title("Proporsi Dataset Stroke")
                plt.ylabel("")
                plt.show()
            elif choice == '2':
                numeric_df = self.df.select_dtypes(include=['float64', 'int64'])
                sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt=".2f")
                plt.title("Matriks Korelasi Antar Fitur")
                plt.show()
            elif choice == '3':
                sns.histplot(data=self.df, x='Age', kde=True, hue='Stroke', palette='husl')
                plt.title("Distribusi Umur Pasien")
                plt.show()
            elif choice == '4':
                sns.scatterplot(data=self.df, x='BMI', y='Average_Glucose_Level', hue='Stroke', alpha=0.6)
                plt.title("Relasi BMI vs Glukosa")
                plt.show()
            elif choice == '0':
                break
            else:
                print("Pilihan tidak valid.")

    # 5. UTILITY: EXPORT
    def export_cleaned_data(self):
        if self.df is None: return
        try:
            output_path = "data/cleaned_stroke_data.csv"
            self.df.to_csv(output_path, index=False)
            print(f"\n[SUCCESS] Data tersimpan di: {output_path}")
        except Exception as e:
            print(f"[ERROR] Gagal menyimpan data: {e}")

# ==========================
# MAIN PROGRAM (CLI LOOP)
# ==========================
def main_menu():
    # Setup Path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    FILE_PATH = os.path.join(base_dir, 'data', 'stroke_dataset.csv')
    
    clear_screen()
    
    app = StrokeAnalysisApp(FILE_PATH)
    
    if not app.load_data():
        return 

    input("\nData siap. Tekan [Enter] untuk masuk menu...")

    while True:
        clear_screen()
        
        print("="*40)
        print("        STROKE ANALYSIS APP V2.4        ")
        print("="*40)
        print("1. Tampilkan Info Data & Statistik")
        print("2. Bersihkan Data (Cleaning)")
        print("3. Cari Data (Searching)")
        print("4. Urutkan Data (Sorting)")
        print("5. Visualisasi Data (Graph)")
        print("6. Export Data Bersih ke CSV")
        print("0. Keluar")
        print("="*40)
        
        pilihan = input("Pilih menu (1-6): ")

        if pilihan == '0':
            print("Terima kasih telah menggunakan aplikasi ini. Bye!")
            break
        
        print("\n" + "-"*30) 
        if pilihan == '1':
            app.show_summary()
        elif pilihan == '2':
            app.clean_data()
        elif pilihan == '3':
            app.search_data()
        elif pilihan == '4':
            app.sort_data()
        elif pilihan == '5':
            app.visualization_menu()
        elif pilihan == '6':
            app.export_cleaned_data()
        else:
            print("[ERROR] Input tidak valid, coba lagi.")
        
        if pilihan in ['1', '2', '3', '4', '5', '6']:
            input("\nTekan [Enter] untuk kembali ke menu utama...")

if __name__ == "__main__":
    main_menu()