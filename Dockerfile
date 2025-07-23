 
# Imagen base de Python
FROM python:3.11

# Crear carpeta de trabajo
WORKDIR /app


# Instalar las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar los archivos al contenedor
COPY . .

# Exponer el puerto (por ejemplo, para Flask)
EXPOSE 5000

# Comando para ejecutar la app
CMD ["python", "./app/main.py"]
