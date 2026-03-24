from primer_llm import consultar_llm

PROMPT_ANALISTA = """Eres un analista de datos senior especializado en retail.
Cuando recibas datos, debes:
1. Identificar patrones y anomalías
2. Dar recomendaciones accionables
3. Responder en formato estructurado con bullets
4. Incluir métricas específicas cuando sea posible

Formato de respuesta:
## Análisis
[tu análisis]

## Hallazgos Clave
- [hallazgo 1]
- [hallazgo 2]

## Recomendaciones
1. [recomendación con impacto estimado]
"""

datos = """
Ventas enero: $45,000 | Febrero: $38,000 | Marzo: $52,000
Producto estrella: Widget A (40% del total)
Devoluciones: 12% en febrero (promedio histórico: 5%)
"""

if __name__ == "__main__":
    resultado = consultar_llm(datos, PROMPT_ANALISTA)
    print(resultado)
