import subprocess


def check_pkgs(pkgs):
    for pkg in pkgs:
        try:
            __import__(pkg.lower())
        except ImportError:
            if pkg == 'foreman':
                subprocess.call(['pip', 'install', 'python-foreman'])
            else:
               subprocess.call(['pip', 'install', pkg])