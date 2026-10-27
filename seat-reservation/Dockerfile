# Un único Dockerfile para los cuatro servicios: compose le indica qué proyecto publicar (PROJECT)
# y cuál es su ensamblado de arranque (DLL). Evita repetir cuatro archivos casi idénticos.

# Etapa 1: compilar y publicar con el SDK
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
ARG PROJECT
WORKDIR /repo
COPY src ./src
RUN dotnet publish "src/${PROJECT}" -c Release -o /app /p:UseAppHost=false

# Etapa 2: imagen final, solo con el runtime (más liviana)
FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS runtime
ARG DLL
ENV DLL=${DLL}
WORKDIR /app
COPY --from=build /app .
# "exec" para que dotnet reciba las señales de apagado de Docker
ENTRYPOINT ["sh", "-c", "exec dotnet ${DLL}"]