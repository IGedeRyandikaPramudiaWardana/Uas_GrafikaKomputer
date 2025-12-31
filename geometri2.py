import pygame
import sys
import math

# --- KONFIGURASI ---
WIDTH, HEIGHT = 800, 600
TITIK_PUSAT = (WIDTH // 2, HEIGHT // 2)

PUTIH = (255, 255, 255)
HITAM = (0, 0, 0)
MERAH = (255, 0, 0)
BIRU = (0, 0, 255)
ABU_ABU = (100, 100, 100) # Warna teks label

pygame.init()
layar = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tugas Grafika Komputer: Transformasi 3D")
clock = pygame.time.Clock()

# --- ENGINE GAMBAR ---

def buatPixel(x, y, color):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        layar.set_at((int(x), int(y)), color)

def buatGarisBressenham(p1, p2, color):
    x1, y1 = int(p1[0]), int(p1[1])
    x2, y2 = int(p2[0]), int(p2[1])

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    
    x, y = x1, y1
    
    arah_x = 1 if x1 < x2 else -1
    arah_y = 1 if y1 < y2 else -1

    buatPixel(x, y, color) 

    if abs(dy) > abs(dx): # Garis Curam
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
    else: # Garis Landai
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

# --- MATEMATIKA ---

def perkalianMatriks(matriks, titik):
    vec = [titik[0], titik[1], titik[2], 1]
    hasil = [0, 0, 0, 0]
    for i in range(4):
        total = 0
        for j in range(4):
            total += matriks[i][j] * vec[j]
        hasil[i] = total
    return [hasil[0], hasil[1], hasil[2]]

def translasi(tx, ty, tz):
    return [
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1]
    ]

def skala(sx, sy, sz):
    return [
        [sx, 0, 0, 0],
        [0, sy, 0, 0],
        [0, 0, sz, 0],
        [0, 0, 0, 1]
    ]

def rotasi_X(sudut):
    rad = math.radians(sudut)
    c = math.cos(rad)
    s = math.sin(rad)
    return [
        [1, 0, 0, 0],
        [0, c, -s, 0],
        [0, s, c, 0],
        [0, 0, 0, 1]
    ]

def rotasi_Y(sudut):
    rad = math.radians(sudut)
    c = math.cos(rad)
    s = math.sin(rad)
    return [
        [c, 0, s, 0],
        [0, 1, 0, 0],
        [-s, 0, c, 0],
        [0, 0, 0, 1]
    ]

