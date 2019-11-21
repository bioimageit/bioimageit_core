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
from ipywidgets import Button, Layout, Label, VBox, HBox, Accordion, Text, Box, DatePicker, Tab, Checkbox, Dropdown, HTML, IntText, ToggleButton
from IPython.display import display, Javascript
import IPython
from pathlib import Path

from .experiment import *
from .process import *
from .runner import BiRunnerExperiment

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
        self.htmlArea.value = self._dataset_to_table(self.datasetSelect.value)

    def _dataset_to_table(self, dataset_name: str):
        if (dataset_name == 'data'):
            return self._dataset_data_to_table()
        else:
            processeddataset = self.experiment.processeddataset_by_name(dataset_name)
            process_url = processeddataset.process_url()
            process_info = BiProcessParser(process_url).parse()

            if process_info.type == 'sequential':
                return self._dataset_to_table_sequential(processeddataset, process_info)
            else:
                return self._dataset_to_table_merge(processeddataset, process_info)     

    def _dataset_data_to_table(self):
        html = self._html_header()
        html+= '<th></th>'
        html+= '<th>Name</th>'
        if 'tags' in self.experiment.metadata:  
            for tag in self.experiment.metadata['tags']:
                html += '<th>'+tag+'</th>'

        html += '<th>Author</th>' 
        html += '<th>Created date</th>' 
        html += '</thead>'
        html += '<tbody>'

        bi_rawdataset = self.experiment.rawdataset()
        for i in range(bi_rawdataset.size()):
            html += '<tr>'
            bi_rawdata = bi_rawdataset.raw_data(i)
            html+= '<td><img src='+bi_rawdata.thumbnail_relative_experiment()+'></td>'
            html+= '<td>'+bi_rawdata.name()+'</td>'
            if 'tags' in self.experiment.metadata: 
                for key in self.experiment.metadata['tags']:
                    html += '<td>'+bi_rawdata.tag(key)+'</td>'

            html += '<td>'+bi_rawdata.author()+'</td>'
            html += '<td>'+bi_rawdata.createddate()+'</td>'
            html += '</tr>' 
        return html 

    def _dataset_to_table_sequential(self, processeddataset: BiProcessedDataSet, process_info: BiProcessInfo): 

        # extract the processed middle name filenames
        process_data = processeddataset.processed_data(0)
        origin_raw_data = process_data.origin_raw_data() 
        filename = str(Path(origin_raw_data.name()).with_suffix(''))
        middle_name = process_data.name()
        middle_name = middle_name.replace(process_data.metadata['origin']['output']['name'], '')
        middle_name = middle_name.replace(filename, '')
        middle_name = middle_name.replace('.md.json', '')    

        html = self._html_header()
        html+= '<th></th>'
        html+= '<th>Name</th>'
        if 'tags' in self.experiment.metadata:  
            for tag in self.experiment.metadata['tags']:
                html += '<th>'+tag+'</th>'

        for output in process_info.outputs:
            html += '<th>'+output.description+'</th>' 
        html += '</thead>'
        html += '<tbody>'

        bi_rawdataset = self.experiment.rawdataset()
        for i in range(bi_rawdataset.size()):
            html += '<tr>'
            # remind raw data
            bi_rawdata = bi_rawdataset.raw_data(i)
            html+= '<td><img src='+bi_rawdata.thumbnail_relative_experiment()+'></td>'
            html+= '<td>'+bi_rawdata.name()+'</td>'
            if 'tags' in self.experiment.metadata: 
                for key in self.experiment.metadata['tags']:
                    html += '<td>'+bi_rawdata.tag(key)+'</td>'

            # processed data    
            for output in process_info.outputs:
                processed_filename = str(Path(bi_rawdata.name()).with_suffix('')) + middle_name + output.name + '.md.json'
                processed_info = BiProcessedData( os.path.join(processeddataset.md_file_dir(), processed_filename ))
                if processed_info.datatype() == 'image':
                    html+= '<td><img src='+processed_info.thumbnail_relative_experiment()+'></td>'
                    #html+= '<td>'+processed_info.thumbnail_relative_experiment()+'</td>'
                elif processed_info.datatype() == 'number':
                    with open(processed_info.url_relative_experiment(), 'r') as content_file:
                        p = content_file.read() 
                        html += '<td>'+p+'</td>'
                elif processed_info.datatype() == 'array':
                    html += '<td>'+processed_info.url_relative_experiment()+'</td>'
                elif processed_info.datatype() == 'table':
                    html += '<td><span style="float:right;"><i class="fa fa-table" style="font-size:60px;color:#999999;"></i></span></td>'
            html += '</tr>' 
        return html 

    def _dataset_to_table_merge(self, processeddataset: BiProcessedDataSet, process_info: BiProcessInfo):
        html = self._html_header()
        # header
        for output in process_info.outputs:
            html+= '<th>'+output.description+'</th>'
        html += '</thead>'
        html += '<tbody>'    
        # data
        for j in range(processeddataset.size()):
            processed_data = processeddataset.processed_data(j)        
            oID = 0
            for output in process_info.outputs:
                oID += 1
                if processed_data.metadata['origin']['output']['label'] == output.description:
                    if processed_data.metadata['origin']['output']['label'] == output.description:
                        if processed_data.datatype() == 'image': 
                            html += '<td>'+processed_data.url_relative_experiment()+'</td>'   
                        elif processed_data.datatype() == 'number':
                            with open(processed_data.url(), 'r') as content_file:
                                p = content_file.read() 
                                html += '<td>'+p+'</td>'
                        elif processed_data.datatype() == 'array':
                            with open(processed_data.url(), 'r') as content_file:
                                p = content_file.read() 
                                html += '<td>'+p+'</td>'
                        elif processed_data.datatype() == 'table':
                            html += '<td><span style="float:right;"><i class="fa fa-table" style="font-size:60px;color:#999999;"></i></span></td>'
                            #html += '<td>'+processed_data.url_relative_experiment()+'</td>'      
        return html     

    def _html_header(self):
        html = '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.5.0/css/font-awesome.min.css">'
        html += '<style>'
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
        return html

    def to_html(self, table):
        html = self._html_header()
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


