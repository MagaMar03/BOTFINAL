"""
BOT DE REGISTRO MASIVO DE DENUNCIAS - SUNAT
Versión Microsoft Edge - V3 MEJORADO
Autor: Sistema Automatizado
Fecha: 2025

✨ FUNCIONALIDADES:
═══════════════════════════════════════════════════════════════
✅ Interfaz mejorada - Diseño profesional y moderno
✅ Corrección de iframe con carga AJAX
✅ Búsqueda inteligente de elementos en formularios
✅ Múltiples estrategias de clic y llenado de campos
═══════════════════════════════════════════════════════════════
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime, timedelta
import time
import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json


# ============================================
# CLASE PRINCIPAL DEL BOT
# ============================================
class BotDenunciasSUNAT:
    
    def __init__(self, archivo_excel, usuario, password, interfaz):
        self.archivo_excel = archivo_excel
        self.USUARIO = usuario
        self.PASSWORD = password
        self.interfaz = interfaz
        
        self.driver = None
        self.wait = None
        self.denuncias_exitosas = 0
        self.denuncias_fallidas = 0
        
        self.URL_LOGIN = "https://intranet.sunat.peru/cl-at-iamenu/"
        
        self.log("Bot inicializado correctamente (Microsoft Edge)")
    
    def log(self, mensaje):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.interfaz.escribir_consola(f"[{timestamp}] {mensaje}\n")
    
    # ============================================
    # INICIALIZACIÓN
    # ============================================
    
    def iniciar_navegador(self):
        try:
            self.log("Iniciando Microsoft Edge...")
            
            edge_options = Options()
            edge_options.add_argument('--start-maximized')
            edge_options.add_argument('--disable-blink-features=AutomationControlled')
            edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            edge_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Edge(options=edge_options)
            self.wait = WebDriverWait(self.driver, 20)
            
            self.log("✅ Microsoft Edge iniciado correctamente")
            return True
        except Exception as e:
            self.log(f"❌ Error al iniciar Edge: {str(e)}")
            self.log("ℹ️ Asegúrese de tener Microsoft Edge instalado")
            return False
    
    def cerrar_navegador(self):
        try:
            if self.driver:
                self.driver.quit()
                self.log("Navegador cerrado")
        except:
            pass
    
    # ============================================
    # LOGIN Y NAVEGACIÓN
    # ============================================

    def hacer_clic_robusto(self, elemento, descripcion, max_intentos=3):
        """
        Intenta hacer clic en un elemento usando múltiples estrategias
        hasta que sea exitoso o se agoten los intentos.

        Estrategias:
        1. Click normal con Selenium
        2. Click con JavaScript
        3. Click con ActionChains
        4. Click con offset
        """
        for intento in range(1, max_intentos + 1):
            try:
                self.log(f"    → Intento {intento}/{max_intentos} para {descripcion}...")

                # Estrategia 1: Scroll y click normal
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", elemento)
                    time.sleep(0.5)
                    elemento.click()
                    self.log(f"    ✅ Clic exitoso (método normal)")
                    return True
                except:
                    pass

                # Estrategia 2: JavaScript click
                try:
                    self.driver.execute_script("arguments[0].click();", elemento)
                    self.log(f"    ✅ Clic exitoso (JavaScript)")
                    return True
                except:
                    pass

                # Estrategia 3: ActionChains
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(self.driver)
                    actions.move_to_element(elemento).click().perform()
                    self.log(f"    ✅ Clic exitoso (ActionChains)")
                    return True
                except:
                    pass

                # Estrategia 4: Force click con JavaScript (más agresivo)
                try:
                    self.driver.execute_script("""
                        arguments[0].dispatchEvent(new MouseEvent('click', {
                            view: window,
                            bubbles: true,
                            cancelable: true
                        }));
                    """, elemento)
                    self.log(f"    ✅ Clic exitoso (Force JavaScript)")
                    return True
                except:
                    pass

                if intento < max_intentos:
                    self.log(f"    ⚠️ Intento {intento} falló, esperando antes de reintentar...")
                    time.sleep(2)

            except Exception as e:
                self.log(f"    ❌ Error en intento {intento}: {str(e)}")
                if intento < max_intentos:
                    time.sleep(2)

        self.log(f"    ❌ FALLO: No se pudo hacer clic en {descripcion} después de {max_intentos} intentos")
        return False

    def pausa_interactiva_y_captura(self):
        """
        🔬 FUNCIÓN DE PAUSA INTERACTIVA PARA DEBUGGING

        Esta función:
        1. PAUSA el programa después del clic en "Registro de Denuncias"
        2. Te permite hacer clic MANUAL en el formulario que aparece
        3. Espera tu confirmación
        4. CAPTURA TODO el HTML del iframe y selectores en ese momento exacto
        5. EXPORTA toda la información a archivos TXT para análisis

        Esto nos permite obtener el HTML REAL del iframe problemático.
        """
        try:
            self.log("\n" + "="*80)
            self.log("⏸️  PAUSA INTERACTIVA ACTIVADA")
            self.log("="*80)

            # Esperar a que cargue el iframe
            self.log("⏳ Esperando 5 segundos para que cargue el iframe...")
            time.sleep(5)

            # Mostrar diálogo al usuario
            respuesta = messagebox.showinfo(
                "🔬 PAUSA INTERACTIVA - DEBUGGING",
                "El bot se ha pausado después de hacer clic en 'Registro de Denuncias'.\n\n"
                "📋 INSTRUCCIONES:\n\n"
                "1. Observa la ventana del navegador Edge\n"
                "2. Si ves un formulario, haz clic MANUAL sobre él\n"
                "3. Si hay campos de entrada, haz clic en alguno\n"
                "4. Cuando termines, haz clic en OK aquí\n\n"
                "⚠️ El bot capturará TODA la información HTML\n"
                "   del iframe en ese momento exacto.\n\n"
                "Haz clic en OK cuando estés listo..."
            )

            self.log("✅ Usuario confirmó - Iniciando captura completa...")

            # Esperar un momento adicional
            time.sleep(2)

            # EJECUTAR DIAGNÓSTICO COMPLETO
            self.log("\n🔍 Ejecutando diagnóstico ultra completo...")
            carpeta = self.exportar_diagnostico_completo(nombre_archivo="captura_interactiva")

            # Además, crear archivo TXT adicional con información específica
            if carpeta:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archivo_adicional = os.path.join(carpeta, f"CAPTURA_MANUAL_{timestamp}.txt")

                with open(archivo_adicional, "w", encoding="utf-8") as f:
                    f.write("="*80 + "\n")
                    f.write("CAPTURA DESPUÉS DE INTERVENCIÓN MANUAL\n")
                    f.write("="*80 + "\n")
                    f.write(f"Timestamp: {timestamp}\n")
                    f.write(f"URL actual: {self.driver.current_url}\n")
                    f.write(f"Título: {self.driver.title}\n\n")

                    f.write("="*80 + "\n")
                    f.write("IFRAMES ENCONTRADOS EN PÁGINA PRINCIPAL\n")
                    f.write("="*80 + "\n\n")

                    # Volver a contexto principal
                    self.driver.switch_to.default_content()
                    iframes = self.driver.find_elements(By.TAG_NAME, "iframe")

                    f.write(f"Total de iframes: {len(iframes)}\n\n")

                    for i, iframe in enumerate(iframes):
                        f.write(f"\n{'='*60}\n")
                        f.write(f"IFRAME #{i}\n")
                        f.write(f"{'='*60}\n")
                        f.write(f"ID: {iframe.get_attribute('id') or 'sin_id'}\n")
                        f.write(f"NAME: {iframe.get_attribute('name') or 'sin_name'}\n")
                        f.write(f"SRC: {iframe.get_attribute('src') or 'sin_src'}\n")
                        f.write(f"CLASS: {iframe.get_attribute('class') or 'sin_class'}\n")
                        f.write(f"VISIBLE: {iframe.is_displayed()}\n")
                        f.write(f"ENABLED: {iframe.is_enabled()}\n\n")

                        # Intentar acceder y buscar elementos clave
                        try:
                            self.driver.switch_to.default_content()
                            self.driver.switch_to.frame(i)

                            f.write("ACCESO: ✅ Exitoso\n\n")

                            # Buscar elementos clave
                            f.write("BÚSQUEDA DE ELEMENTOS CLAVE:\n")

                            # Campo tipodoc
                            try:
                                tipodoc = self.driver.find_element(By.NAME, "tipodoc")
                                f.write("  ✅ Campo 'tipodoc' ENCONTRADO ⭐⭐⭐\n")
                                f.write(f"     Tag: {tipodoc.tag_name}\n")
                                f.write(f"     ID: {tipodoc.get_attribute('id')}\n")
                                f.write(f"     Visible: {tipodoc.is_displayed()}\n")
                            except:
                                f.write("  ❌ Campo 'tipodoc' NO encontrado\n")

                            # Campo numdoc
                            try:
                                numdoc = self.driver.find_element(By.NAME, "numdoc")
                                f.write("  ✅ Campo 'numdoc' ENCONTRADO\n")
                            except:
                                f.write("  ❌ Campo 'numdoc' NO encontrado\n")

                            # Formulario registroden
                            try:
                                form = self.driver.find_element(By.NAME, "registroden")
                                f.write("  ✅ Formulario 'registroden' ENCONTRADO\n")
                            except:
                                f.write("  ❌ Formulario 'registroden' NO encontrado\n")

                            # Contar elementos
                            f.write(f"\nCONTEO DE ELEMENTOS:\n")
                            f.write(f"  Forms: {len(self.driver.find_elements(By.TAG_NAME, 'form'))}\n")
                            f.write(f"  Inputs: {len(self.driver.find_elements(By.TAG_NAME, 'input'))}\n")
                            f.write(f"  Selects: {len(self.driver.find_elements(By.TAG_NAME, 'select'))}\n")
                            f.write(f"  Buttons: {len(self.driver.find_elements(By.TAG_NAME, 'button'))}\n")

                            self.driver.switch_to.default_content()

                        except Exception as e:
                            f.write(f"ACCESO: ❌ Falló - {str(e)}\n")
                            self.driver.switch_to.default_content()

                    f.write("\n" + "="*80 + "\n")
                    f.write("🎯 RECOMENDACIÓN PARA CORRECCIÓN\n")
                    f.write("="*80 + "\n")
                    f.write("Busca en este archivo el iframe que tenga:\n")
                    f.write("  ✅ Campo 'tipodoc' ENCONTRADO ⭐⭐⭐\n\n")
                    f.write("Ese iframe es el correcto. Usa su ID o índice para corregir el código.\n")

                self.log(f"\n📁 Información adicional guardada en: {archivo_adicional}")

                # Mostrar cuadro final
                messagebox.showinfo(
                    "✅ Captura Completada",
                    f"La captura se completó exitosamente.\n\n"
                    f"📁 Carpeta: {os.path.basename(carpeta)}\n\n"
                    f"Archivos importantes:\n"
                    f"• 00_REPORTE_RESUMEN.txt\n"
                    f"• CAPTURA_MANUAL_{timestamp}.txt\n"
                    f"• iframe_X_*.html (HTML de cada iframe)\n\n"
                    f"Busca el iframe que contenga el campo 'tipodoc'"
                )

            self.log("✅ Pausa interactiva completada - Continuando...")

        except Exception as e:
            self.log(f"❌ Error en pausa interactiva: {str(e)}")
            import traceback
            self.log(traceback.format_exc())

    def cambiar_a_iframe_formulario_v2(self):
        """
        MÉTODO CORREGIDO - Incluye cambio al frame 'det'

        Estructura:
        - Página principal
          └─ iframe 'iframeApplication'
             └─ frame 'det'
                └─ Formulario con 'tipodoc'
        """
        self.log("  🔍 Accediendo al iframe anidado...")

        for intento in range(1, 4):
            try:
                self.log(f"\n  📍 Intento {intento}/3")

                # Volver al contexto principal
                self.driver.switch_to.default_content()

                # PASO 1: Cambiar a iframe 'iframeApplication'
                self.log("  → PASO 1: Buscando iframe 'iframeApplication'...")
                wait = WebDriverWait(self.driver, 10)

                iframe = wait.until(
                    EC.presence_of_element_located((By.ID, "iframeApplication"))
                )
                self.log("  ✓ Iframe encontrado")

                self.driver.switch_to.frame(iframe)
                self.log("  ✓ Cambio al iframe exitoso")
                time.sleep(1)

                # PASO 2: Cambiar al frame 'det' DENTRO del iframe
                self.log("  → PASO 2: Buscando frame 'det'...")
                wait_frame = WebDriverWait(self.driver, 10)

                frame_det = wait_frame.until(
                    EC.presence_of_element_located((By.NAME, "det"))
                )
                self.log("  ✓ Frame 'det' encontrado")

                self.driver.switch_to.frame(frame_det)
                self.log("  ✓ Cambio al frame 'det' exitoso")
                time.sleep(1)

                # PASO 3: Verificar que el campo 'tipodoc' existe
                self.log("  → PASO 3: Verificando campo 'tipodoc'...")
                campo_tipodoc = wait_frame.until(
                    EC.presence_of_element_located((By.NAME, "tipodoc"))
                )

                self.log("  ✅ ¡Campo 'tipodoc' encontrado!")

                if campo_tipodoc.tag_name.lower() == "select":
                    self.log("  ✅ Formulario completamente cargado")
                    return True

            except TimeoutException:
                self.log(f"  ⏱️ Timeout en intento {intento}")
                if intento < 3:
                    time.sleep(3)

            except Exception as e:
                self.log(f"  ❌ Error en intento {intento}: {str(e)[:100]}")
                if intento < 3:
                    time.sleep(3)

        self.log("  ❌ FALLO: No se pudo acceder al formulario")
        return False

    def encontrar_campo_en_cualquier_iframe(self, by, valor, max_intentos=3):
        """
        MÉTODO ULTRA ROBUSTO
        Busca un elemento en TODOS los iframes de forma recursiva
        """
        self.log(f"  🔍 Buscando '{valor}' en todos los iframes...")

        for intento in range(1, max_intentos + 1):
            try:
                # Intentar en página principal
                self.driver.switch_to.default_content()
                try:
                    elemento = self.driver.find_element(by, valor)
                    if elemento.is_displayed():
                        self.log(f"  ✅ Encontrado en página principal")
                        return elemento
                except:
                    pass

                # Buscar en iframes de nivel 1
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                self.log(f"  → {len(iframes)} iframes detectados")

                for i, iframe in enumerate(iframes):
                    try:
                        self.driver.switch_to.default_content()
                        self.driver.switch_to.frame(i)

                        # Buscar directamente
                        try:
                            elemento = self.driver.find_element(by, valor)
                            if elemento.is_displayed():
                                self.log(f"  ✅ Encontrado en iframe #{i}")
                                return elemento
                        except:
                            pass

                        # Buscar frames internos (nivel 2)
                        frames_internos = self.driver.find_elements(By.TAG_NAME, "frame")
                        frames_internos.extend(self.driver.find_elements(By.TAG_NAME, "iframe"))

                        for j, frame_interno in enumerate(frames_internos):
                            try:
                                self.driver.switch_to.frame(j)

                                elemento = self.driver.find_element(by, valor)
                                if elemento.is_displayed():
                                    self.log(f"  ✅ Encontrado en iframe #{i} → frame #{j}")
                                    return elemento

                                self.driver.switch_to.parent_frame()
                            except:
                                try:
                                    self.driver.switch_to.parent_frame()
                                except:
                                    pass

                    except:
                        pass

                if intento < max_intentos:
                    self.log(f"  → Intento {intento} falló, esperando...")
                    time.sleep(2)

            except Exception as e:
                self.log(f"  ⚠️ Error: {str(e)[:100]}")

        self.log(f"  ❌ No se encontró '{valor}' en ningún iframe")
        return None

    def encontrar_campo_por_texto_visible(self, texto_label, tipo_elemento="input"):
        """
        Busca campo usando el texto visible del label
        """
        self.log(f"  🔍 Buscando campo con label '{texto_label}'...")

        # XPaths que buscan por texto visible
        xpaths = [
            f"//td[contains(text(), '{texto_label}')]/following-sibling::td//{tipo_elemento}",
            f"//td[contains(text(), '{texto_label}')]//following::{tipo_elemento}[1]",
            f"//label[contains(text(), '{texto_label}')]/following::{tipo_elemento}[1]",
        ]

        # Buscar en página principal
        self.driver.switch_to.default_content()
        for xpath in xpaths:
            try:
                elemento = self.driver.find_element(By.XPATH, xpath)
                if elemento.is_displayed():
                    self.log(f"  ✅ Encontrado en página principal")
                    return elemento
            except:
                pass

        # Buscar en iframes
        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        for i, iframe in enumerate(iframes):
            try:
                self.driver.switch_to.default_content()
                self.driver.switch_to.frame(i)

                for xpath in xpaths:
                    try:
                        elemento = self.driver.find_element(By.XPATH, xpath)
                        if elemento.is_displayed():
                            self.log(f"  ✅ Encontrado en iframe #{i}")
                            return elemento
                    except:
                        pass

                # Buscar en frames internos
                frames = self.driver.find_elements(By.TAG_NAME, "frame")
                for j, frame in enumerate(frames):
                    try:
                        self.driver.switch_to.frame(j)

                        for xpath in xpaths:
                            try:
                                elemento = self.driver.find_element(By.XPATH, xpath)
                                if elemento.is_displayed():
                                    self.log(f"  ✅ Encontrado en iframe #{i} → frame #{j}")
                                    return elemento
                            except:
                                pass

                        self.driver.switch_to.parent_frame()
                    except:
                        pass

            except:
                pass

        self.log(f"  ❌ No se encontró campo con label '{texto_label}'")
        return None

    def acceder_al_formulario_y_buscar_campo(self, nombre_campo):
        """
        MÉTODO HÍBRIDO - Combina todos los enfoques

        1. Intenta método directo (iframeApplication → det → campo)
        2. Si falla, busca en todos los iframes
        3. Si falla, busca por texto visible
        """
        self.log(f"  🎯 Buscando campo '{nombre_campo}'...")

        # INTENTO 1: Método directo (el más rápido)
        try:
            self.log("  → Método 1: Ruta directa")
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame("iframeApplication")
            time.sleep(0.5)
            self.driver.switch_to.frame("det")
            time.sleep(0.5)

            elemento = self.driver.find_element(By.NAME, nombre_campo)
            if elemento.is_displayed():
                self.log(f"  ✅ Encontrado por método directo")
                return elemento
        except Exception as e:
            self.log(f"  → Método 1 falló: {str(e)[:50]}")

        # INTENTO 2: Búsqueda exhaustiva en iframes
        self.log("  → Método 2: Búsqueda en todos los iframes")
        elemento = self.encontrar_campo_en_cualquier_iframe(By.NAME, nombre_campo)
        if elemento:
            return elemento

        # INTENTO 3: Por texto visible
        mapeo_textos = {
            "tipodoc": "Tipo Documento",
            "numdoc": "Número",
            "nombre": "Apellidos y Nombres",
            "dpto": "Departamento",
            "prov": "Provincia",
            "dist": "Distrito",
            "telefono": "Teléfono",
            "correo": "Correo Electrónico"
        }

        if nombre_campo in mapeo_textos:
            self.log("  → Método 3: Búsqueda por texto visible")
            tipo_elemento = "select" if nombre_campo in ["tipodoc", "dpto", "prov", "dist"] else "input"
            elemento = self.encontrar_campo_por_texto_visible(mapeo_textos[nombre_campo], tipo_elemento)
            if elemento:
                return elemento

        self.log(f"  ❌ No se pudo encontrar '{nombre_campo}' con ningún método")
        return None

    # ═══════════════════════════════════════════════════════════════════════════
    # 🏆 SISTEMA PROFESIONAL DE LOCALIZACIÓN DE ELEMENTOS
    # ═══════════════════════════════════════════════════════════════════════════

    # Diccionario COMPLETO de definiciones de campos del formulario SUNAT
    CAMPOS_SUNAT = {
        # ─────────────────────────────────────────────────────────────────────────
        # SECCIÓN 1: IDENTIFICACIÓN DEL DENUNCIANTE
        # ─────────────────────────────────────────────────────────────────────────
        "tipodoc": {
            "tipo": "select",
            "selectores": ["tipodoc", "tipoDoc", "tipo_doc", "cboTipoDoc"],
            "textos_visibles": ["Tipo Documento", "Tipo Doc.", "Tipo de Documento", "TIPO DOCUMENTO", "Tipo Docum"],
            "xpaths": [
                "//select[@name='tipodoc']",
                "//select[contains(@id,'tipo')]",
                "//td[contains(text(),'Tipo')]/following::select[1]",
                "//label[contains(text(),'Tipo')]/following::select[1]"
            ]
        },
        "numdoc": {
            "tipo": "input",
            "selectores": ["numdoc", "numDoc", "num_doc", "txtNumDoc", "numero"],
            "textos_visibles": ["Número", "Numero", "Nro.", "NRO", "NÚMERO", "Nº", "N°", "Núm"],
            "xpaths": [
                "//input[@name='numdoc']",
                "//input[contains(@id,'num')]",
                "//td[contains(text(),'mero')]/following::input[1]",
                "//td[contains(text(),'Nro')]/following::input[1]"
            ]
        },
        "nombre": {
            "tipo": "input",
            "selectores": ["nombre", "nombres", "txtNombre", "razonSocial"],
            "textos_visibles": ["Apellidos y Nombres", "Razón Social", "Nombre", "APELLIDOS Y NOMBRES", "Denominación"],
            "xpaths": [
                "//input[@name='nombre']",
                "//input[@id='nombre']",
                "//td[contains(text(),'Apellidos')]/following::input[1]",
                "//td[contains(text(),'Razón')]/following::input[1]"
            ]
        },
        "dpto": {
            "tipo": "select",
            "selectores": ["dpto", "departamento", "cboDpto", "dep"],
            "textos_visibles": ["Departamento", "DEPARTAMENTO", "Dpto.", "Dpto"],
            "xpaths": [
                "//select[@name='dpto']",
                "//select[contains(@id,'dpto')]",
                "//td[contains(text(),'Departamento')]/following::select[1]"
            ]
        },
        "prov": {
            "tipo": "select",
            "selectores": ["prov", "provincia", "cboProv"],
            "textos_visibles": ["Provincia", "PROVINCIA", "Prov."],
            "xpaths": [
                "//select[@name='prov']",
                "//select[contains(@id,'prov')]",
                "//td[contains(text(),'Provincia')]/following::select[1]"
            ]
        },
        "dist": {
            "tipo": "select",
            "selectores": ["dist", "distrito", "cboDist"],
            "textos_visibles": ["Distrito", "DISTRITO", "Dist."],
            "xpaths": [
                "//select[@name='dist']",
                "//select[contains(@id,'dist')]",
                "//td[contains(text(),'Distrito')]/following::select[1]"
            ]
        },
        "telefono": {
            "tipo": "input",
            "selectores": ["telefono", "telef", "txtTelefono", "fono"],
            "textos_visibles": ["Teléfono", "Telefono", "TELÉFONO", "Tel.", "Fono"],
            "xpaths": [
                "//input[@name='telefono']",
                "//input[contains(@id,'telef')]",
                "//td[contains(text(),'fono')]/following::input[1]"
            ]
        },
        "correo": {
            "tipo": "input",
            "selectores": ["correo", "email", "mail", "txtCorreo"],
            "textos_visibles": ["Correo", "Email", "E-mail", "CORREO", "Correo electrónico"],
            "xpaths": [
                "//input[@name='correo']",
                "//input[contains(@id,'correo')]",
                "//input[contains(@id,'mail')]",
                "//td[contains(text(),'Correo')]/following::input[1]"
            ]
        },

        # ─────────────────────────────────────────────────────────────────────────
        # BOTONES DE ACCIÓN
        # ─────────────────────────────────────────────────────────────────────────
        "buscar": {
            "tipo": "button",
            "selectores": ["buscar", "btnBuscar", "btn_buscar"],
            "textos_visibles": ["Buscar", "BUSCAR", "Buscar "],
            "xpaths": [
                "//input[@type='button'][@value='Buscar']",
                "//input[@type='submit'][@value='Buscar']",
                "//button[contains(text(),'Buscar')]",
                "//input[contains(@onclick,'buscar')]",
                "//a[contains(text(),'Buscar')]"
            ],
            "onclick": ["buscar()", "fnBuscar()", "buscarDatos()"]
        },
        "siguiente": {
            "tipo": "button",
            "selectores": ["siguiente", "btnSiguiente", "btn_siguiente", "validar"],
            "textos_visibles": ["Siguiente", "SIGUIENTE", "Validar", "Continuar", ">>"],
            "xpaths": [
                "//input[@type='button'][@value='Siguiente']",
                "//input[@type='button'][contains(@value,'iguiente')]",
                "//button[contains(text(),'Siguiente')]",
                "//input[contains(@onclick,'siguiente')]",
                "//input[contains(@onclick,'validar')]",
                "//a[contains(text(),'Siguiente')]"
            ],
            "onclick": ["siguiente()", "fnSiguiente()", "validar()", "fnValidar()"]
        },
        "grabar": {
            "tipo": "button",
            "selectores": ["grabar", "btnGrabar", "guardar"],
            "textos_visibles": ["Grabar", "GRABAR", "Guardar", "Enviar"],
            "xpaths": [
                "//input[@type='button'][@value='Grabar']",
                "//input[@type='submit'][@value='Grabar']",
                "//button[contains(text(),'Grabar')]"
            ],
            "onclick": ["grabar()", "fnGrabar()", "guardar()"]
        }
    }

    def buscar_elemento_profesional(self, nombre_campo):
        """
        🏆 MÉTODO PROFESIONAL - Garantiza encontrar el elemento usando TODAS las estrategias

        Orden de búsqueda:
        1. PRIMERO: Buscar en el contexto ACTUAL (ya estamos en el iframe correcto)
        2. Si no encuentra, navegar a todos los iframes/frames posibles
        3. En cada contexto, probar TODOS los selectores definidos
        4. Probar TODOS los XPaths definidos
        5. Buscar por texto literal visible en pantalla
        6. Buscar por función onclick (para botones)

        Returns:
            WebElement si encuentra, None si no
        """
        if nombre_campo not in self.CAMPOS_SUNAT:
            self.log(f"  ⚠️ Campo '{nombre_campo}' no está definido en CAMPOS_SUNAT")
            return None

        campo = self.CAMPOS_SUNAT[nombre_campo]
        self.log(f"\n  🔎 BÚSQUEDA PROFESIONAL: '{nombre_campo}' ({campo['tipo']})")

        # ═══════════════════════════════════════════════════════════════════════
        # PRIMERO: Intentar en el CONTEXTO ACTUAL (sin cambiar de iframe)
        # ═══════════════════════════════════════════════════════════════════════
        self.log(f"  📂 Buscando en contexto ACTUAL (sin cambiar iframe)...")

        elemento = self._buscar_en_contexto_actual(nombre_campo, campo)
        if elemento:
            self.log(f"  ✅ ENCONTRADO en contexto actual")
            return elemento

        # ═══════════════════════════════════════════════════════════════════════
        # SEGUNDO: Si no encontró, buscar en TODOS los contextos
        # ═══════════════════════════════════════════════════════════════════════
        self.log(f"  → No encontrado en contexto actual, buscando en todos los contextos...")

        # Obtener todos los contextos de iframes
        contextos = self._obtener_todos_los_contextos()

        for ctx_nombre, ctx_path in contextos:
            self.log(f"  📂 Buscando en contexto: {ctx_nombre}")

            # Cambiar al contexto
            if not self._cambiar_a_contexto(ctx_path):
                continue

            elemento = self._buscar_en_contexto_actual(nombre_campo, campo)
            if elemento:
                self.log(f"  ✅ ENCONTRADO en {ctx_nombre}")
                return elemento

        self.log(f"  ❌ No se encontró '{nombre_campo}' en ningún contexto")
        return None

    def _buscar_en_contexto_actual(self, nombre_campo, campo):
        """
        🔍 Busca el elemento en el contexto actual sin cambiar de iframe
        """
        # ESTRATEGIA 1: Por selectores (name, id)
        for selector in campo["selectores"]:
            try:
                elem = self.driver.find_element(By.NAME, selector)
                if elem and elem.is_displayed():
                    self.log(f"    ✓ Encontrado por NAME='{selector}'")
                    return elem
            except: pass

            try:
                elem = self.driver.find_element(By.ID, selector)
                if elem and elem.is_displayed():
                    self.log(f"    ✓ Encontrado por ID='{selector}'")
                    return elem
            except: pass

        # ESTRATEGIA 2: Por XPaths definidos
        for xpath in campo["xpaths"]:
            try:
                elem = self.driver.find_element(By.XPATH, xpath)
                if elem and elem.is_displayed():
                    self.log(f"    ✓ Encontrado por XPATH")
                    return elem
            except: pass

        # ESTRATEGIA 3: Por texto visible literal
        for texto in campo["textos_visibles"]:
            elem = self._buscar_campo_por_texto_cercano(texto, campo["tipo"])
            if elem:
                self.log(f"    ✓ Encontrado por TEXTO '{texto}'")
                return elem

        # ESTRATEGIA 4: Por onclick (solo botones)
        if campo["tipo"] == "button" and "onclick" in campo:
            for onclick in campo["onclick"]:
                try:
                    elem = self.driver.find_element(
                        By.XPATH, f"//*[contains(@onclick,'{onclick.replace('()', '')}')]"
                    )
                    if elem:
                        self.log(f"    ✓ Encontrado por ONCLICK='{onclick}'")
                        return elem
                except: pass

        return None

    def _obtener_todos_los_contextos(self):
        """
        📋 Obtiene lista de todos los contextos (main + iframes) para buscar
        Returns: Lista de tuplas (nombre, path_para_navegar)
        """
        contextos = [("main", [])]

        try:
            self.driver.switch_to.default_content()

            # Buscar iframes en documento principal
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            frames = self.driver.find_elements(By.TAG_NAME, "frame")

            self.log(f"  📊 Detectados: {len(iframes)} iframes, {len(frames)} frames en main")

            for i, iframe in enumerate(iframes):
                nombre = iframe.get_attribute("name") or iframe.get_attribute("id") or f"iframe_{i}"
                contextos.append((f"iframe:{nombre}", [("iframe", nombre, i)]))

                # Buscar frames anidados dentro de este iframe
                try:
                    self.driver.switch_to.frame(iframe)
                    frames_internos = self.driver.find_elements(By.TAG_NAME, "frame")
                    self.log(f"    → Dentro de '{nombre}': {len(frames_internos)} frames anidados")
                    for j, frame in enumerate(frames_internos):
                        nombre_frame = frame.get_attribute("name") or f"frame_{j}"
                        self.log(f"      - Frame encontrado: '{nombre_frame}'")
                        contextos.append((
                            f"iframe:{nombre}→frame:{nombre_frame}",
                            [("iframe", nombre, i), ("frame", nombre_frame, j)]
                        ))
                    self.driver.switch_to.default_content()
                except Exception as e:
                    self.log(f"    ⚠️ Error explorando iframe '{nombre}': {str(e)[:50]}")
                    self.driver.switch_to.default_content()

            for i, frame in enumerate(frames):
                nombre = frame.get_attribute("name") or f"frame_{i}"
                contextos.append((f"frame:{nombre}", [("frame", nombre, i)]))

        except Exception as e:
            self.log(f"  ⚠️ Error obteniendo contextos: {e}")

        self.log(f"  📋 Total contextos detectados: {len(contextos)}")
        for ctx_nombre, _ in contextos:
            self.log(f"     - {ctx_nombre}")

        return contextos

    def _cambiar_a_contexto(self, path):
        """
        🔄 Cambia al contexto especificado por el path
        """
        try:
            self.driver.switch_to.default_content()

            for tipo, nombre, indice in path:
                if tipo in ("iframe", "frame"):
                    try:
                        # Intentar por nombre primero
                        self.driver.switch_to.frame(nombre)
                    except:
                        # Si falla, intentar por índice
                        elementos = self.driver.find_elements(By.TAG_NAME, tipo)
                        if indice < len(elementos):
                            self.driver.switch_to.frame(elementos[indice])
                        else:
                            return False
            return True
        except:
            return False

    def _buscar_campo_por_texto_cercano(self, texto, tipo_elemento):
        """
        🔍 Busca un campo por el texto visible que aparece cerca (en la misma fila, celda, etc.)
        """
        # XPaths para encontrar el campo asociado al texto
        xpaths_busqueda = [
            # Texto en TD, campo en siguiente TD
            f"//td[contains(normalize-space(text()),'{texto}')]/following-sibling::td[1]//{tipo_elemento if tipo_elemento != 'button' else '*'}",
            # Texto en TD, campo en TD siguiente cualquier nivel
            f"//td[contains(normalize-space(.),'{texto}')]/following::td[1]//{tipo_elemento if tipo_elemento != 'button' else '*'}[1]",
            # Texto en cualquier elemento, campo siguiente
            f"//*[contains(normalize-space(text()),'{texto}')]/following::{tipo_elemento if tipo_elemento != 'button' else '*'}[1]",
            # Label con for
            f"//label[contains(normalize-space(.),'{texto}')]/@for",
            # Texto en TH, campo en TD de misma fila
            f"//tr[th[contains(normalize-space(.),'{texto}')]]/td//{tipo_elemento if tipo_elemento != 'button' else '*'}",
        ]

        # Para botones, agregar búsquedas específicas
        if tipo_elemento == "button":
            xpaths_busqueda.extend([
                f"//input[@type='button'][@value='{texto}']",
                f"//input[@type='submit'][@value='{texto}']",
                f"//button[normalize-space(.)='{texto}']",
                f"//a[normalize-space(.)='{texto}']",
                f"//input[@type='button'][contains(@value,'{texto}')]",
            ])

        for xpath in xpaths_busqueda:
            try:
                # Si es un atributo (for), obtener el ID y buscar el elemento
                if "/@for" in xpath:
                    label = self.driver.find_element(By.XPATH, xpath.replace("/@for", ""))
                    for_id = label.get_attribute("for")
                    if for_id:
                        elem = self.driver.find_element(By.ID, for_id)
                        if elem and elem.is_displayed():
                            return elem
                else:
                    elem = self.driver.find_element(By.XPATH, xpath)
                    if elem and elem.is_displayed():
                        return elem
            except:
                pass

        return None

    # ═══════════════════════════════════════════════════════════════════════════
    # MÉTODOS DE COMPATIBILIDAD (mantener los anteriores funcionando)
    # ═══════════════════════════════════════════════════════════════════════════

    def buscar_elemento_universal(self, nombre_campo, tipo_elemento="input"):
        """
        🎯 MÉTODO MAESTRO - Ahora usa el sistema profesional primero
        """
        # Primero intentar con el sistema profesional
        resultado = self.buscar_elemento_profesional(nombre_campo)
        if resultado:
            return resultado

        # Fallback al sistema anterior
        self.log(f"  → Usando sistema de fallback para '{nombre_campo}'...")

        # Mapeo de campos a textos visibles literales
        mapeo_textos = {
            # SECCIÓN 1: Identificación del denunciado
            "tipodoc": ["Tipo Documento", "Tipo Doc", "TIPO DOCUMENTO"],
            "numdoc": ["Número", "Numero", "NRO", "NÚMERO"],
            "nombre": ["Apellidos y Nombres", "Razón social", "APELLIDOS"],
            "buscar": ["Buscar", "BUSCAR"],
            "siguiente": ["Siguiente", "SIGUIENTE", "Validar"],

            # SECCIÓN 2: Atención de denuncias
            "modalidad": ["Modalidad Evasión Denunciada", "Modalidad", "MODALIDAD"],
            "detalle": ["DETALLE DE LA DENUNCIA", "Detalle", "DETALLE"],
            "fecha_sid": ["Fecha SID", "FECHA SID"],
            "MesDesde": ["Del Mes", "Mes Desde", "DEL MES"],
            "AnioDesde": ["Del Año", "Año Desde", "DEL AÑO"],
            "MesHasta": ["Al Mes", "Mes Hasta", "AL MES"],
            "AnioHasta": ["Al Año", "Año Hasta", "AL AÑO"],
            "elementos": ["Tipo de Pruebas", "Elementos", "ELEMENTOS"],
            "otros": ["Otros", "OTROS", "Detalle Otros"],

            # SECCIÓN 3: Identificación del denunciante
            "dpto": ["Departamento", "DEPARTAMENTO"],
            "prov": ["Provincia", "PROVINCIA"],
            "dist": ["Distrito", "DISTRITO"],
            "telefono": ["Teléfono", "TELEFONO", "Telefono"],
            "correo": ["Correo", "CORREO", "Email", "Correo Electrónico"],
            "tipvia": ["Tipo Vía", "Vía", "TIPO VIA"],
            "nomvia": ["Nombre Vía", "Nombre de Vía", "NOMBRE VIA"]
        }

        # ═══════════════════════════════════════
        # INTENTO 1: JavaScript en todos los iframes
        # ═══════════════════════════════════════
        self.log("  → Intento 1: JavaScript en iframes...")
        try:
            resultado = self.buscar_con_javascript(nombre_campo, tipo_elemento)
            if resultado:
                self.log("  ✅ Encontrado con JavaScript")
                return resultado
        except Exception as e:
            self.log(f"  → JavaScript falló: {str(e)[:50]}")

        # ═══════════════════════════════════════
        # INTENTO 2: Selenium recursivo por selector
        # ═══════════════════════════════════════
        self.log("  → Intento 2: Selenium recursivo por selector...")
        try:
            resultado = self.buscar_en_todos_contextos_recursivo(By.NAME, nombre_campo)
            if resultado:
                self.log("  ✅ Encontrado con Selenium recursivo (by NAME)")
                return resultado
        except Exception as e:
            self.log(f"  → Selenium recursivo falló: {str(e)[:50]}")

        # También probar por ID si el nombre coincide
        self.log("  → Intento 2b: Selenium recursivo por ID...")
        try:
            resultado = self.buscar_en_todos_contextos_recursivo(By.ID, nombre_campo)
            if resultado:
                self.log("  ✅ Encontrado con Selenium recursivo (by ID)")
                return resultado
        except:
            pass

        # ═══════════════════════════════════════
        # INTENTO 3: Por texto literal visible
        # ═══════════════════════════════════════
        if nombre_campo in mapeo_textos:
            self.log("  → Intento 3: Búsqueda por texto literal...")
            for texto in mapeo_textos[nombre_campo]:
                try:
                    resultado = self.buscar_por_texto_literal(texto, tipo_elemento)
                    if resultado:
                        self.log(f"  ✅ Encontrado por texto literal '{texto}'")
                        return resultado
                except:
                    pass

        # ═══════════════════════════════════════
        # INTENTO 4: Método anterior (fallback)
        # ═══════════════════════════════════════
        self.log("  → Intento 4: Método híbrido anterior...")
        try:
            resultado = self.acceder_al_formulario_y_buscar_campo(nombre_campo)
            if resultado:
                self.log("  ✅ Encontrado con método híbrido anterior")
                return resultado
        except:
            pass

        self.log(f"  ❌ No se encontró '{nombre_campo}' con ningún método")
        return None

    def buscar_con_javascript(self, nombre_campo, tipo_elemento="input"):
        """
        🌐 Busca elemento usando JavaScript que accede a todos los iframes
        """
        script = """
        function buscarEnTodosLosContextos(nombreCampo, tipoElemento) {
            // Buscar en documento principal
            var elemento = document.querySelector('[name="' + nombreCampo + '"]') ||
                          document.getElementById(nombreCampo);
            if (elemento) return elemento;

            // Buscar en todos los iframes
            var iframes = document.querySelectorAll('iframe, frame');
            for (var i = 0; i < iframes.length; i++) {
                try {
                    var iframeDoc = iframes[i].contentDocument || iframes[i].contentWindow.document;

                    // Buscar directo en este iframe
                    elemento = iframeDoc.querySelector('[name="' + nombreCampo + '"]') ||
                              iframeDoc.getElementById(nombreCampo);
                    if (elemento) return elemento;

                    // Buscar en frames anidados dentro del iframe
                    var framesInternos = iframeDoc.querySelectorAll('iframe, frame');
                    for (var j = 0; j < framesInternos.length; j++) {
                        try {
                            var frameDoc = framesInternos[j].contentDocument ||
                                          framesInternos[j].contentWindow.document;
                            elemento = frameDoc.querySelector('[name="' + nombreCampo + '"]') ||
                                      frameDoc.getElementById(nombreCampo);
                            if (elemento) return elemento;
                        } catch(e) {}
                    }
                } catch(e) {
                    // Error de Same-Origin, continuar con siguiente iframe
                }
            }
            return null;
        }
        return buscarEnTodosLosContextos(arguments[0], arguments[1]);
        """

        try:
            elemento = self.driver.execute_script(script, nombre_campo, tipo_elemento)
            return elemento
        except Exception as e:
            return None

    def buscar_en_todos_contextos_recursivo(self, by, valor, max_profundidad=3):
        """
        🔄 Busca elemento de forma RECURSIVA en todos los iframes/frames
        Cuando encuentra el elemento, SE QUEDA en ese contexto.
        """
        self.driver.switch_to.default_content()

        def buscar_recursivo(profundidad=0):
            if profundidad > max_profundidad:
                return None

            # Buscar en contexto actual
            try:
                elemento = self.driver.find_element(by, valor)
                if elemento.is_displayed() or elemento.is_enabled():
                    return elemento
            except:
                pass

            # Buscar en cada iframe/frame hijo
            frames = []
            try:
                frames = self.driver.find_elements(By.TAG_NAME, "iframe")
                frames += self.driver.find_elements(By.TAG_NAME, "frame")
            except:
                pass

            for i, frame in enumerate(frames):
                try:
                    self.driver.switch_to.frame(frame)
                    resultado = buscar_recursivo(profundidad + 1)
                    if resultado:
                        return resultado  # ¡Mantener contexto!
                    self.driver.switch_to.parent_frame()
                except:
                    try:
                        self.driver.switch_to.parent_frame()
                    except:
                        self.driver.switch_to.default_content()

            return None

        return buscar_recursivo()

    def buscar_por_texto_literal(self, texto_buscar, tipo_elemento="input"):
        """
        📝 Busca elemento por el texto visible literal (ej: "Tipo Documento")
        Busca en todos los contextos de forma recursiva.
        """
        self.driver.switch_to.default_content()

        # XPaths para buscar por texto visible
        xpaths = [
            # Buscar label/td con texto y luego el input/select siguiente
            f"//td[contains(text(), '{texto_buscar}')]/following::*[self::input or self::select or self::button][1]",
            f"//td[contains(text(), '{texto_buscar}')]//following-sibling::td//{tipo_elemento}",
            f"//label[contains(text(), '{texto_buscar}')]/following::*[self::input or self::select][1]",
            f"//th[contains(text(), '{texto_buscar}')]/following::*[self::input or self::select][1]",
            # Para botones
            f"//input[@value='{texto_buscar}']",
            f"//button[contains(text(), '{texto_buscar}')]",
            f"//input[contains(@value, '{texto_buscar}')]",
        ]

        def buscar_en_contexto():
            for xpath in xpaths:
                try:
                    elemento = self.driver.find_element(By.XPATH, xpath)
                    if elemento.is_displayed() or elemento.is_enabled():
                        return elemento
                except:
                    pass
            return None

        def buscar_recursivo(profundidad=0):
            if profundidad > 3:
                return None

            # Buscar en contexto actual
            resultado = buscar_en_contexto()
            if resultado:
                return resultado

            # Buscar en frames hijos
            frames = []
            try:
                frames = self.driver.find_elements(By.TAG_NAME, "iframe")
                frames += self.driver.find_elements(By.TAG_NAME, "frame")
            except:
                pass

            for frame in frames:
                try:
                    self.driver.switch_to.frame(frame)
                    resultado = buscar_recursivo(profundidad + 1)
                    if resultado:
                        return resultado
                    self.driver.switch_to.parent_frame()
                except:
                    try:
                        self.driver.switch_to.parent_frame()
                    except:
                        self.driver.switch_to.default_content()

            return None

        return buscar_recursivo()

    def llenar_campo_universal(self, nombre_campo, valor, tipo_elemento="input"):
        """
        ✏️ Llena un campo usando el método universal de búsqueda
        """
        self.log(f"\n  ✏️ Llenando campo '{nombre_campo}' con valor '{valor}'")

        elemento = self.buscar_elemento_universal(nombre_campo, tipo_elemento)
        if not elemento:
            self.log(f"  ❌ No se encontró el campo '{nombre_campo}'")
            return False

        try:
            if tipo_elemento == "select":
                return self._llenar_select_inteligente(elemento, valor, nombre_campo)
            else:
                # Input normal
                try:
                    elemento.clear()
                    time.sleep(0.2)
                    elemento.send_keys(valor)
                    self.log(f"  ✅ Valor ingresado: '{valor}'")
                    return True
                except:
                    # Fallback JavaScript
                    self.driver.execute_script(f"arguments[0].value = '{valor}';", elemento)
                    self.log(f"  ✅ Valor ingresado (JS): '{valor}'")
                    return True

        except Exception as e:
            self.log(f"  ❌ Error al llenar campo: {str(e)[:50]}")
            return False

    def llenar_campo_con_espera_robusta(self, nombre_campo, valor, tipo_elemento="input", timeout=20):
        """
        🚀 Método ROBUSTO para llenar campos con espera extendida y múltiples estrategias

        Similar al patrón usado para encontrar el campo 'modalidad' en Sección 2.
        Usa 4 estrategias diferentes con timeout configurable.

        Args:
            nombre_campo: nombre del campo (name attribute)
            valor: valor a llenar
            tipo_elemento: "input", "select", etc.
            timeout: segundos de espera (default 20)
        """
        self.log(f"\n  🚀 Llenando campo '{nombre_campo}' (modo robusto)...")
        elemento_encontrado = False

        # INTENTO 1: Búsqueda directa por NAME con espera extendida
        try:
            self.log(f"    → Intento 1: Búsqueda directa por NAME ({timeout}s espera)...")
            wait = WebDriverWait(self.driver, timeout)
            elemento = wait.until(
                EC.presence_of_element_located((By.NAME, nombre_campo))
            )
            self.log(f"    ✅ Campo '{nombre_campo}' encontrado (búsqueda directa)")
            elemento_encontrado = True
        except Exception as e:
            self.log(f"    ⚠️ Intento 1 falló: {str(e)[:50]}")

        # INTENTO 2: Verificar usando JavaScript
        if not elemento_encontrado:
            try:
                self.log("    → Intento 2: Verificación con JavaScript...")
                resultado = self.driver.execute_script(f"""
                    var campo = document.getElementsByName('{nombre_campo}')[0];
                    if (campo) {{
                        return true;
                    }}
                    return false;
                """)
                if resultado:
                    self.log(f"    ✅ Campo '{nombre_campo}' encontrado (JavaScript)")
                    elemento_encontrado = True
            except Exception as e:
                self.log(f"    ⚠️ Intento 2 falló: {str(e)[:50]}")

        # INTENTO 3: Usar método universal (con todas sus estrategias)
        if not elemento_encontrado:
            try:
                self.log("    → Intento 3: Usando buscar_elemento_universal...")
                elemento_test = self.buscar_elemento_universal(nombre_campo, tipo_elemento)
                if elemento_test:
                    self.log(f"    ✅ Campo '{nombre_campo}' encontrado (método universal)")
                    elemento_encontrado = True
            except Exception as e:
                self.log(f"    ⚠️ Intento 3 falló: {str(e)[:50]}")

        if not elemento_encontrado:
            self.log(f"    ❌ No se encontró el campo '{nombre_campo}' después de 3 intentos")
            return False

        # Ahora llenar el campo usando el método estándar
        self.log(f"    → Llenando campo con valor: '{valor}'...")
        resultado = self.llenar_campo_universal(nombre_campo, valor, tipo_elemento)

        if resultado:
            self.log(f"    ✅ Campo '{nombre_campo}' llenado exitosamente")
        else:
            self.log(f"    ❌ No se pudo llenar el campo '{nombre_campo}'")

        return resultado

    def _llenar_select_inteligente(self, elemento, valor, nombre_campo):
        """
        🎯 Rellena un SELECT con búsqueda inteligente y flexible

        Estrategias en orden:
        1. Coincidencia exacta
        2. Coincidencia exacta ignorando mayúsculas
        3. Valor del Excel contenido en opción
        4. Opción contenida en valor del Excel
        5. Similitud por palabras clave
        6. Búsqueda de palabras parciales

        Si no encuentra, muestra TODAS las opciones disponibles
        """
        select = Select(elemento)
        opciones = select.options

        # Obtener lista de textos de opciones (excluyendo vacías)
        opciones_texto = [(i, op.text.strip()) for i, op in enumerate(opciones) if op.text.strip()]

        self.log(f"  📋 Campo '{nombre_campo}' tiene {len(opciones_texto)} opciones disponibles")

        valor_buscar = str(valor).strip()
        valor_upper = valor_buscar.upper()
        valor_lower = valor_buscar.lower()

        # ═══════════════════════════════════════════════════════════
        # ESTRATEGIA 1: Coincidencia EXACTA
        # ═══════════════════════════════════════════════════════════
        for idx, texto in opciones_texto:
            if texto == valor_buscar:
                select.select_by_visible_text(texto)
                self.log(f"  ✅ Seleccionado (exacto): '{texto}'")
                return True

        # ═══════════════════════════════════════════════════════════
        # ESTRATEGIA 2: Coincidencia exacta SIN MAYÚSCULAS
        # ═══════════════════════════════════════════════════════════
        for idx, texto in opciones_texto:
            if texto.upper() == valor_upper:
                select.select_by_visible_text(texto)
                self.log(f"  ✅ Seleccionado (sin mayúsculas): '{texto}'")
                return True

        # ═══════════════════════════════════════════════════════════
        # ESTRATEGIA 3: Valor del Excel CONTENIDO en opción
        # Ejemplo: Excel="DNI" → Opción="6 - DNI"
        # ═══════════════════════════════════════════════════════════
        for idx, texto in opciones_texto:
            if valor_upper in texto.upper():
                select.select_by_visible_text(texto)
                self.log(f"  ✅ Seleccionado (contenido): '{texto}' contiene '{valor_buscar}'")
                return True

        # ═══════════════════════════════════════════════════════════
        # ESTRATEGIA 4: Opción CONTENIDA en valor del Excel
        # Ejemplo: Excel="DOCUMENTO NACIONAL DE IDENTIDAD" → Opción="DNI"
        # ═══════════════════════════════════════════════════════════
        for idx, texto in opciones_texto:
            if texto.upper() in valor_upper:
                select.select_by_visible_text(texto)
                self.log(f"  ✅ Seleccionado (inverso): '{valor_buscar}' contiene '{texto}'")
                return True

        # ═══════════════════════════════════════════════════════════
        # ESTRATEGIA 5: Búsqueda por PALABRAS CLAVE
        # Divide el valor en palabras y busca coincidencias
        # ═══════════════════════════════════════════════════════════
        palabras_valor = [p.strip().upper() for p in valor_buscar.split() if len(p.strip()) > 2]

        if palabras_valor:
            mejor_coincidencia = None
            max_coincidencias = 0

            for idx, texto in opciones_texto:
                texto_upper = texto.upper()
                coincidencias = sum(1 for palabra in palabras_valor if palabra in texto_upper)

                if coincidencias > max_coincidencias:
                    max_coincidencias = coincidencias
                    mejor_coincidencia = (idx, texto)

            if mejor_coincidencia and max_coincidencias > 0:
                select.select_by_visible_text(mejor_coincidencia[1])
                self.log(f"  ✅ Seleccionado (palabras clave, {max_coincidencias} coincidencias): '{mejor_coincidencia[1]}'")
                return True

        # ═══════════════════════════════════════════════════════════
        # ESTRATEGIA 6: Búsqueda PARCIAL por caracteres
        # Busca si los primeros caracteres coinciden
        # ═══════════════════════════════════════════════════════════
        if len(valor_buscar) >= 3:
            prefijo = valor_upper[:3]
            for idx, texto in opciones_texto:
                if texto.upper().startswith(prefijo):
                    select.select_by_visible_text(texto)
                    self.log(f"  ✅ Seleccionado (prefijo '{prefijo}'): '{texto}'")
                    return True

        # ═══════════════════════════════════════════════════════════
        # NO ENCONTRADO: Mostrar TODAS las opciones disponibles
        # ═══════════════════════════════════════════════════════════
        self.log(f"  ❌ No se encontró coincidencia para '{valor_buscar}'")
        self.log(f"  📋 Opciones disponibles en el SELECT:")
        for idx, texto in opciones_texto[:20]:  # Mostrar máximo 20 opciones
            self.log(f"     [{idx}] {texto}")

        if len(opciones_texto) > 20:
            self.log(f"     ... y {len(opciones_texto) - 20} opciones más")

        # Seleccionar primera opción válida como fallback
        if len(opciones_texto) > 1:
            idx_fallback, texto_fallback = opciones_texto[1]  # Ignorar opción 0 (suele ser vacía)
            select.select_by_visible_text(texto_fallback)
            self.log(f"  ⚠️ Seleccionado PRIMERA opción por defecto: '{texto_fallback}'")
            return True

        return False

    def clic_boton_universal(self, nombre_boton):
        """
        🖱️ Hace clic en un botón usando múltiples métodos
        """
        self.log(f"\n  🖱️ Haciendo clic en botón '{nombre_boton}'")

        # Mapeo de nombres a textos/funciones
        mapeo_botones = {
            "buscar": {
                "textos": ["Buscar", "BUSCAR"],
                "ids": ["buscar"],
                "funciones_js": ["clickbtn_buscar()"]
            },
            "siguiente": {
                "textos": ["Siguiente", "SIGUIENTE", "Validar"],
                "ids": ["siguiente", "btnSiguiente"],
                "funciones_js": ["clickbtn_validar()"]
            },
            "registro": {
                "textos": ["Registro", "REGISTRO"],
                "ids": ["registro"],
                "funciones_js": ["clickbtn_registro()"]
            },
            "grabar": {
                "textos": ["Grabar", "GRABAR"],
                "ids": ["grabar", "btnsubmit", "btnGrabar"],
                "funciones_js": ["clickbtn_validar()"]
            }
        }

        config = mapeo_botones.get(nombre_boton.lower(), {
            "textos": [nombre_boton],
            "ids": [nombre_boton],
            "funciones_js": []
        })

        # INTENTO 1: Buscar por ID
        for id_boton in config.get("ids", []):
            try:
                elemento = self.buscar_elemento_universal(id_boton, "button")
                if elemento:
                    # Usar método robusto de clic con múltiples estrategias
                    if self.hacer_clic_robusto(elemento, f"botón '{nombre_boton}'", max_intentos=2):
                        self.log(f"  ✅ Clic exitoso (por ID)")
                        return True
            except Exception as e:
                self.log(f"  ⚠️ Intento por ID falló: {str(e)[:50]}")
                pass

        # INTENTO 2: Buscar por texto literal
        for texto in config.get("textos", []):
            try:
                elemento = self.buscar_por_texto_literal(texto, "button")
                if elemento:
                    # Usar método robusto de clic
                    if self.hacer_clic_robusto(elemento, f"botón '{texto}'", max_intentos=2):
                        self.log(f"  ✅ Clic exitoso (por texto '{texto}')")
                        return True
            except Exception as e:
                self.log(f"  ⚠️ Intento por texto '{texto}' falló: {str(e)[:50]}")
                pass

        # INTENTO 3: Ejecutar función JavaScript directamente
        for func_js in config.get("funciones_js", []):
            try:
                self.driver.execute_script(func_js)
                self.log(f"  ✅ Función JS ejecutada: {func_js}")
                return True
            except:
                pass

        # INTENTO 4: Buscar por XPath con onclick
        xpaths_onclick = [
            f"//input[@onclick='clickbtn_{nombre_boton.lower()}()']",
            f"//button[@onclick='clickbtn_{nombre_boton.lower()}()']",
            f"//input[contains(@onclick, '{nombre_boton.lower()}')]",
        ]

        for xpath in xpaths_onclick:
            try:
                self.driver.switch_to.default_content()
                # Buscar recursivamente
                def buscar_boton_recursivo(profundidad=0):
                    if profundidad > 3:
                        return None
                    try:
                        elem = self.driver.find_element(By.XPATH, xpath)
                        return elem
                    except:
                        pass

                    frames = self.driver.find_elements(By.TAG_NAME, "iframe") + \
                             self.driver.find_elements(By.TAG_NAME, "frame")
                    for frame in frames:
                        try:
                            self.driver.switch_to.frame(frame)
                            resultado = buscar_boton_recursivo(profundidad + 1)
                            if resultado:
                                return resultado
                            self.driver.switch_to.parent_frame()
                        except:
                            pass
                    return None

                elemento = buscar_boton_recursivo()
                if elemento:
                    self.driver.execute_script("arguments[0].click();", elemento)
                    self.log(f"  ✅ Clic exitoso (por onclick)")
                    return True
            except:
                pass

        self.log(f"  ❌ No se pudo hacer clic en '{nombre_boton}'")
        return False

    def _verificar_dentro_iframe(self):
        """
        Verifica si estamos dentro del iframe correcto buscando elementos del formulario.

        Returns:
            True si estamos en el iframe correcto, False en caso contrario
        """
        try:
            # Buscar el campo tipodoc
            campo = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "tipodoc"))
            )
            self.log("      ✓ Campo 'tipodoc' encontrado")
            return True
        except:
            # Intentar buscar el formulario
            try:
                form = self.driver.find_element(By.NAME, "registroden")
                self.log("      ✓ Formulario 'registroden' encontrado")
                return True
            except:
                return False

    def hacer_login(self):
        try:
            self.log("Realizando login...")
            self.driver.get(self.URL_LOGIN)
            time.sleep(2)
            
            # Usuario
            campo_usuario = self.wait.until(
                EC.presence_of_element_located((By.NAME, "cuenta"))
            )
            campo_usuario.clear()
            campo_usuario.send_keys(self.USUARIO)
            
            # Password
            campo_password = self.driver.find_element(By.NAME, "password")
            campo_password.clear()
            campo_password.send_keys(self.PASSWORD)
            
            # Click Iniciar Sesion
            boton_login = self.driver.find_element(By.XPATH, "//input[@onclick='validaIA()']")
            boton_login.click()
            
            time.sleep(3)
            self.log("✅ Login exitoso")
            return True
            
        except Exception as e:
            self.log(f"❌ Error en login: {str(e)}")
            return False
    
    def navegar_a_formulario_registro(self):
        """
        FUNCIÓN CORREGIDA - Flujo real del sistema SUNAT

        Flujo correcto:
        1. Ventana principal → Clic en "Tributarios" → Clic en "Denuncias"
        2. Se abre NUEVA VENTANA (menuS03Alias) con nivel2 "Denuncias" YA DESPLEGADO
        3. En el menú lateral de la nueva ventana:
           - Expandir nivel3 "Denuncias" (id="nivel3_5_5_2_1")
           - Clic en nivel4 "Registro de Denuncias" (id="nivel4_5_5_2_10")
        4. El formulario se carga EN LA MISMA PESTAÑA al lado derecho (iframe)

        OPTIMIZACIÓN: Si ya estamos en menuS03Alias, solo hacer clic en "Registro de Denuncias"
        """
        try:
            self.log("Navegando al formulario...")

            wait_largo = WebDriverWait(self.driver, 30)

            # ═══════════════════════════════════════════════════════════════
            # VERIFICAR SI YA ESTAMOS EN LA VENTANA CORRECTA (menuS03Alias)
            # ═══════════════════════════════════════════════════════════════
            url_actual = self.driver.current_url
            self.log(f"  → URL actual: {url_actual[:80]}...")

            if "menuS03Alias" in url_actual:
                self.log("  ✅ Ya estamos en ventana menuS03Alias - saltando navegación")
                self.log("  → Solo hacer clic en 'Registro de Denuncias'...")

                # Intentar hacer clic directo en "Registro de Denuncias"
                if self.volver_a_registro_denuncias():
                    time.sleep(3)
                    return True
                else:
                    # Si falló, continuar con el flujo normal de expansión del menú
                    self.log("  ⚠️ Clic directo falló, expandiendo menú...")

            # ═══════════════════════════════════════════════════════════════
            # FLUJO COMPLETO: Navegar desde la ventana principal
            # ═══════════════════════════════════════════════════════════════

            ventana_original = self.driver.current_window_handle
            ventanas_iniciales = len(self.driver.window_handles)

            # ═══ PASO 1: Click en "Tributarios" ═══
            self.log("  → Paso 1: Buscando 'Tributarios'...")
            try:
                time.sleep(2)
                link_tributarios = wait_largo.until(
                    EC.element_to_be_clickable((By.LINK_TEXT, "Tributarios"))
                )
                self.log("  → Haciendo clic en 'Tributarios'...")
                link_tributarios.click()
                time.sleep(2)
                self.log("  ✅ Clic en 'Tributarios' exitoso")
            except Exception as e:
                self.log(f"  ⚠️ 'Tributarios' no encontrado o no necesario: {str(e)}")

            # ═══ PASO 2: Click en "Denuncias" - ABRE NUEVA VENTANA ═══
            self.log("  → Paso 2: Buscando 'Denuncias' (abre nueva ventana)...")
            try:
                link_denuncias = wait_largo.until(
                    EC.element_to_be_clickable((By.LINK_TEXT, "Denuncias"))
                )
                self.log("  → Haciendo clic en 'Denuncias'...")
                link_denuncias.click()
                time.sleep(3)
                self.log("  ✅ Clic en 'Denuncias' - Esperando nueva ventana...")
            except Exception as e:
                self.log(f"  ❌ Error al hacer clic en 'Denuncias': {str(e)}")
                raise

            # ═══ PASO 3: Detectar y cambiar a la NUEVA VENTANA ═══
            self.log("  → Paso 3: Detectando nueva ventana menuS03Alias...")
            try:
                # Esperar hasta que se abra una nueva ventana
                wait_largo.until(lambda d: len(d.window_handles) > ventanas_iniciales)
                time.sleep(2)

                ventanas = self.driver.window_handles
                self.log(f"  → {len(ventanas)} ventanas detectadas")

                # Cambiar a la última ventana (la nueva)
                nueva_ventana = ventanas[-1]
                self.driver.switch_to.window(nueva_ventana)
                time.sleep(2)

                url_actual = self.driver.current_url
                self.log(f"  ✅ Cambiado a nueva ventana: {url_actual}")

                # Verificar que sea la ventana correcta (menuS03Alias)
                if "menuS03Alias" not in url_actual:
                    self.log(f"  ⚠️ URL no esperada: {url_actual}")
                else:
                    self.log(f"  ✅ Ventana correcta detectada (menuS03Alias)")

            except Exception as e:
                self.log(f"  ❌ Error al cambiar de ventana: {str(e)}")
                raise

            # NOTA: nivel2 "Denuncias" ya está desplegado automáticamente, no hacer clic

            # ═══ PASO 4: Expandir nivel3 "Denuncias" (GARANTIZADO CON REINTENTOS) ═══
            self.log("  → Paso 4: Expandiendo nivel3 'Denuncias' (id=nivel3_5_5_2_1)...")
            nivel3_expandido = False

            # Intentar múltiples estrategias para encontrar y hacer clic en nivel3
            for intento_nivel3 in range(1, 4):
                try:
                    self.log(f"  → Intento {intento_nivel3}/3 para expandir nivel3...")

                    # Estrategia 1: Por ID exacto
                    try:
                        nivel3_denuncias = wait_largo.until(
                            EC.presence_of_element_located((By.ID, "nivel3_5_5_2_1"))
                        )
                        self.log(f"  → Nivel3 encontrado por ID")

                        # Usar método robusto de clic
                        if self.hacer_clic_robusto(nivel3_denuncias, "nivel3 'Denuncias'"):
                            time.sleep(2)
                            nivel3_expandido = True
                            break
                    except:
                        self.log(f"  → Estrategia 1 falló (ID directo)")

                    # Estrategia 2: Por XPATH con clase y data-id
                    if not nivel3_expandido:
                        try:
                            nivel3_denuncias = wait_largo.until(
                                EC.presence_of_element_located((
                                    By.XPATH,
                                    "//li[@class='nivel3 liOpcion opcionEmpresas opcionHuerfano' and @data-id='5_5_2_1']"
                                ))
                            )
                            self.log(f"  → Nivel3 encontrado por XPATH")

                            if self.hacer_clic_robusto(nivel3_denuncias, "nivel3 'Denuncias' (XPATH)"):
                                time.sleep(2)
                                nivel3_expandido = True
                                break
                        except:
                            self.log(f"  → Estrategia 2 falló (XPATH)")

                    # Estrategia 3: Por texto "Denuncias" en nivel3
                    if not nivel3_expandido:
                        try:
                            nivel3_denuncias = wait_largo.until(
                                EC.presence_of_element_located((
                                    By.XPATH,
                                    "//li[contains(@class, 'nivel3')]//span[text()='Denuncias']"
                                ))
                            )
                            self.log(f"  → Nivel3 encontrado por texto")

                            if self.hacer_clic_robusto(nivel3_denuncias, "nivel3 'Denuncias' (texto)"):
                                time.sleep(2)
                                nivel3_expandido = True
                                break
                        except:
                            self.log(f"  → Estrategia 3 falló (texto)")

                    # Estrategia 4: Búsqueda SIN selectores - iterando sobre elementos
                    if not nivel3_expandido:
                        try:
                            self.log(f"  → Estrategia 4: Búsqueda nivel3 sin selectores...")

                            # Obtener todos los elementos <li>
                            todos_elementos = self.driver.find_elements(By.TAG_NAME, "li")

                            for elem in todos_elementos:
                                try:
                                    # Obtener las clases del elemento
                                    clases = elem.get_attribute("class") or ""
                                    texto = elem.text.strip()

                                    # Buscar elementos que sean nivel3 Y tengan texto "Denuncias"
                                    if "nivel3" in clases and "Denuncias" in texto and len(texto) < 50:
                                        self.log(f"  → Encontrado nivel3 con texto: '{texto}'")

                                        if elem.is_displayed():
                                            if self.hacer_clic_robusto(elem, "nivel3 'Denuncias' (sin selector)"):
                                                time.sleep(2)
                                                nivel3_expandido = True
                                                break
                                except:
                                    continue

                            if nivel3_expandido:
                                self.log(f"  ✅ Nivel3 encontrado sin selectores")
                                break
                            else:
                                self.log(f"  → Estrategia 4 falló")

                        except Exception as e:
                            self.log(f"  → Estrategia 4 falló: {str(e)}")

                    if intento_nivel3 < 3:
                        self.log(f"  ⚠️ Intento {intento_nivel3} falló, esperando antes de reintentar...")
                        time.sleep(3)

                except Exception as e:
                    self.log(f"  ⚠️ Error en intento {intento_nivel3}: {str(e)}")
                    if intento_nivel3 < 3:
                        time.sleep(3)

            if not nivel3_expandido:
                # DEBUG: Mostrar opciones disponibles
                self.log("  ❌ No se pudo expandir nivel3 después de todos los intentos")
                try:
                    self.log("  ℹ️ Listando opciones nivel3 disponibles:")
                    opciones = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'nivel3')]")
                    for i, opc in enumerate(opciones[:10]):
                        try:
                            id_elem = opc.get_attribute("id")
                            texto = opc.text.strip()
                            self.log(f"     {i+1}. ID={id_elem} | Texto={texto}")
                        except:
                            pass
                except:
                    pass
                raise Exception("FALLO CRÍTICO: No se pudo expandir nivel3 'Denuncias'")

            self.log("  ✅ Nivel3 'Denuncias' expandido exitosamente")

            # ═══ PASO 5: Clic en nivel4 "Registro de Denuncias" (GARANTIZADO CON REINTENTOS) ═══
            self.log("  → Paso 5: Haciendo clic en 'Registro de Denuncias' (id=nivel4_5_5_2_10)...")
            registro_clickeado = False

            # Intentar múltiples estrategias para encontrar y hacer clic en "Registro de Denuncias"
            for intento_registro in range(1, 4):
                try:
                    self.log(f"  → Intento {intento_registro}/3 para clic en 'Registro de Denuncias'...")

                    # Estrategia 1: Por ID exacto
                    try:
                        registro_denuncias = wait_largo.until(
                            EC.presence_of_element_located((By.ID, "nivel4_5_5_2_10"))
                        )
                        self.log(f"  → 'Registro de Denuncias' encontrado por ID")

                        # Usar método robusto de clic
                        if self.hacer_clic_robusto(registro_denuncias, "'Registro de Denuncias'"):
                            time.sleep(3)
                            registro_clickeado = True
                            break
                    except:
                        self.log(f"  → Estrategia 1 falló (ID directo)")

                    # Estrategia 2: Por XPATH con data-id
                    if not registro_clickeado:
                        try:
                            registro_denuncias = wait_largo.until(
                                EC.presence_of_element_located((
                                    By.XPATH,
                                    "//li[@class='nivel4 liOpcion opcionEmpresas opcionHuerfano subMenu' and @data-id='5.5.2.1.1']"
                                ))
                            )
                            self.log(f"  → 'Registro de Denuncias' encontrado por XPATH")

                            if self.hacer_clic_robusto(registro_denuncias, "'Registro de Denuncias' (XPATH)"):
                                time.sleep(3)
                                registro_clickeado = True
                                break
                        except:
                            self.log(f"  → Estrategia 2 falló (XPATH)")

                    # Estrategia 3: Por texto "Registro de Denuncias"
                    if not registro_clickeado:
                        try:
                            registro_denuncias = wait_largo.until(
                                EC.presence_of_element_located((
                                    By.XPATH,
                                    "//li[contains(@class, 'nivel4')]//span[text()='Registro de Denuncias']"
                                ))
                            )
                            self.log(f"  → 'Registro de Denuncias' encontrado por texto")

                            # Necesitamos hacer clic en el <li>, no en el <span>
                            registro_li = registro_denuncias.find_element(By.XPATH, "..")
                            if self.hacer_clic_robusto(registro_li, "'Registro de Denuncias' (texto)"):
                                time.sleep(3)
                                registro_clickeado = True
                                break
                        except:
                            self.log(f"  → Estrategia 3 falló (texto)")

                    # Estrategia 4: Buscar SIN selectores - solo por texto visible
                    if not registro_clickeado:
                        try:
                            self.log(f"  → Estrategia 4: Búsqueda avanzada sin selectores...")

                            # Obtener TODOS los elementos <li> del menú
                            todos_elementos = self.driver.find_elements(By.TAG_NAME, "li")

                            for elem in todos_elementos:
                                try:
                                    texto_elem = elem.text.strip()

                                    # Buscar el que contenga exactamente "Registro de Denuncias"
                                    if "Registro de Denuncias" in texto_elem and len(texto_elem) < 100:
                                        self.log(f"  → Encontrado elemento con texto: '{texto_elem}'")

                                        # Verificar que sea visible y clickeable
                                        if elem.is_displayed():
                                            if self.hacer_clic_robusto(elem, "'Registro de Denuncias' (búsqueda sin selector)"):
                                                time.sleep(3)
                                                registro_clickeado = True
                                                break
                                except:
                                    continue

                            if registro_clickeado:
                                self.log(f"  ✅ 'Registro de Denuncias' encontrado sin selectores")
                                break
                            else:
                                self.log(f"  → Estrategia 4 falló (búsqueda sin selector)")

                        except Exception as e:
                            self.log(f"  → Estrategia 4 falló: {str(e)}")

                    # Estrategia 5: JavaScript para buscar por texto
                    if not registro_clickeado:
                        try:
                            self.log(f"  → Estrategia 5: Búsqueda con JavaScript...")

                            # Script JavaScript que busca el elemento por texto
                            script = """
                            var elementos = document.querySelectorAll('li');
                            for (var i = 0; i < elementos.length; i++) {
                                if (elementos[i].textContent.includes('Registro de Denuncias') &&
                                    elementos[i].textContent.length < 100) {
                                    return elementos[i];
                                }
                            }
                            return null;
                            """

                            registro_elem = self.driver.execute_script(script)

                            if registro_elem:
                                self.log(f"  → 'Registro de Denuncias' encontrado con JavaScript")
                                if self.hacer_clic_robusto(registro_elem, "'Registro de Denuncias' (JavaScript)"):
                                    time.sleep(3)
                                    registro_clickeado = True
                                    break
                            else:
                                self.log(f"  → Estrategia 5 falló (JavaScript no encontró elemento)")

                        except Exception as e:
                            self.log(f"  → Estrategia 5 falló: {str(e)}")

                    if intento_registro < 3:
                        self.log(f"  ⚠️ Intento {intento_registro} falló, esperando antes de reintentar...")
                        time.sleep(3)

                except Exception as e:
                    self.log(f"  ⚠️ Error en intento {intento_registro}: {str(e)}")
                    if intento_registro < 3:
                        time.sleep(3)

            if not registro_clickeado:
                # DEBUG: Mostrar opciones disponibles
                self.log("  ❌ No se pudo hacer clic en 'Registro de Denuncias' después de todos los intentos")
                try:
                    self.log("  ℹ️ Listando opciones nivel4 disponibles:")
                    opciones = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'nivel4')]")
                    for i, opc in enumerate(opciones[:10]):
                        try:
                            id_elem = opc.get_attribute("id")
                            texto = opc.text.strip()
                            self.log(f"     {i+1}. ID={id_elem} | Texto={texto}")
                        except:
                            pass
                except:
                    pass
                raise Exception("FALLO CRÍTICO: No se pudo hacer clic en 'Registro de Denuncias'")

            self.log("  ✅ Clic en 'Registro de Denuncias' exitoso")

            # ═══ PASO OPCIONAL: PAUSA INTERACTIVA PARA DEBUGGING ═══
            # ⚠️ FUNCIÓN DESACTIVADA - Ya se implementó la corrección
            # Para ACTIVAR nuevamente si es necesario: Descomenta la siguiente línea
            # self.pausa_interactiva_y_captura()

            # ═══ PASO 6: Cambiar al iframe del formulario (ULTRA ROBUSTO) ═══
            self.log("  → Paso 6: Cambiando al iframe del formulario...")

            # Llamar al método especializado para cambiar al iframe (V2 CORREGIDA)
            if not self.cambiar_a_iframe_formulario_v2():
                raise Exception("No se pudo cargar el formulario en el iframe")

            # ✅ Navegación exitosa
            return True

        except Exception as e:
            self.log(f"❌ ERROR GENERAL EN NAVEGACIÓN: {str(e)}")
            return False
    
    # ============================================
    # SECCIÓN 1: IDENTIFICACIÓN DEL DENUNCIADO
    # ============================================
    
    def diagnosticar_iframe_y_campos(self):
        """
        DIAGNÓSTICO COMPLETO - Verifica si estamos en el iframe y qué campos hay
        """
        self.log("\n" + "=" * 80)
        self.log("🔍 DIAGNÓSTICO COMPLETO DEL IFRAME Y CAMPOS")
        self.log("=" * 80)

        # 1. Verificar contexto actual
        try:
            url = self.driver.current_url
            self.log(f"\n1️⃣ URL ACTUAL: {url}")
        except:
            self.log(f"\n1️⃣ URL ACTUAL: No se pudo obtener")

        # 2. Verificar si estamos en página principal o iframe
        try:
            # Si encontramos el menú de la izquierda, estamos en página principal
            menu = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'nivel')]")
            if len(menu) > 0:
                self.log(f"\n2️⃣ CONTEXTO: PÁGINA PRINCIPAL (se encontró menú con {len(menu)} elementos)")
                self.log("   ⚠️ PROBLEMA: Estamos fuera del iframe!")
            else:
                self.log(f"\n2️⃣ CONTEXTO: Posiblemente dentro del iframe (no hay menú visible)")
        except:
            pass

        # 3. Buscar formulario registroden
        try:
            form = self.driver.find_element(By.NAME, "registroden")
            self.log(f"\n3️⃣ FORMULARIO 'registroden': ✅ ENCONTRADO")
            self.log(f"   → Estamos DENTRO del iframe correcto")
        except:
            self.log(f"\n3️⃣ FORMULARIO 'registroden': ❌ NO ENCONTRADO")
            self.log(f"   → NO estamos en el iframe del formulario")

        # 4. Buscar select tipodoc
        try:
            select_elem = self.driver.find_element(By.NAME, "tipodoc")
            self.log(f"\n4️⃣ SELECT 'tipodoc': ✅ ENCONTRADO")

            select_obj = Select(select_elem)
            opciones = select_obj.options
            self.log(f"   → Total de opciones: {len(opciones)}")
            self.log(f"   → Opciones disponibles:")
            for i, opt in enumerate(opciones[:8]):
                val = opt.get_attribute("value")
                txt = opt.text.strip()
                self.log(f"      [{i}] value='{val}' | text='{txt}'")
        except Exception as e:
            self.log(f"\n4️⃣ SELECT 'tipodoc': ❌ NO ENCONTRADO")
            self.log(f"   Error: {str(e)}")

        # 5. Buscar input numdoc
        try:
            input_elem = self.driver.find_element(By.NAME, "numdoc")
            self.log(f"\n5️⃣ INPUT 'numdoc': ✅ ENCONTRADO")
            tipo = input_elem.get_attribute("type")
            max_len = input_elem.get_attribute("maxlength")
            self.log(f"   → type='{tipo}', maxlength='{max_len}'")
        except Exception as e:
            self.log(f"\n5️⃣ INPUT 'numdoc': ❌ NO ENCONTRADO")
            self.log(f"   Error: {str(e)}")

        # 6. Buscar botón buscar
        try:
            btn = self.driver.find_element(By.ID, "buscar")
            self.log(f"\n6️⃣ BOTÓN 'buscar': ✅ ENCONTRADO")
            visible = btn.is_displayed()
            enabled = btn.is_enabled()
            self.log(f"   → Visible: {visible}, Enabled: {enabled}")
        except Exception as e:
            self.log(f"\n6️⃣ BOTÓN 'buscar': ❌ NO ENCONTRADO")
            self.log(f"   Error: {str(e)}")

        # 7. Listar TODOS los iframes disponibles en página principal
        try:
            self.driver.switch_to.default_content()  # Volver a página principal
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            self.log(f"\n7️⃣ IFRAMES EN PÁGINA PRINCIPAL: {len(iframes)} encontrados")
            for i, ifr in enumerate(iframes):
                iframe_id = ifr.get_attribute("id") or "sin_id"
                iframe_name = ifr.get_attribute("name") or "sin_name"
                iframe_src = ifr.get_attribute("src") or "sin_src"
                visible = "VISIBLE" if ifr.is_displayed() else "OCULTO"
                self.log(f"   [{i}] ID='{iframe_id}', NAME='{iframe_name}'")
                self.log(f"        SRC='{iframe_src[:80]}'")
                self.log(f"        Estado: {visible}")
        except Exception as e:
            self.log(f"\n7️⃣ ERROR listando iframes: {str(e)}")

        self.log("\n" + "=" * 80)
        self.log("FIN DEL DIAGNÓSTICO")
        self.log("=" * 80)

    def llenar_seccion1_identificacion(self, datos):
        """
        🎯 MÉTODO DEFINITIVO - Usa los métodos UNIVERSALES de búsqueda

        Combina TODOS los enfoques:
        1. JavaScript en todos los iframes
        2. Selenium recursivo en todos los contextos
        3. Búsqueda por texto literal visible ("Tipo Documento", "Número", etc.)
        4. Métodos anteriores como fallback
        """
        try:
            self.log("="*70)
            self.log("📝 SECCIÓN 1: IDENTIFICACIÓN DEL DENUNCIADO")
            self.log("="*70)
            self.log("🔄 Usando métodos UNIVERSALES de búsqueda...")

            # ═══════════════════════════════════════
            # PASO 1: TIPO DOCUMENTO (select)
            # ═══════════════════════════════════════
            self.log("\n📋 PASO 1/4: Tipo Documento")

            if 'TIPO' not in datos or pd.isna(datos['TIPO']):
                raise Exception("Dato 'TIPO' requerido no encontrado")

            valor_tipo = str(datos['TIPO']).strip()
            self.log(f"   📥 Valor desde Excel: '{valor_tipo}'")

            # Usar método UNIVERSAL para llenar el select
            if not self.llenar_campo_universal("tipodoc", valor_tipo, "select"):
                raise Exception("No se pudo llenar campo 'tipodoc'")

            time.sleep(0.5)

            # ═══════════════════════════════════════
            # PASO 2: NÚMERO (input)
            # ═══════════════════════════════════════
            self.log("\n📋 PASO 2/4: Número")

            if 'NRO' not in datos or pd.isna(datos['NRO']):
                raise Exception("Dato 'NRO' requerido no encontrado")

            valor_numero = str(int(datos['NRO'])) if isinstance(datos['NRO'], float) else str(datos['NRO'])
            valor_numero = valor_numero.strip()
            self.log(f"   📥 Valor desde Excel: '{valor_numero}'")

            # Usar método UNIVERSAL para llenar el input
            if not self.llenar_campo_universal("numdoc", valor_numero, "input"):
                raise Exception("No se pudo llenar campo 'numdoc'")

            time.sleep(0.5)

            # ═══════════════════════════════════════
            # PASO 3: BOTÓN BUSCAR
            # ═══════════════════════════════════════
            self.log("\n📋 PASO 3/4: Botón Buscar")

            # ESTRATEGIA: Ejecutar DIRECTAMENTE la función JavaScript del botón
            # El clic normal de Selenium no dispara el evento onclick correctamente
            clic_exitoso = False

            # INTENTO 1: Ejecutar función JavaScript directamente
            try:
                self.log("   → Intento 1: Ejecutando función JavaScript clickbtn_buscar()...")
                self.driver.execute_script("clickbtn_buscar();")
                self.log("   ✅ Función JavaScript ejecutada correctamente")
                clic_exitoso = True
            except Exception as e:
                self.log(f"   ⚠️ Falló ejecución directa de JS: {str(e)[:50]}")

            # INTENTO 2: Buscar el botón y ejecutar su función onclick
            if not clic_exitoso:
                try:
                    self.log("   → Intento 2: Buscando botón y ejecutando su onclick...")
                    boton_buscar = self.driver.find_element(By.ID, "buscar")
                    onclick_func = boton_buscar.get_attribute("onclick")
                    if onclick_func:
                        self.driver.execute_script(onclick_func)
                        self.log("   ✅ Función onclick ejecutada")
                        clic_exitoso = True
                except Exception as e:
                    self.log(f"   ⚠️ Falló ejecución onclick: {str(e)[:50]}")

            # INTENTO 3: Clic con JavaScript en el elemento
            if not clic_exitoso:
                try:
                    self.log("   → Intento 3: Clic JavaScript en elemento...")
                    boton_buscar = self.driver.find_element(By.ID, "buscar")
                    self.driver.execute_script("arguments[0].click();", boton_buscar)
                    self.log("   ✅ Clic JavaScript ejecutado")
                    clic_exitoso = True
                except Exception as e:
                    self.log(f"   ⚠️ Falló clic JS: {str(e)[:50]}")

            # INTENTO 4: MODO NUCLEAR como último recurso
            if not clic_exitoso:
                try:
                    self.log("   → Intento 4: MODO NUCLEAR...")
                    if self.clic_boton_con_javascript("buscar"):
                        clic_exitoso = True
                except:
                    pass

            if not clic_exitoso:
                raise Exception("No se pudo hacer clic en botón Buscar después de 4 intentos")

            # ESPERAR hasta que se carguen los datos automáticamente
            self.log("   ⏳ Esperando a que se carguen los datos del denunciado...")

            try:
                # Esperar hasta que el campo de "Apellidos y Nombres" tenga contenido
                # Este campo se llena automáticamente después de hacer clic en Buscar
                wait_busqueda = WebDriverWait(self.driver, 10)

                # Buscar el campo que contiene los apellidos/nombres (puede tener diferentes nombres)
                campos_posibles = ["razonsocial", "nombre", "apellidos", "razon"]
                campo_encontrado = False

                for nombre_campo in campos_posibles:
                    try:
                        # Esperar a que el campo exista Y tenga contenido
                        def campo_tiene_contenido(driver):
                            try:
                                campos = driver.find_elements(By.XPATH,
                                    f"//input[contains(@name, '{nombre_campo}') or contains(@id, '{nombre_campo}')]")
                                for campo in campos:
                                    valor = campo.get_attribute("value")
                                    if valor and len(valor.strip()) > 2:
                                        return True
                                return False
                            except:
                                return False

                        if wait_busqueda.until(campo_tiene_contenido):
                            self.log(f"   ✅ Datos cargados correctamente (campo '{nombre_campo}' tiene contenido)")
                            campo_encontrado = True
                            break
                    except:
                        continue

                if not campo_encontrado:
                    # Fallback: esperar que el select de Departamento tenga opciones
                    try:
                        def departamento_cargado(driver):
                            try:
                                dept = driver.find_element(By.NAME, "departamento")
                                if dept.tag_name.lower() == "select":
                                    select_dept = Select(dept)
                                    return len(select_dept.options) > 1
                                return False
                            except:
                                return False

                        if wait_busqueda.until(departamento_cargado):
                            self.log("   ✅ Datos cargados correctamente (departamento tiene opciones)")
                            campo_encontrado = True
                    except:
                        pass

                if not campo_encontrado:
                    self.log("   ⚠️ No se pudo verificar la carga de datos, esperando 5 segundos adicionales...")
                    time.sleep(5)
                else:
                    # Pequeña espera adicional para asegurar que todo esté cargado
                    time.sleep(1)

            except Exception as e:
                self.log(f"   ⚠️ Error esperando carga: {str(e)}, continuando...")
                time.sleep(3)

            # ═══════════════════════════════════════
            # PASO 4: BOTÓN SIGUIENTE
            # ═══════════════════════════════════════
            self.log("\n📋 PASO 4/4: Botón Siguiente")

            # ESTRATEGIA: Ejecutar DIRECTAMENTE la función JavaScript del botón
            clic_siguiente_exitoso = False

            # INTENTO 1: Ejecutar función JavaScript directamente
            try:
                self.log("   → Intento 1: Ejecutando función JavaScript clickbtn_validar()...")
                self.driver.execute_script("clickbtn_validar();")
                self.log("   ✅ Función JavaScript ejecutada correctamente")
                clic_siguiente_exitoso = True
            except Exception as e:
                self.log(f"   ⚠️ Falló ejecución directa de JS: {str(e)[:50]}")

            # INTENTO 2: Buscar el botón y ejecutar su función onclick
            if not clic_siguiente_exitoso:
                try:
                    self.log("   → Intento 2: Buscando botón 'siguiente' y ejecutando onclick...")
                    boton_siguiente = self.driver.find_element(By.ID, "siguiente")
                    onclick_func = boton_siguiente.get_attribute("onclick")
                    if onclick_func:
                        self.driver.execute_script(onclick_func)
                        self.log("   ✅ Función onclick ejecutada")
                        clic_siguiente_exitoso = True
                except Exception as e:
                    self.log(f"   ⚠️ Falló ejecución onclick: {str(e)[:50]}")

            # INTENTO 3: MODO NUCLEAR
            if not clic_siguiente_exitoso:
                try:
                    self.log("   → Intento 3: MODO NUCLEAR...")
                    if self.clic_boton_con_javascript("siguiente"):
                        clic_siguiente_exitoso = True
                except:
                    pass

            if not clic_siguiente_exitoso:
                raise Exception("No se pudo hacer clic en botón Siguiente después de 3 intentos")

            time.sleep(2)

            self.log("\n" + "="*70)
            self.log("✅✅✅ SECCIÓN 1 COMPLETADA ✅✅✅")
            self.log("="*70)
            return True

        except Exception as e:
            self.log(f"\n❌ ERROR EN SECCIÓN 1: {str(e)}")
            return False

    def _debug_formulario_seccion1(self):
        """Debug exhaustivo del formulario de Sección 1"""
        try:
            self.log("\n🔍 DEBUG - Estado actual del formulario:")
            self.log("-" * 70)

            # Verificar contexto
            try:
                current_url = self.driver.current_url
                self.log(f"   URL actual: {current_url}")
            except:
                self.log("   ⚠️ No se pudo obtener URL")

            # Listar todos los selects
            try:
                selects = self.driver.find_elements(By.TAG_NAME, "select")
                self.log(f"\n   📋 Total de SELECTs encontrados: {len(selects)}")
                for i, sel in enumerate(selects[:5]):
                    name = sel.get_attribute("name") or "sin_name"
                    self.log(f"      [{i}] name='{name}'")

                    if name == "tipodoc":
                        select_obj = Select(sel)
                        self.log(f"         Opciones:")
                        for opt in select_obj.options[:8]:
                            self.log(f"           - value='{opt.get_attribute('value')}' text='{opt.text.strip()}'")
            except Exception as e:
                self.log(f"   ⚠️ Error listando selects: {str(e)}")

            # Listar todos los inputs
            try:
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                self.log(f"\n   📋 Total de INPUTs encontrados: {len(inputs)}")
                for i, inp in enumerate(inputs[:10]):
                    name = inp.get_attribute("name") or "sin_name"
                    tipo = inp.get_attribute("type") or "sin_tipo"
                    value = inp.get_attribute("value") or ""
                    self.log(f"      [{i}] name='{name}', type='{tipo}', value='{value[:30]}'")
            except Exception as e:
                self.log(f"   ⚠️ Error listando inputs: {str(e)}")

            self.log("-" * 70)
        except Exception as e:
            self.log(f"⚠️ Error en debug: {str(e)}")
    
    # ============================================
    # SECCIÓN 2: ATENCIÓN DE DENUNCIAS
    # ============================================

    def buscar_y_rellenar_con_javascript(self, nombre_campo, valor, tipo="select"):
        """
        🚨🚨🚨 MODO NUCLEAR - USA JAVASCRIPT DIRECTO 🚨🚨🚨

        Busca y rellena un campo usando JavaScript puro, sin importar
        en qué iframe/frame esté. Busca recursivamente hasta nivel 10.

        Args:
            nombre_campo: nombre del campo (name attribute)
            valor: valor a rellenar
            tipo: "select", "input", "textarea", "radio"

        Returns:
            True si se rellenó exitosamente, False si no
        """
        self.log(f"🚨 MODO NUCLEAR: Rellenando '{nombre_campo}' = '{valor[:50] if len(str(valor)) > 50 else valor}'")

        # JavaScript que busca recursivamente en TODOS los frames hasta nivel 10
        js_code = f"""
        function buscarYRellenarRecursivo(ventana, nivelActual, nivelMaximo) {{
            if (nivelActual > nivelMaximo) return false;

            try {{
                // Buscar en la ventana actual
                var elementos = ventana.document.getElementsByName('{nombre_campo}');
                if (elementos.length > 0) {{
                    var elemento = elementos[0];

                    // Rellenar según el tipo
                    if ('{tipo}' === 'select') {{
                        // Para SELECT: buscar la mejor opción con múltiples estrategias
                        var opciones = elemento.options;
                        var valorBuscado = '{valor}'.toUpperCase().trim();
                        var mejorCoincidencia = {{ indice: -1, longitud: 0 }};

                        // Estrategia 1: Coincidencia EXACTA (prioridad máxima)
                        for (var i = 0; i < opciones.length; i++) {{
                            var textoOpcion = opciones[i].text.toUpperCase().trim();
                            if (textoOpcion === valorBuscado) {{
                                mejorCoincidencia = {{ indice: i, longitud: textoOpcion.length }};
                                break;
                            }}
                        }}

                        // Estrategia 2: La opción COMIENZA con el valor buscado (para texto truncado)
                        if (mejorCoincidencia.indice === -1) {{
                            for (var i = 0; i < opciones.length; i++) {{
                                var textoOpcion = opciones[i].text.toUpperCase().trim();
                                if (textoOpcion.indexOf(valorBuscado) === 0) {{
                                    // Seleccionar la opción MÁS LARGA que coincida
                                    if (textoOpcion.length > mejorCoincidencia.longitud) {{
                                        mejorCoincidencia = {{ indice: i, longitud: textoOpcion.length }};
                                    }}
                                }}
                            }}
                        }}

                        // Estrategia 3: El valor buscado COMIENZA con la opción (coincidencia parcial)
                        if (mejorCoincidencia.indice === -1) {{
                            for (var i = 0; i < opciones.length; i++) {{
                                var textoOpcion = opciones[i].text.toUpperCase().trim();
                                if (valorBuscado.indexOf(textoOpcion) === 0) {{
                                    // Seleccionar la opción MÁS LARGA que coincida
                                    if (textoOpcion.length > mejorCoincidencia.longitud) {{
                                        mejorCoincidencia = {{ indice: i, longitud: textoOpcion.length }};
                                    }}
                                }}
                            }}
                        }}

                        // Estrategia 4: Contiene el valor (último recurso)
                        if (mejorCoincidencia.indice === -1) {{
                            for (var i = 0; i < opciones.length; i++) {{
                                var textoOpcion = opciones[i].text.toUpperCase().trim();
                                if (textoOpcion.indexOf(valorBuscado) !== -1) {{
                                    // Seleccionar la opción MÁS LARGA que coincida
                                    if (textoOpcion.length > mejorCoincidencia.longitud) {{
                                        mejorCoincidencia = {{ indice: i, longitud: textoOpcion.length }};
                                    }}
                                }}
                            }}
                        }}

                        // Seleccionar la mejor coincidencia encontrada
                        if (mejorCoincidencia.indice !== -1) {{
                            // PASO 1: Dar foco al elemento (importante para formularios antiguos)
                            try {{
                                elemento.focus();
                            }} catch(e) {{}}

                            // PASO 2: Seleccionar el valor
                            elemento.selectedIndex = mejorCoincidencia.indice;
                            elemento.value = opciones[mejorCoincidencia.indice].value;

                            // PASO 3: Disparar TODOS los eventos necesarios en el orden correcto
                            // Eventos modernos (addEventListener)
                            try {{
                                elemento.dispatchEvent(new Event('input', {{ bubbles: true, cancelable: true }}));
                                elemento.dispatchEvent(new Event('change', {{ bubbles: true, cancelable: true }}));
                                elemento.dispatchEvent(new Event('blur', {{ bubbles: true, cancelable: true }}));
                            }} catch(e) {{}}

                            // PASO 4: Ejecutar handlers antiguos (on* properties)
                            try {{
                                if (elemento.oninput) elemento.oninput();
                            }} catch(e) {{}}
                            try {{
                                if (elemento.onchange) elemento.onchange();
                            }} catch(e) {{}}
                            try {{
                                if (elemento.onblur) elemento.onblur();
                            }} catch(e) {{}}

                            // PASO 5: Intentar fireEvent para IE/navegadores antiguos
                            try {{
                                if (elemento.fireEvent) {{
                                    elemento.fireEvent('onchange');
                                }}
                            }} catch(e) {{}}

                            // PASO 6: Marcar el elemento como modificado (flag común en formularios)
                            try {{
                                elemento.setAttribute('data-changed', 'true');
                            }} catch(e) {{}}

                            return true;
                        }}

                        // No se encontró ninguna coincidencia
                        return false;
                    }} else if ('{tipo}' === 'textarea' || '{tipo}' === 'input') {{
                        elemento.value = '{valor}';
                        elemento.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        elemento.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        elemento.dispatchEvent(new Event('blur', {{ bubbles: true }}));

                        if (elemento.onblur) elemento.onblur();
                        if (elemento.onchange) elemento.onchange();

                        return true;
                    }} else if ('{tipo}' === 'radio') {{
                        elemento.checked = true;
                        elemento.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        elemento.dispatchEvent(new Event('click', {{ bubbles: true }}));

                        if (elemento.onclick) elemento.onclick();

                        return true;
                    }}
                }}

                // Buscar en todos los iframes/frames de esta ventana
                var frames = ventana.frames;
                for (var i = 0; i < frames.length; i++) {{
                    try {{
                        if (buscarYRellenarRecursivo(frames[i], nivelActual + 1, nivelMaximo)) {{
                            return true;
                        }}
                    }} catch (e) {{
                        // Acceso denegado al frame, continuar
                    }}
                }}

                return false;
            }} catch (e) {{
                return false;
            }}
        }}

        // Iniciar búsqueda desde window.top (nivel más alto)
        return buscarYRellenarRecursivo(window.top, 0, 10);
        """

        try:
            # Ejecutar el JavaScript
            resultado = self.driver.execute_script(js_code)

            if resultado:
                self.log(f"  ✅ Campo '{nombre_campo}' rellenado con éxito usando JavaScript")

                # Verificar qué valor se seleccionó (solo para SELECT)
                if tipo == "select":
                    try:
                        verificacion = self.driver.execute_script(f"""
                            function obtenerValorSeleccionado(ventana, nivel) {{
                                if (nivel > 10) return null;
                                try {{
                                    var elementos = ventana.document.getElementsByName('{nombre_campo}');
                                    if (elementos.length > 0) {{
                                        var elemento = elementos[0];
                                        var opcionSeleccionada = elemento.options[elemento.selectedIndex];
                                        return {{
                                            texto: opcionSeleccionada ? opcionSeleccionada.text : null,
                                            valor: elemento.value,
                                            indice: elemento.selectedIndex
                                        }};
                                    }}
                                    for (var i = 0; i < ventana.frames.length; i++) {{
                                        var resultado = obtenerValorSeleccionado(ventana.frames[i], nivel + 1);
                                        if (resultado) return resultado;
                                    }}
                                }} catch(e) {{}}
                                return null;
                            }}
                            return obtenerValorSeleccionado(window.top, 0);
                        """)
                        if verificacion:
                            self.log(f"     → Opción seleccionada: '{verificacion['texto']}'")
                            self.log(f"     → Valor: '{verificacion['valor']}', Índice: {verificacion['indice']}")

                            # Verificar que NO esté en índice 0 (opción vacía/por defecto)
                            if verificacion['indice'] == 0:
                                self.log(f"     ⚠️ ADVERTENCIA: Índice 0 puede ser opción vacía")
                        else:
                            self.log(f"     ⚠️ No se pudo verificar el valor seleccionado")
                    except Exception as e:
                        self.log(f"     ⚠️ Error en verificación: {str(e)[:50]}")

                return True
            else:
                self.log(f"  ⚠️ No se encontró el campo '{nombre_campo}' en ningún frame")

                # Debug: Listar todas las opciones disponibles (solo para SELECT)
                if tipo == "select":
                    try:
                        opciones = self.driver.execute_script(f"""
                            function obtenerOpciones(ventana, nivel) {{
                                if (nivel > 10) return null;
                                try {{
                                    var elementos = ventana.document.getElementsByName('{nombre_campo}');
                                    if (elementos.length > 0) {{
                                        var elemento = elementos[0];
                                        var lista = [];
                                        for (var i = 0; i < elemento.options.length; i++) {{
                                            lista.push(elemento.options[i].text);
                                        }}
                                        return lista;
                                    }}
                                    for (var i = 0; i < ventana.frames.length; i++) {{
                                        var resultado = obtenerOpciones(ventana.frames[i], nivel + 1);
                                        if (resultado) return resultado;
                                    }}
                                }} catch(e) {{}}
                                return null;
                            }}
                            return obtenerOpciones(window.top, 0);
                        """)
                        if opciones and len(opciones) > 0:
                            self.log(f"     → Campo encontrado con {len(opciones)} opciones:")
                            for i, opcion in enumerate(opciones[:10]):  # Mostrar solo las primeras 10
                                self.log(f"        {i+1}. {opcion[:80]}")
                            if len(opciones) > 10:
                                self.log(f"        ... y {len(opciones)-10} más")
                    except:
                        pass

                return False

        except Exception as e:
            self.log(f"  ❌ Error ejecutando JavaScript: {str(e)[:100]}")
            return False

    def clic_boton_con_javascript(self, nombre_boton):
        """
        🚨🚨🚨 MODO NUCLEAR PARA BOTONES - USA JAVASCRIPT DIRECTO 🚨🚨🚨

        Hace clic en un botón usando JavaScript puro, buscando recursivamente
        en TODOS los frames hasta nivel 10.

        Args:
            nombre_boton: tipo de botón ("siguiente", "grabar")

        Returns:
            True si se hizo clic exitosamente, False si no
        """
        self.log(f"🚨 MODO NUCLEAR BOTÓN: Buscando y haciendo clic en '{nombre_boton}'")

        # Mapeo de nombres de botón a sus características
        config_botones = {
            "siguiente": {
                "onclick": "clickbtn_validar",
                "value": "Siguiente",
                "name": "btnsubmit"
            },
            "grabar": {
                "onclick": "clickbtn_validar",
                "value": "Grabar",
                "name": "btnsubmit"
            },
            "buscar": {
                "onclick": "clickbtn_buscar",
                "value": "Buscar",
                "name": "buscar"
            },
            "aceptar": {
                "onclick": "clickbtn_ejecutar",
                "value": "Aceptar",
                "name": "btnsubmit"
            }
        }

        config = config_botones.get(nombre_boton.lower(), {
            "onclick": f"clickbtn_{nombre_boton}",
            "value": nombre_boton.capitalize(),
            "name": "btnsubmit"
        })

        # JavaScript que busca y hace clic recursivamente en TODOS los frames
        js_code = f"""
        function buscarYClickBoton(ventana, nivelActual, nivelMaximo) {{
            if (nivelActual > nivelMaximo) return false;

            try {{
                // ESTRATEGIA 1: Ejecutar función onclick directamente
                if (typeof ventana.{config['onclick']} === 'function') {{
                    ventana.{config['onclick']}();
                    return true;
                }}

                // ESTRATEGIA 2: Buscar por onclick attribute
                var botones = ventana.document.querySelectorAll("input[onclick*='{config['onclick']}']");
                if (botones.length > 0) {{
                    botones[0].click();
                    return true;
                }}

                // ESTRATEGIA 3: Buscar por name
                botones = ventana.document.querySelectorAll("input[name='{config['name']}']");
                if (botones.length > 0) {{
                    botones[0].click();
                    return true;
                }}

                // ESTRATEGIA 4: Buscar por value
                botones = ventana.document.querySelectorAll("input[value*='{config['value']}']");
                if (botones.length > 0) {{
                    botones[0].click();
                    return true;
                }}

                // ESTRATEGIA 5: Buscar por type=button
                botones = ventana.document.querySelectorAll("input[type='button']");
                for (var i = 0; i < botones.length; i++) {{
                    var valor = botones[i].value || botones[i].textContent || '';
                    if (valor.toUpperCase().indexOf('{config['value']}'.toUpperCase()) !== -1) {{
                        botones[i].click();
                        return true;
                    }}
                }}

                // Buscar recursivamente en todos los frames
                var frames = ventana.frames;
                for (var i = 0; i < frames.length; i++) {{
                    try {{
                        if (buscarYClickBoton(frames[i], nivelActual + 1, nivelMaximo)) {{
                            return true;
                        }}
                    }} catch (e) {{
                        // Acceso denegado al frame, continuar
                    }}
                }}

                return false;
            }} catch (e) {{
                return false;
            }}
        }}

        // Iniciar búsqueda desde window.top
        return buscarYClickBoton(window.top, 0, 10);
        """

        try:
            resultado = self.driver.execute_script(js_code)

            if resultado:
                self.log(f"  ✅ Botón '{nombre_boton}' clickeado con éxito usando JavaScript")
                return True
            else:
                self.log(f"  ⚠️ No se encontró el botón '{nombre_boton}' en ningún frame")
                return False

        except Exception as e:
            self.log(f"  ❌ Error ejecutando JavaScript: {str(e)[:100]}")
            return False

    def llenar_seccion2_atencion_denuncias(self, datos):
        try:
            self.log("📝 Llenando Sección 2: ATENCIÓN DE DENUNCIAS...")
            self.log("🚨🚨🚨 USANDO MODO NUCLEAR - JavaScript directo 🚨🚨🚨")

            # Esperar 5 segundos para que la página cargue completamente
            self.log("  ⏳ Esperando 5 segundos para carga completa...")
            time.sleep(5)

            # ═══════════════════════════════════════════════════════════════
            # MODO NUCLEAR: Rellenar TODO con JavaScript directo
            # ACCESO POR ÍNDICE DE COLUMNA (no por nombre de encabezado)
            # ═══════════════════════════════════════════════════════════════

            # 1. Modalidad Evasión (Columna C = índice 2)
            valor_modalidad_seleccionado = None  # Para determinar selector de submodalidad
            if len(datos) > 2 and pd.notna(datos.iloc[2]):
                valor = str(datos.iloc[2]).strip()
                if valor != "" and valor != "-":
                    self.log(f"\n📋 CAMPO 1: Modalidad Evasión = '{valor}'")
                    if not self.buscar_y_rellenar_con_javascript("modalidad", valor, "select"):
                        raise Exception(f"No se pudo seleccionar la Modalidad: '{valor}'")
                    time.sleep(2)

                    # OBTENER EL VALOR DE MODALIDAD SELECCIONADO (03000, 04000, etc.)
                    js_obtener_valor = """
                    function obtenerValorModalidad(ventana) {
                        try {
                            var selects = ventana.document.getElementsByName('modalidad');
                            if (selects.length > 0) {
                                return selects[0].value;
                            }
                            for (var i = 0; i < ventana.frames.length; i++) {
                                var resultado = obtenerValorModalidad(ventana.frames[i]);
                                if (resultado) return resultado;
                            }
                        } catch(e) {}
                        return null;
                    }
                    return obtenerValorModalidad(window.top);
                    """
                    try:
                        valor_modalidad_seleccionado = self.driver.execute_script(js_obtener_valor)
                        self.log(f"  → Valor de modalidad seleccionado: {valor_modalidad_seleccionado}")
                    except Exception as e:
                        self.log(f"  ⚠️ No se pudo obtener valor de modalidad: {str(e)[:50]}")

            # 2. Sub Modalidad (Columna D = índice 3) - OPCIONAL
            # 🚨🚨🚨 MODO NUCLEAR COMPLETO - MISMO PATRÓN QUE LOS DEMÁS CAMPOS 🚨🚨🚨
            if len(datos) > 3 and pd.notna(datos.iloc[3]):
                valor_sub = str(datos.iloc[3]).strip()
                if valor_sub != "" and valor_sub != "-":
                    self.log(f"\n📋 CAMPO 2: Sub Modalidad = '{valor_sub}'")

                    # Obtener el selector correcto según la modalidad
                    nombre_selector_sub = self.obtener_selector_submodalidad(valor_modalidad_seleccionado)

                    if nombre_selector_sub:
                        self.log(f"  → Usando selector: '{nombre_selector_sub}'")

                        # 🚨 MÉTODO NUCLEAR COMPLETO - JavaScript recursivo con todas las estrategias
                        js_submodalidad_nuclear = f"""
                        (function() {{
                            function buscarYRellenarSubmodalidad(ventana, nivel) {{
                                if (nivel > 10) return false;

                                try {{
                                    // Buscar el select por nombre
                                    var selects = ventana.document.getElementsByName('{nombre_selector_sub}');

                                    if (selects.length > 0) {{
                                        var select = selects[0];

                                        // PASO 1: Hacer visible el TR padre (está oculto por defecto)
                                        var tr = select.closest('tr');
                                        if (tr) {{
                                            tr.style.display = '';
                                            tr.style.visibility = 'visible';
                                            tr.removeAttribute('hidden');
                                        }}

                                        // PASO 2: Hacer visible el select
                                        select.style.display = '';
                                        select.style.visibility = 'visible';
                                        select.disabled = false;

                                        // PASO 3: Buscar la mejor opción con múltiples estrategias
                                        var opciones = select.options;
                                        var valorBuscado = '{valor_sub}'.toUpperCase().trim();
                                        var mejorIndice = -1;

                                        // Estrategia 1: Coincidencia EXACTA
                                        for (var i = 0; i < opciones.length; i++) {{
                                            var textoOpcion = (opciones[i].text || '').toUpperCase().trim();
                                            if (textoOpcion === valorBuscado) {{
                                                mejorIndice = i;
                                                break;
                                            }}
                                        }}

                                        // Estrategia 2: La opción COMIENZA con el valor
                                        if (mejorIndice === -1) {{
                                            for (var i = 0; i < opciones.length; i++) {{
                                                var textoOpcion = (opciones[i].text || '').toUpperCase().trim();
                                                if (textoOpcion.indexOf(valorBuscado) === 0) {{
                                                    mejorIndice = i;
                                                    break;
                                                }}
                                            }}
                                        }}

                                        // Estrategia 3: El valor COMIENZA con la opción
                                        if (mejorIndice === -1) {{
                                            for (var i = 0; i < opciones.length; i++) {{
                                                var textoOpcion = (opciones[i].text || '').toUpperCase().trim();
                                                if (valorBuscado.indexOf(textoOpcion) === 0 && textoOpcion.length > 3) {{
                                                    mejorIndice = i;
                                                    break;
                                                }}
                                            }}
                                        }}

                                        // Estrategia 4: CONTIENE el valor
                                        if (mejorIndice === -1) {{
                                            for (var i = 0; i < opciones.length; i++) {{
                                                var textoOpcion = (opciones[i].text || '').toUpperCase().trim();
                                                if (textoOpcion.indexOf(valorBuscado) !== -1) {{
                                                    mejorIndice = i;
                                                    break;
                                                }}
                                            }}
                                        }}

                                        // Estrategia 5: El valor CONTIENE la opción
                                        if (mejorIndice === -1) {{
                                            for (var i = 0; i < opciones.length; i++) {{
                                                var textoOpcion = (opciones[i].text || '').toUpperCase().trim();
                                                if (valorBuscado.indexOf(textoOpcion) !== -1 && textoOpcion.length > 3) {{
                                                    mejorIndice = i;
                                                    break;
                                                }}
                                            }}
                                        }}

                                        if (mejorIndice !== -1) {{
                                            // PASO 4: Dar foco y seleccionar
                                            try {{ select.focus(); }} catch(e) {{}}

                                            select.selectedIndex = mejorIndice;
                                            select.value = opciones[mejorIndice].value;

                                            // PASO 5: Disparar TODOS los eventos
                                            try {{
                                                select.dispatchEvent(new Event('input', {{bubbles: true}}));
                                                select.dispatchEvent(new Event('change', {{bubbles: true}}));
                                                select.dispatchEvent(new Event('blur', {{bubbles: true}}));
                                            }} catch(e) {{}}

                                            // Eventos legacy
                                            try {{
                                                if (select.onchange) select.onchange();
                                                if (select.oninput) select.oninput();
                                            }} catch(e) {{}}

                                            return true;
                                        }}
                                    }}

                                    // Buscar en frames hijos
                                    for (var i = 0; i < ventana.frames.length; i++) {{
                                        try {{
                                            if (buscarYRellenarSubmodalidad(ventana.frames[i], nivel + 1)) {{
                                                return true;
                                            }}
                                        }} catch(e) {{}}
                                    }}
                                }} catch(e) {{}}
                                return false;
                            }}

                            return buscarYRellenarSubmodalidad(window.top, 0);
                        }})();
                        """

                        try:
                            resultado = self.driver.execute_script(js_submodalidad_nuclear)
                            if resultado:
                                self.log(f"  ✅ Sub Modalidad seleccionada correctamente (NUCLEAR)")
                            else:
                                # Fallback: usar método estándar
                                self.log(f"  ⚠️ Método nuclear falló, intentando método estándar...")
                                if self.buscar_y_rellenar_con_javascript(nombre_selector_sub, valor_sub, "select"):
                                    self.log(f"  ✅ Sub Modalidad seleccionada (fallback)")
                                else:
                                    self.log(f"  ⚠️ No se pudo seleccionar Sub Modalidad")
                        except Exception as e:
                            self.log(f"  ⚠️ Error en Sub Modalidad: {str(e)[:50]}")
                    else:
                        self.log(f"  ⚠️ No hay selector de submodalidad para modalidad: {valor_modalidad_seleccionado}")

                    time.sleep(1)

            # 3. Tipo de Denuncia (Columna E = índice 4 - Radio button)
            if len(datos) > 4 and pd.notna(datos.iloc[4]):
                valor_tipo = str(datos.iloc[4]).strip()
                if valor_tipo != "" and valor_tipo != "-":
                    self.log(f"\n📋 CAMPO 3: Tipo de Denuncia = '{valor_tipo}'")

                    mapeo_tipo = {
                        "telefónica": "1", "telefonica": "1",
                        "verbal": "2",
                        "escrita": "3",
                        "formato electrónico": "4", "formato electronico": "4", "electronico": "4"
                    }
                    valor_radio = mapeo_tipo.get(valor_tipo.lower(), "3")

                    js_radio = f"""
                    function buscarEnFrames(win) {{
                        try {{
                            var radios = win.document.querySelectorAll("input[name='rdoTipo'][value='{valor_radio}']");
                            if (radios.length > 0) {{
                                radios[0].checked = true;
                                if (radios[0].onclick) radios[0].onclick();
                                return true;
                            }}
                            for (var i = 0; i < win.frames.length; i++) {{
                                if (buscarEnFrames(win.frames[i])) return true;
                            }}
                        }} catch(e) {{}}
                        return false;
                    }}
                    return buscarEnFrames(window.top);
                    """

                    try:
                        resultado = self.driver.execute_script(js_radio)
                        if resultado:
                            self.log(f"  ✅ Radio button seleccionado")
                        else:
                            self.log(f"  ⚠️ No se pudo seleccionar")
                    except Exception as e:
                        self.log(f"  ⚠️ Error: {str(e)[:80]}")

                    time.sleep(1)

            # 4. Fecha SID (Columna F = índice 5 - OBLIGATORIO)
            if len(datos) > 5 and pd.notna(datos.iloc[5]):
                valor_raw = datos.iloc[5]
                if str(valor_raw).strip() != "" and str(valor_raw).strip() != "-":
                    fecha_formateada = self.convertir_fecha_excel(valor_raw)
                    if fecha_formateada:
                        self.log(f"\n📋 CAMPO 4: Fecha SID = '{fecha_formateada}'")
                        if not self.buscar_y_rellenar_con_javascript("fecha_sid", fecha_formateada, "input"):
                            self.log(f"  ⚠️ No se pudo llenar Fecha SID")
                        time.sleep(1)

            # 5. Detalle de la Denuncia (Columna G = índice 6 - TEXTAREA)
            if len(datos) > 6 and pd.notna(datos.iloc[6]):
                valor_detalle = str(datos.iloc[6]).strip()
                if valor_detalle != "" and valor_detalle != "-":
                    self.log(f"\n📋 CAMPO 5: Detalle de la Denuncia")
                    self.log(f"  → Texto: {valor_detalle[:100]}...")
                    self.buscar_y_rellenar_con_javascript("detalle", valor_detalle, "textarea")
                    time.sleep(1)

            # 6-7. Del Mes/Año (Columna H = índice 7 - extraer mes y año)
            if len(datos) > 7 and pd.notna(datos.iloc[7]):
                valor_raw = str(datos.iloc[7]).strip()
                if valor_raw != "" and valor_raw != "-":
                    fecha_desde = self.extraer_mes_anio(datos.iloc[7])
                    if fecha_desde:
                        self.log(f"\n📋 CAMPO 6-7: Del Mes/Año = {fecha_desde['mes']}/{fecha_desde['anio']}")
                        self.buscar_y_rellenar_con_javascript("MesDesde", fecha_desde['mes'], "select")
                        time.sleep(0.5)
                        self.buscar_y_rellenar_con_javascript("AnioDesde", str(fecha_desde['anio']), "select")
                        time.sleep(0.5)

            # 8-9. Al Mes/Año (Columna I = índice 8 - extraer mes y año)
            if len(datos) > 8 and pd.notna(datos.iloc[8]):
                valor_raw = str(datos.iloc[8]).strip()
                if valor_raw != "" and valor_raw != "-":
                    fecha_hasta = self.extraer_mes_anio(datos.iloc[8])
                    if fecha_hasta:
                        self.log(f"\n📋 CAMPO 8-9: Al Mes/Año = {fecha_hasta['mes']}/{fecha_hasta['anio']}")
                        self.buscar_y_rellenar_con_javascript("MesHasta", fecha_hasta['mes'], "select")
                        time.sleep(0.5)
                        self.buscar_y_rellenar_con_javascript("AnioHasta", str(fecha_hasta['anio']), "select")
                        time.sleep(0.5)

            # 10. Pruebas Ofrecidas (Columna J = índice 9 - SI/NO con lógica condicional)
            if len(datos) > 9 and pd.notna(datos.iloc[9]):
                valor_prueba = str(datos.iloc[9]).strip().upper()
                self.log(f"\n📋 CAMPO 10: Pruebas Ofrecidas = '{valor_prueba}'")

                if valor_prueba in ["NO", "N"]:
                    # Marcar NO
                    js_pruebas_no = """
                    function buscarEnFrames(win) {
                        try {
                            var radios = win.document.querySelectorAll("input[name='tipoPru'][value='N']");
                            if (radios.length > 0) {
                                radios[0].checked = true;
                                if (radios[0].onclick) radios[0].onclick();
                                return true;
                            }
                            for (var i = 0; i < win.frames.length; i++) {
                                if (buscarEnFrames(win.frames[i])) return true;
                            }
                        } catch(e) {}
                        return false;
                    }
                    return buscarEnFrames(window.top);
                    """
                    try:
                        self.driver.execute_script(js_pruebas_no)
                        self.log("  ✅ Pruebas = NO seleccionado")
                    except:
                        pass

                elif valor_prueba in ["SI", "SÍ", "S", "YES"]:
                    # Marcar SI
                    js_pruebas_si = """
                    function buscarEnFrames(win) {
                        try {
                            var radios = win.document.querySelectorAll("input[name='tipoPru'][value='S']");
                            if (radios.length > 0) {
                                radios[0].checked = true;
                                if (radios[0].onclick) radios[0].onclick();
                                return true;
                            }
                            for (var i = 0; i < win.frames.length; i++) {
                                if (buscarEnFrames(win.frames[i])) return true;
                            }
                        } catch(e) {}
                        return false;
                    }
                    return buscarEnFrames(window.top);
                    """
                    try:
                        self.driver.execute_script(js_pruebas_si)
                        self.log("  ✅ Pruebas = SI seleccionado")
                        time.sleep(1)
                    except:
                        pass

                    # 11. Tipo de Prueba (Columna K = índice 10) - Solo si es SI
                    if len(datos) > 10 and pd.notna(datos.iloc[10]):
                        valor_tipo_prueba = str(datos.iloc[10]).strip()
                        if valor_tipo_prueba != "" and valor_tipo_prueba != "-":
                            self.log(f"\n📋 CAMPO 11: Tipo de Prueba = '{valor_tipo_prueba}'")
                            if self.buscar_y_rellenar_con_javascript("elementos", valor_tipo_prueba, "select"):
                                time.sleep(1)

                                # 12. Detalle Otros (Columna L = índice 11) - Solo si K es "Otros, detalle"
                                if "otros" in valor_tipo_prueba.lower() and "detalle" in valor_tipo_prueba.lower():
                                    if len(datos) > 11 and pd.notna(datos.iloc[11]):
                                        valor_detalle_otros = str(datos.iloc[11]).strip()
                                        if valor_detalle_otros != "" and valor_detalle_otros != "-":
                                            self.log(f"\n📋 CAMPO 12: Detalle Otros = '{valor_detalle_otros[:50]}...'")
                                            self.buscar_y_rellenar_con_javascript("otros", valor_detalle_otros, "input")
                                            time.sleep(1)
                            else:
                                self.log(f"  ⚠️ No se pudo seleccionar Tipo de Prueba")
            else:
                # Si no hay valor en columna J, marcar NO por defecto
                self.log(f"\n📋 CAMPO 10: Pruebas Ofrecidas = NO (por defecto)")
                js_pruebas_no = """
                function buscarEnFrames(win) {
                    try {
                        var radios = win.document.querySelectorAll("input[name='tipoPru'][value='N']");
                        if (radios.length > 0) {
                            radios[0].checked = true;
                            if (radios[0].onclick) radios[0].onclick();
                            return true;
                        }
                        for (var i = 0; i < win.frames.length; i++) {
                            if (buscarEnFrames(win.frames[i])) return true;
                        }
                    } catch(e) {}
                    return false;
                }
                return buscarEnFrames(window.top);
                """
                try:
                    self.driver.execute_script(js_pruebas_no)
                    self.log("  ✅ Pruebas = NO seleccionado")
                except:
                    pass

            time.sleep(2)

            # ═══════════════════════════════════════════════════════════════
            # HACER CLIC EN BOTÓN SIGUIENTE - MODO NUCLEAR
            # ═══════════════════════════════════════════════════════════════
            self.log(f"\n🖱️ HACIENDO CLIC EN BOTÓN SIGUIENTE (MODO NUCLEAR)...")

            if not self.clic_boton_con_javascript("siguiente"):
                self.log("  ⚠️ Intento 1 falló, reintentando...")
                time.sleep(2)
                if not self.clic_boton_con_javascript("siguiente"):
                    raise Exception("No se pudo hacer clic en botón SIGUIENTE después de 2 intentos")

            time.sleep(3)

            self.log("\n" + "="*70)
            self.log("✅✅✅ SECCIÓN 2 COMPLETADA (MODO NUCLEAR) ✅✅✅")
            self.log("="*70)
            return True

        except Exception as e:
            self.log(f"\n❌ ERROR EN SECCIÓN 2: {str(e)}")
            return False

    def llenar_seccion2_atencion_denuncias_ANTIGUO(self, datos):
        try:
            self.log("📝 Llenando Sección 2: ATENCIÓN DE DENUNCIAS...")

            # PASO CRÍTICO: Verificar que la nueva sección cargó completamente
            self.log("  → Verificando que la página cargó correctamente...")

            # MÉTODO 1: Verificar que el título "ATENCIÓN DE DENUNCIAS" esté visible
            try:
                wait_titulo = WebDriverWait(self.driver, 20)
                titulo_visible = wait_titulo.until(
                    lambda d: "ATENCIÓN DE DENUNCIAS" in d.page_source
                )
                if titulo_visible:
                    self.log("  ✅ Título 'ATENCIÓN DE DENUNCIAS' detectado")
            except:
                self.log("  ⚠️ No se detectó el título en 20 segundos")

            # 5. Modalidad Evasión (Columna C) - USAR MÉTODO ROBUSTO
            valor_seleccionado = None
            if 'Modalidad de evasion' in datos and pd.notna(datos['Modalidad de evasion']):
                valor = str(datos['Modalidad de evasion']).strip()
                self.log(f"  → Modalidad: {valor[:50]}...")

                # MÉTODO ROBUSTO: Búsqueda con múltiples estrategias y espera extendida
                if self.llenar_campo_con_espera_robusta("modalidad", valor, "select", timeout=20):
                    # Obtener el valor seleccionado para usar en submodalidad
                    try:
                        elemento_modalidad = self.buscar_elemento_universal("modalidad", "select")
                        if elemento_modalidad:
                            select_obj = Select(elemento_modalidad)
                            valor_seleccionado = select_obj.first_selected_option.get_attribute("value")
                    except:
                        pass
                    time.sleep(1)
                else:
                    raise Exception("No se pudo seleccionar Modalidad")
            
            # 6. Sub Modalidad (Columna D) - OPCIONAL
            if 'Submodalidad' in datos and pd.notna(datos['Submodalidad']):
                valor_sub = str(datos['Submodalidad']).strip()

                if valor_sub != "" and valor_sub != "-":
                    name_submodalidad = self.obtener_selector_submodalidad(valor_seleccionado)

                    if name_submodalidad:
                        # MÉTODO ROBUSTO para submodalidad
                        if self.llenar_campo_con_espera_robusta(name_submodalidad, valor_sub, "select", timeout=15):
                            self.log(f"  → Sub Modalidad: {valor_sub}")
                            time.sleep(0.5)
                        else:
                            self.log(f"  ⚠️ No se pudo seleccionar Sub Modalidad")
            
            # 7. Tipo de Denuncia (Columna E) - Radio button con reintentos
            if 'Tipo de denuncia' in datos and pd.notna(datos['Tipo de denuncia']):
                valor = str(datos['Tipo de denuncia']).strip()
                self.log(f"  → Tipo Denuncia: {valor}")

                mapeo_tipo = {
                    "telefónica": "1", "telefonica": "1",
                    "verbal": "2",
                    "escrita": "3",
                    "formato electrónico": "4", "formato electronico": "4", "electronico": "4"
                }

                valor_radio = mapeo_tipo.get(valor.lower(), "4")

                # Reintentos para hacer clic en radio button
                for intento in range(1, 4):
                    try:
                        radio_button = self.driver.find_element(By.XPATH,
                            f"//input[@name='rdoTipo' and @value='{valor_radio}']")
                        self.driver.execute_script("arguments[0].click();", radio_button)
                        self.log(f"    ✅ Radio button seleccionado (intento {intento})")
                        time.sleep(0.5)
                        break
                    except Exception as e:
                        if intento < 3:
                            self.log(f"    ⚠️ Intento {intento} falló, reintentando...")
                            time.sleep(1)
                        else:
                            self.log(f"    ⚠️ No se pudo seleccionar radio button después de 3 intentos")
            
            # 8. Fecha SID (Columna F) - CONDICIONAL
            if 'Fecha SID' in datos and pd.notna(datos['Fecha SID']):
                valor_raw = datos['Fecha SID']

                if str(valor_raw).strip() != "":
                    fecha_formateada = self.convertir_fecha_excel(valor_raw)

                    if fecha_formateada:
                        self.log(f"  → Fecha SID: {fecha_formateada}")
                        # MÉTODO ROBUSTO para campo de fecha
                        if not self.llenar_campo_con_espera_robusta("fecha_sid", fecha_formateada, "input", timeout=15):
                            self.log(f"    ⚠️ No se pudo llenar Fecha SID")
                        time.sleep(0.5)

            # 9. Detalle (Columna G)
            if 'Detalle de la denuncia' in datos and pd.notna(datos['Detalle de la denuncia']):
                valor = str(datos['Detalle de la denuncia']).strip()

                # Limitar longitud
                if len(valor) > 1440:
                    valor = valor[:1440]

                self.log(f"  → Detalle: {valor[:50]}...")

                # MÉTODO ROBUSTO para llenar campo de detalle
                if not self.llenar_campo_con_espera_robusta("detalle", valor, "input", timeout=15):
                    self.log(f"    ⚠️ No se pudo llenar Detalle")
                time.sleep(0.5)
            
            # 10-11. Del Mes / Del Año (Columna H)
            if 'Desde' in datos and pd.notna(datos['Desde']):
                fecha_desde = self.extraer_mes_anio(datos['Desde'])

                if fecha_desde:
                    self.log(f"  → Del: {fecha_desde['mes']}/{fecha_desde['anio']}")

                    # MÉTODO ROBUSTO para selects de fecha
                    if self.llenar_campo_con_espera_robusta("MesDesde", fecha_desde['mes'], "select", timeout=15):
                        self.log(f"    ✅ Mes Desde seleccionado")
                    else:
                        self.log(f"    ⚠️ No se pudo seleccionar Mes Desde")

                    if self.llenar_campo_con_espera_robusta("AnioDesde", str(fecha_desde['anio']), "select", timeout=15):
                        self.log(f"    ✅ Año Desde seleccionado")
                    else:
                        self.log(f"    ⚠️ No se pudo seleccionar Año Desde")

                    time.sleep(0.5)

            # 12-13. Al Mes / Al Año (Columna I)
            if 'Hasta' in datos and pd.notna(datos['Hasta']):
                fecha_hasta = self.extraer_mes_anio(datos['Hasta'])

                if fecha_hasta:
                    self.log(f"  → Al: {fecha_hasta['mes']}/{fecha_hasta['anio']}")

                    # MÉTODO ROBUSTO para selects de fecha
                    if self.llenar_campo_con_espera_robusta("MesHasta", fecha_hasta['mes'], "select", timeout=15):
                        self.log(f"    ✅ Mes Hasta seleccionado")
                    else:
                        self.log(f"    ⚠️ No se pudo seleccionar Mes Hasta")

                    if self.llenar_campo_con_espera_robusta("AnioHasta", str(fecha_hasta['anio']), "select", timeout=15):
                        self.log(f"    ✅ Año Hasta seleccionado")
                    else:
                        self.log(f"    ⚠️ No se pudo seleccionar Año Hasta")

                    time.sleep(0.5)
            
            # 14. Pruebas Ofrecidas (Columna J) - Radio buttons con reintentos
            if 'PRUEBA' in datos and pd.notna(datos['PRUEBA']):
                valor_prueba = str(datos['PRUEBA']).strip().upper()
                self.log(f"  → Pruebas: {valor_prueba}")

                if valor_prueba in ["NO", "N"]:
                    # Reintentos para radio button NO
                    for intento in range(1, 4):
                        try:
                            radio_no = self.driver.find_element(By.XPATH,
                                "//input[@name='tipoPru' and @value='N']")
                            self.driver.execute_script("arguments[0].click();", radio_no)
                            self.log(f"    ✅ Radio 'NO' seleccionado")
                            time.sleep(0.5)
                            break
                        except:
                            if intento < 3:
                                time.sleep(1)

                elif valor_prueba in ["SI", "SÍ", "S"]:
                    # Reintentos para radio button SI
                    for intento in range(1, 4):
                        try:
                            radio_si = self.driver.find_element(By.XPATH,
                                "//input[@name='tipoPru' and @value='S']")
                            self.driver.execute_script("arguments[0].click();", radio_si)
                            self.log(f"    ✅ Radio 'SI' seleccionado")
                            time.sleep(1)
                            break
                        except:
                            if intento < 3:
                                time.sleep(1)

                    # 15. Tipo de Pruebas (Columna K)
                    if 'EN CASO DE SI' in datos and pd.notna(datos['EN CASO DE SI']):
                        valor_tipo_prueba = str(datos['EN CASO DE SI']).strip()

                        if valor_tipo_prueba != "" and valor_tipo_prueba != "-":
                            self.log(f"    → Tipo Prueba: {valor_tipo_prueba}")

                            # MÉTODO ROBUSTO para select de pruebas
                            if self.llenar_campo_con_espera_robusta("elementos", valor_tipo_prueba, "select", timeout=15):
                                time.sleep(0.5)

                                # 16. Si es "Otros, detalle" (Columna L)
                                if "otros" in valor_tipo_prueba.lower() and "detalle" in valor_tipo_prueba.lower():
                                    if 'OTRO, DETALLE' in datos and pd.notna(datos['OTRO, DETALLE']):
                                        valor_detalle = str(datos['OTRO, DETALLE']).strip()

                                        if valor_detalle != "" and valor_detalle != "-":
                                            self.log(f"    → Detalle Otros: {valor_detalle}")

                                            # MÉTODO ROBUSTO para campo otros
                                            if not self.llenar_campo_con_espera_robusta("otros", valor_detalle, "input", timeout=15):
                                                self.log(f"      ⚠️ No se pudo llenar Detalle Otros")
                                            time.sleep(0.5)
                            else:
                                self.log(f"    ⚠️ No se pudo seleccionar Tipo de Prueba")
            
            # 17. Siguiente - Ejecutar JavaScript directamente (MÉTODO QUE FUNCIONA)
            self.log("  → Clic en 'Siguiente'...")

            clic_siguiente_exitoso = False

            # MÉTODO PRINCIPAL: Ejecutar función JavaScript directamente (✅ COMPROBADO QUE FUNCIONA)
            try:
                self.log("    → Ejecutando clickbtn_validar() con JavaScript...")
                self.driver.execute_script("clickbtn_validar();")
                self.log("    ✅ Función JavaScript ejecutada exitosamente")
                clic_siguiente_exitoso = True
            except Exception as e:
                self.log(f"    ⚠️ Falló JS directo: {str(e)[:50]}")

                # FALLBACK: Click con JavaScript en el elemento
                try:
                    self.log("    → Fallback: Click JS en elemento...")
                    boton_siguiente = self.driver.find_element(By.XPATH,
                        "//input[@onclick='clickbtn_validar()']")
                    self.driver.execute_script("arguments[0].click();", boton_siguiente)
                    self.log("    ✅ Click JS ejecutado")
                    clic_siguiente_exitoso = True
                except Exception as e2:
                    self.log(f"    ⚠️ Falló fallback: {str(e2)[:50]}")

            if not clic_siguiente_exitoso:
                raise Exception("No se pudo hacer clic en Siguiente después de intentos")

            # ESPERA AUMENTADA: La página necesita tiempo para cargar la nueva sección
            self.log("  → Esperando carga de nueva sección (5 segundos)...")
            time.sleep(5)

            self.log("✅ Sección 2 completada")
            return True
            
        except Exception as e:
            self.log(f"❌ Error en Sección 2: {str(e)}")
            return False
    
    # ============================================
    # SECCIÓN 3: IDENTIFICACIÓN DEL DENUNCIANTE
    # ============================================
    
    def llenar_seccion3_identificacion_denunciante(self, datos):
        try:
            self.log("="*70)
            self.log("📝 SECCIÓN 3: IDENTIFICACIÓN DEL DENUNCIANTE")
            self.log("="*70)
            self.log("🚨🚨🚨 USANDO MODO NUCLEAR - JavaScript directo 🚨🚨🚨")

            # Esperar 5 segundos para que la página cargue completamente
            self.log("  ⏳ Esperando 5 segundos para carga completa...")
            time.sleep(5)

            # ═══════════════════════════════════════════════════════════════
            # SECCIÓN IV: IDENTIFICACIÓN DE LA PERSONA DENUNCIANTE
            # ═══════════════════════════════════════════════════════════════

            # 1. Tipo Denunciante (Columna M = índice 12)
            if len(datos) > 12 and pd.notna(datos.iloc[12]):
                valor = str(datos.iloc[12]).strip()
                if valor != "" and valor != "-":
                    self.log(f"\n📋 CAMPO 1: Tipo Denunciante = '{valor}'")
                    if not self.buscar_y_rellenar_con_javascript("tipodoc", valor, "select"):
                        self.log(f"  ⚠️ No se pudo seleccionar Tipo Denunciante")
                    time.sleep(1)

            # 2. Número/Nombre (Columna N = índice 13)
            if len(datos) > 13 and pd.notna(datos.iloc[13]):
                valor_raw = datos.iloc[13]
                # Convertir a string, manejando números
                valor = str(int(valor_raw)) if isinstance(valor_raw, float) else str(valor_raw)
                valor = valor.strip()

                if valor != "" and valor != "-":
                    self.log(f"\n📋 CAMPO 2: Número/Nombre = '{valor}'")
                    if not self.buscar_y_rellenar_con_javascript("numdoc", valor, "input"):
                        self.log(f"  ⚠️ No se pudo llenar Número/Nombre")
                    time.sleep(1)

            # ═══════════════════════════════════════════════════════════════
            # SECCIÓN V: DATOS PARA CONTACTARNOS CON USTED
            # ═══════════════════════════════════════════════════════════════

            # 3. Teléfono (Columna O = índice 14)
            if len(datos) > 14 and pd.notna(datos.iloc[14]):
                valor_raw = datos.iloc[14]
                valor = str(int(valor_raw)) if isinstance(valor_raw, float) else str(valor_raw)
                valor = valor.strip()

                if valor != "" and valor != "-":
                    self.log(f"\n📋 CAMPO 3: Teléfono = '{valor}'")
                    if not self.buscar_y_rellenar_con_javascript("telefono", valor, "input"):
                        self.log(f"  ⚠️ No se pudo llenar Teléfono")
                    time.sleep(1)

            # 4. Correo Electrónico (Columna P = índice 15)
            if len(datos) > 15 and pd.notna(datos.iloc[15]):
                valor = str(datos.iloc[15]).strip()
                if valor != "" and valor != "-":
                    self.log(f"\n📋 CAMPO 4: Correo Electrónico = '{valor}'")
                    if not self.buscar_y_rellenar_con_javascript("correo", valor, "input"):
                        self.log(f"  ⚠️ No se pudo llenar Correo")
                    time.sleep(1)

            # 5. Departamento (Columna Q = índice 16)
            if len(datos) > 16 and pd.notna(datos.iloc[16]):
                valor = str(datos.iloc[16]).strip()
                if valor != "" and valor != "-":
                    self.log(f"\n📋 CAMPO 5: Departamento = '{valor}'")
                    if not self.buscar_y_rellenar_con_javascript("dpto", valor, "select"):
                        self.log(f"  ⚠️ No se pudo seleccionar Departamento")
                    # Espera EXTRA para que cargue Provincia dinámicamente
                    self.log("  ⏳ Esperando carga de Provincia...")
                    time.sleep(2)

            # 6. Provincia (Columna R = índice 17)
            if len(datos) > 17 and pd.notna(datos.iloc[17]):
                valor = str(datos.iloc[17]).strip()
                if valor != "" and valor != "-":
                    self.log(f"\n📋 CAMPO 6: Provincia = '{valor}'")
                    if not self.buscar_y_rellenar_con_javascript("prov", valor, "select"):
                        self.log(f"  ⚠️ No se pudo seleccionar Provincia")
                    # Espera EXTRA para que cargue Distrito dinámicamente
                    self.log("  ⏳ Esperando carga de Distrito...")
                    time.sleep(2)

            # 7. Distrito (Columna S = índice 18)
            if len(datos) > 18 and pd.notna(datos.iloc[18]):
                valor = str(datos.iloc[18]).strip()
                if valor != "" and valor != "-":
                    self.log(f"\n📋 CAMPO 7: Distrito = '{valor}'")
                    if not self.buscar_y_rellenar_con_javascript("dist", valor, "select"):
                        self.log(f"  ⚠️ No se pudo seleccionar Distrito")
                    time.sleep(1)

            # 8. Vía (Columna T = índice 19)
            if len(datos) > 19 and pd.notna(datos.iloc[19]):
                valor = str(datos.iloc[19]).strip()
                if valor != "" and valor != "-":
                    self.log(f"\n📋 CAMPO 8: Vía = '{valor}'")
                    if not self.buscar_y_rellenar_con_javascript("tipvia", valor, "select"):
                        self.log(f"  ⚠️ No se pudo seleccionar Vía")
                    time.sleep(1)

            # 9. Nombre de Vía - Cuadro limpio (Columna U = índice 20)
            if len(datos) > 20 and pd.notna(datos.iloc[20]):
                valor = str(datos.iloc[20]).strip()
                if valor != "" and valor != "-":
                    self.log(f"\n📋 CAMPO 9: Nombre de Vía = '{valor}'")
                    if not self.buscar_y_rellenar_con_javascript("nomvia", valor, "input"):
                        self.log(f"  ⚠️ No se pudo llenar Nombre de Vía")
                    time.sleep(1)

            # 10. N°/Mzn./Km. (Columna V = índice 21)
            if len(datos) > 21 and pd.notna(datos.iloc[21]):
                valor = str(datos.iloc[21]).strip()
                if valor != "" and valor != "-":
                    self.log(f"\n📋 CAMPO 10: N°/Mzn./Km. = '{valor}'")
                    if not self.buscar_y_rellenar_con_javascript("nro", valor, "input"):
                        self.log(f"  ⚠️ No se pudo llenar N°/Mzn./Km.")
                    time.sleep(1)

            # 11. Dpto/Int/Lote/Stand (Columna W = índice 22)
            if len(datos) > 22 and pd.notna(datos.iloc[22]):
                valor = str(datos.iloc[22]).strip()
                if valor != "" and valor != "-":
                    self.log(f"\n📋 CAMPO 11: Dpto/Int/Lote/Stand = '{valor}'")
                    if not self.buscar_y_rellenar_con_javascript("interior", valor, "input"):
                        self.log(f"  ⚠️ No se pudo llenar Dpto/Int/Lote/Stand")
                    time.sleep(1)

            # 12. Zona (Columna X = índice 23)
            if len(datos) > 23 and pd.notna(datos.iloc[23]):
                valor = str(datos.iloc[23]).strip()
                if valor != "" and valor != "-":
                    self.log(f"\n📋 CAMPO 12: Zona = '{valor}'")
                    if not self.buscar_y_rellenar_con_javascript("tipzona", valor, "select"):
                        self.log(f"  ⚠️ No se pudo seleccionar Zona")
                    time.sleep(1)

            time.sleep(2)

            # ═══════════════════════════════════════════════════════════════
            # HACER CLIC EN BOTÓN GRABAR - MODO NUCLEAR
            # ═══════════════════════════════════════════════════════════════
            self.log(f"\n🖱️ HACIENDO CLIC EN BOTÓN GRABAR (MODO NUCLEAR)...")

            if not self.clic_boton_con_javascript("grabar"):
                self.log("  ⚠️ Intento 1 falló, reintentando...")
                time.sleep(2)
                if not self.clic_boton_con_javascript("grabar"):
                    raise Exception("No se pudo hacer clic en botón GRABAR después de 2 intentos")

            # Esperar respuesta del servidor
            time.sleep(5)

            self.log("\n" + "="*70)
            self.log("✅ SECCIÓN 3 COMPLETADA - DENUNCIA GRABADA")
            self.log("="*70)

            # Continuar con el procesamiento del resumen y guardado
            return self.procesar_resumen_y_guardar(datos)

        except Exception as e:
            self.log(f"\n❌ ERROR EN SECCIÓN 3: {str(e)}")
            return False
    
    def procesar_resumen_y_guardar(self, datos):
        """
        🚨 PROCESA EL RESUMEN DE LA DENUNCIA Y GUARDA EL ARCHIVO PDF

        Después de presionar "Grabar", esta función:
        1. Extrae el "Número de Orden" usando MODO NUCLEAR
        2. Verifica si hay email en la columna Y del Excel
        3. Si hay email: lo ingresa y presiona "Aceptar"
        4. Si no hay email: presiona directamente "Imprimir Constancia"
        5. Presiona el botón "Imprimir"
        6. Guarda el archivo con el nombre del Número de Orden
        """
        try:
            self.log("\n" + "="*70)
            self.log("📄 PROCESANDO RESUMEN Y GUARDANDO ARCHIVO")
            self.log("="*70)

            # ═══════════════════════════════════════════════════════════════
            # PASO 1: EXTRAER NÚMERO DE ORDEN usando MODO NUCLEAR
            # ═══════════════════════════════════════════════════════════════
            self.log("\n🔍 PASO 1: Extrayendo Número de Orden...")

            numero_orden = self.extraer_numero_orden_nuclear()

            if not numero_orden:
                raise Exception("No se pudo extraer el Número de Orden")

            self.log(f"  ✅ Número de Orden extraído: {numero_orden}")

            # ═══════════════════════════════════════════════════════════════
            # PASO 2: VERIFICAR SI HAY EMAIL EN COLUMNA Y (índice 24)
            # ═══════════════════════════════════════════════════════════════
            self.log("\n📧 PASO 2: Verificando si hay email en columna Y...")

            email = ""
            try:
                # Columna Y es el índice 24 (A=0, B=1, ... Y=24)
                email_raw = datos.iloc[24] if len(datos) > 24 else ""
                email = str(email_raw).strip() if pd.notna(email_raw) else ""

                if email and email.lower() not in ['', 'nan', 'none']:
                    self.log(f"  ✅ Email encontrado en columna Y: {email}")
                else:
                    email = ""
                    self.log(f"  ℹ️ Columna Y vacía, se omitirá el email")
            except Exception as e:
                self.log(f"  ⚠️ Error leyendo columna Y: {str(e)}")
                email = ""

            time.sleep(2)

            # ═══════════════════════════════════════════════════════════════
            # PASO 3: PROCESAR EMAIL O IR DIRECTO A IMPRIMIR
            # ═══════════════════════════════════════════════════════════════
            if email:
                # Si hay email: rellenar y presionar Aceptar
                self.log("\n📝 PASO 3: Ingresando email y presionando Aceptar...")

                # Rellenar campo de email
                if not self.buscar_y_rellenar_con_javascript("correo", email, "input"):
                    self.log("  ⚠️ No se pudo rellenar el campo de email, continuando...")

                time.sleep(1)

                # Presionar botón Aceptar - USANDO FUNCIÓN SUPER NUCLEAR
                self.log("  🚨 Presionando botón ACEPTAR (MODO SUPER NUCLEAR)...")
                if not self.clic_boton_aceptar_nuclear():
                    self.log("  ⚠️ Función nuclear falló, intentando método directo...")
                    # Fallback: ejecutar función directamente
                    try:
                        self.driver.execute_script("""
                        (function() {
                            function buscar(win, nivel) {
                                if (nivel > 10) return false;
                                try {
                                    if (typeof win.clickbtn_ejecutar === 'function') {
                                        win.clickbtn_ejecutar();
                                        return true;
                                    }
                                    for (var i = 0; i < win.frames.length; i++) {
                                        if (buscar(win.frames[i], nivel + 1)) return true;
                                    }
                                } catch(e) {}
                                return false;
                            }
                            return buscar(window.top, 0);
                        })();
                        """)
                        self.log("  ✅ Función clickbtn_ejecutar() ejecutada (fallback)")
                    except Exception as e:
                        self.log(f"  ⚠️ Error ejecutando fallback: {str(e)[:50]}")

                time.sleep(3)

            # ═══════════════════════════════════════════════════════════════
            # PASO 4: PRESIONAR "IMPRIMIR CONSTANCIA"
            # ═══════════════════════════════════════════════════════════════
            self.log("\n🖨️ PASO 4: Presionando 'Imprimir Constancia'...")

            if not self.clic_imprimir_constancia_nuclear():
                raise Exception("No se pudo hacer clic en 'Imprimir Constancia'")

            time.sleep(3)

            # ═══════════════════════════════════════════════════════════════
            # PASO 5: PRESIONAR BOTÓN "IMPRIMIR"
            # ═══════════════════════════════════════════════════════════════
            self.log("\n🖨️ PASO 5: Presionando botón 'Imprimir'...")

            if not self.clic_boton_imprimir_chrome():
                raise Exception("No se pudo hacer clic en el botón Imprimir")

            time.sleep(2)

            # ═══════════════════════════════════════════════════════════════
            # PASO 6: GUARDAR ARCHIVO PDF
            # ═══════════════════════════════════════════════════════════════
            self.log("\n💾 PASO 6: Guardando archivo PDF...")

            ruta_guardado = r"D:\DATA\Karencita\PROGRAMACIÓN\DENUNCIAS\DENUNCIAS MASIVAS"
            nombre_archivo = f"{numero_orden}.pdf"

            if not self.guardar_pdf_chrome(ruta_guardado, nombre_archivo):
                raise Exception("No se pudo guardar el archivo PDF")

            self.log(f"\n{'='*70}")
            self.log(f"✅✅✅ DENUNCIA COMPLETADA Y GUARDADA ✅✅✅")
            self.log(f"📁 Archivo: {nombre_archivo}")
            self.log(f"📂 Ruta: {ruta_guardado}")
            self.log(f"{'='*70}")

            return True

        except Exception as e:
            self.log(f"\n❌ ERROR EN PROCESAMIENTO DE RESUMEN: {str(e)}")
            return False

    def extraer_numero_orden_nuclear(self):
        """
        🚨 MODO NUCLEAR - Extrae el Número de Orden del resumen

        Busca recursivamente en todos los iframes el texto "Número de Orden:"
        y extrae el valor que está a su mismo nivel.
        """
        self.log("  🔍 Buscando 'Número de Orden' en todos los iframes...")

        js_code = """
        function buscarNumeroOrden(ventana, nivel) {
            if (nivel > 10) return null;

            try {
                // Buscar por texto que contenga "Número de Orden" o "Numero de Orden"
                var textos = [
                    "Número de Orden:",
                    "Numero de Orden:",
                    "NÚMERO DE ORDEN:",
                    "NUMERO DE ORDEN:",
                    "Nº de Orden:",
                    "N° de Orden:"
                ];

                // Estrategia 1: Buscar en todo el texto del documento
                var todoElTexto = ventana.document.body.innerText || ventana.document.body.textContent;

                for (var i = 0; i < textos.length; i++) {
                    var indice = todoElTexto.indexOf(textos[i]);
                    if (indice !== -1) {
                        // Extraer el número que viene después
                        var despues = todoElTexto.substring(indice + textos[i].length, indice + textos[i].length + 50);

                        // Buscar el primer número (secuencia de dígitos)
                        var match = despues.match(/([0-9]+)/);
                        if (match && match[1]) {
                            return match[1];
                        }
                    }
                }

                // Estrategia 2: Buscar en todos los elementos TD, SPAN, DIV, etc.
                var elementos = ventana.document.querySelectorAll('td, span, div, p, label');
                for (var i = 0; i < elementos.length; i++) {
                    var texto = elementos[i].innerText || elementos[i].textContent || '';

                    for (var j = 0; j < textos.length; j++) {
                        if (texto.indexOf(textos[j]) !== -1) {
                            // Buscar en el mismo elemento
                            var match = texto.match(/([0-9]{10,})/);
                            if (match && match[1]) {
                                return match[1];
                            }

                            // Buscar en el siguiente elemento hermano
                            var siguiente = elementos[i].nextElementSibling;
                            if (siguiente) {
                                var textoSiguiente = siguiente.innerText || siguiente.textContent || '';
                                var matchSiguiente = textoSiguiente.match(/([0-9]{10,})/);
                                if (matchSiguiente && matchSiguiente[1]) {
                                    return matchSiguiente[1];
                                }
                            }
                        }
                    }
                }

                // Buscar recursivamente en todos los iframes
                var frames = ventana.frames;
                for (var i = 0; i < frames.length; i++) {
                    try {
                        var resultado = buscarNumeroOrden(frames[i], nivel + 1);
                        if (resultado) return resultado;
                    } catch (e) {
                        // Acceso denegado al frame
                    }
                }

                return null;
            } catch (e) {
                return null;
            }
        }

        return buscarNumeroOrden(window.top, 0);
        """

        try:
            resultado = self.driver.execute_script(js_code)

            if resultado:
                self.log(f"  ✅ Número de Orden encontrado: {resultado}")
                return resultado
            else:
                self.log(f"  ❌ No se pudo encontrar el Número de Orden")
                return None

        except Exception as e:
            self.log(f"  ❌ Error ejecutando JavaScript: {str(e)[:100]}")
            return None

    def clic_imprimir_constancia_nuclear(self):
        """
        🚨🚨🚨 FUNCIÓN GARANTIZADA - IMPRIMIR CONSTANCIA 🚨🚨🚨

        Selector objetivo:
        <a href="#" class="lnk10" onclick="return printPage(parent.mainFrame, this)">
            <img src="/a/imagenes/impresora.gif">Imprimir Constancia
        </a>

        ESTRATEGIA: Probar TODOS los métodos hasta que uno funcione
        """
        self.log("  🚨🚨🚨 MODO NUCLEAR TOTAL: Imprimir Constancia 🚨🚨🚨")
        self.log("  → Máximo 3 intentos con 5 niveles cada uno")

        for intento in range(1, 4):
            self.log(f"\n  🔄 INTENTO {intento}/3 - Imprimir Constancia")

            # ═══════════════════════════════════════════════════════════════
            # NIVEL 1: JavaScript NUCLEAR - Buscar y ejecutar en TODOS los frames
            # ═══════════════════════════════════════════════════════════════
            self.log("  🔥 NIVEL 1: JavaScript NUCLEAR recursivo...")

            try:
                js_nuclear = """
                (function() {
                    var intentos = [
                        // Método 1: Buscar enlace con onclick printPage
                        function(win) {
                            var enlaces = win.document.querySelectorAll('a[onclick*="printPage"]');
                            if (enlaces.length > 0) { enlaces[0].click(); return true; }
                            return false;
                        },
                        // Método 2: Buscar por clase lnk10 con texto Imprimir
                        function(win) {
                            var enlaces = win.document.querySelectorAll('a.lnk10');
                            for (var i = 0; i < enlaces.length; i++) {
                                var txt = (enlaces[i].innerText || enlaces[i].textContent || '').toLowerCase();
                                if (txt.indexOf('imprimir') !== -1) { enlaces[i].click(); return true; }
                            }
                            return false;
                        },
                        // Método 3: Buscar imagen de impresora y clickear padre
                        function(win) {
                            var imgs = win.document.querySelectorAll('img[src*="impresora"]');
                            for (var i = 0; i < imgs.length; i++) {
                                var padre = imgs[i].parentElement;
                                if (padre && padre.tagName === 'A') { padre.click(); return true; }
                            }
                            return false;
                        },
                        // Método 4: Buscar cualquier enlace con Imprimir Constancia
                        function(win) {
                            var enlaces = win.document.querySelectorAll('a');
                            for (var i = 0; i < enlaces.length; i++) {
                                var txt = (enlaces[i].innerText || enlaces[i].textContent || '').toLowerCase();
                                if (txt.indexOf('imprimir constancia') !== -1) { enlaces[i].click(); return true; }
                            }
                            return false;
                        },
                        // Método 5: Ejecutar función printPage si existe
                        function(win) {
                            if (typeof win.printPage === 'function') {
                                try { win.printPage(win.parent.mainFrame || win); return true; } catch(e) {}
                            }
                            return false;
                        },
                        // Método 6: Buscar href="#" con onclick que contenga print
                        function(win) {
                            var enlaces = win.document.querySelectorAll('a[href="#"][onclick*="print"]');
                            if (enlaces.length > 0) { enlaces[0].click(); return true; }
                            return false;
                        }
                    ];

                    function buscarEnFrames(win, nivel) {
                        if (nivel > 10) return false;
                        try {
                            // Probar todos los métodos en la ventana actual
                            for (var m = 0; m < intentos.length; m++) {
                                try { if (intentos[m](win)) return true; } catch(e) {}
                            }
                            // Buscar en frames hijos
                            for (var i = 0; i < win.frames.length; i++) {
                                try { if (buscarEnFrames(win.frames[i], nivel + 1)) return true; } catch(e) {}
                            }
                        } catch(e) {}
                        return false;
                    }
                    return buscarEnFrames(window.top, 0);
                })();
                """
                resultado = self.driver.execute_script(js_nuclear)
                if resultado:
                    self.log("  ✅ NIVEL 1 EXITOSO: JavaScript NUCLEAR encontró y clickeó")
                    time.sleep(2)
                    return True
                else:
                    self.log("  ⚠️ Nivel 1 falló, continuando...")
            except Exception as e:
                self.log(f"  ⚠️ Nivel 1 error: {str(e)[:50]}")

            # ═══════════════════════════════════════════════════════════════
            # NIVEL 2: Selenium - Buscar en TODOS los iframes recursivamente
            # ═══════════════════════════════════════════════════════════════
            self.log("  🎯 NIVEL 2: Selenium - Búsqueda exhaustiva en iframes...")

            try:
                self.driver.switch_to.default_content()
                selectores = [
                    (By.XPATH, "//a[contains(@onclick,'printPage')]"),
                    (By.XPATH, "//a[@class='lnk10'][contains(.,'Imprimir')]"),
                    (By.XPATH, "//img[contains(@src,'impresora')]/parent::a"),
                    (By.PARTIAL_LINK_TEXT, "Imprimir"),
                    (By.XPATH, "//a[contains(.,'Imprimir Constancia')]"),
                    (By.XPATH, "//a[contains(@href,'#')][contains(@onclick,'print')]"),
                    (By.CSS_SELECTOR, "a.lnk10"),
                ]

                def buscar_en_contexto():
                    for by, selector in selectores:
                        try:
                            elementos = self.driver.find_elements(by, selector)
                            for elem in elementos:
                                try:
                                    if elem.is_displayed() or elem.is_enabled():
                                        self.driver.execute_script("arguments[0].scrollIntoView(true);", elem)
                                        time.sleep(0.3)
                                        self.driver.execute_script("arguments[0].click();", elem)
                                        return True
                                except:
                                    pass
                        except:
                            pass
                    return False

                # Buscar en contexto principal
                if buscar_en_contexto():
                    self.log("  ✅ NIVEL 2 EXITOSO: Encontrado en contexto principal")
                    time.sleep(2)
                    return True

                # Buscar en todos los iframes
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    try:
                        self.driver.switch_to.default_content()
                        self.driver.switch_to.frame(iframe)
                        if buscar_en_contexto():
                            self.log("  ✅ NIVEL 2 EXITOSO: Encontrado en iframe")
                            time.sleep(2)
                            return True

                        # Buscar frames internos
                        frames = self.driver.find_elements(By.TAG_NAME, "frame")
                        for frame in frames:
                            try:
                                self.driver.switch_to.frame(frame)
                                if buscar_en_contexto():
                                    self.log("  ✅ NIVEL 2 EXITOSO: Encontrado en frame interno")
                                    time.sleep(2)
                                    return True
                                self.driver.switch_to.parent_frame()
                            except:
                                pass
                    except:
                        pass

                self.driver.switch_to.default_content()
                self.log("  ⚠️ Nivel 2 falló, continuando...")
            except Exception as e:
                self.log(f"  ⚠️ Nivel 2 error: {str(e)[:50]}")
                try:
                    self.driver.switch_to.default_content()
                except:
                    pass

            # ═══════════════════════════════════════════════════════════════
            # NIVEL 3: pyautogui - Buscar y hacer clic en texto "Imprimir"
            # ═══════════════════════════════════════════════════════════════
            self.log("  🖱️ NIVEL 3: pyautogui - Buscar texto en pantalla...")

            try:
                import pyautogui
                time.sleep(1)

                # Intentar localizar el texto "Imprimir Constancia" en pantalla
                try:
                    ubicacion = pyautogui.locateOnScreen('imprimir_constancia.png', confidence=0.7)
                    if ubicacion:
                        centro = pyautogui.center(ubicacion)
                        pyautogui.click(centro)
                        self.log("  ✅ NIVEL 3 EXITOSO: Imagen encontrada y clickeada")
                        time.sleep(2)
                        return True
                except:
                    pass

                self.log("  ⚠️ Nivel 3 falló, continuando...")
            except Exception as e:
                self.log(f"  ⚠️ Nivel 3 error: {str(e)[:50]}")

            # ═══════════════════════════════════════════════════════════════
            # NIVEL 4: pyautogui - Ctrl+P directo
            # ═══════════════════════════════════════════════════════════════
            self.log("  ⌨️ NIVEL 4: pyautogui - Ctrl+P directo...")

            try:
                import pyautogui
                time.sleep(1)
                pyautogui.hotkey('ctrl', 'p')
                self.log("  ✅ NIVEL 4 EXITOSO: Ctrl+P ejecutado")
                time.sleep(3)
                return True
            except Exception as e:
                self.log(f"  ⚠️ Nivel 4 error: {str(e)[:50]}")

            # ═══════════════════════════════════════════════════════════════
            # NIVEL 5: ActionChains - Buscar y hacer clic
            # ═══════════════════════════════════════════════════════════════
            self.log("  🎮 NIVEL 5: ActionChains con movimiento...")

            try:
                from selenium.webdriver.common.action_chains import ActionChains
                self.driver.switch_to.default_content()

                # Buscar el elemento
                for by, selector in selectores:
                    try:
                        elem = self.driver.find_element(by, selector)
                        actions = ActionChains(self.driver)
                        actions.move_to_element(elem).pause(0.5).click().perform()
                        self.log("  ✅ NIVEL 5 EXITOSO: ActionChains clickeó el elemento")
                        time.sleep(2)
                        return True
                    except:
                        pass
            except Exception as e:
                self.log(f"  ⚠️ Nivel 5 error: {str(e)[:50]}")

            # Esperar antes del siguiente intento
            if intento < 3:
                wait_time = intento * 2
                self.log(f"  ⏳ Esperando {wait_time}s antes del siguiente intento...")
                time.sleep(wait_time)

        self.log("  ❌❌❌ FALLO después de 3 intentos - Imprimir Constancia")
        return False

    def clic_boton_imprimir_chrome(self):
        """
        🚨🚨🚨 FUNCIÓN GARANTIZADA - BOTÓN IMPRIMIR 🚨🚨🚨

        Selector objetivo (diálogo de impresión de Edge/Chrome):
        <cr-button class="action-button" role="button">Imprimir</cr-button>

        IMPORTANTE: El diálogo de impresión es NATIVO del navegador.
        Múltiples métodos para garantizar el éxito.
        """
        self.log("  🚨🚨🚨 MODO NUCLEAR TOTAL: Botón Imprimir 🚨🚨🚨")
        self.log("  → Máximo 3 intentos con 6 niveles cada uno")

        for intento in range(1, 4):
            self.log(f"\n  🔄 INTENTO {intento}/3 - Botón Imprimir")

            # ═══════════════════════════════════════════════════════════════
            # NIVEL 1: pyautogui - Enter directo (más confiable)
            # ═══════════════════════════════════════════════════════════════
            self.log("  🔥 NIVEL 1: pyautogui - Enter directo...")

            try:
                import pyautogui
                time.sleep(2)
                pyautogui.press('enter')
                self.log("  ✅ NIVEL 1 EXITOSO: Enter presionado")
                time.sleep(2)
                return True
            except Exception as e:
                self.log(f"  ⚠️ Nivel 1 error: {str(e)[:50]}")

            # ═══════════════════════════════════════════════════════════════
            # NIVEL 2: pyautogui - Alt+I (atajo en español para Imprimir)
            # ═══════════════════════════════════════════════════════════════
            self.log("  🎯 NIVEL 2: pyautogui - Alt+I...")

            try:
                import pyautogui
                time.sleep(1)
                pyautogui.hotkey('alt', 'i')
                self.log("  ✅ NIVEL 2 EXITOSO: Alt+I ejecutado")
                time.sleep(2)
                return True
            except Exception as e:
                self.log(f"  ⚠️ Nivel 2 error: {str(e)[:50]}")

            # ═══════════════════════════════════════════════════════════════
            # NIVEL 3: pyautogui - Tab múltiple + Enter
            # ═══════════════════════════════════════════════════════════════
            self.log("  ⌨️ NIVEL 3: pyautogui - Tab múltiple + Enter...")

            try:
                import pyautogui
                time.sleep(1)
                for i in range(8):
                    pyautogui.press('tab')
                    time.sleep(0.1)
                pyautogui.press('enter')
                self.log("  ✅ NIVEL 3 EXITOSO: Tab + Enter ejecutado")
                time.sleep(2)
                return True
            except Exception as e:
                self.log(f"  ⚠️ Nivel 3 error: {str(e)[:50]}")

            # ═══════════════════════════════════════════════════════════════
            # NIVEL 4: JavaScript en Shadow DOM (estructura Chrome/Edge)
            # ═══════════════════════════════════════════════════════════════
            self.log("  🔧 NIVEL 4: JavaScript en Shadow DOM...")

            try:
                js_shadow = """
                (function() {
                    try {
                        // Método 1: Estructura estándar
                        var printPreview = document.querySelector('print-preview-app');
                        if (printPreview && printPreview.shadowRoot) {
                            var sidebar = printPreview.shadowRoot.querySelector('print-preview-sidebar');
                            if (sidebar && sidebar.shadowRoot) {
                                var buttonStrip = sidebar.shadowRoot.querySelector('print-preview-button-strip');
                                if (buttonStrip && buttonStrip.shadowRoot) {
                                    var boton = buttonStrip.shadowRoot.querySelector('cr-button.action-button');
                                    if (boton) { boton.click(); return true; }
                                }
                            }
                        }

                        // Método 2: Buscar directamente cr-button.action-button
                        var botones = document.querySelectorAll('cr-button.action-button');
                        for (var i = 0; i < botones.length; i++) {
                            if (botones[i].innerText.indexOf('Imprimir') !== -1 ||
                                botones[i].innerText.indexOf('Print') !== -1) {
                                botones[i].click();
                                return true;
                            }
                        }

                        // Método 3: Buscar en todos los shadow roots
                        function buscarEnShadow(root) {
                            var botones = root.querySelectorAll('cr-button, button');
                            for (var i = 0; i < botones.length; i++) {
                                var texto = (botones[i].innerText || '').toLowerCase();
                                if (texto.indexOf('imprimir') !== -1 || texto.indexOf('print') !== -1) {
                                    if (botones[i].className.indexOf('action') !== -1 ||
                                        botones[i].className.indexOf('primary') !== -1) {
                                        botones[i].click();
                                        return true;
                                    }
                                }
                            }
                            var elementos = root.querySelectorAll('*');
                            for (var i = 0; i < elementos.length; i++) {
                                if (elementos[i].shadowRoot) {
                                    if (buscarEnShadow(elementos[i].shadowRoot)) return true;
                                }
                            }
                            return false;
                        }
                        return buscarEnShadow(document);
                    } catch(e) { return false; }
                })();
                """
                resultado = self.driver.execute_script(js_shadow)
                if resultado:
                    self.log("  ✅ NIVEL 4 EXITOSO: JavaScript clickeó el botón")
                    time.sleep(2)
                    return True
                else:
                    self.log("  ⚠️ Nivel 4: No se encontró el botón")
            except Exception as e:
                self.log(f"  ⚠️ Nivel 4 error: {str(e)[:50]}")

            # ═══════════════════════════════════════════════════════════════
            # NIVEL 5: pyautogui - Shift+Tab + Enter (navegación inversa)
            # ═══════════════════════════════════════════════════════════════
            self.log("  🔄 NIVEL 5: pyautogui - Shift+Tab + Enter...")

            try:
                import pyautogui
                time.sleep(1)
                for i in range(3):
                    pyautogui.hotkey('shift', 'tab')
                    time.sleep(0.1)
                pyautogui.press('enter')
                self.log("  ✅ NIVEL 5 EXITOSO: Shift+Tab + Enter ejecutado")
                time.sleep(2)
                return True
            except Exception as e:
                self.log(f"  ⚠️ Nivel 5 error: {str(e)[:50]}")

            # ═══════════════════════════════════════════════════════════════
            # NIVEL 6: pyautogui - Escape + Ctrl+P + Enter (reiniciar)
            # ═══════════════════════════════════════════════════════════════
            self.log("  🔁 NIVEL 6: Reiniciar diálogo y Enter...")

            try:
                import pyautogui
                time.sleep(1)
                # Cerrar diálogo actual
                pyautogui.press('escape')
                time.sleep(1)
                # Reabrir con Ctrl+P
                pyautogui.hotkey('ctrl', 'p')
                time.sleep(3)
                # Enter directo
                pyautogui.press('enter')
                self.log("  ✅ NIVEL 6 EXITOSO: Diálogo reiniciado y Enter")
                time.sleep(2)
                return True
            except Exception as e:
                self.log(f"  ⚠️ Nivel 6 error: {str(e)[:50]}")

            # Esperar antes del siguiente intento
            if intento < 3:
                wait_time = intento * 2
                self.log(f"  ⏳ Esperando {wait_time}s antes del siguiente intento...")
                time.sleep(wait_time)

        self.log("  ❌❌❌ FALLO después de 3 intentos - Botón Imprimir")
        return False

    def clic_boton_aceptar_nuclear(self):
        """
        🚨🚨🚨 FUNCIÓN SUPER NUCLEAR - BOTÓN ACEPTAR 🚨🚨🚨

        Selector objetivo:
        <input type="button" name="btnsubmit" value="Aceptar" onclick="clickbtn_ejecutar()">

        TODOS LOS MÉTODOS DISPONIBLES:
        - JavaScript Nuclear recursivo (6 estrategias)
        - Selenium con múltiples selectores
        - pyautogui
        - ActionChains
        - hacer_clic_robusto
        """
        self.log("  🚨🚨🚨 MODO SUPER NUCLEAR: Botón Aceptar 🚨🚨🚨")
        self.log("  → Máximo 3 intentos con 7 niveles cada uno")

        for intento in range(1, 4):
            self.log(f"\n  🔄 INTENTO {intento}/3 - Botón Aceptar")

            # ═══════════════════════════════════════════════════════════════
            # NIVEL 1: JavaScript NUCLEAR - Ejecutar clickbtn_ejecutar()
            # ═══════════════════════════════════════════════════════════════
            self.log("  🔥 NIVEL 1: JavaScript - Ejecutar clickbtn_ejecutar()...")

            try:
                js_nuclear = """
                (function() {
                    function buscarYClickAceptar(win, nivel) {
                        if (nivel > 10) return false;
                        try {
                            // Método 1: Ejecutar función clickbtn_ejecutar directamente
                            if (typeof win.clickbtn_ejecutar === 'function') {
                                win.clickbtn_ejecutar();
                                return true;
                            }

                            // Método 2: Buscar botón por onclick
                            var btns = win.document.querySelectorAll("input[onclick*='clickbtn_ejecutar']");
                            if (btns.length > 0) { btns[0].click(); return true; }

                            // Método 3: Buscar por value="Aceptar"
                            btns = win.document.querySelectorAll("input[value='Aceptar']");
                            if (btns.length > 0) { btns[0].click(); return true; }

                            // Método 4: Buscar por name="btnsubmit" con value Aceptar
                            btns = win.document.querySelectorAll("input[name='btnsubmit']");
                            for (var i = 0; i < btns.length; i++) {
                                if (btns[i].value && btns[i].value.indexOf('Aceptar') !== -1) {
                                    btns[i].click();
                                    return true;
                                }
                            }

                            // Método 5: Buscar cualquier input type=button con Aceptar
                            btns = win.document.querySelectorAll("input[type='button']");
                            for (var i = 0; i < btns.length; i++) {
                                var val = (btns[i].value || '').toLowerCase();
                                if (val.indexOf('aceptar') !== -1) {
                                    btns[i].click();
                                    return true;
                                }
                            }

                            // Método 6: Buscar botones HTML
                            btns = win.document.querySelectorAll("button");
                            for (var i = 0; i < btns.length; i++) {
                                var txt = (btns[i].innerText || btns[i].textContent || '').toLowerCase();
                                if (txt.indexOf('aceptar') !== -1) {
                                    btns[i].click();
                                    return true;
                                }
                            }

                            // Buscar en frames hijos
                            for (var i = 0; i < win.frames.length; i++) {
                                try { if (buscarYClickAceptar(win.frames[i], nivel + 1)) return true; } catch(e) {}
                            }
                        } catch(e) {}
                        return false;
                    }
                    return buscarYClickAceptar(window.top, 0);
                })();
                """
                resultado = self.driver.execute_script(js_nuclear)
                if resultado:
                    self.log("  ✅ NIVEL 1 EXITOSO: JavaScript NUCLEAR clickeó Aceptar")
                    time.sleep(2)
                    return True
                else:
                    self.log("  ⚠️ Nivel 1 falló, continuando...")
            except Exception as e:
                self.log(f"  ⚠️ Nivel 1 error: {str(e)[:50]}")

            # ═══════════════════════════════════════════════════════════════
            # NIVEL 2: clic_boton_con_javascript (método existente)
            # ═══════════════════════════════════════════════════════════════
            self.log("  🎯 NIVEL 2: Usando clic_boton_con_javascript...")

            try:
                if self.clic_boton_con_javascript("aceptar"):
                    self.log("  ✅ NIVEL 2 EXITOSO: clic_boton_con_javascript")
                    time.sleep(2)
                    return True
            except Exception as e:
                self.log(f"  ⚠️ Nivel 2 error: {str(e)[:50]}")

            # ═══════════════════════════════════════════════════════════════
            # NIVEL 3: Selenium - Búsqueda exhaustiva en iframes
            # ═══════════════════════════════════════════════════════════════
            self.log("  🔍 NIVEL 3: Selenium - Búsqueda exhaustiva...")

            try:
                self.driver.switch_to.default_content()
                selectores = [
                    (By.XPATH, "//input[@onclick=\"clickbtn_ejecutar()\"]"),
                    (By.XPATH, "//input[contains(@onclick,'clickbtn_ejecutar')]"),
                    (By.XPATH, "//input[@value='Aceptar']"),
                    (By.XPATH, "//input[@name='btnsubmit'][@value='Aceptar']"),
                    (By.XPATH, "//input[@type='button'][contains(@value,'Aceptar')]"),
                    (By.XPATH, "//button[contains(text(),'Aceptar')]"),
                    (By.CSS_SELECTOR, "input[value='Aceptar']"),
                    (By.CSS_SELECTOR, "input[onclick*='ejecutar']"),
                ]

                def buscar_y_click():
                    for by, selector in selectores:
                        try:
                            elementos = self.driver.find_elements(by, selector)
                            for elem in elementos:
                                try:
                                    if elem.is_displayed() or elem.is_enabled():
                                        self.driver.execute_script("arguments[0].scrollIntoView(true);", elem)
                                        time.sleep(0.3)
                                        self.driver.execute_script("arguments[0].click();", elem)
                                        return True
                                except:
                                    pass
                        except:
                            pass
                    return False

                # Buscar en contexto principal
                if buscar_y_click():
                    self.log("  ✅ NIVEL 3 EXITOSO: Selenium en contexto principal")
                    time.sleep(2)
                    return True

                # Buscar en iframes
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    try:
                        self.driver.switch_to.default_content()
                        self.driver.switch_to.frame(iframe)
                        if buscar_y_click():
                            self.log("  ✅ NIVEL 3 EXITOSO: Selenium en iframe")
                            time.sleep(2)
                            return True

                        frames = self.driver.find_elements(By.TAG_NAME, "frame")
                        for frame in frames:
                            try:
                                self.driver.switch_to.frame(frame)
                                if buscar_y_click():
                                    self.log("  ✅ NIVEL 3 EXITOSO: Selenium en frame interno")
                                    time.sleep(2)
                                    return True
                                self.driver.switch_to.parent_frame()
                            except:
                                pass
                    except:
                        pass

                self.driver.switch_to.default_content()
                self.log("  ⚠️ Nivel 3 falló, continuando...")
            except Exception as e:
                self.log(f"  ⚠️ Nivel 3 error: {str(e)[:50]}")
                try:
                    self.driver.switch_to.default_content()
                except:
                    pass

            # ═══════════════════════════════════════════════════════════════
            # NIVEL 4: buscar_elemento_universal + hacer_clic_robusto
            # ═══════════════════════════════════════════════════════════════
            self.log("  🎯 NIVEL 4: buscar_elemento_universal + hacer_clic_robusto...")

            try:
                elemento = self.buscar_elemento_universal("aceptar", "button")
                if elemento:
                    if self.hacer_clic_robusto(elemento, "Botón Aceptar"):
                        self.log("  ✅ NIVEL 4 EXITOSO: Universal + Robusto")
                        time.sleep(2)
                        return True
            except Exception as e:
                self.log(f"  ⚠️ Nivel 4 error: {str(e)[:50]}")

            # ═══════════════════════════════════════════════════════════════
            # NIVEL 5: buscar_en_todos_contextos_recursivo + clic
            # ═══════════════════════════════════════════════════════════════
            self.log("  🔄 NIVEL 5: Búsqueda recursiva en todos contextos...")

            try:
                elemento = self.buscar_en_todos_contextos_recursivo(By.XPATH, "//input[@value='Aceptar']")
                if elemento:
                    self.driver.execute_script("arguments[0].click();", elemento)
                    self.log("  ✅ NIVEL 5 EXITOSO: Recursivo + clic")
                    time.sleep(2)
                    return True
            except Exception as e:
                self.log(f"  ⚠️ Nivel 5 error: {str(e)[:50]}")

            # ═══════════════════════════════════════════════════════════════
            # NIVEL 6: ActionChains
            # ═══════════════════════════════════════════════════════════════
            self.log("  🎮 NIVEL 6: ActionChains...")

            try:
                from selenium.webdriver.common.action_chains import ActionChains
                self.driver.switch_to.default_content()

                for by, selector in selectores[:4]:
                    try:
                        elem = self.driver.find_element(by, selector)
                        actions = ActionChains(self.driver)
                        actions.move_to_element(elem).pause(0.5).click().perform()
                        self.log("  ✅ NIVEL 6 EXITOSO: ActionChains")
                        time.sleep(2)
                        return True
                    except:
                        pass
            except Exception as e:
                self.log(f"  ⚠️ Nivel 6 error: {str(e)[:50]}")

            # ═══════════════════════════════════════════════════════════════
            # NIVEL 7: pyautogui - Tab + Enter
            # ═══════════════════════════════════════════════════════════════
            self.log("  ⌨️ NIVEL 7: pyautogui - Tab + Enter...")

            try:
                import pyautogui
                time.sleep(1)
                # Intentar Tab para llegar al botón
                for i in range(5):
                    pyautogui.press('tab')
                    time.sleep(0.2)
                pyautogui.press('enter')
                self.log("  ✅ NIVEL 7 EXITOSO: pyautogui Tab + Enter")
                time.sleep(2)
                return True
            except Exception as e:
                self.log(f"  ⚠️ Nivel 7 error: {str(e)[:50]}")

            # Esperar antes del siguiente intento
            if intento < 3:
                wait_time = intento * 2
                self.log(f"  ⏳ Esperando {wait_time}s antes del siguiente intento...")
                time.sleep(wait_time)

        self.log("  ❌❌❌ FALLO después de 3 intentos - Botón Aceptar")
        return False

    def guardar_pdf_chrome(self, ruta_guardado, nombre_archivo):
        """
        🚨🚨🚨 FUNCIÓN SUPER NUCLEAR - GUARDAR PDF 🚨🚨🚨

        Guarda el PDF en: D:\DATA\Karencita\PROGRAMACIÓN\DENUNCIAS\DENUNCIAS MASIVAS
        Con nombre: {numero_orden}.pdf

        TODOS LOS MÉTODOS DISPONIBLES:
        - NIVEL 1: pyperclip + Ctrl+A + Ctrl+V + Enter
        - NIVEL 2: Alt+D (barra dirección) + navegación
        - NIVEL 3: pyautogui.write() directo
        - NIVEL 4: F6 + navegación alternativa
        - NIVEL 5: Buscar en Downloads y mover
        - NIVEL 6: Esperar y reintentar con verificación
        """
        self.log(f"  🚨🚨🚨 MODO SUPER NUCLEAR: Guardando PDF 🚨🚨🚨")
        self.log(f"  💾 Archivo: {nombre_archivo}")
        self.log(f"  📂 Ruta: {ruta_guardado}")

        try:
            # Crear la ruta completa
            ruta_completa = os.path.join(ruta_guardado, nombre_archivo)

            # Asegurar que el directorio existe
            if not os.path.exists(ruta_guardado):
                os.makedirs(ruta_guardado)
                self.log(f"  ✅ Directorio creado: {ruta_guardado}")

            # Esperar a que aparezca la ventana de guardado
            self.log("  ⏳ Esperando ventana de guardado...")
            time.sleep(3)

            for intento in range(1, 4):
                self.log(f"\n  🔄 INTENTO {intento}/3 - Guardando PDF")

                # ═══════════════════════════════════════════════════════════════
                # MÉTODO 1: pyperclip + Ctrl+A + Ctrl+V + Enter
                # ═══════════════════════════════════════════════════════════════
                self.log("  🔥 NIVEL 1: Clipboard + Ctrl+A + Ctrl+V + Enter...")

                try:
                    import pyautogui
                    import pyperclip

                    time.sleep(1)

                    # Copiar la ruta completa al portapapeles
                    pyperclip.copy(ruta_completa)
                    self.log(f"  → Ruta copiada: {ruta_completa}")
                    time.sleep(0.5)

                    # Ctrl+A para seleccionar todo el texto actual
                    pyautogui.hotkey('ctrl', 'a')
                    time.sleep(0.3)

                    # Ctrl+V para pegar la ruta
                    pyautogui.hotkey('ctrl', 'v')
                    self.log(f"  → Ruta pegada con Ctrl+V")
                    time.sleep(0.5)

                    # Enter para guardar
                    pyautogui.press('enter')
                    self.log(f"  → Enter presionado (guardando...)")
                    time.sleep(3)

                    # Enter adicional por si aparece diálogo de confirmación
                    pyautogui.press('enter')
                    time.sleep(2)

                    # Verificar si el archivo se guardó
                    if os.path.exists(ruta_completa):
                        self.log(f"  ✅ NIVEL 1 EXITOSO: Archivo guardado correctamente")
                        return True
                    else:
                        self.log(f"  ⚠️ Nivel 1: Archivo no encontrado aún...")

                except ImportError:
                    self.log(f"  ⚠️ pyautogui/pyperclip no disponibles")
                except Exception as e:
                    self.log(f"  ⚠️ Nivel 1 error: {str(e)[:80]}")

                # ═══════════════════════════════════════════════════════════════
                # MÉTODO 2: Alt+D (barra dirección) + navegación
                # ═══════════════════════════════════════════════════════════════
                self.log("  🎯 NIVEL 2: Alt+D + Navegación...")

                try:
                    import pyautogui
                    import pyperclip

                    time.sleep(1)

                    # Alt+D para ir a la barra de dirección
                    pyautogui.hotkey('alt', 'd')
                    time.sleep(0.5)

                    # Pegar la ruta de la carpeta
                    pyperclip.copy(ruta_guardado)
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.3)

                    # Enter para navegar
                    pyautogui.press('enter')
                    time.sleep(1.5)

                    # Tab para ir al campo de nombre
                    for _ in range(3):
                        pyautogui.press('tab')
                        time.sleep(0.2)

                    # Pegar el nombre del archivo
                    pyperclip.copy(nombre_archivo)
                    pyautogui.hotkey('ctrl', 'a')
                    time.sleep(0.2)
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.3)

                    # Enter para guardar
                    pyautogui.press('enter')
                    self.log(f"  → Enter presionado (guardando...)")
                    time.sleep(3)

                    # Enter por si hay confirmación
                    pyautogui.press('enter')
                    time.sleep(2)

                    if os.path.exists(ruta_completa):
                        self.log(f"  ✅ NIVEL 2 EXITOSO: Archivo guardado")
                        return True
                    else:
                        self.log(f"  ⚠️ Nivel 2: Archivo no encontrado...")

                except Exception as e:
                    self.log(f"  ⚠️ Nivel 2 error: {str(e)[:80]}")

                # ═══════════════════════════════════════════════════════════════
                # MÉTODO 3: pyautogui.write() directo (caracteres uno por uno)
                # ═══════════════════════════════════════════════════════════════
                self.log("  ⌨️ NIVEL 3: pyautogui.write() directo...")

                try:
                    import pyautogui

                    time.sleep(1)

                    # Seleccionar todo y escribir la ruta directamente
                    pyautogui.hotkey('ctrl', 'a')
                    time.sleep(0.3)

                    # Escribir la ruta caracter por caracter (más lento pero más confiable)
                    pyautogui.write(ruta_completa, interval=0.02)
                    time.sleep(0.5)

                    # Enter para guardar
                    pyautogui.press('enter')
                    self.log(f"  → Enter presionado")
                    time.sleep(3)

                    pyautogui.press('enter')  # Confirmación
                    time.sleep(2)

                    if os.path.exists(ruta_completa):
                        self.log(f"  ✅ NIVEL 3 EXITOSO: Archivo guardado con write()")
                        return True
                    else:
                        self.log(f"  ⚠️ Nivel 3: Archivo no encontrado...")

                except Exception as e:
                    self.log(f"  ⚠️ Nivel 3 error: {str(e)[:80]}")

                # ═══════════════════════════════════════════════════════════════
                # MÉTODO 4: F6 + navegación alternativa
                # ═══════════════════════════════════════════════════════════════
                self.log("  🔧 NIVEL 4: F6 + navegación alternativa...")

                try:
                    import pyautogui
                    import pyperclip

                    time.sleep(1)

                    # F6 a veces funciona para ir a la barra de dirección
                    pyautogui.press('f6')
                    time.sleep(0.5)

                    # Pegar ruta completa
                    pyperclip.copy(ruta_completa)
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.5)

                    pyautogui.press('enter')
                    time.sleep(3)

                    pyautogui.press('enter')
                    time.sleep(2)

                    if os.path.exists(ruta_completa):
                        self.log(f"  ✅ NIVEL 4 EXITOSO: Archivo guardado con F6")
                        return True
                    else:
                        self.log(f"  ⚠️ Nivel 4: Archivo no encontrado...")

                except Exception as e:
                    self.log(f"  ⚠️ Nivel 4 error: {str(e)[:80]}")

                # ═══════════════════════════════════════════════════════════════
                # MÉTODO 5: Buscar en Downloads y mover
                # ═══════════════════════════════════════════════════════════════
                self.log("  🔍 NIVEL 5: Buscando en Downloads...")

                try:
                    # Buscar en Downloads
                    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
                    archivo_downloads = os.path.join(downloads_path, nombre_archivo)

                    # Esperar un poco más
                    time.sleep(2)

                    if os.path.exists(archivo_downloads):
                        self.log(f"  → Archivo encontrado en Downloads, moviendo...")
                        import shutil
                        shutil.move(archivo_downloads, ruta_completa)

                        if os.path.exists(ruta_completa):
                            self.log(f"  ✅ NIVEL 5 EXITOSO: Archivo movido desde Downloads")
                            return True

                    # También buscar con variaciones del nombre
                    for archivo in os.listdir(downloads_path):
                        if archivo.endswith('.pdf') and nombre_archivo.replace('.pdf', '') in archivo:
                            archivo_encontrado = os.path.join(downloads_path, archivo)
                            import shutil
                            shutil.move(archivo_encontrado, ruta_completa)
                            if os.path.exists(ruta_completa):
                                self.log(f"  ✅ NIVEL 5 EXITOSO: Archivo encontrado y movido")
                                return True

                except Exception as e:
                    self.log(f"  ⚠️ Nivel 5 error: {str(e)[:80]}")

                # ═══════════════════════════════════════════════════════════════
                # MÉTODO 6: Reintentar con Escape + combinación
                # ═══════════════════════════════════════════════════════════════
                self.log("  🔁 NIVEL 6: Reintentar con Escape + combinación...")

                try:
                    import pyautogui
                    import pyperclip

                    # Cancelar cualquier estado anterior
                    pyautogui.press('escape')
                    time.sleep(1)

                    # Ctrl+S por si no se abrió el diálogo
                    pyautogui.hotkey('ctrl', 's')
                    time.sleep(2)

                    # Intentar pegar la ruta
                    pyperclip.copy(ruta_completa)
                    pyautogui.hotkey('ctrl', 'a')
                    time.sleep(0.2)
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.5)

                    pyautogui.press('enter')
                    time.sleep(3)

                    pyautogui.press('enter')
                    time.sleep(2)

                    if os.path.exists(ruta_completa):
                        self.log(f"  ✅ NIVEL 6 EXITOSO: Archivo guardado con reintentar")
                        return True

                except Exception as e:
                    self.log(f"  ⚠️ Nivel 6 error: {str(e)[:80]}")

                # Esperar antes del siguiente intento
                if intento < 3:
                    wait_time = intento * 2
                    self.log(f"  ⏳ Esperando {wait_time}s antes del siguiente intento...")
                    time.sleep(wait_time)

            # Si llegamos aquí, todos los intentos fallaron
            self.log("  ❌❌❌ FALLO después de 3 intentos - Guardado de PDF")
            self.log("  ℹ️ CONSEJO: Asegúrate de que la ventana de guardado esté visible")
            return False

        except Exception as e:
            self.log(f"  ❌ Error general: {str(e)[:100]}")
            return False

    # ============================================
    # FUNCIONES AUXILIARES
    # ============================================
    
    def obtener_selector_submodalidad(self, valor_modalidad):
        mapeo = {
            "03000": "codigosubtrib1",
            "04000": "codigosubtrib2",
            "05000": "codigosubtrib3",
            "06000": "codigosubtrib4",
            "07000": "codigosubtrib5",
            "11000": "codigosubtrib6",
            "12000": "codigosubtrib7",
        }
        return mapeo.get(valor_modalidad, None)
    
    def convertir_fecha_excel(self, fecha):
        try:
            if isinstance(fecha, (int, float)):
                fecha_base = datetime(1899, 12, 30)
                fecha_real = fecha_base + timedelta(days=int(fecha))
                return fecha_real.strftime('%d/%m/%Y')
            elif isinstance(fecha, pd.Timestamp):
                return fecha.strftime('%d/%m/%Y')
            else:
                from dateutil import parser
                fecha_real = parser.parse(str(fecha))
                return fecha_real.strftime('%d/%m/%Y')
        except:
            return None
    
    def extraer_mes_anio(self, fecha):
        try:
            if isinstance(fecha, (int, float)):
                fecha_base = datetime(1899, 12, 30)
                fecha_real = fecha_base + timedelta(days=int(fecha))
            elif isinstance(fecha, pd.Timestamp):
                fecha_real = fecha
            else:
                from dateutil import parser
                fecha_real = parser.parse(str(fecha))

            meses = {
                1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                9: "Setiembre",
                10: "Octubre", 11: "Noviembre", 12: "Diciembre"
            }

            return {'mes': meses[fecha_real.month], 'anio': fecha_real.year}
        except:
            return None

    # ============================================
    # FUNCIÓN DE DIAGNÓSTICO ULTRA COMPLETA
    # ============================================

    def exportar_diagnostico_completo(self, nombre_archivo="diagnostico_completo"):
        """
        FUNCIÓN DE DIAGNÓSTICO MEGA COMPLETA
        Exporta TODA la información de la página actual:
        - HTML completo
        - Todos los iframes con detalles
        - Todos los selectores (inputs, selects, buttons, etc.)
        - Screenshots
        - Estructura del DOM

        Returns:
            str: Ruta de la carpeta donde se guardó el diagnóstico
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            carpeta_diagnostico = f"diagnostico_{timestamp}"

            # Crear carpeta de diagnóstico
            if not os.path.exists(carpeta_diagnostico):
                os.makedirs(carpeta_diagnostico)

            self.log(f"\n{'='*80}")
            self.log(f"🔬 INICIANDO DIAGNÓSTICO ULTRA COMPLETO")
            self.log(f"{'='*80}")
            self.log(f"📁 Carpeta: {carpeta_diagnostico}")

            # ========== 1. INFORMACIÓN GENERAL ==========
            self.log("\n1️⃣ Exportando información general...")
            info_general = {
                "timestamp": timestamp,
                "url": self.driver.current_url,
                "titulo": self.driver.title,
                "ventanas_abiertas": len(self.driver.window_handles)
            }

            with open(f"{carpeta_diagnostico}/01_info_general.json", "w", encoding="utf-8") as f:
                json.dump(info_general, f, indent=2, ensure_ascii=False)

            # ========== 2. HTML COMPLETO DE LA PÁGINA ==========
            self.log("2️⃣ Exportando HTML completo de la página principal...")
            html_principal = self.driver.page_source
            with open(f"{carpeta_diagnostico}/02_html_principal.html", "w", encoding="utf-8") as f:
                f.write(html_principal)

            # ========== 3. INFORMACIÓN DETALLADA DE TODOS LOS IFRAMES ==========
            self.log("3️⃣ Analizando todos los iframes...")
            iframes_info = []

            self.driver.switch_to.default_content()
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")

            self.log(f"   → {len(iframes)} iframes encontrados")

            for idx, iframe in enumerate(iframes):
                try:
                    iframe_data = {
                        "indice": idx,
                        "id": iframe.get_attribute("id") or "sin_id",
                        "name": iframe.get_attribute("name") or "sin_name",
                        "src": iframe.get_attribute("src") or "sin_src",
                        "class": iframe.get_attribute("class") or "sin_class",
                        "visible": iframe.is_displayed(),
                        "enabled": iframe.is_enabled(),
                        "width": iframe.get_attribute("width") or "auto",
                        "height": iframe.get_attribute("height") or "auto"
                    }

                    # Intentar acceder al iframe y obtener su contenido
                    try:
                        self.driver.switch_to.default_content()
                        self.driver.switch_to.frame(idx)

                        # Obtener HTML del iframe
                        iframe_html = self.driver.page_source
                        iframe_data["html_length"] = len(iframe_html)
                        iframe_data["accesible"] = True

                        # Guardar HTML del iframe
                        with open(f"{carpeta_diagnostico}/iframe_{idx}_{iframe_data['id']}.html", "w", encoding="utf-8") as f:
                            f.write(iframe_html)

                        # Buscar elementos clave en el iframe
                        iframe_data["elementos"] = {
                            "forms": len(self.driver.find_elements(By.TAG_NAME, "form")),
                            "inputs": len(self.driver.find_elements(By.TAG_NAME, "input")),
                            "selects": len(self.driver.find_elements(By.TAG_NAME, "select")),
                            "buttons": len(self.driver.find_elements(By.TAG_NAME, "button")),
                            "textareas": len(self.driver.find_elements(By.TAG_NAME, "textarea"))
                        }

                        # Buscar campo tipodoc específicamente
                        try:
                            tipodoc = self.driver.find_element(By.NAME, "tipodoc")
                            iframe_data["tiene_tipodoc"] = True
                            iframe_data["POSIBLE_IFRAME_CORRECTO"] = "⭐⭐⭐ SÍ ⭐⭐⭐"
                        except:
                            iframe_data["tiene_tipodoc"] = False
                            iframe_data["POSIBLE_IFRAME_CORRECTO"] = "No"

                        # Buscar formulario registroden
                        try:
                            form = self.driver.find_element(By.NAME, "registroden")
                            iframe_data["tiene_form_registroden"] = True
                        except:
                            iframe_data["tiene_form_registroden"] = False

                        self.driver.switch_to.default_content()

                    except Exception as e:
                        iframe_data["accesible"] = False
                        iframe_data["error_acceso"] = str(e)[:100]
                        self.driver.switch_to.default_content()

                    iframes_info.append(iframe_data)
                    self.log(f"   ✓ Iframe {idx} ({iframe_data['id']}): {'✅ ACCESIBLE' if iframe_data.get('accesible') else '❌ NO ACCESIBLE'}")

                except Exception as e:
                    self.log(f"   ⚠️ Error en iframe {idx}: {str(e)[:50]}")

            # Guardar información de iframes
            with open(f"{carpeta_diagnostico}/03_iframes_detalle.json", "w", encoding="utf-8") as f:
                json.dump(iframes_info, f, indent=2, ensure_ascii=False)

            # Crear reporte legible de iframes
            with open(f"{carpeta_diagnostico}/03_iframes_reporte.txt", "w", encoding="utf-8") as f:
                f.write("="*80 + "\n")
                f.write("REPORTE DE IFRAMES\n")
                f.write("="*80 + "\n\n")

                for iframe in iframes_info:
                    f.write(f"\n{'='*80}\n")
                    f.write(f"IFRAME #{iframe['indice']}\n")
                    f.write(f"{'='*80}\n")
                    f.write(f"ID: {iframe['id']}\n")
                    f.write(f"NAME: {iframe['name']}\n")
                    f.write(f"SRC: {iframe['src']}\n")
                    f.write(f"VISIBLE: {iframe['visible']}\n")
                    f.write(f"ACCESIBLE: {iframe.get('accesible', False)}\n")
                    f.write(f"⭐ IFRAME CORRECTO: {iframe.get('POSIBLE_IFRAME_CORRECTO', 'No')}\n")

                    if iframe.get('accesible'):
                        f.write(f"\nElementos encontrados:\n")
                        for key, value in iframe.get('elementos', {}).items():
                            f.write(f"  - {key}: {value}\n")
                        f.write(f"\nTiene campo 'tipodoc': {iframe.get('tiene_tipodoc', False)}\n")
                        f.write(f"Tiene formulario 'registroden': {iframe.get('tiene_form_registroden', False)}\n")
                    else:
                        f.write(f"\nError: {iframe.get('error_acceso', 'N/A')}\n")

            # ========== 4. SELECTORES EN PÁGINA PRINCIPAL ==========
            self.log("4️⃣ Extrayendo selectores de página principal...")
            self.driver.switch_to.default_content()

            selectores = {
                "inputs": [],
                "selects": [],
                "buttons": [],
                "textareas": [],
                "forms": [],
                "links": []
            }

            # Inputs
            for inp in self.driver.find_elements(By.TAG_NAME, "input")[:50]:
                try:
                    selectores["inputs"].append({
                        "name": inp.get_attribute("name"),
                        "id": inp.get_attribute("id"),
                        "type": inp.get_attribute("type"),
                        "value": inp.get_attribute("value"),
                        "visible": inp.is_displayed()
                    })
                except:
                    pass

            # Selects
            for sel in self.driver.find_elements(By.TAG_NAME, "select")[:50]:
                try:
                    selectores["selects"].append({
                        "name": sel.get_attribute("name"),
                        "id": sel.get_attribute("id"),
                        "visible": sel.is_displayed()
                    })
                except:
                    pass

            # Buttons
            for btn in self.driver.find_elements(By.TAG_NAME, "button")[:50]:
                try:
                    selectores["buttons"].append({
                        "name": btn.get_attribute("name"),
                        "id": btn.get_attribute("id"),
                        "text": btn.text.strip()[:50],
                        "visible": btn.is_displayed()
                    })
                except:
                    pass

            with open(f"{carpeta_diagnostico}/04_selectores_principal.json", "w", encoding="utf-8") as f:
                json.dump(selectores, f, indent=2, ensure_ascii=False)

            # ========== 5. SCREENSHOT ==========
            self.log("5️⃣ Capturando screenshot...")
            try:
                self.driver.save_screenshot(f"{carpeta_diagnostico}/05_screenshot.png")
                self.log("   ✓ Screenshot guardado")
            except Exception as e:
                self.log(f"   ⚠️ No se pudo guardar screenshot: {str(e)[:50]}")

            # ========== 6. CREAR REPORTE RESUMEN ==========
            self.log("6️⃣ Generando reporte resumen...")

            with open(f"{carpeta_diagnostico}/00_REPORTE_RESUMEN.txt", "w", encoding="utf-8") as f:
                f.write("="*80 + "\n")
                f.write("REPORTE DE DIAGNÓSTICO COMPLETO\n")
                f.write("="*80 + "\n")
                f.write(f"Fecha: {timestamp}\n")
                f.write(f"URL: {info_general['url']}\n")
                f.write(f"Título: {info_general['titulo']}\n")
                f.write(f"\n{'='*80}\n")
                f.write("RESUMEN DE IFRAMES\n")
                f.write(f"{'='*80}\n")
                f.write(f"Total de iframes: {len(iframes_info)}\n\n")

                iframe_correcto = None
                for iframe in iframes_info:
                    status = "✅" if iframe.get('accesible') else "❌"
                    f.write(f"{status} Iframe #{iframe['indice']}: {iframe['id']}\n")

                    if iframe.get('tiene_tipodoc'):
                        f.write(f"   ⭐⭐⭐ ESTE ES EL IFRAME CORRECTO ⭐⭐⭐\n")
                        iframe_correcto = iframe

                if iframe_correcto:
                    f.write(f"\n{'='*80}\n")
                    f.write("🎯 IFRAME CORRECTO IDENTIFICADO\n")
                    f.write(f"{'='*80}\n")
                    f.write(f"Índice: {iframe_correcto['indice']}\n")
                    f.write(f"ID: {iframe_correcto['id']}\n")
                    f.write(f"NAME: {iframe_correcto['name']}\n")
                    f.write(f"\n⚠️ USAR ESTE ID PARA CORREGIR EL CÓDIGO:\n")
                    f.write(f"   self.driver.switch_to.frame('{iframe_correcto['id']}')\n")
                    f.write(f"   O BIEN:\n")
                    f.write(f"   self.driver.switch_to.frame({iframe_correcto['indice']})\n")
                else:
                    f.write(f"\n⚠️ NO SE ENCONTRÓ EL IFRAME CON EL CAMPO 'tipodoc'\n")

                f.write(f"\n{'='*80}\n")
                f.write("ARCHIVOS GENERADOS\n")
                f.write(f"{'='*80}\n")
                f.write("01_info_general.json - Información general de la página\n")
                f.write("02_html_principal.html - HTML completo de la página principal\n")
                f.write("03_iframes_detalle.json - Información detallada de iframes (JSON)\n")
                f.write("03_iframes_reporte.txt - Reporte legible de iframes\n")
                f.write("04_selectores_principal.json - Selectores de la página principal\n")
                f.write("05_screenshot.png - Captura de pantalla\n")
                f.write("iframe_X_*.html - HTML de cada iframe accesible\n")

            self.log(f"\n{'='*80}")
            self.log(f"✅ DIAGNÓSTICO COMPLETADO")
            self.log(f"{'='*80}")
            self.log(f"📁 Archivos guardados en: {os.path.abspath(carpeta_diagnostico)}")

            # Mostrar iframe correcto si se encontró
            iframe_correcto = next((ifr for ifr in iframes_info if ifr.get('tiene_tipodoc')), None)
            if iframe_correcto:
                self.log(f"\n🎯 IFRAME CORRECTO ENCONTRADO:")
                self.log(f"   ID: {iframe_correcto['id']}")
                self.log(f"   NAME: {iframe_correcto['name']}")
                self.log(f"   Índice: {iframe_correcto['indice']}")

            messagebox.showinfo(
                "Diagnóstico Completado",
                f"✅ Diagnóstico exportado exitosamente\n\n"
                f"📁 Carpeta: {carpeta_diagnostico}\n\n"
                f"Revisa el archivo:\n00_REPORTE_RESUMEN.txt"
            )

            return os.path.abspath(carpeta_diagnostico)

        except Exception as e:
            self.log(f"❌ Error en diagnóstico: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            return None

    # ============================================
    # PROCESO PRINCIPAL
    # ============================================
    
    def volver_a_registro_denuncias(self):
        """
        🔄 Volver a hacer clic en "Registro de Denuncias" en el menú lateral

        Esta función se usa después de completar una denuncia para empezar otra.
        NO cierra ni abre nuevas ventanas - solo hace clic en el menú.
        """
        self.log("\n🔄 Volviendo a 'Registro de Denuncias' para siguiente denuncia...")

        try:
            # Volver al contexto principal
            self.driver.switch_to.default_content()
            time.sleep(1)

            # Intentar hacer clic en "Registro de Denuncias" con múltiples estrategias
            for intento in range(1, 4):
                self.log(f"  → Intento {intento}/3 para clic en 'Registro de Denuncias'...")

                # Estrategia 1: JavaScript NUCLEAR - buscar en todos los frames
                try:
                    js_clic = """
                    (function() {
                        function buscarYClicRegistro(win, nivel) {
                            if (nivel > 10) return false;
                            try {
                                // Buscar por ID exacto
                                var elem = win.document.getElementById('nivel4_5_5_2_10');
                                if (elem) { elem.click(); return true; }

                                // Buscar por texto en elementos nivel4
                                var nivel4s = win.document.querySelectorAll('li.nivel4, [class*="nivel4"]');
                                for (var i = 0; i < nivel4s.length; i++) {
                                    var texto = (nivel4s[i].innerText || nivel4s[i].textContent || '').trim();
                                    if (texto.indexOf('Registro de Denuncias') !== -1) {
                                        nivel4s[i].click();
                                        return true;
                                    }
                                }

                                // Buscar cualquier elemento con ese texto
                                var todos = win.document.querySelectorAll('span, a, li');
                                for (var i = 0; i < todos.length; i++) {
                                    var texto = (todos[i].innerText || todos[i].textContent || '').trim();
                                    if (texto === 'Registro de Denuncias' || texto.indexOf('Registro de Denuncias') === 0) {
                                        todos[i].click();
                                        return true;
                                    }
                                }

                                // Buscar en frames hijos
                                for (var i = 0; i < win.frames.length; i++) {
                                    try { if (buscarYClicRegistro(win.frames[i], nivel + 1)) return true; } catch(e) {}
                                }
                            } catch(e) {}
                            return false;
                        }
                        return buscarYClicRegistro(window.top, 0);
                    })();
                    """
                    resultado = self.driver.execute_script(js_clic)
                    if resultado:
                        self.log("  ✅ Clic en 'Registro de Denuncias' exitoso (JavaScript)")
                        time.sleep(3)
                        return True
                except:
                    pass

                # Estrategia 2: Selenium - buscar por ID
                try:
                    elemento = self.driver.find_element(By.ID, "nivel4_5_5_2_10")
                    self.driver.execute_script("arguments[0].click();", elemento)
                    self.log("  ✅ Clic en 'Registro de Denuncias' exitoso (Selenium ID)")
                    time.sleep(3)
                    return True
                except:
                    pass

                # Estrategia 3: Selenium - buscar por XPATH
                try:
                    elemento = self.driver.find_element(By.XPATH,
                        "//li[contains(@class,'nivel4')]//span[contains(text(),'Registro de Denuncias')]")
                    self.driver.execute_script("arguments[0].click();", elemento)
                    self.log("  ✅ Clic en 'Registro de Denuncias' exitoso (Selenium XPATH)")
                    time.sleep(3)
                    return True
                except:
                    pass

                time.sleep(2)

            self.log("  ⚠️ No se pudo volver a 'Registro de Denuncias' - continuando...")
            return False

        except Exception as e:
            self.log(f"  ⚠️ Error al volver a Registro: {str(e)[:50]}")
            return False

    def procesar_una_denuncia(self, datos_fila, numero_fila):
        try:
            if not self.interfaz.proceso_activo:
                return False

            self.log(f"\n{'='*50}")
            self.log(f"📋 PROCESANDO DENUNCIA #{numero_fila}")
            self.log(f"{'='*50}")

            # Navegar al formulario
            if not self.navegar_a_formulario_registro():
                self.log("❌ Fallo en navegación al formulario")
                self.denuncias_fallidas += 1
                return False

            if not self.interfaz.proceso_activo:
                self.log("⚠️ Proceso cancelado por usuario")
                return False

            # Sección 1
            self.log("\n🔄 Iniciando llenado de Sección 1...")
            resultado_seccion1 = self.llenar_seccion1_identificacion(datos_fila)
            self.log(f"📊 Resultado Sección 1: {resultado_seccion1}")

            if not resultado_seccion1:
                self.log("❌ Fallo en Sección 1 - Identificación")
                self.denuncias_fallidas += 1
                return False

            if not self.interfaz.proceso_activo:
                return False

            # Sección 2
            if not self.llenar_seccion2_atencion_denuncias(datos_fila):
                return False

            if not self.interfaz.proceso_activo:
                return False

            # Sección 3 (incluye guardar PDF)
            if not self.llenar_seccion3_identificacion_denunciante(datos_fila):
                return False

            self.log(f"🎉 ¡DENUNCIA #{numero_fila} REGISTRADA Y GUARDADA EXITOSAMENTE!")
            self.denuncias_exitosas += 1

            # ═══════════════════════════════════════════════════════════════
            # VOLVER A "REGISTRO DE DENUNCIAS" PARA LA SIGUIENTE DENUNCIA
            # NO cerramos la ventana - volvemos al menú lateral
            # ═══════════════════════════════════════════════════════════════
            self.log("\n🔄 Preparando para siguiente denuncia...")
            time.sleep(2)

            # Volver a hacer clic en "Registro de Denuncias"
            self.volver_a_registro_denuncias()
            time.sleep(2)

            return True

        except Exception as e:
            self.log(f"❌ Error en denuncia #{numero_fila}: {str(e)}")
            self.denuncias_fallidas += 1

            # Intentar recuperarse para la siguiente denuncia
            try:
                self.log("  🔄 Intentando recuperarse para siguiente denuncia...")
                self.driver.switch_to.default_content()
                time.sleep(1)
                self.volver_a_registro_denuncias()
            except:
                pass

            return False
    
    def ejecutar(self):
        try:
            self.log("="*50)
            self.log("🤖 INICIANDO PROCESO")
            self.log("="*50)
            
            # Leer Excel
            self.log(f"📂 Leyendo: {os.path.basename(self.archivo_excel)}")
            df = pd.read_excel(self.archivo_excel)
            total = len(df)
            self.log(f"✅ {total} denuncias encontradas\n")
            
            # Iniciar navegador
            if not self.iniciar_navegador():
                return
            
            # Login
            if not self.hacer_login():
                self.cerrar_navegador()
                return
            
            # Procesar cada denuncia
            for index, fila in df.iterrows():
                if not self.interfaz.proceso_activo:
                    self.log("\n⚠️ PROCESO CANCELADO")
                    break
                
                numero_fila = index + 2
                self.procesar_una_denuncia(fila, numero_fila)
                time.sleep(2)
            
            # Resumen
            self.log("\n" + "="*50)
            self.log("📊 RESUMEN FINAL")
            self.log("="*50)
            self.log(f"✅ Exitosas: {self.denuncias_exitosas}/{total}")
            self.log(f"❌ Fallidas: {self.denuncias_fallidas}/{total}")
            if total > 0:
                tasa = (self.denuncias_exitosas/total)*100
                self.log(f"📈 Tasa de éxito: {tasa:.2f}%")
            self.log("="*50)
            
            self.log("\nCerrando navegador...")
            time.sleep(3)
            self.cerrar_navegador()
            
            self.log("\n🏁 ¡PROCESO COMPLETADO!")
            
            messagebox.showinfo(
                "Proceso Completado",
                f"✅ Exitosas: {self.denuncias_exitosas}\n"
                f"❌ Fallidas: {self.denuncias_fallidas}\n"
                f"📊 Total: {total}"
            )
            
        except Exception as e:
            self.log(f"\n❌ ERROR CRÍTICO: {str(e)}")
            messagebox.showerror("Error", f"Error:\n{str(e)}")
            self.cerrar_navegador()


# ============================================
# PUNTO DE ENTRADA
# ============================================

# ============================================
# INTERFAZ GRÁFICA MEJORADA V3
# ============================================
class InterfazBotMejorada:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Bot SUNAT - Registro de Denuncias")
        self.ventana.geometry("950x750")  # Aumentado para mostrar todos los botones
        self.ventana.resizable(True, True)  # Permitir redimensionar
        self.ventana.configure(bg="#f0f4f8")

        # Variables
        self.ruta_archivo = tk.StringVar()
        self.usuario = tk.StringVar()
        self.password = tk.StringVar()
        self.bot = None
        self.proceso_activo = False
        self.hilo_proceso = None

        # Colores profesionales
        self.COLOR_PRIMARIO = "#1e40af"  # Azul profesional
        self.COLOR_SECUNDARIO = "#3b82f6"  # Azul claro
        self.COLOR_EXITO = "#059669"  # Verde
        self.COLOR_PELIGRO = "#dc2626"  # Rojo
        self.COLOR_INFO = "#0891b2"  # Cyan
        self.COLOR_ADVERTENCIA = "#d97706"  # Naranja
        self.COLOR_FONDO = "#f0f4f8"  # Gris claro
        self.COLOR_TARJETA = "#ffffff"  # Blanco

        self.crear_interfaz_mejorada()

        # Mensaje de bienvenida en consola
        self.escribir_consola("="*60 + "\n")
        self.escribir_consola("🏛️ BOT SUNAT - SISTEMA DE REGISTRO DE DENUNCIAS\n")
        self.escribir_consola("="*60 + "\n")
        self.escribir_consola("✅ Interfaz cargada correctamente\n")
        self.escribir_consola("\n📋 BOTONES DISPONIBLES:\n")
        self.escribir_consola("  1. ▶️ INICIAR PROCESO AUTOMÁTICO\n")
        self.escribir_consola("  2. ⏹️ CANCELAR PROCESO\n")
        self.escribir_consola("="*60 + "\n\n")

    def crear_interfaz_mejorada(self):
        """Crea interfaz profesional y moderna"""

        # ═══════════════════════════════════════
        # HEADER CON GRADIENTE (COMPACTO)
        # ═══════════════════════════════════════
        frame_header = tk.Frame(self.ventana, bg=self.COLOR_PRIMARIO, height=50)
        frame_header.pack(fill=tk.X)
        frame_header.pack_propagate(False)

        label_titulo = tk.Label(
            frame_header,
            text="🏛️ SISTEMA DE REGISTRO DE DENUNCIAS",
            font=("Segoe UI", 13, "bold"),
            bg=self.COLOR_PRIMARIO,
            fg="white"
        )
        label_titulo.pack(pady=12)

        # ═══════════════════════════════════════
        # CONTENEDOR PRINCIPAL COMPACTO
        # ═══════════════════════════════════════
        frame_principal = tk.Frame(self.ventana, bg=self.COLOR_FONDO)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # ═══════════════════════════════════════
        # FILA 1: CREDENCIALES + ARCHIVO (HORIZONTAL)
        # ═══════════════════════════════════════
        frame_fila_superior = tk.Frame(frame_principal, bg=self.COLOR_FONDO)
        frame_fila_superior.pack(fill=tk.X, pady=(0, 8))

        # ═══════════════════════════════════════
        # TARJETA 1: CREDENCIALES (IZQUIERDA)
        # ═══════════════════════════════════════
        frame_credenciales = tk.Frame(frame_fila_superior, bg=self.COLOR_TARJETA, relief=tk.RAISED, bd=1)
        frame_credenciales.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        label_seccion1 = tk.Label(
            frame_credenciales,
            text="🔐  CREDENCIALES DE ACCESO",
            font=("Segoe UI", 9, "bold"),
            bg=self.COLOR_TARJETA,
            fg=self.COLOR_PRIMARIO,
            anchor="w"
        )
        label_seccion1.pack(fill=tk.X, padx=10, pady=(8, 5))

        # Separador
        tk.Frame(frame_credenciales, height=1, bg="#e5e7eb").pack(fill=tk.X, padx=10)

        # Grid interno para campos
        frame_campos_cred = tk.Frame(frame_credenciales, bg=self.COLOR_TARJETA)
        frame_campos_cred.pack(fill=tk.X, padx=10, pady=8)

        # Usuario
        tk.Label(
            frame_campos_cred,
            text="Usuario:",
            font=("Segoe UI", 8),
            bg=self.COLOR_TARJETA,
            fg="#374151"
        ).grid(row=0, column=0, sticky="e", padx=5, pady=4)

        entry_usuario = tk.Entry(
            frame_campos_cred,
            textvariable=self.usuario,
            font=("Segoe UI", 8),
            width=25,
            relief=tk.SOLID,
            bd=1
        )
        entry_usuario.grid(row=0, column=1, sticky="ew", padx=5, pady=4)

        # Contraseña
        tk.Label(
            frame_campos_cred,
            text="Contraseña:",
            font=("Segoe UI", 8),
            bg=self.COLOR_TARJETA,
            fg="#374151"
        ).grid(row=1, column=0, sticky="e", padx=5, pady=4)

        entry_password = tk.Entry(
            frame_campos_cred,
            textvariable=self.password,
            font=("Segoe UI", 8),
            width=25,
            show="●",
            relief=tk.SOLID,
            bd=1
        )
        entry_password.grid(row=1, column=1, sticky="ew", padx=5, pady=4)

        # Configurar columna para que se expanda
        frame_campos_cred.columnconfigure(1, weight=1)

        # ═══════════════════════════════════════
        # TARJETA 2: ARCHIVO (DERECHA)
        # ═══════════════════════════════════════
        frame_archivo = tk.Frame(frame_fila_superior, bg=self.COLOR_TARJETA, relief=tk.RAISED, bd=1)
        frame_archivo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        label_seccion2 = tk.Label(
            frame_archivo,
            text="📂  ARCHIVO DE DENUNCIAS",
            font=("Segoe UI", 9, "bold"),
            bg=self.COLOR_TARJETA,
            fg=self.COLOR_PRIMARIO,
            anchor="w"
        )
        label_seccion2.pack(fill=tk.X, padx=10, pady=(8, 5))

        tk.Frame(frame_archivo, height=1, bg="#e5e7eb").pack(fill=tk.X, padx=10)

        frame_campos_archivo = tk.Frame(frame_archivo, bg=self.COLOR_TARJETA)
        frame_campos_archivo.pack(fill=tk.X, padx=10, pady=8)

        tk.Label(
            frame_campos_archivo,
            text="Archivo:",
            font=("Segoe UI", 8),
            bg=self.COLOR_TARJETA,
            fg="#374151"
        ).grid(row=0, column=0, sticky="e", padx=5, pady=8)

        entry_archivo = tk.Entry(
            frame_campos_archivo,
            textvariable=self.ruta_archivo,
            font=("Segoe UI", 8),
            width=20,
            state="readonly",
            relief=tk.SOLID,
            bd=1
        )
        entry_archivo.grid(row=0, column=1, sticky="ew", padx=5, pady=8)

        btn_examinar = tk.Button(
            frame_campos_archivo,
            text="📁",
            command=self.seleccionar_archivo,
            font=("Segoe UI", 9, "bold"),
            bg=self.COLOR_SECUNDARIO,
            fg="white",
            cursor="hand2",
            width=3,
            relief=tk.FLAT,
            bd=0,
            padx=3,
            pady=3
        )
        btn_examinar.grid(row=0, column=2, padx=5, pady=8)

        # Configurar columna para que se expanda
        frame_campos_archivo.columnconfigure(1, weight=1)

        # ═══════════════════════════════════════
        # TARJETA 3: REGISTRO DE ACTIVIDAD (COMPACTO)
        # ═══════════════════════════════════════
        frame_consola = tk.Frame(frame_principal, bg=self.COLOR_TARJETA, relief=tk.RAISED, bd=1)
        frame_consola.pack(fill=tk.X, expand=False, pady=(0, 8))

        label_seccion3 = tk.Label(
            frame_consola,
            text="📋  REGISTRO DE ACTIVIDAD",
            font=("Segoe UI", 9, "bold"),
            bg=self.COLOR_TARJETA,
            fg=self.COLOR_PRIMARIO,
            anchor="w"
        )
        label_seccion3.pack(fill=tk.X, padx=10, pady=(8, 5))

        tk.Frame(frame_consola, height=1, bg="#e5e7eb").pack(fill=tk.X, padx=10)

        self.consola = scrolledtext.ScrolledText(
            frame_consola,
            width=95,
            height=5,
            font=("Consolas", 8),
            bg="#1e293b",
            fg="#e2e8f0",
            state="disabled",
            relief=tk.FLAT,
            padx=8,
            pady=6
        )
        self.consola.pack(fill=tk.BOTH, expand=False, padx=10, pady=8)

        # ═══════════════════════════════════════
        # BOTONES DE ACCIÓN PRINCIPALES (COMPACTOS)
        # ═══════════════════════════════════════
        frame_botones_container = tk.Frame(frame_principal, bg=self.COLOR_TARJETA, relief=tk.RAISED, bd=2)
        frame_botones_container.pack(fill=tk.X, pady=(0, 5))

        # Título de sección de botones
        label_botones = tk.Label(
            frame_botones_container,
            text="⚙️  ACCIONES DISPONIBLES",
            font=("Segoe UI", 9, "bold"),
            bg=self.COLOR_TARJETA,
            fg=self.COLOR_PRIMARIO,
            anchor="w"
        )
        label_botones.pack(fill=tk.X, padx=10, pady=(8, 5))

        tk.Frame(frame_botones_container, height=1, bg="#e5e7eb").pack(fill=tk.X, padx=10)

        # Frame para los 3 botones principales (una sola fila)
        frame_botones = tk.Frame(frame_botones_container, bg=self.COLOR_TARJETA)
        frame_botones.pack(fill=tk.X, padx=10, pady=10)

        # Botón 1: INICIAR PROCESO AUTOMÁTICO
        self.btn_iniciar = tk.Button(
            frame_botones,
            text="▶️ INICIAR PROCESO\nAUTOMÁTICO",
            command=self.iniciar_proceso,
            font=("Segoe UI", 9, "bold"),
            bg=self.COLOR_EXITO,
            fg="white",
            cursor="hand2",
            width=20,
            height=2,
            relief=tk.RAISED,
            bd=2,
            activebackground="#047857"
        )
        self.btn_iniciar.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.BOTH)

        # Botón 2: CANCELAR PROCESO
        self.btn_cancelar = tk.Button(
            frame_botones,
            text="⏹️ CANCELAR\nPROCESO",
            command=self.cancelar_proceso,
            font=("Segoe UI", 9, "bold"),
            bg=self.COLOR_PELIGRO,
            fg="white",
            cursor="hand2",
            width=20,
            height=2,
            state="disabled",
            relief=tk.RAISED,
            bd=2,
            activebackground="#b91c1c"
        )
        self.btn_cancelar.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.BOTH)

        # ═══════════════════════════════════════
        # BARRA DE ESTADO (COMPACTA)
        # ═══════════════════════════════════════
        self.label_estado = tk.Label(
            self.ventana,
            text="●  Estado: Esperando inicio del proceso...",
            font=("Segoe UI", 8),
            bg="#ffffff",
            fg="#6b7280",
            anchor="w",
            padx=10,
            relief=tk.RAISED,
            bd=1
        )
        self.label_estado.pack(side=tk.BOTTOM, fill=tk.X)

    def seleccionar_archivo(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo Excel de denuncias",
            filetypes=[
                ("Archivos Excel", "*.xlsx *.xls"),
                ("Todos los archivos", "*.*")
            ]
        )
        if archivo:
            self.ruta_archivo.set(archivo)
            self.escribir_consola(f"✅ Archivo seleccionado: {os.path.basename(archivo)}\n")

    def escribir_consola(self, mensaje):
        self.consola.config(state="normal")
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.consola.insert(tk.END, f"[{timestamp}] {mensaje}")
        self.consola.see(tk.END)
        self.consola.config(state="disabled")
        self.ventana.update()

    def limpiar_consola(self):
        self.consola.config(state="normal")
        self.consola.delete(1.0, tk.END)
        self.consola.config(state="disabled")

    def validar_campos(self, requiere_excel=True):
        if not self.usuario.get().strip():
            messagebox.showerror("Error", "Por favor ingrese el usuario")
            return False

        if not self.password.get().strip():
            messagebox.showerror("Error", "Por favor ingrese la contraseña")
            return False

        if requiere_excel:
            if not self.ruta_archivo.get().strip():
                messagebox.showerror("Error", "Por favor seleccione un archivo Excel")
                return False

            if not os.path.exists(self.ruta_archivo.get()):
                messagebox.showerror("Error", "El archivo seleccionado no existe")
                return False

        return True

    def iniciar_proceso(self):
        """Inicia el proceso automático normal"""
        if not self.validar_campos():
            return

        respuesta = messagebox.askyesno(
            "Confirmar",
            "¿Desea iniciar el proceso AUTOMÁTICO de registro de denuncias?\n\n"
            "El bot procesará todas las denuncias del Excel de forma automática.\n\n"
            "Si desea un modo manual asistido, use el otro botón."
        )

        if not respuesta:
            return

        self.limpiar_consola()
        self.btn_iniciar.config(state="disabled")
        self.btn_cancelar.config(state="normal")
        self.proceso_activo = True
        self.label_estado.config(text="●  Estado: Proceso automático en ejecución...", fg=self.COLOR_EXITO)

        # Ejecutar bot en hilo separado
        self.hilo_proceso = threading.Thread(target=self._ejecutar_bot_automatico, daemon=True)
        self.hilo_proceso.start()

    def cancelar_proceso(self):
        respuesta = messagebox.askyesno(
            "Confirmar Cancelación",
            "¿Está seguro que desea cancelar el proceso?"
        )

        if respuesta:
            self.proceso_activo = False
            self.escribir_consola("\n⚠️ CANCELANDO PROCESO...\n")
            self.label_estado.config(text="●  Estado: Proceso cancelado", fg=self.COLOR_PELIGRO)

            # Cerrar navegador si existe
            if self.bot and hasattr(self.bot, 'driver') and self.bot.driver:
                try:
                    self.bot.driver.quit()
                except:
                    pass

            self.btn_iniciar.config(state="normal")
            self.btn_cancelar.config(state="disabled")

    def _ejecutar_bot_automatico(self):
        """Hilo que ejecuta el bot automático completo"""
        try:
            self.escribir_consola("🚀 Iniciando proceso automático...\n")
            self.escribir_consola("="*60 + "\n")

            # Crear instancia del bot
            self.bot = BotDenunciasSUNAT(
                archivo_excel=self.ruta_archivo.get(),
                usuario=self.usuario.get(),
                password=self.password.get(),
                interfaz=self
            )

            # Ejecutar bot
            self.bot.ejecutar()

            # Mostrar resumen final
            if hasattr(self.bot, 'denuncias_exitosas'):
                self.escribir_consola("\n" + "="*60 + "\n")
                self.escribir_consola(f"✅ PROCESO COMPLETADO\n")
                self.escribir_consola(f"   Denuncias exitosas: {self.bot.denuncias_exitosas}\n")
                if hasattr(self.bot, 'denuncias_fallidas'):
                    self.escribir_consola(f"   Denuncias fallidas: {self.bot.denuncias_fallidas}\n")
                self.escribir_consola("="*60 + "\n")

                self.label_estado.config(
                    text=f"●  Estado: Completado - {self.bot.denuncias_exitosas} denuncias exitosas",
                    fg=self.COLOR_EXITO
                )
            else:
                self.label_estado.config(text="●  Estado: Proceso finalizado", fg="#6b7280")

        except Exception as e:
            self.escribir_consola(f"\n❌ ERROR CRÍTICO: {str(e)}\n")
            messagebox.showerror("Error", f"Error crítico en el bot:\n{str(e)}")
            self.label_estado.config(text="●  Estado: Error en proceso", fg=self.COLOR_PELIGRO)

        finally:
            self.btn_iniciar.config(state="normal")
            self.btn_cancelar.config(state="disabled")
            self.proceso_activo = False

    def ejecutar(self):
        self.ventana.mainloop()



# ============================================
# PUNTO DE ENTRADA
# ============================================
if __name__ == "__main__":
    app = InterfazBotMejorada()
    app.ejecutar()
