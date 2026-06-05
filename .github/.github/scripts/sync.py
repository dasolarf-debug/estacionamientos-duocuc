import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os
import subprocess
from datetime import datetime

def main():
    try:
        # ============================================
        # 1. AUTENTICACIÓN CON GOOGLE
        # ============================================
        credentials_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
        if not credentials_json:
            print("❌ Error: GOOGLE_SHEETS_CREDENTIALS no configurado")
            return
        
        credentials = json.loads(credentials_json)
        
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        auth = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
        client = gspread.authorize(auth)
        
        # ============================================
        # 2. ABRE LA HOJA DE CÁLCULO
        # ============================================
        sheet_id = os.getenv('SHEET_ID')
        if not sheet_id:
            print("❌ Error: SHEET_ID no configurado")
            return
        
        sheet = client.open_by_key(sheet_id).sheet1
        
        # ============================================
        # 3. OBTÉN INFORMACIÓN DEL REPOSITORIO
        # ============================================
        repo_full = os.getenv('GITHUB_REPOSITORY')  # dasolarf-debug/estacionamientos-duocuc
        repo_name = repo_full.split('/')[-1]  # estacionamientos-duocuc
        repo_url = f"https://github.com/{repo_full}"
        
        # ============================================
        # 4. OBTÉN EL ÚLTIMO COMMIT
        # ============================================
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True
        )
        commit_hash = result.stdout.strip()[:7]  # Primeros 7 caracteres
        
        # ============================================
        # 5. OBTÉN LA FECHA Y HORA ACTUAL
        # ============================================
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # ============================================
        # 6. LEE LA DESCRIPCIÓN DEL README
        # ============================================
        descripcion = "Sistema de estacionamientos"  # Por defecto
        if os.path.exists('README.md'):
            with open('README.md', 'r', encoding='utf-8') as f:
                contenido = f.read()
                # Obtén la primera línea que no sea vacía
                for linea in contenido.split('\n'):
                    if linea.strip() and not linea.startswith('#'):
                        descripcion = linea.strip()[:100]  # Primeros 100 caracteres
                        break
        
        # ============================================
        # 7. DETECTA EL LENGUAJE DEL PROYECTO
        # ============================================
        lenguaje = "Desconocido"
        if os.path.exists('package.json'):
            lenguaje = "JavaScript/Node.js"
        elif os.path.exists('requirements.txt'):
            lenguaje = "Python"
        elif os.path.exists('pom.xml'):
            lenguaje = "Java"
        elif os.path.exists('Gemfile'):
            lenguaje = "Ruby"
        elif os.path.exists('go.mod'):
            lenguaje = "Go"
        elif os.path.exists('Cargo.toml'):
            lenguaje = "Rust"
        
        # ============================================
        # 8. CUENTA LOS COMMITS
        # ============================================
        result = subprocess.run(
            ['git', 'rev-list', '--count', 'HEAD'],
            capture_output=True,
            text=True
        )
        num_commits = result.stdout.strip()
        
        # ============================================
        # 9. AGREGA LA FILA A GOOGLE SHEETS
        # ============================================
        row = [
            repo_name,           # Nombre del proyecto
            repo_url,            # URL de GitHub
            descripcion,         # Descripción
            lenguaje,            # Lenguaje detectado
            "En desarrollo",     # Estado
            commit_hash,         # Último commit
            num_commits,         # Total de commits
            fecha                # Fecha de sincronización
        ]
        
        sheet.append_row(row)
        
        # ============================================
        # 10. MENSAJE DE ÉXITO
        # ============================================
        print(f"✅ Sincronizado exitosamente!")
        print(f"   Proyecto: {repo_name}")
        print(f"   URL: {repo_url}")
        print(f"   Lenguaje: {lenguaje}")
        print(f"   Commits: {num_commits}")
        print(f"   Fecha: {fecha}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
