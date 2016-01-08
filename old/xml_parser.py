import xml.etree.ElementTree as ET



def get_fields(path):
    fields = {}
    tree = ET.parse(path)
    for child in tree.getroot():
        attr = child.attrib
        x = {}
        x[attr['name']] = attr['value']
        fields.update(x)
    return fields


def write_fields(path, **attr):
    root = ET.Element('fields')
    for a in attr:
        b = ET.SubElement(root, 'field')
        b.set('name', a)
        b.set('value', attr[a])
    f = ET.ElementTree()
    f._setroot(root)
    f.write(path)


if __name__ == "__main__":
    write_fields('a.xml', a="5", b="4533", c="{4,3}")
