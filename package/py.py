from concurrent.futures import ThreadPoolExecutor
import subprocess


scripts = [
    r"D:\CODE\PYTHON\CODE\Projects\Personaldrive\package\build_exe.py",
    r"D:\CODE\PYTHON\CODE\Projects\Personaldrive\package\build_server_exe.py",
]


def run(script):
    subprocess.run(["python", script], check=True)


with ThreadPoolExecutor(max_workers=2) as executor:
    executor.map(run, scripts)

print("Both builds completed.")