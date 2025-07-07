import xml.etree.ElementTree as ET

def parse_form4_xml(xml_content):
    root = ET.fromstring(xml_content)

    data = {
        "issuer": root.findtext(".//issuer/issuerName", default="N/A").strip(),
        "reporting_owner": root.findtext(".//reportingOwner/reportingOwnerId/rptOwnerName", default="N/A").strip(),
        "security": root.findtext(".//nonDerivativeTable/nonDerivativeTransaction/securityTitle/value", default="N/A").strip(),
        "transaction_date": root.findtext(".//nonDerivativeTable/nonDerivativeTransaction/transactionDate/value", default="N/A").strip(),
        "transaction_shares": root.findtext(".//nonDerivativeTable/nonDerivativeTransaction/transactionAmounts/transactionShares/value", default="N/A").strip(),
        "price_per_share": root.findtext(".//nonDerivativeTable/nonDerivativeTransaction/transactionAmounts/transactionPricePerShare/value", default="N/A").strip(),
        "transaction_code": root.findtext(".//nonDerivativeTable/nonDerivativeTransaction/transactionCoding/transactionCode", default="N/A").strip()
    }

    return data