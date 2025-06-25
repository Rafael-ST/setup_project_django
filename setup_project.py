
import os
import sys
import subprocess

def create_gitignore():
    content = """# Ambiente virtual
venv/

# Arquivos compilados Python
__pycache__/
*.py[cod]
*.pyo

# Configurações locais
*.env
*.sqlite3

# Django stuff:
db.sqlite3
/staticfiles/
media/

# VSCode, PyCharm, etc.
.vscode/
.idea/

# Arquivos de log
*.log

# Arquivos do sistema
.DS_Store
Thumbs.db
"""
    with open(".gitignore", "w") as file:
        file.write(content)
    print("Arquivo .gitignore criado.")


def run_command(command):
    print(f"Executando: {command}")
    subprocess.run(command, shell=True, check=True)


def create_env_file():
    content = """USE_SQLITE=True
DEBUG=True
ALLOWED_HOSTS='*'

DB_NAME='*'
DB_USER='*'
DB_PASSWORD='*'
DB_HOST='*'
DB_PORT='*'
"""
    with open(".env", "w") as file:
        file.write(content)
    print("Arquivo .env criado.")


def modify_settings(project_name):
    settings_path = os.path.join(project_name, "settings.py")

    with open(settings_path, "r") as file:
        content = file.read()

    # Adiciona o app "app" em INSTALLED_APPS
    if  'django.contrib.staticfiles' in content and "'app'" not in content:
        content = content.replace(
        "'django.contrib.staticfiles',",
        "'django.contrib.staticfiles',\n    'app',"
        )
    if 'app' in content and "'csp'" not in content:
        print('csp')
        content = content.replace(
        "'app',",
        "'app',\n    'csp',"
        )
    
    if 'django.middleware.security.SecurityMiddleware' in content and 'CSPMiddleware' not in content:
        content = content.replace(
            "'django.middleware.security.SecurityMiddleware',",
            "'django.middleware.security.SecurityMiddleware',\n    'csp.middleware.CSPMiddleware',"
        )
    

    # Adiciona configurações CSP padrão ao final
    if "CSP_DEFAULT_SRC" not in content:
        content += """

CONTENT_SECURITY_POLICY = {
    "EXCLUDE_URL_PREFIXES": ["/admin/"],
    "DIRECTIVES": {
        "default-src": ['self', "cdn.example.net", "'unsafe-inline'"],
        "frame-ancestors": ['self'],
        "form-action": ['self'],
        "img-src": ['self', 'data:'],
        "report-uri": "/csp-report/",
    },
}
"""

    content = content.replace(
        "LANGUAGE_CODE = 'en-us'",
        "LANGUAGE_CODE = 'pt-BR'"
    )

    content = content.replace(
        "TIME_ZONE = 'UTC'",
        "TIME_ZONE = 'America/Sao_Paulo'"
    )

    content = content.replace(
        "from pathlib import Path",
        "from pathlib import Path \nimport os\nfrom dotenv import load_dotenv\n\nload_dotenv()\n"
    )

    content = content.replace(
        "'DIRS': [],",
        """'DIRS': [
            BASE_DIR / 'base',
        ],"""
    )

    content = content.replace(
        "STATIC_URL = '/static/'",
        "STATIC_URL = '/static/teste'"
    )

    content = content.replace("DEBUG = True", "DEBUG = os.getenv('DEBUG', 'False') == 'True'")


    content = content.replace("ALLOWED_HOSTS = []", "ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')")


    db_block = """
USE_SQLITE = os.getenv('USE_SQLITE', 'True') == 'True'

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': os.getenv('DB_PORT'),
        }
    }
"""

    content = content.replace(
        "DATABASES = {\n    'default': {\n        'ENGINE': 'django.db.backends.sqlite3',\n        'NAME': BASE_DIR / 'db.sqlite3',\n    }\n}",
        db_block.strip()
    )

    with open(settings_path, "w") as file:
        file.write(content)

    print("settings.py atualizado com variáveis do .env")


def main():
    print("Inicializando criação do projeto Django")

    project_name = input("Digite o nome do projeto: ").strip()

    os.makedirs(project_name, exist_ok=True)
    os.chdir(project_name)

    print("Criando ambiente virtual...")
    run_command(f"{sys.executable} -m venv venv")

    pip_path = os.path.join("venv", "Scripts" if os.name == "nt" else "bin", "pip")
    django_admin = os.path.join("venv", "Scripts" if os.name == "nt" else "bin", "django-admin")

    print("Instalando pacotes...")
    run_command(f"{pip_path} install django python-dotenv psycopg2-binary gunicorn whitenoise django-csp")

    print("Criando projeto Django...")
    run_command(f"{django_admin} startproject {project_name} .")

    manage_py = "manage.py"
    python_exec = os.path.join("venv", "Scripts" if os.name == "nt" else "bin", "python")
    print("Criando app 'app'...")
    run_command(f"{python_exec} {manage_py} startapp app")

    print("Atualizando settings.py")
    modify_settings(project_name)

    create_gitignore()
    create_env_file()


if __name__ == "__main__":
    main()