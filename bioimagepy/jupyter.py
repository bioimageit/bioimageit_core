# -*- coding: utf-8 -*-
"""BioImagePy jupyter module.

Contains a set of classes and methods for bioimagepy jupyter widgets

Classes
-------
BiTileArea

Methods
-------
BiTileWidget


"""

import os
import json
from ipywidgets import Button, Layout, Label, VBox, HBox, Accordion, Text, Box, DatePicker, Tab, Checkbox, Dropdown, HTML, IntText
from IPython.display import display, Javascript
import IPython

from .experiment import *

class BiButtonInfo:
    def __init__(self, title: str, info: str):
        self.widget = Button(description=title, layout=Layout(width='200px', height='100px'))
        self.info = info

class BiTileWidget:
    def __init__(self):
        self.count = 0
        self.buttons = [] 

    def add(self, title: str, link: str):
        self.count += 1
        buttonInfo = BiButtonInfo(title, link)
        self.buttons.append(buttonInfo) 
        buttonInfo.widget.on_click(self.on_button_clicked)
         
    def on_button_clicked(self, b):
        for bb in self.buttons:
            if bb.widget == b:
                display(Javascript("window.open('"+bb.info+"', '_blank');"))
                #print(bb.info)      

    def getWidget(self):
        butts = []
        for b in self.buttons:
            butts.append(b.widget)
        return HBox(butts)            

class BiTileArea:
    def __init__(self):
        self.tilesCount = 0
        self.tilesTitles = []
        self.tilesWidgets = []

    def add(self, title: str, widget: BiTileWidget):
        self.tilesCount += 1
        self.tilesTitles.append(title)
        self.tilesWidgets.append(widget.getWidget())

    def getWidget(self):
        accordion = Accordion(children=self.tilesWidgets)
        for i in range(self.tilesCount):
            accordion.set_title(i, self.tilesTitles)
        return accordion  


class BiCreateExperimentWidget:
    def __init__(self, validatedLink : str):

        self.validatedLink = validatedLink

        form_item_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-between'
        )

        self.directoryText = Text()
        self.nameText = Text()
        self.authorText = Text()
        self.createButton = Button(description='Create')
        self.createButton.on_click(self.action)

        form_items = [
            Box([Label(value='Directory'), self.directoryText], layout=form_item_layout),
            Box([Label(value='Project Name'), self.nameText], layout=form_item_layout),
            Box([Label(value='Author'), self.authorText], layout=form_item_layout),
            Box([self.createButton], layout=form_item_layout)
        ]

        self.form = Box(form_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 0px',
            align_items='stretch',
            width='50%'
        ))
    
    def action(self, button):
        create(name=self.nameText.value, 
                                  author=self.authorText.value, 
                                  path=self.directoryText.value)
        display(Javascript("window.open('"+self.validatedLink+"', '_blank');"))                          

    def getWidget(self):
        return self.form


class BiInformationExperimentWidget():

    def __init__(self, experiment: BiExperiment):

        form_item_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-between'
        )

        self.directoryText = Text(value=experiment.md_file_dir())
        self.nameText = Text(value=experiment.name())
        self.authorText = Text(value=experiment.author())
        self.datePicker = Text(value=experiment.createddate())

        form_items = [
            Box([Label(value='Directory'), self.directoryText], layout=form_item_layout),
            Box([Label(value='Project Name'), self.nameText], layout=form_item_layout),
            Box([Label(value='Author'), self.authorText], layout=form_item_layout),
            Box([Label(value='Date'), self.datePicker], layout=form_item_layout)
        ]

        self.form = Box(form_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 0px',
            align_items='stretch',
            width='50%'
        ))

    def getWidget(self):
        return self.form    


class BiImportExperimentWidget:
    def __init__(self, experiment: BiExperiment):
        self.experiment = experiment

        form_item_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-between'
        )

        self.directoryText = Text()
        self.recursiveCheckbox = Checkbox()
        self.filterSelect = Dropdown(options=['Ends with', 'Starts with', 'Contains'])
        self.filterText = Text()
        self.copyCheckbox = Checkbox()
        self.authorText = Text()
        self.datePicker = Text()
        self.importButton = Button(description='Import')
        self.importButton.on_click(self.action)


        form_items = [
            Box([Label(value='Directory'), self.directoryText], layout=form_item_layout),
            Box([Label(value='Recursive'), self.recursiveCheckbox], layout=form_item_layout),
            Box([Label(value='Filter'), self.filterSelect], layout=form_item_layout),
            Box([Label(value=''), self.filterText], layout=form_item_layout),
            Box([Label(value='Copy data'), self.copyCheckbox], layout=form_item_layout),
            Box([Label(value='Author'), self.authorText], layout=form_item_layout),
            Box([Label(value='Date'), self.datePicker], layout=form_item_layout),
            Box([self.importButton], layout=form_item_layout)
        ]

        self.form = Box(form_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 0px',
            align_items='stretch',
            width='50%'
        ))

    def action(self, b):

        filter_regexp = ''
        if self.filterSelect.value == 'Ends with':
            filter_regexp = '\\' + self.filterText.value + '$'
        elif self.filterSelect.value == 'Starts with':
            filter_regexp = self.filterText.value    
        elif self.filterSelect.value == 'Contains':
            filter_regexp = '^' + self.filterText.value  

        import_dir(experiment=self.experiment, 
                      dir_path=self.directoryText.value, 
                      filter=filter_regexp, 
                      author=self.authorText.value, 
                      datatype='image', 
                      createddate=self.datePicker.value, 
                      copy_data=self.copyCheckbox.value)
        display(Javascript("alert('Data imported');"))              

    def getWidget(self):   
        return self.form 


