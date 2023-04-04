import $ from 'jquery';
import BpmnModeler from 'bpmn-js/lib/Modeler';  // modeler from lib
import diagramXML from '../resources/newDiagram.bpmn';
import {Client} from './client.js';

var container = $('#js-drop-zone');
var path = "http://localhost:8000";
var submit_button = document.getElementById("button1")
var download_button = document.getElementById("button2")

var intro_message = $('#messagetodelete')
var loader_container = $('#loader');

var thresh_output = document.getElementById("thresh-value")
var eps_output = document.getElementById("epsilon-value")


var eps_slider = document.getElementById("epsilon-slider")
var thresh_slider = document.getElementById("thresh-slider")


const client = new Client(path);

var modeler = new BpmnModeler({
    container: '#js-canvas',
    keyboard: {
        bindTo: window
    }
});


eps_slider.oninput = function () {
    eps_output.innerHTML = "Epsilon: " + this.value + "%";

}
thresh_slider.oninput = function () {
    thresh_output.innerHTML = "Threshold: " + this.value;
}

function createNewDiagram() {
    openDiagram(diagramXML);
}

async function openDiagram(xmlPromise) {

    try {
        var xml = await xmlPromise.then()
        await modeler.importXML(xml);
        container
            .removeClass('with-error')
            .addClass('with-diagram');
        container.show()
        loader_container.hide()
        submit_button.disabled = false;
        eps_slider.disabled = false;
        thresh_slider.disabled = false;
        download_button.disabled = false;
        var max_value = await client.getMaxW();
        thresh_slider.setAttribute("max", max_value);

        //alert(await client.getMaxW());

    } catch (err) {
        container
            .removeClass('with-diagram')
            .addClass('with-error');

        submit_button.disabled = true;

        // container.find('.error pre').text(err.message);
        container.find('.error pre').text("Wrong text format or parameters");
        console.error(err);
    }
}


function registerFileDrop(container, callback) {

    async function handleFileSelect(e) {
        container.removeClass('with-diagram')
        intro_message.hide();
        e.stopPropagation();
        e.preventDefault();

        var files = e.dataTransfer.files;

        var file = files[0];

        await client.uploadFile(file)
        await client.setEpsFilter(0.2, 20);

        var reader = new FileReader();

        reader.onload = function (e) {
            var xml = client.getBpmn();
            callback(xml);
        };

        reader.readAsText(file);
    }

    function handleDragOver(e) {
        e.stopPropagation();
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy'; // Explicitly show this is a copy.
    }

    container.get(0).addEventListener('dragover', handleDragOver, false); // jak bedzie plik nad kontenerem to sie to odpala
    container.get(0).addEventListener('drop', handleFileSelect, false);
}


//document.querySelectorAll('#js-form-zone input')

//document.getElementById("js-form-zone")


function sendFilterParams() {
    const eps_v = eps_slider.value / 100;
    const thresh_v = thresh_slider.value;
    console.log(eps_v)
    console.log(thresh_v)
    client.setEpsFilter(eps_v, thresh_v)
    container.removeClass('with-diagram');
    openDiagram(client.getBpmn())
}

submit_button.addEventListener("click", sendFilterParams, false);


// file drag / drop ///////////////////////

// check file api availability
if (!window.FileList || !window.FileReader) {
    window.alert(
        'Looks like you use an older browser that does not support drag and drop. ' +
        'Try using Chrome, Firefox or the Internet Explorer > 10.');
} else {
    registerFileDrop(container, openDiagram);
}

// bootstrap diagram functions

$(function () {
    // document is ready -> proceed
    // strap div with function?
    $('#js-create-diagram').click(function (e) {
        // creation not drag and drop
        e.stopPropagation();
        e.preventDefault();
        createNewDiagram();
    });

    var downloadLink = $('#js-download-diagram');
    var downloadSvgLink = $('#js-download-svg');

    $('.buttons a').click(function (e) {
        if (!$(this).is('.active')) {
            e.preventDefault();
            e.stopPropagation();
        }
    });

    function setEncoded(link, name, data) {
        var encodedData = encodeURIComponent(data);

        if (data) {
            link.addClass('active').attr({
                'href': 'data:application/bpmn20-xml;charset=UTF-8,' + encodedData,
                'download': name
            });
        } else {
            link.removeClass('active');
        }
    }

    var exportArtifacts = debounce(async function () {

        try {

            const {svg} = await modeler.saveSVG();

            setEncoded(downloadSvgLink, 'diagram.svg', svg);
        } catch (err) {

            console.error('Error happened saving svg: ', err);
            setEncoded(downloadSvgLink, 'diagram.svg', null);
        }

        try {

            const {xml} = await modeler.saveXML({format: true});
            setEncoded(downloadLink, 'diagram.bpmn', xml);
        } catch (err) {

            console.error('Error happened saving XML: ', err);
            setEncoded(downloadLink, 'diagram.bpmn', null);
        }
    }, 500);

    modeler.on('commandStack.changed', exportArtifacts);
});


// helpers //////////////////////

function debounce(fn, timeout) {

    var timer;

    return function () {
        if (timer) {
            clearTimeout(timer);
        }

        timer = setTimeout(fn, timeout);
    };
}

async function downloadDiagram() {
    var xmlPromise = client.getBpmn()
    var xml = await xmlPromise.then()
    const blob = new Blob([xml], {type: "text"})
    const href = URL.createObjectURL(blob)
    const a = Object.assign(document.createElement('a'), {href, style: "display:none", download: "bpmn_diagram"})
    document.body.appendChild(a)
    a.click();
    URL.revokeObjectURL(href) // remove it from memory
    a.remove();
}

download_button.addEventListener("click", downloadDiagram, false);

