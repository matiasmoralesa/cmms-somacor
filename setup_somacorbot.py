#!/usr/bin/env python3
"""
Script de configuración rápida para Somacorbot
"""
import requests
import sys

BOT_TOKEN = "8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def get_bot_info():
    """Obtener información del bot"""
    print("📱 Obteniendo información del bot...")
    response = requests.get(f"{API_URL}/getMe")
    if response.json().get('ok'):
        bot_info = response.json()['result']
        print(f"✅ Bot: @{bot_info['username']}")
        print(f"   ID: {bot_info['id']}")
        print(f"   Nombre: {bot_info['first_name']}")
        return bot_info
    else:
        print("❌ Error al obtener información del bot")
        return None


def set_webhook(webhook_url):
    """Configurar webhook"""
    print(f"\n🌐 Configurando webhook: {webhook_url}")
    response = requests.post(
        f"{API_URL}/setWebhook",
        json={"url": webhook_url}
    )
    if response.json().get('ok'):
        print("✅ Webhook configurado exitosamente")
        return True
    else:
        print(f"❌ Error: {response.json().get('description')}")
        return False


def get_webhook_info():
    """Obtener información del webhook"""
    print("\n🔍 Verificando webhook...")
    response = requests.get(f"{API_URL}/getWebhookInfo")
    if response.json().get('ok'):
        info = response.json()['result']
        print(f"✅ URL: {info.get('url', 'No configurado')}")
        print(f"   Pendientes: {info.get('pending_update_count', 0)}")
        if info.get('last_error_message'):
            print(f"   ⚠️  Último error: {info['last_error_message']}")
        return info
    else:
        print("❌ Error al obtener información del webhook")
        return None


def delete_webhook():
    """Eliminar webhook"""
    print("\n🗑️  Eliminando webhook...")
    response = requests.post(f"{API_URL}/deleteWebhook")
    if response.json().get('ok'):
        print("✅ Webhook eliminado")
        return True
    else:
        print("❌ Error al eliminar webhook")
        return False


def send_test_message(chat_id):
    """Enviar mensaje de prueba"""
    print(f"\n📨 Enviando mensaje de prueba a {chat_id}...")
    message = """
🧪 <b>Mensaje de Prueba</b>

Este es un mensaje de prueba de Somacorbot.

Si ves este mensaje, el bot está funcionando correctamente.
"""
    response = requests.post(
        f"{API_URL}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": message.strip(),
            "parse_mode": "HTML"
        }
    )
    if response.json().get('ok'):
        print("✅ Mensaje enviado exitosamente")
        return True
    else:
        print(f"❌ Error: {response.json().get('description')}")
        return False


def main():
    """Función principal"""
    print("=" * 60)
    print("🤖 CONFIGURACIÓN DE SOMACORBOT")
    print("=" * 60)
    
    # Obtener info del bot
    bot_info = get_bot_info()
    if not bot_info:
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("OPCIONES:")
    print("=" * 60)
    print("1. Configurar webhook")
    print("2. Ver información del webhook")
    print("3. Eliminar webhook")
    print("4. Enviar mensaje de prueba")
    print("5. Salir")
    
    while True:
        print("\n" + "-" * 60)
        opcion = input("Selecciona una opción (1-5): ").strip()
        
        if opcion == "1":
            webhook_url = input("Ingresa la URL del webhook: ").strip()
            if webhook_url:
                set_webhook(webhook_url)
                get_webhook_info()
        
        elif opcion == "2":
            get_webhook_info()
        
        elif opcion == "3":
            confirmar = input("¿Estás seguro? (s/n): ").strip().lower()
            if confirmar == 's':
                delete_webhook()
        
        elif opcion == "4":
            chat_id = input("Ingresa el Chat ID: ").strip()
            if chat_id:
                send_test_message(chat_id)
        
        elif opcion == "5":
            print("\n👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción inválida")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Configuración cancelada")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
