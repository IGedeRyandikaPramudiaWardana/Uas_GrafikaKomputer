import pygame
import sys
import math
import os  # Digunakan untuk mengecek keberadaan file

# ==========================================
# KONFIGURASI WINDOW & WARNA
# ==========================================
LEBAR, TINGGI = 800, 600
TITIK_PUSAT_LAYAR = (LEBAR // 2, TINGGI // 2)

PUTIH = (255, 255, 255)
HITAM = (0, 0, 0)
MERAH = (255, 0, 0)
BIRU = (0, 0, 255)

pygame.init()
window = pygame.display.set_mode((LEBAR, TINGGI))
pygame.display.set_caption("Tugas Grafika Komputer: Transformasi 3D")
clock = pygame.time.Clock()

# ==========================================
# BAGIAN 1: ENGINE MENGGAMBAR (RASTERIZER)
# Menggunakan Algoritma Bresenham & Set Pixel
# ==========================================

def buatPixel(x, y, color):
    # Menggambar pixel langsung ke layar
    if 0 <= x < LEBAR and 0 <= y < TINGGI:
        window.set_at((int(x), int(y)), color)

def garis_bresenham(p1, p2, color):
    # Menggambar garis pixel demi pixel tanpa library plotting
    x1, y1 = int(p1[0]), int(p1[1])
    x2, y2 = int(p2[0]), int(p2[1])

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    
    err = dx - dy
    
    while True:
        buatPixel(x1, y1, color)
        
        if x1 == x2 and y1 == y2:
            break
            
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

# ==========================================
# BAGIAN 2: MATEMATIKA MATRIKS (TRANSFORMASI)
# ==========================================

def perkalian_matriks(matriks, titik):
    # Mengubah titik [x,y,z] menjadi Homogeneous [x,y,z,1] lalu dikalikan matriks
    vec = [titik[0], titik[1], titik[2], 1]
    hasil = [0, 0, 0, 0]

    for i in range(4):
        total = 0
        for j in range(4):
            total += matriks[i][j] * vec[j]
        hasil[i] = total
    
    return [hasil[0], hasil[1], hasil[2]]

def get_matriks_translasi(tx, ty, tz):
    return [
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1]
    ]

def get_matriks_skala(sx, sy, sz):
    return [
        [sx, 0,  0,  0],
        [0,  sy, 0,  0],
        [0,  0,  sz, 0],
        [0,  0,  0,  1]
    ]

def get_matriks_rotasi_x(sudut):
    c = math.cos(sudut)
    s = math.sin(sudut)
    return [
        [1, 0,  0, 0],
        [0, c, -s, 0],
        [0, s,  c, 0],
        [0, 0,  0, 1]
    ]

def get_matriks_rotasi_y(sudut):
    c = math.cos(sudut)
    s = math.sin(sudut)
    return [
        [ c, 0, s, 0],
        [ 0, 1, 0, 0],
        [-s, 0, c, 0],
        [ 0, 0, 0, 1]
    ]

def get_matriks_rotasi_z(sudut):
    c = math.cos(sudut)
    s = math.sin(sudut)
    return [
        [c, -s, 0, 0],
        [s,  c, 0, 0],
        [0,  0, 1, 0],
        [0,  0, 0, 1]
    ]

def komposit_matriks(m1, m2):
    # Mengalikan dua matriks 4x4
    hasil = [[0 for _ in range(4)] for _ in range(4)]
    for i in range(4):
        for j in range(4):
            for k in range(4):
                hasil[i][j] += m1[i][k] * m2[k][j]
    return hasil

# ==========================================
# BAGIAN 3: LOGIKA UTAMA (OBJECT & FILE)
# ==========================================

