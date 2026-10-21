import argparse
import urllib.request
from xml.etree import ElementTree as ET

URL = "http://127.0.0.1:8000/soap"
SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"
BAN_NS = "http://bancoseguro.example/pagos"
ET.register_namespace("soap", SOAP_NS)
ET.register_namespace("ban", BAN_NS)


def crear_solicitud(cuenta, valor, moneda="COP"):
    envelope = ET.Element(f"{{{SOAP_NS}}}Envelope")
    ET.SubElement(envelope, f"{{{SOAP_NS}}}Header")
    body = ET.SubElement(envelope, f"{{{SOAP_NS}}}Body")
    operation = ET.SubElement(body, f"{{{BAN_NS}}}EvaluarPago")
    ET.SubElement(operation, f"{{{BAN_NS}}}cuenta").text = cuenta
    ET.SubElement(operation, f"{{{BAN_NS}}}valor").text = str(valor)
    ET.SubElement(operation, f"{{{BAN_NS}}}moneda").text = moneda
    return ET.tostring(envelope, encoding="utf-8", xml_declaration=True)


def enviar_pago(cuenta, valor):
    xml_solicitud = crear_solicitud(cuenta, valor)
    print("\n========== SOLICITUD SOAP ENVIADA ==========")
    print(xml_solicitud.decode("utf-8"))

    request = urllib.request.Request(
        URL, data=xml_solicitud,
        headers={"Content-Type": "text/xml; charset=utf-8", "SOAPAction": "EvaluarPago"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            xml_respuesta = response.read()
            print("\n========== RESPUESTA SOAP RECIBIDA ==========")
            print(xml_respuesta.decode("utf-8"))
    except Exception as exc:
        print(f"\nNo se pudo contactar el servidor SOAP: {exc}")
        print("Verifica que server.py esté ejecutándose en la otra terminal.")
        return

    root = ET.fromstring(xml_respuesta)
    body = root.find(f"{{{SOAP_NS}}}Body")
    result = body.find(f"{{{BAN_NS}}}EvaluarPagoResponse") if body is not None else None
    if result is None:
        print("El servidor respondió, pero no se encontró EvaluarPagoResponse.")
        return

    def valor_tag(name):
        node = result.find(f"{{{BAN_NS}}}{name}")
        return node.text if node is not None and node.text else ""

    print("\n========== RESUMEN DEL RESULTADO ==========")
    print("Estado:", valor_tag("estado"))
    print("Cuenta:", valor_tag("cuenta"))
    print("Saldo inicial:", valor_tag("saldoInicial"), "COP")
    print("Valor del pago:", valor_tag("valorPago"), "COP")
    print("Saldo restante:", valor_tag("saldoRestante"), "COP")
    print("Mensaje:", valor_tag("mensaje"))


def main():
    parser = argparse.ArgumentParser(description="Cliente del ejercicio SOAP Banco Seguro")
    parser.add_argument("--cuenta", default="CTA-001", help="Ejemplo: CTA-001 o CTA-999")
    parser.add_argument("--valor", type=int, default=50000, help="Valor del pago en COP")
    args = parser.parse_args()
    enviar_pago(args.cuenta, args.valor)


if __name__ == "__main__":
    main()