class BiRunInputsExperimentWidget:
    def __init__(self, experiment: BiExperiment, process_info: BiProcessInfo):
        self.experiment = experiment
        self.info = process_info

        form_item_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-between'
        )

        inputBoxes = []
        for inp in self.info.inputs:
            if inp.io == IO_INPUT():
                nameLabel = Label(value=inp.description)
                dataComboBox = Dropdown(options=self.get_experiment_data_list())
                inputBoxes.append(Box([nameLabel, dataComboBox], layout=form_item_layout))

        self.widget = Box(inputBoxes, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 1px gray',
            align_items='stretch',
            width='80%'
        ))  

    def getWidget(self):
        return self.widget

    def get_experiment_data_list(self):

        data_list = [] 
        data_list.append('data:data') 
        experiment = self.experiment
        for i in range(experiment.processeddatasets_size()):
            processeddataset = experiment.processeddataset(i)
            parser = BiProcessParser(processeddataset.process_url())
            process_info = parser.parse()
            for output in process_info.outputs:
                data_list.append(processeddataset.name() + ':' + output.description)

        return data_list    

class BiProcessInputWidget:
    def __init__(self):
        super().__init__()
        self._dataType = ''
        self._key = ''
        self._advanced = False

    def datatype(self) -> str:
        return self._dataType

    def key(self) -> str:
        return self._key

    def isAdvanced(self) -> bool:
        return self._advanced

    def setAdvanced(self, adv: bool):
        self._advanced = adv

    def setKey(self, key: str):
        self._key = key

    def setValue(self, value: str):
        self._value = value

    def setDatatype(self, datatype: str):
        self._dataType = datatype


