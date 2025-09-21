# Ejemplo de Renderizado Markdown GitHub-like

## Encabezados

### Encabezado H3
#### Encabezado H4
##### Encabezado H5
###### Encabezado H6

## Párrafos y Texto

Este es un párrafo normal con **texto en negrita** y *texto en cursiva*. También podemos tener `código inline` que se ve diferente.

## Listas

### Lista Desordenada
- Elemento 1
- Elemento 2
  - Sub-elemento 2.1
  - Sub-elemento 2.2
- Elemento 3

### Lista Ordenada
1. Primer elemento
2. Segundo elemento
3. Tercer elemento

## Bloques de Código

### Código Inline
Puedes usar `console.log('Hola Mundo')` para debugging.

### Bloques de Código
```javascript
function saludar(nombre) {
    console.log(`Hola, ${nombre}!`);
    return true;
}

// Llamada a la función
saludar('Mundo');
```

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Calcular factorial de 5
resultado = factorial(5)
print(f"El factorial de 5 es: {resultado}")
```

## Tablas

| Lenguaje | Paradigma | Popularidad |
|----------|-----------|-------------|
| Python   | Multiparadigma | Alta |
| JavaScript | Multiparadigma | Muy Alta |
| Java     | Orientado a Objetos | Alta |
| C++      | Multiparadigma | Media |

## Blockquotes

> Esta es una cita en bloque.
> Puede tener múltiples líneas.
>
> Y también puede contener **formato**.

## Enlaces e Imágenes

### Enlaces
- [Enlace a Google](https://www.google.com)
- [Enlace relativo](./archivo.md)

### Imágenes
![Logo de Python](https://www.python.org/static/img/python-logo.png)

## Listas de Tareas

- [x] Tarea completada
- [ ] Tarea pendiente
- [x] Otra tarea completada
- [ ] Tarea importante por hacer

## Elementos Especiales

### Líneas Horizontales
---

### Detalles Expansibles
<details>
<summary>Haz clic para ver más información</summary>

Esta es información adicional que se puede ocultar/mostrar.

Puedes incluir:
- Listas
- **Texto formateado**
- `Código`

Todo se renderiza correctamente dentro del elemento expansible.
</details>

---

*Este ejemplo demuestra todos los elementos de formato Markdown soportados con estilos GitHub-like.*