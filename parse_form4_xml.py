
import xml.etree.ElementTree as ET

def parse_form4_xml(xml_content):
    root = ET.fromstring(xml_content)
    issuer = root.findtext('.//issuer/issuerName', default='N/A')
    owner = root.findtext('.//reportingOwner/reportingOwnerId/rptOwnerName', default='N/A')
    shares = root.findtext('.//nonDerivativeTable/nonDerivativeTransaction/nonDerivativeTransactionAmounts/transactionShares/value', default='N/A')
    return {
        'issuer': issuer.strip(),
        'owner': owner.strip(),
        'shares': shares.strip()
    }
