"""
Pruebas Automatizadas de Frontend con Selenium - Sistema CMMS SOMACOR
Prueba la interfaz de usuario web del sistema
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
from datetime import datetime

# Configuración
FRONTEND_URL = "https://cmms-somacor-prod.web.app"
ADMIN_EMAIL = "admin@cmms.com"
ADMIN_PASSWORD = "admin123"

# Resultados de pruebas
test_results = []

def log_test(module: str, test_name: str, status: str, details: str = "", screenshot: str = ""):
    """Registrar resultado de prueba"""
    result = {
        "timestamp": datetime.now().isoformat(),
        "module": module,
        "test": test_name,
        "status": status,  # PASS, FAIL, SKIP
        "details": details,
        "screenshot": screenshot
    }
    test_results.append(result)
    
    icon = "✓" if status == "PASS" else "✗" if status == "FAIL" else "○"
    print(f"  {icon} {test_name}: {status}")
    if details:
        print(f"    {details}")

def setup_driver():
    """Configurar el driver de Chrome"""
    print("\nConfigurando navegador Chrome...")
    
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Descomentar para modo sin interfaz
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✓ Navegador configurado correctamente")
        return driver
    except Exception as e:
        print(f"✗ Error configurando navegador: {e}")
        return None

def take_screenshot(driver, name):
    """Tomar captura de pantalla"""
    try:
        filename = f"screenshot_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(filename)
        return filename
    except:
        return ""

def test_page_load(driver):
    """Módulo 1: Carga de Página"""
    print("\n" + "="*70)
    print("MÓDULO 1: CARGA DE PÁGINA")
    print("="*70)
    
    try:
        # Test 1.1: Cargar página principal
        start_time = time.time()
        driver.get(FRONTEND_URL)
        load_time = time.time() - start_time
        
        # Esperar a que la página cargue
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        screenshot = take_screenshot(driver, "page_load")
        
        if load_time < 5:
            log_test("Carga de Página", "Cargar página principal", "PASS", 
                    f"Tiempo de carga: {load_time:.2f}s", screenshot)
        else:
            log_test("Carga de Página", "Cargar página principal", "FAIL", 
                    f"Tiempo de carga muy lento: {load_time:.2f}s", screenshot)
        
        # Test 1.2: Verificar título de la página
        title = driver.title
        if "CMMS" in title or "Somacor" in title or title:
            log_test("Carga de Página", "Verificar título", "PASS", 
                    f"Título: {title}")
        else:
            log_test("Carga de Página", "Verificar título", "FAIL", 
                    f"Título no encontrado o vacío")
        
        # Test 1.3: Verificar que no hay errores de consola críticos
        logs = driver.get_log('browser')
        critical_errors = [log for log in logs if log['level'] == 'SEVERE']
        
        if len(critical_errors) == 0:
            log_test("Carga de Página", "Sin errores críticos de consola", "PASS")
        else:
            log_test("Carga de Página", "Sin errores críticos de consola", "FAIL", 
                    f"{len(critical_errors)} errores encontrados")
        
        return True
        
    except Exception as e:
        log_test("Carga de Página", "Cargar página principal", "FAIL", str(e))
        return False

def test_login(driver):
    """Módulo 2: Login y Autenticación"""
    print("\n" + "="*70)
    print("MÓDULO 2: LOGIN Y AUTENTICACIÓN")
    print("="*70)
    
    try:
        # Test 2.1: Encontrar formulario de login
        try:
            # Buscar campo de email
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email'], input[placeholder*='email' i]"))
            )
            log_test("Login", "Encontrar formulario de login", "PASS")
        except TimeoutException:
            screenshot = take_screenshot(driver, "login_form_not_found")
            log_test("Login", "Encontrar formulario de login", "FAIL", 
                    "No se encontró el formulario de login", screenshot)
            return False
        
        # Test 2.2: Ingresar credenciales
        try:
            email_field.clear()
            email_field.send_keys(ADMIN_EMAIL)
            
            # Buscar campo de password
            password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[name='password']")
            password_field.clear()
            password_field.send_keys(ADMIN_PASSWORD)
            
            screenshot = take_screenshot(driver, "credentials_entered")
            log_test("Login", "Ingresar credenciales", "PASS", "", screenshot)
        except Exception as e:
            screenshot = take_screenshot(driver, "credentials_error")
            log_test("Login", "Ingresar credenciales", "FAIL", str(e), screenshot)
            return False
        
        # Test 2.3: Hacer click en botón de login
        try:
            # Buscar botón de login con diferentes estrategias
            login_button = None
            
            # Estrategia 1: Por tipo submit
            try:
                login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            except:
                pass
            
            # Estrategia 2: Por texto del botón
            if not login_button:
                try:
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    for btn in buttons:
                        btn_text = btn.text.lower()
                        if any(word in btn_text for word in ['login', 'ingresar', 'entrar', 'iniciar']):
                            login_button = btn
                            break
                except:
                    pass
            
            # Estrategia 3: Por clase o ID común
            if not login_button:
                try:
                    login_button = driver.find_element(By.CSS_SELECTOR, 
                        ".btn-login, #login-button, .login-btn, button.primary")
                except:
                    pass
            
            if login_button:
                login_button.click()
                log_test("Login", "Click en botón de login", "PASS")
            else:
                screenshot = take_screenshot(driver, "login_button_not_found")
                log_test("Login", "Click en botón de login", "FAIL", 
                        "No se encontró el botón de login", screenshot)
                return False
                
        except Exception as e:
            screenshot = take_screenshot(driver, "login_button_error")
            log_test("Login", "Click en botón de login", "FAIL", str(e), screenshot)
            return False
        
        # Test 2.4: Verificar redirección después del login
        try:
            # Esperar a que cambie la URL o aparezca el dashboard
            WebDriverWait(driver, 10).until(
                lambda d: d.current_url != FRONTEND_URL or 
                         "dashboard" in d.current_url.lower() or
                         len(d.find_elements(By.CSS_SELECTOR, "nav, .navbar, header")) > 0
            )
            
            time.sleep(2)  # Esperar a que cargue completamente
            screenshot = take_screenshot(driver, "after_login")
            
            current_url = driver.current_url
            if current_url != FRONTEND_URL:
                log_test("Login", "Redirección después del login", "PASS", 
                        f"URL actual: {current_url}", screenshot)
                return True
            else:
                log_test("Login", "Redirección después del login", "FAIL", 
                        "No hubo redirección", screenshot)
                return False
                
        except TimeoutException:
            screenshot = take_screenshot(driver, "no_redirect")
            log_test("Login", "Redirección después del login", "FAIL", 
                    "Timeout esperando redirección", screenshot)
            return False
            
    except Exception as e:
        screenshot = take_screenshot(driver, "login_error")
        log_test("Login", "Proceso de login", "FAIL", str(e), screenshot)
        return False

def test_navigation(driver):
    """Módulo 3: Navegación"""
    print("\n" + "="*70)
    print("MÓDULO 3: NAVEGACIÓN")
    print("="*70)
    
    try:
        # Test 3.1: Verificar que existe menú de navegación
        try:
            nav = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "nav, .navbar, .sidebar, aside"))
            )
            log_test("Navegación", "Menú de navegación presente", "PASS")
        except TimeoutException:
            screenshot = take_screenshot(driver, "no_nav")
            log_test("Navegación", "Menú de navegación presente", "FAIL", 
                    "No se encontró menú de navegación", screenshot)
            return False
        
        # Test 3.2: Buscar enlaces principales
        menu_items = [
            ("Activos", ["activos", "assets", "vehiculos", "vehicles"]),
            ("Órdenes", ["ordenes", "orders", "trabajo", "work"]),
            ("Inventario", ["inventario", "inventory", "repuestos", "parts"]),
            ("Checklists", ["checklist", "check"]),
        ]
        
        found_items = 0
        for item_name, keywords in menu_items:
            try:
                # Buscar enlaces que contengan alguna de las palabras clave
                links = driver.find_elements(By.TAG_NAME, "a")
                found = False
                
                for link in links:
                    link_text = link.text.lower()
                    link_href = link.get_attribute("href") or ""
                    
                    if any(keyword in link_text or keyword in link_href.lower() for keyword in keywords):
                        found = True
                        found_items += 1
                        break
                
                if found:
                    log_test("Navegación", f"Enlace '{item_name}' encontrado", "PASS")
                else:
                    log_test("Navegación", f"Enlace '{item_name}' encontrado", "SKIP", 
                            "No se encontró en el menú")
                    
            except Exception as e:
                log_test("Navegación", f"Enlace '{item_name}' encontrado", "FAIL", str(e))
        
        # Test 3.3: Intentar navegar a sección de activos
        try:
            # Buscar y hacer click en enlace de activos
            activos_link = None
            links = driver.find_elements(By.TAG_NAME, "a")
            
            for link in links:
                link_text = link.text.lower()
                link_href = link.get_attribute("href") or ""
                
                if any(word in link_text or word in link_href.lower() 
                       for word in ["activos", "assets", "vehiculos", "vehicles"]):
                    activos_link = link
                    break
            
            if activos_link:
                activos_link.click()
                time.sleep(2)
                screenshot = take_screenshot(driver, "activos_page")
                log_test("Navegación", "Navegar a sección de activos", "PASS", "", screenshot)
            else:
                log_test("Navegación", "Navegar a sección de activos", "SKIP", 
                        "No se encontró enlace de activos")
                
        except Exception as e:
            screenshot = take_screenshot(driver, "nav_activos_error")
            log_test("Navegación", "Navegar a sección de activos", "FAIL", str(e), screenshot)
        
        return found_items > 0
        
    except Exception as e:
        log_test("Navegación", "Navegación general", "FAIL", str(e))
        return False

def test_data_display(driver):
    """Módulo 4: Visualización de Datos"""
    print("\n" + "="*70)
    print("MÓDULO 4: VISUALIZACIÓN DE DATOS")
    print("="*70)
    
    try:
        # Test 4.1: Verificar que se muestran datos en tablas o listas
        try:
            # Buscar tablas, listas o cards con datos
            data_elements = driver.find_elements(By.CSS_SELECTOR, 
                "table, .table, ul.list, .card, .data-grid, [role='grid']")
            
            if len(data_elements) > 0:
                screenshot = take_screenshot(driver, "data_display")
                log_test("Visualización", "Elementos de datos presentes", "PASS", 
                        f"{len(data_elements)} elementos encontrados", screenshot)
            else:
                screenshot = take_screenshot(driver, "no_data")
                log_test("Visualización", "Elementos de datos presentes", "FAIL", 
                        "No se encontraron elementos de datos", screenshot)
        except Exception as e:
            log_test("Visualización", "Elementos de datos presentes", "FAIL", str(e))
        
        # Test 4.2: Verificar que hay contenido de texto
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
            
            if len(body_text) > 100:
                log_test("Visualización", "Contenido de texto presente", "PASS", 
                        f"{len(body_text)} caracteres")
            else:
                log_test("Visualización", "Contenido de texto presente", "FAIL", 
                        "Muy poco contenido")
        except Exception as e:
            log_test("Visualización", "Contenido de texto presente", "FAIL", str(e))
        
        # Test 4.3: Verificar que no hay mensajes de error visibles
        try:
            error_elements = driver.find_elements(By.CSS_SELECTOR, 
                ".error, .alert-danger, [role='alert']")
            
            visible_errors = [e for e in error_elements if e.is_displayed()]
            
            if len(visible_errors) == 0:
                log_test("Visualización", "Sin mensajes de error visibles", "PASS")
            else:
                screenshot = take_screenshot(driver, "visible_errors")
                error_texts = [e.text for e in visible_errors]
                log_test("Visualización", "Sin mensajes de error visibles", "FAIL", 
                        f"{len(visible_errors)} errores: {error_texts}", screenshot)
        except Exception as e:
            log_test("Visualización", "Sin mensajes de error visibles", "FAIL", str(e))
        
        return True
        
    except Exception as e:
        log_test("Visualización", "Visualización de datos", "FAIL", str(e))
        return False

def test_responsive(driver):
    """Módulo 5: Diseño Responsive"""
    print("\n" + "="*70)
    print("MÓDULO 5: DISEÑO RESPONSIVE")
    print("="*70)
    
    viewports = [
        ("Desktop", 1920, 1080),
        ("Laptop", 1366, 768),
        ("Tablet", 768, 1024),
        ("Mobile", 375, 667)
    ]
    
    for name, width, height in viewports:
        try:
            driver.set_window_size(width, height)
            time.sleep(1)
            
            screenshot = take_screenshot(driver, f"responsive_{name.lower()}")
            
            # Verificar que no hay scroll horizontal
            has_horizontal_scroll = driver.execute_script(
                "return document.documentElement.scrollWidth > document.documentElement.clientWidth;"
            )
            
            if not has_horizontal_scroll:
                log_test("Responsive", f"Vista {name} ({width}x{height})", "PASS", 
                        "Sin scroll horizontal", screenshot)
            else:
                log_test("Responsive", f"Vista {name} ({width}x{height})", "FAIL", 
                        "Tiene scroll horizontal", screenshot)
                
        except Exception as e:
            log_test("Responsive", f"Vista {name}", "FAIL", str(e))
    
    # Restaurar tamaño original
    driver.set_window_size(1920, 1080)
    return True

def generate_report():
    """Generar reporte de pruebas"""
    print("\n" + "="*70)
    print("RESUMEN DE PRUEBAS FRONTEND")
    print("="*70)
    
    total = len(test_results)
    passed = len([r for r in test_results if r['status'] == 'PASS'])
    failed = len([r for r in test_results if r['status'] == 'FAIL'])
    skipped = len([r for r in test_results if r['status'] == 'SKIP'])
    
    print(f"\nTotal de pruebas: {total}")
    print(f"✓ Exitosas: {passed} ({passed/total*100:.1f}%)")
    print(f"✗ Fallidas: {failed} ({failed/total*100:.1f}%)")
    print(f"○ Omitidas: {skipped} ({skipped/total*100:.1f}%)")
    
    # Agrupar por módulo
    modules = {}
    for result in test_results:
        module = result['module']
        if module not in modules:
            modules[module] = {'PASS': 0, 'FAIL': 0, 'SKIP': 0}
        modules[module][result['status']] += 1
    
    print("\n" + "-"*70)
    print("RESULTADOS POR MÓDULO")
    print("-"*70)
    for module, stats in modules.items():
        total_mod = sum(stats.values())
        print(f"\n{module}:")
        print(f"  ✓ {stats['PASS']}/{total_mod} exitosas")
        if stats['FAIL'] > 0:
            print(f"  ✗ {stats['FAIL']}/{total_mod} fallidas")
        if stats['SKIP'] > 0:
            print(f"  ○ {stats['SKIP']}/{total_mod} omitidas")
    
    # Guardar reporte
    report = {
        "fecha_ejecucion": datetime.now().isoformat(),
        "sistema": "CMMS SOMACOR - Frontend",
        "frontend_url": FRONTEND_URL,
        "resumen": {
            "total": total,
            "exitosas": passed,
            "fallidas": failed,
            "omitidas": skipped,
            "porcentaje_exito": round(passed/total*100, 2) if total > 0 else 0
        },
        "modulos": modules,
        "pruebas": test_results
    }
    
    with open('reporte_selenium_frontend.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Reporte guardado en: reporte_selenium_frontend.json")
    print(f"✓ Capturas de pantalla guardadas en el directorio actual")

def main():
    """Ejecutar todas las pruebas"""
    print("="*70)
    print("PRUEBAS AUTOMATIZADAS DE FRONTEND - SISTEMA CMMS SOMACOR")
    print("="*70)
    print(f"Frontend: {FRONTEND_URL}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Configurar driver
    driver = setup_driver()
    if not driver:
        print("\n✗ No se pudo configurar el navegador. Abortando pruebas.")
        return
    
    try:
        # Ejecutar pruebas
        if test_page_load(driver):
            if test_login(driver):
                test_navigation(driver)
                test_data_display(driver)
                test_responsive(driver)
        
        # Generar reporte
        generate_report()
        
    except Exception as e:
        print(f"\n✗ Error durante las pruebas: {e}")
        take_screenshot(driver, "error_general")
    
    finally:
        # Cerrar navegador
        print("\nCerrando navegador...")
        driver.quit()
        print("✓ Navegador cerrado")
    
    print("\n" + "="*70)
    print("PRUEBAS COMPLETADAS")
    print("="*70)

if __name__ == "__main__":
    main()
