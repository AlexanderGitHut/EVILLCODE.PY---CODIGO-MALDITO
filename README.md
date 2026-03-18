<img width="1024" height="1000" alt="Imagen de evillcode" src="https://github.com/user-attachments/assets/7f2d25c0-be54-4e95-a25a-1d3a3bf3660f" />
<img width="1024" height="362" alt="Imagen Proyecto Evillcode" src="https://github.com/user-attachments/assets/d9ed4397-c0f0-423c-823f-c14d214daa56" />

# 🛠️ EVILLCODE.PY - Network Audit & MITM Tool

Este proyecto es una herramienta de auditoría de red desarrollada en Python para realizar escaneos de dispositivos y pruebas de penetración mediante envenenamiento ARP (ARP Spoofing).

## 📋 Características Principales
* **Escaneo de Red**: Localiza de forma rápida todos los dispositivos conectados en un segmento de red específico.
* **Ataque MITM (ARP Spoofing)**: Intercepta el tráfico entre un objetivo y el router para realizar pruebas de seguridad.
* **Interfaz Visual**: Incluye un menú interactivo con arte ASCII y colores para facilitar su uso en la terminal.

## 🚀 Instalación en Kali Linux

```bash
git clone [https://github.com/AlexanderGitHut/EVILLCODE.PY---CODIGO-MALDITO.git](https://github.com/AlexanderGitHut/EVILLCODE.PY---CODIGO-MALDITO.git)
cd EVILLCODE.PY---CODIGO-MALDITO

El script requiere las librerías scapy, colorama y pyfiglet. Instálalas con este comando:
sudo pip3 install scapy colorama pyfiglet --break-system-packages

🛠️ Modo de Uso
Dado que la herramienta manipula paquetes de red a bajo nivel, es obligatorio ejecutarla con privilegios de root (sudo):
sudo python3 evillcode.py

Pasos dentro del programa:
Escaneo: Introduce el rango de IP (ejemplo: 192.168.1.1/24) para ver quién está conectado.
Ataque: Ingresa la IP de la víctima y la IP del router para iniciar el envenenamiento.
Salida: Presiona Ctrl + C para detener el ataque; el script restaurará automáticamente las tablas ARP de los dispositivos.

⚠️ Aviso Legal e Importante
Este software ha sido creado exclusivamente con fines educativos y de aprendizaje en ciberseguridad. El uso de esta herramienta contra infraestructuras sin autorización previa es ilegal. El autor no se hace responsable del uso inadecuado de este código.

👤 Autor
Alexander - AlexanderGitHut
