import $ from 'jquery';

export class Client {


    constructor(path) {
        this.path = path;
        this.file = undefined;
    }

    async uploadFile(file) {

        const formData = new FormData();

        var extension = get_extension(file);

        formData.append("file", file);

        const response = await fetch(this.path + "/uploadfile/", {
            method: 'POST',
            body: formData
        })

        if (extension === "csv") {
            await this.setColumnNames(file)
        }
        load()
        const content = await response.json();
        this.file = file;
    }

    async setColumnNames(file) {
        const reader = new FileReader();
        let arr;
        reader.onload = async (e) => {
            var text = e.target.result;

            var firstLine = text.split('\n').shift();
            arr = firstLine.split(',');
            arr[arr.length - 1] = arr[arr.length - 1].slice(0, -1);
            var form_container = $('#set-col')
            var case_select = document.getElementById("Case");
            var activity_select = document.getElementById("Activity");
            var start_timestamp_select = document.getElementById("StartTimestamp");

            let options = arr.map(el => "<option value='" + el + "'>" + el + "</option>").join('\n');
            case_select.innerHTML = options;
            activity_select.innerHTML = options;
            start_timestamp_select.innerHTML = options;
            form_container.addClass("vis");
        }
        await reader.readAsText(file, 'UTF-8');

        // var submit_button = document.getElementById("col-button")
        // submit_button.addEventListener("click", function(){sendColumnParams()}, false);
        // await submit_button

        const promise = new Promise(resolve => {
            document.getElementById("col-button").addEventListener("click", e => {
                sendColumnParams()
                resolve(e)
            }, false);
        })
        await promise.then(
            e => {
                console.log("promise then")
            }
        )
    }

    async setEpsFilter(eps, filter) {
        load()
        const formData = new FormData();
        formData.append('eps', parseFloat(eps))
        formData.append('filter_threshold', parseInt(filter))

        const response = await fetch(this.path + "/set-eps-filter", {
            method: 'POST',
            body: formData
        })
        load()
        const content = await response.json();
    }

    async getBpmn() {
        try {
            const response = await fetch(this.path + "/get-bpmn", {
                method: 'GET'
            })
            const res = await response.json();
            return res;
        } catch (error) {
            console.log(error)
            stop_load()
            return null
        }
    }

    async getMaxW() {

        const response = await fetch(this.path + "/get-max-w", {
            method: 'GET'
        })
        return await response.json()
    }

    async resetColumns() {

        const response = await fetch(this.path + "/resetColumns", {
            method: 'POST'
        })

        const content = await response.json();
    }

}

async function sendColumnParams() {
    const formData = new FormData();
    var case_select = document.getElementById("Case");
    var activity_select = document.getElementById("Activity");
    var start_timestamp_select = document.getElementById("StartTimestamp");
    formData.append('case_column', case_select.value)
    formData.append('activity_column', activity_select.value)
    formData.append('start_column', start_timestamp_select.value)
    console.log(activity_select.value)
    const response = await fetch("http://localhost:8000" + "/set-column-names/", {
        method: 'POST',
        body: formData
    })

    const content = await response.json();
    var form_container = $('#set-col')
    form_container.removeClass("vis")
}

function load() {
    var container = $('#js-drop-zone');
    var loader_container = $('#loader');
    container.hide()
    loader_container.show()
}

function stop_load() {
    var container = $('#js-drop-zone');
    var loader_container = $('#loader');
    loader_container.hide()
    container.show()
}

function get_extension(file) {
    var filename = file.name
    return filename.split('.').pop();
}