def rotasi_Z(sudut):
    rad = math.radians(sudut)
    c = math.cos(rad)
    s = math.sin(rad)
    return [
        [c, -s, 0, 0],
        [s, c, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ]

def komposit_matriks(m1, m2):
    hasil = [[0 for _ in range(4)] for _ in range(4)]
    for i in range(4):
        for j in range(4):
            for k in range(4):
                hasil[i][j] += m1[i][k] * m2[k][j]
    return hasil

# --- CLASS UTAMA ---

class Objek3D:
    def __init__(self):
        self.vertices = []
        self.edges = []
        
        self.posisi = [0, 0, 0]
        self.rotasi = [0, 0, 0]
        self.skala = [1, 1, 1]
        
        self.font_coord = pygame.font.SysFont("Consolas", 12) # Font Monospace agar rapi
        
        # [BARU] Label untuk titik sudut (Kubus punya 8 titik)
        self.labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

    def load_data(self, file_titik, file_garis):
        try:
            with open(file_titik, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 3:
                        self.vertices.append([float(parts[0]), float(parts[1]), float(parts[2])])
            
            with open(file_garis, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 2:
                        self.edges.append((int(parts[0]), int(parts[1])))
            print(f"Data Loaded: {len(self.vertices)} titik, {len(self.edges)} garis.")
        except Exception as e:
            print(f"Error loading data: {e}")

    def transformasi_dan_render(self):
        # 1. Matriks Skala
        m_skala = skala(self.skala[0], self.skala[1], self.skala[2])

        # 2. Matriks Rotasi
        m_rot_x = rotasi_X(self.rotasi[0])
        m_rot_y = rotasi_Y(self.rotasi[1])
        m_rot_z = rotasi_Z(self.rotasi[2])

        m_rot_gabung = komposit_matriks(m_rot_y, m_rot_x)
        m_rot_gabung = komposit_matriks(m_rot_z, m_rot_gabung)

        # 3. Matriks Translasi
        tx = self.posisi[0] + TITIK_PUSAT[0]
        ty = self.posisi[1] + TITIK_PUSAT[1]
        tz = self.posisi[2]
        m_trans = translasi(tx, ty, tz)

        # Komposit Final
        m_final = komposit_matriks(m_rot_gabung, m_skala)
        m_final = komposit_matriks(m_trans, m_final)

        # -- PROSES RENDERING --
        transformed_vertices = []
        
        # Header Info Koordinat
        header = self.font_coord.render("KOORDINAT TITIK:", True, HITAM)
        layar.blit(header, (10, 120)) # Posisi header

        for i, v in enumerate(self.vertices):
            # Hitung posisi baru
            v_baru = perkalianMatriks(m_final, v)
            transformed_vertices.append(v_baru)
            
            x_screen = int(v_baru[0])
            y_screen = int(v_baru[1])
            z_depth  = int(v_baru[2])

            # 1. Gambar Titik (Merah)
            buatPixel(x_screen, y_screen, MERAH)
            
            # [BARU] 2. Tampilkan Label Huruf di dekat titik (A, B, C...)
            # Agar kita tahu titik mana adalah A, mana B, dst.
            if i < len(self.labels):
                huruf = self.labels[i]
            else:
                huruf = str(i) # Jika titik lebih dari 8, pakai angka
            
            text_huruf = self.font_coord.render(huruf, True, ABU_ABU)
            layar.blit(text_huruf, (x_screen + 5, y_screen - 15))

            # [BARU] 3. Tampilkan Detail Koordinat di Pojok Kiri (List)
            # Format: A(x, y, z)
            info_text = f"{huruf:<2}({x_screen:>4}, {y_screen:>4}, {z_depth:>4})"
            surface_info = self.font_coord.render(info_text, True, HITAM)
            
            # Atur posisi baris per baris (mulai Y=140, jarak 15px)
            posisi_y_list = 140 + (i * 15) 
            layar.blit(surface_info, (10, posisi_y_list))

        # 4. Gambar Garis (Biru)
        for edge in self.edges:
            p1 = transformed_vertices[edge[0]]
            p2 = transformed_vertices[edge[1]]
            buatGarisBressenham(p1, p2, BIRU)

# --- PROGRAM UTAMA ---

def main():
    objek = Objek3D()

    # Pastikan path file benar
    path_titik = r'D:\Grafika Komputer\program3_bruteforceFIX\UAS\titik.txt'
    path_garis = r'D:\Grafika Komputer\program3_bruteforceFIX\UAS\garis.txt'

    objek.load_data(path_titik, path_garis) 
    
    running = True
    while running:
        layar.fill(PUTIH) 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:  objek.posisi[0] -= 2
        if keys[pygame.K_RIGHT]: objek.posisi[0] += 2
        if keys[pygame.K_UP]:    objek.posisi[1] -= 2
        if keys[pygame.K_DOWN]:  objek.posisi[1] += 2
        
        if keys[pygame.K_w]:     objek.rotasi[0] -= 1
        if keys[pygame.K_s]:     objek.rotasi[0] += 1
        if keys[pygame.K_a]:     objek.rotasi[1] -= 1
        if keys[pygame.K_d]:     objek.rotasi[1] += 1
        if keys[pygame.K_q]:     objek.rotasi[2] -= 1
        if keys[pygame.K_e]:     objek.rotasi[2] += 1
        
        if keys[pygame.K_z]:     objek.skala = [s + 0.01 for s in objek.skala]
        if keys[pygame.K_x]:     objek.skala = [s - 0.01 for s in objek.skala]

        # Tampilkan Petunjuk Kontrol
        font_petunjuk = pygame.font.SysFont("Arial", 14)
        teks_petunjuk = [
            "Panah: Geser Posisi",
            "W/S: Rotasi X | A/D: Rotasi Y | Q/E: Rotasi Z",
            "Z/X: Zoom In/Out"
        ]
        for i, baris in enumerate(teks_petunjuk):
            s = font_petunjuk.render(baris, True, HITAM)
            layar.blit(s, (10, 10 + i*20))

        # Render Objek
        objek.transformasi_dan_render()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()