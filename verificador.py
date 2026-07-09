import os
print("Archivos encontrados en esta carpeta:")
for archivo in os.listdir("."):
    print("-", archivo)