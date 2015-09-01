function make_recompute_window(ws_url, name, github_url, box) {

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