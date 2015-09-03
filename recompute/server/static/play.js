/**
 * Based on tty.js
 * Copyright (c) 2012-2013, Christopher Jeffrey (MIT License)
 */

function make_play_window(root, terminal_args, vm, tag, version) {
    var ws_url = "ws://" + window.location.host + "/ws/play/" + vm + "/" + tag + "/" + version;
    var ws = new WebSocket(ws_url);
    var win = new PlayWindow(ws, root, vm, tag, version);
    win.resize(terminal_args.cols, terminal_args.rows);

    ws.onopen = function(event) {
        var term  = new Terminal(terminal_args);

        term.on("data", function(data) {
            ws.send(data);
        });

        term.open(win.element);

        ws.onopen = function(event) {
            term.write("\x1b[31mWelcome to term.js!\x1b[m\r\n");
        };

        ws.onmessage = function(event) {
            term.write(event.data);
        };

        ws.onclose = function(event) {
            term.destroy();
            win.destroy();
        }
    }
}

function PlayWindow(ws, root, vm, tag, version) {
    this.socket = ws;
    this.root = root;

    this.element = document.createElement("div");
    this.element.className = "window";

    this.grip = document.createElement("div");
    this.grip.className = "grip";

    this.bar = document.createElement("div");
    this.bar.className = "bar";

    this.new_button = document.createElement("div");
    this.new_button.className = "tab";
    this.new_button.innerHTML = "~";
    this.new_button.title = "new/close";

    this.tab_button = document.createElement("div");
    this.tab_button.className = "tab";
    this.tab_button.innerHTML = "\u2022";
    this.tab_button.style.fontWeight = "bold";

    this.title = document.createElement("div");
    this.title.className = "title";
    this.title.innerHTML = vm + " - " + tag + ", " + version

    this.cols = Terminal.geometry[0];
    this.rows = Terminal.geometry[1];

    this.tabs = [];
    this.focused = null;

    this.element.appendChild(this.grip);
    this.element.appendChild(this.bar);
    this.bar.appendChild(this.new_button);
    this.bar.appendChild(this.tab_button);
    this.bar.appendChild(this.title);
    this.root.appendChild(this.element);

    this.draggable();
}

PlayWindow.prototype.draggable = function() {
    var self = this;


    $(this.element).draggable({
        cursor: "move",
        start: function() {
            self.element.style.opacity = "0.6";
        },
        stop: function() {
            self.element.style.opacity = "";
        }
    });

    this.bar.onmousedown = function() {
        // re-enable draggable
        var disabled = $(self.element).draggable("option", "disabled");
        if (disabled) {
            $(self.element).draggable("enable");
        }
    }

    this.bar.onmouseup = function() {
        // disable draggable so the user can't drag the window when selecting text in the terminal
        $(self.element).draggable("option", "disabled", true);
    }
}

PlayWindow.prototype.resize = function(cols, rows) {
    this.cols = cols;
    this.rows = rows;
}

PlayWindow.prototype.destroy = function() {
    this.root.removeChild(this.element)
}