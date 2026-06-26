import os
import zipfile

def package_app():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    zip_path = os.path.join(base_dir, 'patagoniasur_cpanel.zip')
    
    exclude_dirs = {'.git', 'venv', '__pycache__', '.history', 'scripts', 'tmp', '.gemini'}
    exclude_files = {'.env', 'patagoniasur_cpanel.zip', 'package.py'}

    print(f"Empaquetando en {zip_path}...")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_dir):
            # Excluir directorios no deseados
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
            
            for file in files:
                if file in exclude_files or file.endswith('.pyc') or file.endswith('.log'):
                    continue
                
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, base_dir)
                zipf.write(file_path, arcname)
                
    print("¡Paquete creado exitosamente!")

if __name__ == '__main__':
    package_app()