class Object3D:
    def __init__(self):
        self.vertices = [] 
        self.edges = []    
        
        # State Transformasi Awal
        self.posisi = [0, 0, 0] 
        self.skala = [1, 1, 1]
        self.rotasi = [0, 0, 0] 

    def load_data(self, file_titik, file_garis):
        # Membaca file dan parsing data koma (CSV format)
        try:
            with open(file_titik, 'r') as f:
                for line in f:
                    if line.strip(): # Pastikan baris tidak kosong
                        xyz = list(map(float, line.strip().split(',')))
                        self.vertices.append(xyz)
            
            with open(file_garis, 'r') as f:
                for line in f:
                    if line.strip():
                        idx = list(map(int, line.strip().split(',')))
                        self.edges.append(idx)
        except Exception as e:
            print(f"Error saat membaca file: {e}")

    def transform_and_render(self):
        # 1. Matriks Skala
        m_skala = get_matriks_skala(self.skala[0], self.skala[1], self.skala[2])
        
        # 2. Matriks Rotasi
        m_rot_x = get_matriks_rotasi_x(self.rotasi[0])
        m_rot_y = get_matriks_rotasi_y(self.rotasi[1])
        m_rot_z = get_matriks_rotasi_z(self.rotasi[2])
        
        # Gabungkan Rotasi
        m_rot_gabung = komposit_matriks(m_rot_y, m_rot_x)
        m_rot_gabung = komposit_matriks(m_rot_z, m_rot_gabung)
        
        # 3. Matriks Translasi (Pindah ke tengah layar)
        tx = self.posisi[0] + TITIK_PUSAT_LAYAR[0]
        ty = self.posisi[1] + TITIK_PUSAT_LAYAR[1]
        tz = self.posisi[2]
        m_trans = get_matriks_translasi(tx, ty, tz)
        
        # KOMPOSIT FINAL: Translasi * Rotasi * Skala
        m_final = komposit_matriks(m_rot_gabung, m_skala)
        m_final = komposit_matriks(m_trans, m_final)
        
        # Hitung Transformasi untuk setiap titik
        transformed_vertices = []
        for v in self.vertices:
            v_baru = perkalian_matriks(m_final, v)
            transformed_vertices.append(v_baru)
            
            # Gambar titik sudut (Vertex) - Merah
            buatPixel(v_baru[0], v_baru[1], MERAH)
            
        # Gambar Garis menghubungkan titik - Biru
        for edge in self.edges:
            p1 = transformed_vertices[edge[0]]
            p2 = transformed_vertices[edge[1]]
            garis_bresenham(p1, p2, BIRU)

# ==========================================
# MAIN PROGRAM
# ==========================================

def main():
    objek = Object3D()
    
    # --- PENGATURAN PATH FILE ---
    # Menggunakan r"..." (raw string) agar backslash terbaca benar di Windows
    path_titik = r"D:\Grafika Komputer\program3_bruteforceFIX\UAS\titik.txt"
    path_garis = r"D:\Grafika Komputer\program3_bruteforceFIX\UAS\garis.txt"
    
    print("="*40)
    print("MEMULAI PROGRAM GRAFIKA 3D")
    print(f"Mencari file di:\n1. {path_titik}\n2. {path_garis}")
    print("="*40)
    
    # Validasi keberadaan file
    if not os.path.exists(path_titik):
        print(f"[ERROR] File titik.txt TIDAK DITEMUKAN di lokasi tersebut!")
        sys.exit()
    if not os.path.exists(path_garis):
        print(f"[ERROR] File garis.txt TIDAK DITEMUKAN di lokasi tersebut!")
        sys.exit()

    # Load Data
    objek.load_data(path_titik, path_garis)
    
    if len(objek.vertices) > 0:
        print(f"[SUKSES] Berhasil memuat {len(objek.vertices)} titik dan {len(objek.edges)} garis.")
    else:
        print("[WARNING] File terbaca tapi kosong.")

    running = True
    while running:
        window.fill(PUTIH) # Bersihkan layar (putih)
        
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Input Keyboard (Continuous Press)
        keys = pygame.key.get_pressed()
        
        # TRANSLASI (Geser Posisi)
        if keys[pygame.K_LEFT]:  objek.posisi[0] -= 3
        if keys[pygame.K_RIGHT]: objek.posisi[0] += 3
        if keys[pygame.K_UP]:    objek.posisi[1] -= 3
        if keys[pygame.K_DOWN]:  objek.posisi[1] += 3
        
        # ROTASI (Putar Objek)
        kecepatan_rotasi = 0.04
        if keys[pygame.K_w]: objek.rotasi[0] -= kecepatan_rotasi # Rotasi X
        if keys[pygame.K_s]: objek.rotasi[0] += kecepatan_rotasi
        if keys[pygame.K_a]: objek.rotasi[1] -= kecepatan_rotasi # Rotasi Y
        if keys[pygame.K_d]: objek.rotasi[1] += kecepatan_rotasi
        if keys[pygame.K_q]: objek.rotasi[2] -= kecepatan_rotasi # Rotasi Z
        if keys[pygame.K_e]: objek.rotasi[2] += kecepatan_rotasi

        # SKALA (Zoom)
        if keys[pygame.K_z]: 
            objek.skala[0] += 0.02
            objek.skala[1] += 0.02
            objek.skala[2] += 0.02
        if keys[pygame.K_x]: 
            if objek.skala[0] > 0.1: # Batas minimal agar tidak hilang
                objek.skala[0] -= 0.02
                objek.skala[1] -= 0.02
                objek.skala[2] -= 0.02

        # Tampilkan Petunjuk
        font = pygame.font.SysFont('Consolas', 14)
        petunjuk = [
            "KONTROL KEYBOARD:",
            "[Panah]   : Translasi (Geser)",
            "[W/S]     : Rotasi Sumbu X",
            "[A/D]     : Rotasi Sumbu Y",
            "[Q/E]     : Rotasi Sumbu Z",
            "[Z/X]     : Scaling (Perbesar/Perkecil)"
        ]
        for i, t in enumerate(petunjuk):
            img = font.render(t, True, HITAM)
            window.blit(img, (10, 10 + i*18))

        # Render Objek
        objek.transform_and_render()
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()