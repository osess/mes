#-*- coding: UTF-8 -*- 
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.template import Template, Context
from companydepartment.models import Department
from person.models import Person, Employee
import cStringIO
import base64
import os
#reportlab
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4, cm
from reportlab.platypus.tables import Table
#charts
from reportlab.graphics.shapes import *
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF
#trml2pdf
from trml2pdf import trml2pdf

# lxy
from technologies.models import Technology, OperationGroup
from manufactureplan.models import *

from settings import TECHNOLOGY_REPORT_ROW, UPLOAD_ROOT
from report.views import generate_report_code

from yt_barcode.views import add_barcode
from yt_barcode.models import Barcode

import re
from PIL import Image, ImageFont, ImageDraw
import base64
import StringIO
import os.path


def convert_special_character_to_rml(string):
    TMD_DIR = '/tmp'
    target = r'\[(.*?)\]'
    special_characters = re.findall(target, string)

    modified_string = '<td>%s</td>' % string
    for character in special_characters:

        #orig_character is used for replace
        orig_character = '[' + character + ']'

        #This is to handle [a, b, c]  [a,b,c] [a, b,c] and so on
        character_value_buff = ''.join(character.split(' '))
        character_value = character_value_buff.split(',')


        #model 1 [123, +0.001, -0.002, 12]
        if ('+' in character) or ('-' in character):
            character_table = '''</td><td>{base_number}</td>               
                        <td>{upper_bound}</td>
                        <td>{lower_bound}'''.format(base_number=character_value[0], upper_bound=character_value[1], 
                    lower_bound=character_value[2], font_size=character_value[-1], bound_number_size=int(character_value[-1])/2)

            modified_string = modified_string.replace(orig_character ,character_table)

        #model 3 [r, 3.2]
        elif len(character_value) == 2:
            image_path = "static/images/symbols/%s.png" %(character_value[0])
            if os.path.isfile(image_path) == True:
                
                font = ImageFont.truetype("static/images/symbols/DejaVuSans.ttf",13)
                value = character_value[1]

                image = Image.open("static/images/symbols/%s.png"% character_value[0])
                draw = ImageDraw.Draw(image)
                draw.text((0, 0), value, fill="black", font=font)
                del draw
                output = StringIO.StringIO()
                image.save(output, format="PNG")
                contents = output.getvalue()
                output.close()
                img_base64 = base64.b64encode(contents)

                character_table = '''</td><td><blockTable><tr><td><illustration><image file="data:image/jpeg;base64,{symbol}" x="0" y="0" width="40" height="30" /></illustration></td></tr></blockTable></td><td>'''.format(symbol=img_base64)

                modified_string = modified_string.replace(orig_character ,character_table)

        else:
            #model 3 [qty, 0.001, 0.002, 12]
            image_path = "static/images/symbols/%s.png" %(character_value[0])
            if os.path.isfile(image_path) == True:
                character_table = '''</td><td><blockTable style="myBlockTableStyle2"><tr><td><image file="static/images/symbols/{symbol}.png" /></td>'''.format(font_size=character_value[-1], symbol=character_value[0])
                for i in xrange(len(character_value) -2 ):
                    character_table += '<td>%s</td>' %(character_value[i+1])
                character_table += '</tr></blockTable>'
                modified_string = modified_string.replace(orig_character ,character_table)
    return modified_string

def report_management(request):
    return render_to_response('report_management.html', {
    }, context_instance=RequestContext(request))