# ///////////////////////////////////////////////// //
#                BiProcessInputValue                //
# ///////////////////////////////////////////////// //
class BiProcessInputValue(BiProcessInputWidget):
    def __init__(self):
        super().__init__()
        self.widget = Text()

    def getWidget(self):
        return self.widget

    def getValue(self):
        return self.widget.value    

    def setValue(self, value: str):
        self.widget.value = value
    

# ///////////////////////////////////////////////// //
#                BiProcessInputSelect
# ///////////////////////////////////////////////// //
class BiProcessInputSelect(BiProcessInputWidget):

    def __init__(self):
        super().__init__()

        self.widget = Dropdown()

    def getWidget(self):
        return self.widget

    def setContentStr(self, content: str):
        contentList = content.split(";")
        self.widget.options = contentList

    def setContentList(self, content: list):
        self.widget.options = content

    def setValue(self, value: str):
        self.widget.value = value

# ///////////////////////////////////////////////// //
#                BiProcessInputBrowser
# ///////////////////////////////////////////////// //
class BiProcessInputBrowser(BiProcessInputWidget):
    def __init__(self, isDir: bool):
        super().__init__()
        self.isDir = isDir
        self.widget = Text()

    def getWidget(self):
        return self.widget

    def setValue(self, value: str):
        self.widget = value  

    def getValue(self):
        return self.widget.value    

class BiRunParameterExperimentWidget:
    def __init__(self, experiment: BiExperiment, process_info: BiProcessInfo):
        self.experiment = experiment
        self.process_info = process_info
        self.labels = dict() # <str, QLabel>
        self.widgets = dict() # <str, BiProcessInputWidget>


        self.advancedToggleButton = ToggleButton(description='Advanced')
        self.advancedToggleButton.observe(self.showHideAdvanced)

        self.advancedMode = True
        self.advancedToggleButton.value = False

        form_item_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-between'
        )

        form_items = [Box([Label(''), self.advancedToggleButton], layout=form_item_layout)]

        row = 0
        for parameter in self.process_info.inputs:
            if parameter.io == IO_PARAM():
                row += 1
                titleLabel = Label(value=parameter.description)
                lineWidgets = []
                self.labels[parameter.name] = titleLabel
                lineWidgets.append(titleLabel)

                if parameter.type == "integer" or parameter.type == PARAM_NUMBER() or parameter.type == PARAM_STRING():
                    valueEdit = BiProcessInputValue() 
                    valueEdit.setKey(parameter.name)
                    valueEdit.setValue(parameter.value)
                    valueEdit.setAdvanced(parameter.is_advanced)
                    self.widgets[parameter.name] = valueEdit
                    lineWidgets.append(valueEdit.getWidget())
                
                elif parameter.type == PARAM_SELECT():
                    w = BiProcessInputSelect()
                    w.setKey(parameter.name)
                    # TODO add contentstr
                    w.setValue(parameter.value)
                    w.setAdvanced(parameter.is_advanced)
                    self.widgets[parameter.name] = w
                    lineWidgets.append(w.getWidget())
        
                elif parameter.type == PARAM_FILE():
                    w = BiProcessInputBrowser(False)
                    w.setKey(parameter.name)
                    w.setAdvanced(parameter.is_advanced)
                    self.widgets[parameter.name] = w
                    lineWidgets.append(w.getWidget())

                form_items.append(Box(lineWidgets, layout=form_item_layout))  

        self.widget = Box(form_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 1px gray',
            align_items='stretch',
            width='80%'
        ))  
        self.showHideAdvanced('')              

    def showHideAdvanced(self, v):
        if self.advancedMode == True:
            self.advancedMode = False
        else:
            self.advancedMode = True

        for key in self.labels:
            label = self.labels[key]
            widget = self.widgets[key]

            if widget.isAdvanced() and self.advancedMode:
                label.layout.visibility = 'visible'
                widget.getWidget().layout.visibility = 'visible'
            elif widget.isAdvanced() and not self.advancedMode:
                label.layout.visibility = 'hidden'
                widget.getWidget().layout.visibility = 'hidden' 

    def getWidget(self):
        return self.widget    
        