class BiTagBySeparatorExperimentWidget:
    def __init__(self, experiment: BiExperiment):
        self.experiment = experiment

        form_item_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-between'
        )

        self.tagText = Text()
        self.separatorText = Text(value='_')
        self.PositionText = IntText(value=1)
        validateButton = Button(description='Validate')
        validateButton.on_click(self.action)

        form_items = [
            Box([Label(value='Tag'), self.tagText], layout=form_item_layout),
            Box([Label(value='Separator (ex: "-" "_")'), self.separatorText], layout=form_item_layout),
            Box([Label(value='Position (after separator)'), self.PositionText], layout=form_item_layout),
            Box([validateButton], layout=form_item_layout)
        ]

        self.form = Box(form_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 0px',
            align_items='stretch',
            width='60%'
        ))

    def action(self, b):
        tag_rawdata_using_seperator(self.experiment, self.tagText.value, self.separatorText.value, self.PositionText.value) 
        display(Javascript("alert('Tags has been extracted !');"))  

    def getWidget(self):
        return self.form 


class BiTagByNameExperimentWidget:
    def __init__(self, experiment: BiExperiment):
        self.experiment = experiment

        form_item_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-between'
        )

        self.tagText = Text()
        self.tagSearchText = Text()
        validateButton = Button(description='Validate')
        validateButton.on_click(self.action)

        form_items = [
            Box([Label(value='Tag'), self.tagText], layout=form_item_layout),
            Box([Label(value='Search names (separated with ";")'), self.tagSearchText], layout=form_item_layout),
            Box([validateButton], layout=form_item_layout)
        ]

        self.form = Box(form_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 0px',
            align_items='stretch',
            width='60%'
        ))

    def action(self, b):
        tag_rawdata_from_name(self.experiment, self.tagText.value, self.tagSearchText.value.split(';')  )
        display(Javascript("alert('Tags has been extracted !');"))  

    def getWidget(self):
        return self.form    
        

class BiTagExperimentWidget:
    def __init__(self, experiment: BiExperiment):
        self.experiment = experiment

        self.tagName = BiTagByNameExperimentWidget(self.experiment)
        self.tagSeparator = BiTagBySeparatorExperimentWidget(self.experiment)

        self.tab = Tab()
        self.tab.children = [self.tagName.getWidget(), self.tagSeparator.getWidget()]
        self.tab.set_title(0, 'Tag using name')
        self.tab.set_title(1, 'Tag using separator')

    def getWidget(self):
        return self.tab 

class BiViewDataExperimentWidget:
    def __init__(self, experiment: BiExperiment):
        self.experiment = experiment

        refreshButton = Button(description='Refresh')
        refreshButton.on_click(self.refresh)

        self.datasetSelect = Dropdown(options=['data'])
        self.htmlArea = HTML()
  
        boxDataset = HBox([ Label(value='Dataset:'), self.datasetSelect, refreshButton ])
        htmlBox = HBox( [self.htmlArea] )

        self.widget = VBox([boxDataset, htmlBox])

    def refresh(self,b):
        options = self.experiment.processeddataset_names()
        options.insert(0, 'data')
        self.datasetSelect.options = options 
        data = self.experiment.to_table(self.datasetSelect.value)
        self.htmlArea.value = self.to_html(data)

    def to_html(self, table):
        html = '<style>'
        html += '#customers {'
        html += 'font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;'
        html += 'border-collapse: collapse;'
        html += 'width: 100%;'
        html += '}'

        html += '#customers td, #customers th {'
        html += '  border: 1px solid #ddd;'
        html += '  padding: 8px;'
        html += '}'

        html += '#customers tr:nth-child(even){background-color: #f2f2f2;}'

        html += '#customers tr:hover {background-color: #ddd;}'

        html += '#customers th {'
        html += '  padding-top: 12px;'
        html += '  padding-bottom: 12px;'
        html += '  text-align: left;'
        html += '  background-color: #018181;'
        html += '  color: white;'
        html += '}'
        html += '</style>'

        html += '<table id="customers">'
        html += '<thead>'
        for item in table[0]:
            html+= '<th>'+item+'</th>'
        html += '</thead>'
        html += '<tbody>'

        c = 0
        for line in table:
            c += 1
            if c > 1:
                html += '<tr>'
                for item in line:
                    html+= '<td>'+item+'</td>'    
                html += '</tr>'  
                  
        html += '</tbody>'
        html += '</table>'
        return html

    def getWidget(self):
        return self.widget    


class BiViewExperimentWidget:
    def __init__(self, path: str):
        self.path = path
        self.experiment = BiExperiment(os.path.join(path, 'experiment.md.json'))

        tabs_titles = ['Information', 'Import data', 'Tag', 'View']

        self.infoWidget = BiInformationExperimentWidget(self.experiment)
        self.importWidget = BiImportExperimentWidget(self.experiment)
        self.tagWidget = BiTagExperimentWidget(self.experiment)
        self.viewWidget = BiViewDataExperimentWidget(self.experiment)

        children = [self.infoWidget.getWidget(), self.importWidget.getWidget(), self.tagWidget.getWidget(), self.viewWidget.getWidget()]
        self.tab = Tab()
        self.tab.children = children
        for i in range(4):
            self.tab.set_title(i, tabs_titles[i])
        
    def getWidget(self):
        return self.tab
