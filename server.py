from http.server import BaseHTTPRequestHandler, HTTPServer
from xml.etree import ElementTree as ET

HOST = "127.0.0.1"
PORT = 8000

SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"
BAN_NS = "http://bancoseguro.example/pagos"
ET.register_namespace("soap", SOAP_NS)
ET.register_namespace("ban", BAN_NS)

# Datos ficticios del ejercicio. El servidor reinicia el saldo al reiniciarse.
CUENTAS = {"CTA-001": 200000, "CTA-002": 20000}


def crear_respuesta(estado, cuenta, saldo_inicial="", valor_pago="", saldo_restante="", mensaje=""):
    envelope = ET.Element(f"{{{SOAP_NS}}}Envelope")
    body = ET.SubElement(envelope, f"{{{SOAP_NS}}}Body")
    response = ET.SubElement(body, f"{{{BAN_NS}}}EvaluarPagoResponse")
    for tag, value in [
        ("estado", estado),
        ("cuenta", cuenta),
        ("saldoInicial", saldo_inicial),
        ("valorPago", valor_pago),
        ("saldoRestante", saldo_restante),
        ("moneda", "COP"),
        ("mensaje", mensaje),
    ]:
        ET.SubElement(response, f"{{{BAN_NS}}}{tag}").text = str(value)
    return ET.tostring(envelope, encoding="utf-8", xml_declaration=True)


class SOAPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/soap":
            self.send_error(404, "Ruta no encontrada. Use /soap")
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw_xml = self.rfile.read(length)
        print("\n========== SOLICITUD SOAP RECIBIDA ==========")
        print(raw_xml.decode("utf-8", errors="replace"))

        try:
            root = ET.fromstring(raw_xml)
            body = root.find(f"{{{SOAP_NS}}}Body")
            operation = body.find(f"{{{BAN_NS}}}EvaluarPago") if body is not None else None
            if operation is None:
                raise ValueError("No se encontró la operación ban:EvaluarPago")

            cuenta_node = operation.find(f"{{{BAN_NS}}}cuenta")
            valor_node = operation.find(f"{{{BAN_NS}}}valor")
            moneda_node = operation.find(f"{{{BAN_NS}}}moneda")
            cuenta = cuenta_node.text.strip() if cuenta_node is not None and cuenta_node.text else ""
            valor = int(valor_node.text) if valor_node is not None and valor_node.text else 0
            moneda = moneda_node.text.strip() if moneda_node is not None and moneda_node.text else ""

            if moneda != "COP":
                response_xml = crear_respuesta("ERROR DE NEGOCIO", cuenta, mensaje="La moneda debe ser COP.")
            elif valor <= 0:
                response_xml = crear_respuesta("ERROR DE NEGOCIO", cuenta, mensaje="El valor del pago debe ser mayor que cero.")
            elif cuenta not in CUENTAS:
                response_xml = crear_respuesta("ERROR DE NEGOCIO", cuenta, mensaje="Cuenta no válida.")
            else:
                saldo = CUENTAS[cuenta]
                if valor > saldo:
                    response_xml = crear_respuesta(
                        "RECHAZADO", cuenta, saldo, valor, saldo,
                        "Fondos insuficientes."
                    )
                else:
                    CUENTAS[cuenta] -= valor
                    response_xml = crear_respuesta(
                        "APROBADO", cuenta, saldo, valor, CUENTAS[cuenta],
                        "Pago procesado correctamente."
                    )

            self.send_response(200)
            self.send_header("Content-Type", "text/xml; charset=utf-8")
            self.send_header("Content-Length", str(len(response_xml)))
            self.end_headers()
            self.wfile.write(response_xml)
            print("\n========== RESPUESTA SOAP ENVIADA ==========")
            print(response_xml.decode("utf-8"))
        except (ET.ParseError, ValueError, AttributeError) as exc:
            fault = ET.Element(f"{{{SOAP_NS}}}Envelope")
            body = ET.SubElement(fault, f"{{{SOAP_NS}}}Body")
            soap_fault = ET.SubElement(body, f"{{{SOAP_NS}}}Fault")
            ET.SubElement(soap_fault, "faultcode").text = "SOAP-Client"
            ET.SubElement(soap_fault, "faultstring").text = str(exc)
            response_xml = ET.tostring(fault, encoding="utf-8", xml_declaration=True)
            self.send_response(400)
            self.send_header("Content-Type", "text/xml; charset=utf-8")
            self.send_header("Content-Length", str(len(response_xml)))
            self.end_headers()
            self.wfile.write(response_xml)
            print("Error procesando SOAP:", exc)

    def log_message(self, fmt, *args):
        print("[HTTP]", fmt % args)


if __name__ == "__main__":
    print(f"Banco Seguro SOAP escuchando en http://{HOST}:{PORT}/soap")
    print("Esperando solicitudes SOAP... (Ctrl+C para detener)")
    HTTPServer((HOST, PORT), SOAPHandler).serve_forever()
