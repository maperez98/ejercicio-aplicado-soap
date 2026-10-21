# Ejercicio aplicado SOAP — Banco Seguro

Simulación académica de integración de pagos mediante SOAP/XML sobre HTTP. No se conecta con un banco real ni mueve dinero.

## Requisitos
- Python 3.10 o superior
- Visual Studio Code

No requiere instalar paquetes externos: usa la biblioteca estándar de Python.

## 1. Abrir el proyecto
Descomprime `BancoSeguro_SOAP.zip` y abre la carpeta `BancoSeguro_SOAP` en Visual Studio Code.

## 2. Terminal 1: iniciar el servidor SOAP
Abre Terminal > New Terminal y ejecuta:

```bash
python server.py
```

En Windows, si `python` no funciona, prueba `py server.py`.

Debe aparecer: `Banco Seguro SOAP escuchando en http://127.0.0.1:8000/soap`

Deja esta terminal abierta.

## 3. Terminal 2: ejecutar el cliente
Abre una segunda terminal en la misma carpeta y ejecuta:

```bash
python client.py
```

En Windows, si hace falta: `py client.py`.

El cliente envía una solicitud SOAP XML por HTTP. El servidor muestra el XML recibido, valida la cuenta y el saldo, y devuelve una respuesta SOAP XML. El cliente imprime la respuesta y un resumen.

## 4. Probar los tres escenarios del documento

Cada comando es una solicitud independiente. Para repetir la prueba con saldo inicial limpio, reinicia el servidor (Ctrl+C y vuelve a ejecutar `python server.py`).

**Caso 1 — saldo suficiente**
```bash
python client.py --cuenta CTA-001 --valor 50000
```
Esperado: `APROBADO`, saldo inicial `200000`, pago `50000`, saldo restante `150000`.

**Caso 2 — saldo insuficiente**
```bash
python client.py --cuenta CTA-002 --valor 50000
```
Esperado: `RECHAZADO`, mensaje `Fondos insuficientes.` La cuenta CTA-002 tiene saldo ficticio de 20000.

**Caso 3 — cuenta inexistente**
```bash
python client.py --cuenta CTA-999 --valor 50000
```
Esperado: `ERROR DE NEGOCIO`, mensaje `Cuenta no válida.`

## ¿Qué demuestra que sí se usa SOAP?
- El cliente envía un `soap:Envelope` con `soap:Header` y `soap:Body`.
- El cuerpo contiene la operación `ban:EvaluarPago`.
- La solicitud se envía por HTTP POST con contenido `text/xml`.
- El servidor interpreta el XML y responde con `ban:EvaluarPagoResponse` dentro de otro `soap:Envelope`.
- La terminal del servidor muestra los XML recibidos y enviados.

## Estructura del proyecto
- `server.py`: servidor HTTP que recibe y procesa solicitudes SOAP.
- `client.py`: cliente que construye el XML, envía la solicitud y lee la respuesta.
- `README.md`: instrucciones de ejecución y pruebas.

## Nota académica
El espacio de nombres `http://bancoseguro.example/pagos` y la operación `EvaluarPago` son ilustrativos, como en el documento de clase. Esta versión implementa el intercambio SOAP/XML y la lógica básica del caso, pero no incluye WSDL, autenticación, HTTPS, persistencia de datos ni controles transaccionales de un sistema bancario real.