class BiRunExperimentWidget:
    def __init__(self, experiment_dir: str, process_xml: str):

        self.experiment = BiExperiment(os.path.join(experiment_dir,'experiment.md.json'))
        self.process_info = BiProcessParser(process_xml).parse()
        
        inputsWidget = BiRunInputsExperimentWidget(self.experiment, self.process_info)
        parametersWidget = BiRunParameterExperimentWidget(self.experiment, self.process_info)
        
        previewButton = Button(description='Preview')
        previewButton.on_click(self.preview)
        execButton = Button(description='Execute')

        previewButton.on_click(self.preview)
        execButton.on_click(self.execute)

        form_item_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-between'
        )

        form_items = [
            Box([Label("Inputs"), inputsWidget.getWidget()], layout=form_item_layout),
            Box([Label("Parameters"), parametersWidget.getWidget()], layout=form_item_layout),
            HBox([previewButton, execButton], layout=form_item_layout)
        ]

        #self.widget = VBox([box1, box2, box3])
        self.widget = Box(form_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 0px',
            align_items='stretch',
            width='100%'
        ))  

    def preview(self):
        pass

    def execute(self):
        pass

    def getWidget(self):
        return self.widget    
        

class BiProcessRunThread:

    def __init__(self):
        super().__init__()
        self.experiment = None
        self.processInfo = None
        self.parametersList = []
        self.selectedDataList = []
        self.outputDataSet = ''
 
    def run(self):
        if len(self.selectedDataList) > 0 and "url" in self.selectedDataList[0]["filters"][0]:
            self.run_list()
        else:
            self.run_filter()    

    def run_list(self):
        # instanciate runner
        runner = BiRunnerExperiment(self.experiment) 
        #configFile = os.path.join(BiSettingsAccess.instance.value("Processes", "Processes directory"), "config.json")
        #runner.set_config(BiConfig(configFile))
        
        # set process and parameters
        params = []
        for p in self.parametersList:
            params.append(p["name"])
            params.append(p["value"])
        runner.set_process(self.processInfo.xml_file_url, *params) 

        # set inputs
        for data in self.selectedDataList:
            _id = data['id']

            _dataset_name = ''

            _names = data['name'].split(':')
            if len(_names) == 2:
                _dataset_name = _names[0]  
            else:
                _dataset_name = data['name']

            _urls = []
            for _filter in data['filters']:
                _urls.append(os.path.join(self.experiment.md_file_dir(), _dataset_name, _filter['url']))
            runner.add_input_by_urls(_id, _urls)

        # output dataset
        if self.outputDataSet != "":
            runner.setOutputDataSet(self.outputDataSet)

        #run
        runner.run()  

        # final progress
        progress = dict()
        progress["progress"] = 100
        progress["message"] = 'done'
        self.progressSignal.emit(progress)  


    def run_filter(self): 
        # instanciate runner
        runner = runnerpy.BiRunnerExperiment(self.experiment) 
        configFile = os.path.join(BiSettingsAccess.instance.value("Processes", "Processes directory"), "config.json")
        runner.set_config(BiConfig(configFile))
        runner.add_observer(self.runObserver)

        # set process and parameters
        params = []
        for p in self.parametersList:
            params.append(p["name"])
            params.append(p["value"])
        runner.set_process(self.processInfo.xml_file_url, *params) 

        # set inputs
        for data in self.selectedDataList:
            _id = data['id']
            
            _dataset_name = ''
            _data_name = ''

            _names = data['name'].split(':')
            if len(_names) == 2:
                _dataset_name = _names[0]  
            else:
                _dataset_name = data['name']   

            _data_name = data["originname"]    

            _query = ''
            for _filter in data['filters']:
                _query += _filter['name'] + _filter['operator'] + _filter['value']
            
            runner.add_input(_id, _dataset_name, _query, _data_name)

        #run
        runner.run()  

        # final progress
        progress = dict()
        progress["progress"] = 100
        progress["message"] = 'done'
        self.progressSignal.emit(progress)         
