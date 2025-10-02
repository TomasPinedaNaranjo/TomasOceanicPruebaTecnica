# 🚀 Configuración de CI/CD con SonarQube

Este documento explica cómo configurar el pipeline de CI/CD que ejecuta SonarQube automáticamente en cada pull request.

## 📋 Prerrequisitos

1. **Cuenta de GitHub** con repositorio configurado
2. **Cuenta de SonarCloud** (gratuita) o instancia de SonarQube
3. **Token de SonarQube** generado

## 🔧 Configuración Paso a Paso

### 1. Configurar SonarCloud

1. Ve a [SonarCloud.io](https://sonarcloud.io)
2. Inicia sesión con tu cuenta de GitHub
3. Crea una nueva organización (si no tienes una)
4. Importa tu repositorio de GitHub
5. Genera un token de acceso:
   - Ve a **My Account** → **Security** → **Generate Tokens**
   - Crea un token con nombre descriptivo (ej: "GitHub Actions - Mars Weather")

### 2. Configurar Secrets en GitHub

1. Ve a tu repositorio en GitHub
2. Navega a **Settings** → **Secrets and variables** → **Actions**
3. Agrega los siguientes secrets:

#### `SONAR_TOKEN`
- **Valor**: El token generado en SonarCloud
- **Descripción**: Token de acceso para SonarCloud

#### `GITHUB_TOKEN` (automático)
- Este se configura automáticamente por GitHub Actions

### 3. Actualizar Configuración de SonarQube

Edita el archivo `sonar-project.properties` y actualiza:

```properties
# Cambia "tu-organizacion" por tu organización real de SonarCloud
sonar.organization=tu-organizacion

# Cambia "mars-weather-monitor" por la clave de tu proyecto
sonar.projectKey=mars-weather-monitor
```

### 4. Actualizar Workflows de GitHub Actions

En los archivos `.github/workflows/*.yml`, actualiza:

```yaml
# En sonar.yml y ci-cd.yml
-Dsonar.organization=tu-organizacion
-Dsonar.projectKey=mars-weather-monitor
```

## 🔄 Flujo de Trabajo

### En Pull Requests:
1. **Pruebas Unitarias** - Ejecuta pytest con cobertura
2. **Linting** - Verifica código con flake8, black, isort
3. **Análisis de Seguridad** - Bandit y Safety
4. **SonarQube** - Análisis de calidad de código
5. **Comentario Automático** - Resultados en el PR

### En Push a main:
1. Todos los pasos anteriores
2. **Análisis completo** de SonarQube
3. **Actualización del dashboard** de SonarCloud

## 📊 Qué Analiza SonarQube

### Calidad de Código:
- **Bugs** - Errores en el código
- **Vulnerabilidades** - Problemas de seguridad
- **Code Smells** - Problemas de mantenibilidad
- **Duplicación** - Código duplicado
- **Complejidad** - Complejidad ciclomática

### Métricas:
- **Cobertura de código** - Porcentaje de líneas probadas
- **Líneas de código** - Tamaño del proyecto
- **Deuda técnica** - Tiempo estimado para arreglar issues

## 🛠️ Comandos Locales

### Ejecutar pruebas:
```bash
pytest tests/ -v
```

### Ejecutar con cobertura:
```bash
pytest tests/ --cov=. --cov-report=html
```

### Linting:
```bash
flake8 .
black --check .
isort --check-only .
```

### Análisis de seguridad:
```bash
bandit -r .
safety check
```

## 🔍 Ver Resultados

### En GitHub:
- **Actions tab** - Ver logs de ejecución
- **Pull Request** - Comentarios automáticos con resultados
- **Code tab** - Badges de estado

### En SonarCloud:
- **Dashboard** - Vista general del proyecto
- **Issues** - Lista detallada de problemas
- **Measures** - Métricas y tendencias
- **Code** - Navegación del código con issues

## 🚨 Solución de Problemas

### Error: "Organization not found"
- Verifica que `sonar.organization` en `sonar-project.properties` sea correcto
- Asegúrate de que la organización existe en SonarCloud

### Error: "Project key not found"
- Verifica que `sonar.projectKey` sea correcto
- Asegúrate de que el proyecto existe en SonarCloud

### Error: "Token invalid"
- Regenera el token en SonarCloud
- Actualiza el secret `SONAR_TOKEN` en GitHub

### Error: "No coverage data"
- Verifica que las pruebas se ejecuten correctamente
- Asegúrate de que `coverage.xml` se genere

## 📈 Mejores Prácticas

1. **Mantén el código limpio** - Arregla issues de SonarQube
2. **Aumenta la cobertura** - Escribe más pruebas
3. **Revisa regularmente** - Monitorea la deuda técnica
4. **Configura Quality Gates** - Define criterios de aceptación
5. **Usa branches** - No mezcles todo en main

## 🔗 Enlaces Útiles

- [SonarCloud Documentation](https://docs.sonarcloud.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pytest Documentation](https://docs.pytest.org/)
- [Python Code Quality Tools](https://realpython.com/python-code-quality/)

## 📞 Soporte

Si tienes problemas con la configuración:
1. Revisa los logs en GitHub Actions
2. Verifica la configuración de SonarCloud
3. Consulta la documentación oficial
4. Crea un issue en el repositorio

