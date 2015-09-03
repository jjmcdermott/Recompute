function make_recompute_window(name, github_url, box) {
    var ws_url = "ws://" + window.location.host + "/ws/recompute/" + name;
    var ws = new WebSocket(ws_url);
    var win = new RecomputeWindow(ws, name, github_url, box);

    ws.onopen = function(event) {
        ws.onopen = function(event) {
            win.write("Connected to " + window.location.host);
        };

        ws.onmessage = function(event) {
            win.write(event.data);
        };

        ws.onclose = function(event) {
            win.destroy();
        }
    }
}

function RecomputeWindow(ws, name, github_url, box) {
    this.window = window.open("", "_blank", "height=800,width=800");
    this.window.document.title = "Recomputing " + name

    var header_name = document.createElement("h3");
    var header_name_text = document.createTextNode("Name: " + name);
    header_name.appendChild(header_name_text);

    var header_github = document.createElement("h3");
    var header_github_text = document.createTextNode("GitHub: " + github_url);
    header_github.appendChild(header_github_text);

    var header_box = document.createElement("h3");
    var header_box_text = document.createTextNode("Box: " + box);
    header_box.appendChild(header_box_text);

    this.output_div = document.createElement("div");
    this.output_div.style.border = "2px solid black";
    this.output_div.style.width = "100%";
    this.output_div.style.height = "650px";
    this.output_div.style.overflowX = "hidden";
    this.output_div.style.overflowY = "auto";

    this.window.document.body.appendChild(header_name);
    this.window.document.body.appendChild(header_github);
    this.window.document.body.appendChild(header_box);
    this.window.document.body.appendChild(this.output_div);
}

RecomputeWindow.prototype.write = function(data) {
    console.log(data)
    this.output_div.innerHTML = this.output_div.innerHTML + data + "<br />";
    this.output_div.scrollTop = this.output_div.scrollHeight;
}

RecomputeWindow.prototype.destroy = function() {
    this.window.close();
}
