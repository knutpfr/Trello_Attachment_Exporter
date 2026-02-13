import json
import os
import requests
from pathlib import Path
import sqlite3
import zipfile
import shutil


# Konfiguration - Pfade relativ zum Skript-Verzeichnis
SCRIPT_DIR = Path(__file__).parent
INPUT_FILE = SCRIPT_DIR / "import_export.json"
OUTPUT_FOLDER = SCRIPT_DIR / "Output"

# 🍪 MANUELLE COOKIES - optional
# Wenn Browser-Autodetect nicht funktioniert, hier eintragen
MANUAL_COOKIES = {
    "cloud.session.token": "YOUR_TOKEN_HERE",
    "dsc": "YOUR_TOKEN_HERE",
    "aaId": "YOUR_TOKEN_HERE",
    "idMember": "YOUR_TOKEN_HERE",
    "atl-bsc-consent-token": "YOUR_TOKEN_HERE",
}


# Browser-Cookies auslesen
def get_browser_cookies():
    """
    Versuche Cookies aus Chrome oder Firefox zu laden
    """
    cookies = {}
    
    # Chrome Cookie Datei (Windows)
    chrome_path = Path.home() / "AppData/Local/Google/Chrome/User Data/Default/Cookies"
    
    # Firefox Cookie Datei (Windows)
    firefox_path = Path.home() / "AppData/Roaming/Mozilla/Firefox"
    
    # Versuche Chrome
    if chrome_path.exists():
        try:
            print("🔍 Lade Cookies aus Chrome...")
            conn = sqlite3.connect(chrome_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name, value FROM cookies WHERE host_key LIKE '%trello%'")
            
            for name, value in cursor.fetchall():
                cookies[name] = value
            conn.close()
            
            if cookies:
                print(f"   ✓ {len(cookies)} Trello-Cookies gefunden")
                return cookies
        except Exception as e:
            print(f"   ⚠ Chrome: {e}")
    
    # Versuche Firefox
    if firefox_path.exists():
        try:
            print("🔍 Lade Cookies aus Firefox...")
            profiles = list(firefox_path.glob("*.default-release"))
            if not profiles:
                profiles = list(firefox_path.glob("*.default"))
            
            if profiles:
                cookie_file = profiles[0] / "cookies.sqlite"
                if cookie_file.exists():
                    conn = sqlite3.connect(cookie_file)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name, value FROM moz_cookies WHERE host LIKE '%trello%'")
                    
                    for name, value in cursor.fetchall():
                        cookies[name] = value
                    conn.close()
                    
                    if cookies:
                        print(f"   ✓ {len(cookies)} Trello-Cookies gefunden")
                        return cookies
        except Exception as e:
            print(f"   ⚠ Firefox: {e}")
    
    return cookies


def load_trello_export(file_path):
    """
    Lade die Trello Export JSON Datei
    """
    try:
        with open(str(file_path), 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Datei nicht gefunden: {file_path}")
        exit(1)
    except json.JSONDecodeError:
        print(f"❌ JSON Fehler in: {file_path}")
        exit(1)


def create_folder_structure(board_name):
    """
    Erstelle die Ordnerstruktur für Output/BoardName/
    """
    board_path = Path(OUTPUT_FOLDER) / board_name
    board_path.mkdir(parents=True, exist_ok=True)
    print(f"✓ Board-Ordner erstellt: {board_path}")
    return board_path


def create_list_folders(board_path, lists):
    """
    Erstelle Unterordner für jede Liste
    """
    list_paths = {}
    for list_obj in lists:
        list_name = list_obj['name']
        list_id = list_obj['id']
        list_path = board_path / list_name
        list_path.mkdir(parents=True, exist_ok=True)
        list_paths[list_id] = list_path
        print(f"  ✓ Liste-Ordner erstellt: {list_path}")
    
    return list_paths


def download_file(url, save_path, cookies):
    """
    Lade eine Datei mit Browser-Cookies herunter
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, timeout=10, stream=True, cookies=cookies, headers=headers)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"    ⚠ Download fehlgeschlagen: {e}")
        return False
    except IOError as e:
        print(f"    ⚠ Fehler beim Speichern: {e}")
        return False


def process_card_attachments(card, list_path, cookies):
    """
    Verarbeite alle Attachments einer Karte
    """
    card_name = card['name']
    attachments = card.get('attachments', [])
    
    if not attachments:
        return 0
    
    downloaded = 0
    for attachment in attachments:
        url = attachment['url']
        file_name = attachment['name']
        
        # Erstelle neuen Dateinamen: KartenName_OriginalName
        new_file_name = f"{card_name}_{file_name}"
        
        # Sanitize Filename
        new_file_name = "".join(c for c in new_file_name if c.isalnum() or c in (' ', '.', '-', '_'))
        
        file_path = list_path / new_file_name
        
        print(f"    ↓ {new_file_name}... ", end="", flush=True)
        
        if download_file(url, file_path, cookies):
            print(f"✓ ({file_path.stat().st_size / 1024:.1f} KB)")
            downloaded += 1
        else:
            print("✗")
    
    return downloaded


def create_zip_archive(folder_path, zip_name=None):
    """
    Packe den kompletten Output-Ordner in eine ZIP-Datei
    """
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        print(f"❌ Ordner nicht gefunden: {folder_path}")
        return None
    
    if zip_name is None:
        zip_name = folder_path.name
    
    zip_path = folder_path.parent / f"{zip_name}.zip"
    
    print(f"\n📦 Erstelle ZIP-Archiv: {zip_path.name}...")
    
    try:
        shutil.make_archive(str(zip_path.with_suffix('')), 'zip', folder_path.parent, folder_path.name)
        zip_size = zip_path.stat().st_size / (1024 * 1024)
        print(f"   ✓ ZIP erstellt: {zip_size:.2f} MB")
        
        # Lösche den Original-Ordner
        print(f"   🗑️  Lösche Original-Ordner...")
        shutil.rmtree(folder_path)
        print(f"   ✓ Original-Ordner gelöscht")
        
        return zip_path
    except Exception as e:
        print(f"❌ Fehler beim ZIP-Erstellen: {e}")
        return None


def main():
    """
    Hauptfunktion - orkestriere den kompletten Export
    """
    print("=" * 60)
    print("🚀 Trello Export Downloader (Cookie Authentifizierung)")
    print("=" * 60)
    
    # Cookies laden
    print("\n🔐 Authentifizierung:")
    cookies = get_browser_cookies()
    
    # Falls keine Cookies gefunden, nutze manuelle
    if not cookies and MANUAL_COOKIES:
        print(f"   💾 Nutze manuelle Cookies ({len(MANUAL_COOKIES)} Cookies)")
        cookies = MANUAL_COOKIES
    elif not cookies:
        print("\n❌ FEHLER: Keine Cookies gefunden!")
        print("📋 Lösungen:")
        print("   1. Chrome/Firefox sollte geöffnet sein (eingeloggt bei Trello)")
        print("   2. ODER: Schließe Chrome/Firefox und führe den Skript erneut aus")
        print("   3. ODER: Manuelle Cookies in Zeile 18 eintragen")
        exit(1)
    
    # 1. Laden
    print("\n📂 Lade Trello Export...")
    trello_data = load_trello_export(INPUT_FILE)
    
    board_name = trello_data['name']
    lists = trello_data['lists']
    cards = trello_data['cards']
    
    print(f"✓ Board: {board_name}")
    print(f"✓ Listen: {len(lists)}")
    print(f"✓ Karten: {len(cards)}")
    
    # 2. Ordnerstruktur erstellen
    print("\n📁 Erstelle Ordnerstruktur...")
    board_path = create_folder_structure(board_name)
    list_paths = create_list_folders(board_path, lists)
    
    # 3. Dateien herunterladen
    print("\n⬇️  Lade Dateien herunter...")
    total_downloads = 0
    
    for card in cards:
        card_name = card['name']
        list_id = card['idList']
        
        if list_id not in list_paths:
            print(f"  ⚠ Karte '{card_name}' hat ungültige Liste ID: {list_id}")
            continue
        
        list_path = list_paths[list_id]
        print(f"  Karte: {card_name}")
        
        downloads = process_card_attachments(card, list_path, cookies)
        total_downloads += downloads
    
    # 4. ZIP-Archiv erstellen
    zip_path = create_zip_archive(board_path)
    
    # 5. Zusammenfassung
    print("\n" + "=" * 60)
    print(f"✅ Fertig! {total_downloads} Dateien heruntergeladen")
    if zip_path:
        print(f"📦 ZIP-Archiv: {zip_path.name}")
        print(f"📍 Speicherort: {zip_path.absolute()}")
    else:
        print(f"📍 Speicherort: {board_path.absolute()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
