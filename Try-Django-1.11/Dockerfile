# 1. Definimos el sistema base: nuestra "cápsula del tiempo"
FROM python:3.6

# 2. Variables de entorno para que Python funcione mejor en Docker
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Definimos nuestro directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Copiamos el requirements.txt desde tu carpeta src/
COPY src/requirements.txt /app/

# 5. Instalamos las dependencias legacy
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 6. Copiamos el resto del proyecto
COPY . /app/