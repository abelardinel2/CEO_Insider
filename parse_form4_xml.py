from lxml import etree

def parse_form4_xml(xml_content):
    parser = etree.XMLParser(recover=True)
    root = etree.fromstring(xml_content.encode(), parser=parser)

    ns = {"ns": root.nsmap[None]} if None in root.nsmap else {}

    def find_text(xpath):
        result = root.xpath(xpath, namespaces=ns)
        return result[0].text.strip() if result else "N/A"

    data = {
        "issuer": find_text(".//issuer/issuerName"),
        "reporting_owner": find_text(".//reportingOwner/reportingOwnerId/rptOwnerName"),
        "security": find_text(".//nonDerivativeTable/nonDerivativeTransaction/securityTitle/value"),
        "transaction_date": find_text(".//nonDerivativeTable/nonDerivativeTransaction/transactionDate/value"),
        "transaction_shares": find_text(".//nonDerivativeTable/nonDerivativeTransaction/transactionAmounts/transactionShares/value"),
        "price_per_share": find_text(".//nonDerivativeTable/nonDerivativeTransaction/transactionAmounts/transactionPricePerShare/value"),
        "transaction_code": find_text(".//nonDerivativeTable/nonDerivativeTransaction/transactionCoding/transactionCode"),
    }

    return data