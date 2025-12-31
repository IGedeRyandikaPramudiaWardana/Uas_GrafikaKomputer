import pygame
import sys 
import math


WIDTH, HEIGHT = 800, 600
TITIK_PUSAT = (WIDTH // 2, HEIGHT // 2) 

PUTIH = (255, 255, 255)
HITAM = (0, 0, 0)
MERAH = (255, 0, 0)
HIJAU = (0, 255, 0)
BIRU = (0, 0, 255)

pygame.init()
layar = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tugas Grafika Komputer: Transformasi 3D")
clock = pygame.time.Clock()

def buatPixel(x, y, color):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        layar.set_at((int(x), int(y)), color)

def buatGarisBressenham(p1, p2, color):
    x1, y1 = int (p1[0]), int (p1[1])
    x2, y2 = int (p2[0]), int (p2[1])

    # cari delta
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    x, y = x1, y1
    pk = 2* dy - dx

    arah_x = 1 if x1 < x2 else -1
    arah_y = 1 if y1 < y2 else -1

    if abs(dy) > abs(dx):
        pk = 2 * abs(dx) - abs(dy)
        for k in range(dy):
            if pk < 0:
                y = y + arah_y
                pk = pk + 2 * abs(dx)
            else:
                x = x + arah_x
                y = y + arah_y
                pk = pk + 2 * abs(dx) - 2 * abs(dy)
            buatPixel(x, y, color)
    else:
        pk = 2 * abs(dy) - abs(dx)
        for k in range(dx):
            if pk < 0:
                x = x + arah_x
                pk = pk + 2 * abs(dy)
            else:
                x = x + arah_x
                y = y + arah_y
                pk = pk + 2 * abs(dy) - 2 * abs(dx)
            buatPixel(x, y, color)

# Membuat fungsi perkalian matriks homogen dengan titik 3D
def perkalianMatriks(matriks, titik):
    # Mengonversi menjadi Homogeneous [x,y,z,1] 
    vec = [titik[0], titik[1], titik[2], 1]
    hasil = [0, 0, 0, 0]

    for i in range(4):
        total = 0
        for j in range(4):
            total += matriks[i][j] * vec[j]
        hasil[i] = total

    return [hasil[0], hasil[1], hasil[2]]

# Inisialisasi matriks operasi transformasi dasar
def skala(sx, sy, sz):
    return [
        [sx, 0, 0, 0],
        [0, sy, 0, 0],
        [0, 0, sz, 0],
        [0, 0, 0, 1]
    ]

# Rotasi sumbu x
def rotasi_x(sudut):
    c = math.cos(sudut)
    s = math.sin(sudut)
    return [
        [1, 0, 0, 0],
        [0, c, -s, 0],
        [0, s, c, 0],
        [0, 0, 0, 1]
    ]

# Rotasi sumbu y
def rotasi_y(sudut):
    c = math.cos(sudut)
    s = math.sin(sudut)
    return [
        [c, 0, s, 0],
        [0, 1, 0, 0],
        [-s, 0, c, 0],
        [0, 0, 0, 1]
    ]

# Rotasi sumbu z
def rotasi_z(sudut):
    c = math.cos(sudut)
    s = math.sin(sudut)
    return [
        [c, -s, 0, 0],
        [s, c, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ]

def translasi(tx, ty, tz):
    return [
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1]
    ]

# Perkalian matriks dengan matriks
def kompositMatriks(matriksA, matriksB):
    hasil = [[0 for _ in range(4)] for _ in range(4)]
    for i in range(4):
        for j in range(4):
            total = 0
            for k in range(4):
                total += matriksA[i][k] * matriksB[k][j]
            hasil[i][j] = total
    return hasil


class render3D:
    # Inisialisasi array untuk menyimpan titik dan garis
    def __init__(self):
        self.vertices = []
        self.edges = []

        # Inisialisasi parameter transformasi awal/asli
        self.posisi = [0, 0, 0] 
        self.rotasi = [0, 0, 0]
        self.skala = [1, 1, 1]

        # Inisialisasi mode otomatis
        self.otomatis = False
        self.kecepatan_auto = [1, 1, 0.5]

        # Menambahkan font
        self.font = pygame.font.SysFont("Arial", 12)

        # Menambahkan label ke setiap titik
        self.labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

        # Menambahkan tempat menyimpan titik yang sudah dihitung
        self.transformed_vertices = []

    # Load data dari file titik dan garis
    def load_data(self, file_titik, file_garis):
        # membaca file yang telah dibuat
        # parsing satu-persatu 
        try:
            with open(file_titik, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 3:
                        self.vertices.append([float(parts[0]), float(parts[1]), float(parts[2])])
                    elif len(parts) != 3:
                        print(f"Baris tidak valid di file titik: {line.strip()}")
            
            with open(file_garis, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 2:
                        self.edges.append([int(parts[0]), int(parts[1])])
                    elif len(parts) != 2:
                        print(f"Baris tidak valid di file garis: {line.strip()}")
            print(f"Data Loaded: {len(self.vertices)} titik, {len(self.edges)} garis.")
        except Exception as e:
            print(f"Error loading data: {e}")

        self.hitung_transformasi()

        
    def hitung_transformasi(self):
        # 1. Matriks Skala
        m_skala = skala(self.skala[0], self.skala[1], self.skala[2])

        # 2. Matriks Rotasi
        m_rot_x = rotasi_x(math.radians(self.rotasi[0]))
        m_rot_y = rotasi_y(math.radians(self.rotasi[1]))
        m_rot_z = rotasi_z(math.radians(self.rotasi[2]))

        # Gabungkan Rotasi (urutan z * y * x)
        m_rot_gabung = kompositMatriks(m_rot_y, m_rot_x)
        m_rot_gabung = kompositMatriks(m_rot_z, m_rot_gabung)

        # Posisi objekt relatif terhadapad (0, 0, 0)
        m_trans = translasi(self.posisi[0], self.posisi[1], self.posisi[2])

        # Gabungkan semua transformasi
        m_final = kompositMatriks(m_rot_gabung, m_skala)
        m_final = kompositMatriks(m_trans, m_final)

        # terapkan ke semua titik
        self.transformed_vertices = []
        for v in self.vertices:
            v_baru = perkalianMatriks(m_final, v)
            self.transformed_vertices.append(v_baru)
    
    # Menampilkan objek
    def tampilkan_objek(self):
        # Loop menelusuri setiap pasangan garis (egde)
        
        for edge in self.edges:
            index1 = edge[0]
            index2 = edge[1]
            
            # # Mendapatkan koordinat titik asli
            # p1_asli = self.vertices[index1]
            # p2_asli = self.vertices[index2]

            # Menggunakan koordinat titik yang sudah ditransformasi
            p1 = self.transformed_vertices[index1]
            p2 = self.transformed_vertices[index2]
            
            # Manambahkan offset agar titik (0,0) berada di tengah layar
            x1_layar = int(p1[0] + TITIK_PUSAT[0])
            y1_layar = int(p1[1] + TITIK_PUSAT[1])
            # z tidak digunakan untuk 2D, nanti pada tranformasi 3D akan dipakai
            z1 = int(p1[2])

            # Menambahkan offset agar titik (0,0) berada di tengah layar
            x2_layar = int(p2[0] + TITIK_PUSAT[0])
            y2_layar = int(p2[1] + TITIK_PUSAT[1])
            # z tidak digunakan untuk 2D, nanti pada tranformasi 3D akan dipakai
            z2 = int(p2[2])

            # Menyiapkan format titik untuk fungsi Bressenham
            titik_start = [x1_layar, y1_layar, z1]
            titik_end = [x2_layar, y2_layar, z2]

            # gambar elemen visual
            buatPixel(x1_layar, y1_layar, MERAH)
            buatPixel(x2_layar, y2_layar, MERAH)

            # Gambar garis penghubung
            buatGarisBressenham(titik_start, titik_end, BIRU)

            # Tampilkan teks
            teks_A = self.font.render(self.labels[index1], True, HITAM)
            layar.blit(teks_A, (x1_layar + 5, y1_layar - 15)) 


    def tampilkan_info(self):
        # Header Status
        status_text = "MODE: OTOMATIS (Tekan SPASI untuk Manual)" if self.otomatis else "MODE: MANUAL (Tekan SPASI untuk Otomatis)"
        warna_status = HIJAU if self.otomatis else MERAH
        
        # Tampilkan instruksi kontrol
        instruksi = [
            "W/S: Rotasi X || A/D: Rotasi Y || Q/E: Rotasi Z",
            "Z/X: Skala (Zoom In/Out)",
            "Arrow Keys: Translasi (Pindah Posisi)"
        ]

        y_offset = 10
        for baris in instruksi:
            teks = self.font.render(baris, True, HITAM)
            layar.blit(teks, (10, y_offset))
            y_offset += 20

        # Meampilkan Header Koordinat
        y_offset += 20
        header = self.font.render("KOORDINAT TITIK: ", True, HITAM)
        layar.blit(header, (10, y_offset))
        y_offset += 20

        # Menampilkan Daftar Koordinat Titik
        for i, v in enumerate(self.transformed_vertices):
            x_layar = int(v[0] + TITIK_PUSAT[0])
            y_layar = int(v[1] + TITIK_PUSAT[1])
            z_layar = int(v[2])

            label = self.labels[i] if i < len(self.labels) else str(i)

            # Format string agar rapi
            info = f"{label}({x_layar:>4}, {y_layar:>4}, {z_layar:>4})"
            teks_koordinat = self.font.render(info, True, HITAM)
            layar.blit(teks_koordinat, (10, y_offset))
            y_offset += 15
            
# Fungsi main menjalankan program
def main():
    # Panggil kelas render3D
    app = render3D()

    # Pastikan path file benar
    path_titik = r'D:\Grafika Komputer\program3_bruteforceFIX\UAS\titik.txt'
    path_garis = r'D:\Grafika Komputer\program3_bruteforceFIX\UAS\garis.txt'

    # Panggil fungsi load_data
    app.load_data(path_titik, path_garis)

    # Inisialisasi Pygame
    pygame.init()
    layar = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tranformasi Geometri 3D")
    clock = pygame.time.Clock()

    # Loop utama program
    running = True
    while running:
        layar.fill(PUTIH)

        # Kontrol event manual
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
            # Kontrol event toggle otomatis
            if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        app.otomatis = not app.otomatis


        if app.otomatis:
            # Mode Otomatis: Putar terus
            app.rotasi[0] += app.kecepatan_auto[0] # Putar X
            app.rotasi[1] += app.kecepatan_auto[1] # Putar Y
            app.rotasi[2] += app.kecepatan_auto[2] # Putar Z
        else:    
            keys = pygame.key.get_pressed()  
            # Rotasi Sumbu x dan y (Huruf WASD)
            if keys[pygame.K_w]:  app.rotasi[0] -= 2 # x
            if keys[pygame.K_s]:  app.rotasi[0] += 2
            if keys[pygame.K_a]:  app.rotasi[1] -= 2 # y
            if keys[pygame.K_d]:  app.rotasi[1] += 2
            if keys[pygame.K_q]:  app.rotasi[2] -= 1 # z
            if keys[pygame.K_e]:  app.rotasi[2] += 1

            # Zoom / Skala (Huruf Z/X)
            if keys[pygame.K_z]: app.skala = [s + 0.05 for s in app.skala] # zoom in
            if keys[pygame.K_x]: app.skala = [s - 0.05 for s in app.skala] # zoom out

            # Peripindahan posisi (translasi) (Panah)
            if keys[pygame.K_LEFT]:  app.posisi[0] -= 2
            if keys[pygame.K_RIGHT]: app.posisi[0] += 2
            if keys[pygame.K_UP]:    app.posisi[1] -= 2
            if keys[pygame.K_DOWN]:  app.posisi[1] += 2

        # Hitung transformasi berdasarkan input    
        app.hitung_transformasi()
        app.tampilkan_objek()
        # app.tampilkan_info() # menambahkan header infornmasi
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

# Panggil fungsi main
if __name__ == "__main__":
    main()