def report_person_list_table(request):
    filedata = open(os.path.dirname(__file__)+'/templates/rml/ex10.rml').read()
    template = Template(filedata)
    persons = Employee.objects.all().order_by('id')
    
    #personsdata
    personsdata = []
    personsdata.append(['名字','描述','性别','部门'])
    for person in persons:
        data_line = []
        data_line.append(person.name)
        data_line.append(person.description)
        data_line.append(person.gender)
        # data_line.append(person.department.name)
        data_line.append(person.department)

        personsdata.append(data_line)
    personsrowHeights = '1.5cm'+',1.5cm'*(len(personsdata)-1)
    personscolWidths = '4cm'+',4cm'*(len(personsdata[0])-1)
    
    #persons_gender_piechart
    persons_genders = [person.gender for person in persons]
    persons_genders_datas = []
    persons_genders_labels = list(set(persons_genders))
    for label in persons_genders_labels:
        persons_genders_datas.append(persons_genders.count(label))
    
    drawing = Drawing(150,150)
    piechart = Pie()
    piechart.x = 25
    piechart.y = 25
    piechart.width = 100
    piechart.height = 100
    piechart.slices.strokeWidth= 1
    piechart.slices.fontSize = 12
    piechart.data = persons_genders_datas
    piechart.labels = persons_genders_labels
    drawing.add(piechart, '')
    drawing.add(String(10,130, 'persons gender piechart', fontSize=16))
    piechartbinaryStuff = base64.b64encode(drawing.asString('png'))

    
    #person_by_department_chart
    departments = Department.objects.all().order_by('id')
    persons_department_datas = []
    persons_department_data_list = []
    for department in departments:
        persons_department_data_list.append(len(departments)) #len(department.departments.all())
    persons_department_data_tuple = tuple(persons_department_data_list)
    persons_department_datas.append(persons_department_data_tuple)
    
    drawing = Drawing(640,300)
    barchart = VerticalBarChart()
    barchart.x = 25
    barchart.y = 80
    barchart.width = 600
    barchart.height = 150
    barchart.categoryAxis.labels.angle = 270
    barchart.categoryAxis.labels.dx = 7
    barchart.categoryAxis.labels.dy = -20
    barchart.categoryAxis.labels.fontSize = 10
    barchart.data = persons_department_datas
    barchart.categoryAxis.categoryNames = [department.name for department in departments]
    drawing.add(barchart, '')
    drawing.add(String(120,280, 'person by department chart', fontSize=24))
    barchartbinaryStuff = base64.b64encode(drawing.asString('png'))
    
    #style
    header = base64.b64encode(open(os.path.dirname(__file__)+'/templates/rml/pict/yuanto_top.png').read())
    booter = base64.b64encode(open(os.path.dirname(__file__)+'/templates/rml/pict/yt_booter.jpg').read())
    header_path = os.path.dirname(__file__)+'/templates/rml/pict/yuanto_top.png'
    #do output
    context = Context({
                       'personsdata': personsdata,'personsrowHeights':personsrowHeights,'personscolWidths':personscolWidths,
                       'piechart':piechartbinaryStuff,'barchart':barchartbinaryStuff,'header':header,'booter':booter,
                       'header_path':header_path,
                       })
    rmldata = template.render(context).encode('utf-8')
    
    #trml2pdf
    pdfData = trml2pdf.parseString(rmldata)
    response = HttpResponse(mimetype='application/pdf')
    response.write(pdfData)
    response['Content-Disposition'] = 'attachment; filename=output.pdf'
    return response

#generate pdf data
def technology_pdf_data(technology_id):

    filedata = open(os.path.dirname(__file__)+'/templates/rml/technology.rml').read()
    template = Template(filedata)
    
    # barcode = base64.b64encode(Code128Encoder(code).get_imagedata(bar_width=1))

    technology = Technology.objects.get(id=technology_id)
    operation_group_objects = technology.operation_groups.all()
    code = generate_report_code(1, technology.code)

    # barcode = base64.b64encode(Code128Encoder(code).get_imagedata(bar_width=1))
    # barcode = 

    try:
        barcode_item = Barcode.objects.get(code=technology.code ,name=technology.name + 'pdf')
    except:
        barcode_item = add_barcode(technology.code , technology.name + 'pdf', 2)

    if TECHNOLOGY_REPORT_ROW != 0:
        row = TECHNOLOGY_REPORT_ROW
    else:
        row = 7

    operation_group_list = []
    for operation_record in operation_group_objects:
        operation_group_list.append(operation_record)

    total_table = []
    three_table = []
    list_length = len(operation_group_list)
    table_count = 0
    for i in xrange(0, list_length, row*3):                   #21

        try:
            table1_list = operation_group_list[i:i+row]      #7
            three_table.append(table1_list)
            table2_list = operation_group_list[i+row:i+row*2]   #7 14
            three_table.append(table2_list)
            table3_list = operation_group_list[i+row*2:i+row*3]  #14 21
            three_table.append(table3_list)
            total_table.append(three_table)
            three_table = []
        except:
            pass

    
    for table in total_table:
        for sub_table in table:
            while len(sub_table) < row:
                sub_table.append(' ')
            
    #do output
    context = Context({
                       'total_table':total_table,
                       'technology':technology,
                       'operation_group_objects':operation_group_objects,
                       'code':code,
                       'barcode':barcode_item.base64_code,
                       'total_pages':technology.operation_groups.all().count() + 1,
                       })
    rmldata = template.render(context).encode('utf-8')
    
    #trml2pdf
    pdfData = trml2pdf.parseString(rmldata)

    return pdfData

def technology_subpicture_pdf_data(operation_group_id):
    filedata = open(os.path.dirname(__file__)+'/templates/rml/technology_subpicture.rml').read()
    template = Template(filedata)
    operation_group = OperationGroup.objects.get(id=operation_group_id)
    context = Context({
                        'operation_group':operation_group,
                        'UPLOAD_ROOT':UPLOAD_ROOT,
                        'page_number':operation_group.order + 1,
                        'total_pages':operation_group.technology.operation_groups.all().count() + 1,
                       })
    rmldata = template.render(context).encode('utf-8')
    
    #trml2pdf
    pdfData = trml2pdf.parseString(rmldata)
    return pdfData   

#generate pdf
def generate_technology_pdf(request, technology_id):

    #trml2pdf
    pdfData = technology_pdf_data(technology_id)
    response = HttpResponse(mimetype='application/pdf')
    response.write(pdfData)
    response['Content-Disposition'] = 'attachment; filename=机械加工工艺过程卡.pdf'
    return response


 
