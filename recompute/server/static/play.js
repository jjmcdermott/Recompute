function make_terminal(element, terminal_opts, ws_url) {
    var ws = new WebSocket(ws_url);
    ws.onopen = function(event) {
        var term  = new Terminal(terminal_opts);

        term.on("data", function(data) {
            ws.send(data);
        });

        term.open(element);

        ws.onopen = function(event) {
            term.write('\x1b[31mWelcome to term.js!\x1b[m\r\n');
        };

        ws.onmessage = function(event) {
            term.write(event.data);
        };

        ws.onclose = function(event) {
            term.destroy();
        }
    }
}