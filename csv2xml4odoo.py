#!/usr/bin/env python
# -*- coding: utf-8 -*-

# convert Odoo csv files in xml files
# csv is easy to maintain but xml data have noupdate feature

# Limitations:
# - relation field One2many is NOT supported
# - csv should have 'id' as first column
# - ambiguous columns: char type but contains float string,
#   should have special suffix on column name '|char'
# - relationnal fields notation in csv should be:
#   myfield_id/id for m2o or myfield_ids/id for m2m


import csv
import glob

NOUPDATE = 1
BOOLEAN = ('True', 'False')
ERP_HEADER = """<odoo noupdate="%s">"""
ERP_FOOTER = """</odoo>
"""

FILES_WITH_UPDATE = ('product.product.csv')


def convert_cell_to_xml(title, cell):
    if title == 'id':
        # 'id' column is supposed to be the first left
        return '  <record id="{cell}" model="{model}">'.format(
            cell=cell, model=model)

    if title.endswith('|char'):
        # ambiguous column (char type but contains float string)
        # should be mark by suffix |char
        title = title[i][:-5]
    elif title.endswith('ids/id'):
        # many2many
        if "eval=" not in cell and "ref=" not in cell:
            if cell == 'False':
                cell = 'eval="[(6, 0, [])]"'
            else:
                values = ["ref('%s')" % v for v in cell.split(',')]
                cell = 'eval="[(6, 0, [%s])]"' % ",".join(values)
        title = title.split('/')[0]
    elif '/' in title:
        # many2one
        if "eval=" not in cell and "ref=" not in cell:
            if not cell:
                pass
            else:
                # many2one
                cell = 'ref="%s"' % cell
        title = title.split('/')[0]
    else:
        try:
            float(cell)
            cell = 'eval="%s"' % cell
        except Exception:
            pass

    cell = cell.replace('&', '&amp;')  # FIXME: better call escape function

    if "eval=" in cell or "ref=" in cell:
        line = '<field name="{name}" {raw}/>'.format(
            name=title, raw=cell)
    elif cell in BOOLEAN:
        line = '<field name="{name}" eval="{value}"/>'.format(
            name=title, value=cell)
    else:
        line = '<field name="{name}">{content}</field>'.format(
            name=title, content=cell)
    return ' '*4 + line


for csv_file in glob.glob('*.csv'):
    print(csv_file)
    no_update = NOUPDATE
    if csv_file in FILES_WITH_UPDATE:
        no_update = 0
    model = csv_file[:-4].split(' ')[-1]
    xml_file = model.replace('.', '_') + '_data.xml'
    csv_data = csv.reader(open(csv_file))
    xml_data = open(xml_file, 'w')
    xml_data.write(ERP_HEADER % NOUPDATE + "\n\n")
    for row_num, row in enumerate(csv_data):
        if row_num == 0:
            header = row
            for i in range(len(header)):
                header[i] = header[i].replace(' ', '_')
        else:
            for i, title in enumerate(header):
                if not title:
                    continue
                if not row[i]:
                    continue
                line = convert_cell_to_xml(title, row[i])
                xml_data.write(line + '\n')
            xml_data.write('  </record>' + "\n\n")
    xml_data.write(ERP_FOOTER)
    xml_data.close()