def generate_technology_subpicture_pdf(request, operation_group_id):

    #trml2pdf
    pdfData = technology_subpicture_pdf_data(operation_group_id)
    response = HttpResponse(mimetype='application/pdf')
    response.write(pdfData)
    response['Content-Disposition'] = 'attachment; filename=机械加工工艺附图卡.pdf'
    return response


def generate_first_item_pdf(request, productionline_id):
    filedata = open(os.path.dirname(__file__)+'/templates/rml/first_item.rml').read()
    template = Template(filedata)

    productionline = ProductionLine.objects.get(id=productionline_id)
    code = generate_report_code(3, productionline.code)
    
    context = Context({
                        'productionline':productionline,
                        'code':code,
                       })
    rmldata = template.render(context).encode('utf-8')
    
    #trml2pdf
    pdfData = trml2pdf.parseString(rmldata)
    response = HttpResponse(mimetype='application/pdf')
    response.write(pdfData)
    if productionline.is_item:
        filename = (u'%s三检实测数值记录卡' % productionline.manufacture_items.all()[0].code).encode('utf-8')
        filename = filename.replace(' ', '_')
    else:
        filename = '工序首件三检实测数值记录卡'
    print filename
    response['Content-Disposition'] = 'attachment; filename=%s.pdf' % filename
    return response    


def generate_reject_project_pdf(request, productionline_id):
    filedata = open(os.path.dirname(__file__)+'/templates/rml/reject.rml').read()
    template = Template(filedata)

    reject_product_records = []
    productionline = ProductionLine.objects.get(id=productionline_id)
    for productionline in productionline.children_productionlines:
        reject_product_records.extend(productionline.reject_product_records.all())
    code = generate_report_code(4, productionline.code)
    
    context = Context({
                    'code':code,'productionline':productionline,
                    'reject_product_records':reject_product_records,
                       })
    rmldata = template.render(context).encode('utf-8')
    
    #trml2pdf
    pdfData = trml2pdf.parseString(rmldata)
    response = HttpResponse(mimetype='application/pdf')
    response.write(pdfData)
    response['Content-Disposition'] = 'attachment; filename=质量记录表.pdf'
    return response


def generate_quality_pdf(request, productionline_id):
    filedata = open(os.path.dirname(__file__)+'/templates/rml/quality.rml').read()
    template = Template(filedata)

    productionline = ProductionLine.objects.get(id=productionline_id)
    code = generate_report_code(2, productionline.code)

    records = productionline.first_child_productionline.oper_group_records.all()
    page_counts = (records.count()-7)/9+(1 if (records.count()-7)%9!=0 else 0)
    records = list(records)
    record_tables = []
    record_tables.append(records[0:7])

    for i in range(0, len(records[7:]), 9):
        try:
            record_tables.append(records[i+7:i+7+9])
        except:
            pass

    while len(record_tables[0]) < 7:
        record_tables[0].append(' ')

    for table in record_tables[1:]:
        while len(table) < 9:
            table.append(' ')

    # print record_tables
    context = Context({
                        'productionline':productionline,'code':code,
                        'first_page':record_tables[0],
                        'page_counts':range(page_counts),
                        'record_tables':record_tables[1:],
                       })
    rmldata = template.render(context).encode('utf-8')
    #trml2pdf
    pdfData = trml2pdf.parseString(rmldata)
    response = HttpResponse(mimetype='application/pdf')
    response.write(pdfData)
    # print pdfData
    response['Content-Disposition'] = 'attachment; filename=产品生产质量控制记录卡（首页）.pdf'
    return response


from django.http import HttpResponse
# from rlextra.rml2pdf import rml2pdf


from PyPDF2 import PdfFileMerger, PdfFileReader
import StringIO
def merge_pdf(request, technology_id):

    # generate_quality_pdf(request, 1)
    technology = Technology.objects.get(id=technology_id)
    operation_groups = technology.operation_groups.all()

    data = technology_pdf_data(technology_id)
    merger = PdfFileMerger()
    file_name = 'technology.pdf'
    with open(file_name, 'w') as mypdf:
        mypdf.write(data)
    merger.append(PdfFileReader(file(file_name, 'rb')))
    os.remove(file_name)

    for operation_group in operation_groups:
        file_name = 'operation_group_%d.pdf' %(operation_group.id)
        with open(file_name, 'w') as mypdf:
            data2= technology_subpicture_pdf_data(operation_group.id)
            mypdf.write(data2)
        merger.append(PdfFileReader(file(file_name, 'rb')))
        os.remove(file_name)

    output_name = "%s.pdf" %(technology.code)
    merger.write(str(output_name))

    response = HttpResponse(mimetype='application/pdf')
    with open(output_name, 'rb') as mypdf:
        response.write(mypdf.read())

    os.remove(output_name)
    
    response['Content-Disposition'] = 'attachment; filename=%s' %(output_name)
    return response