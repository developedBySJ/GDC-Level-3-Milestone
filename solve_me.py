from http.server import BaseHTTPRequestHandler, HTTPServer


class TasksCommand:
    TASKS_FILE = "tasks.txt"
    COMPLETED_TASKS_FILE = "completed.txt"

    current_items = {}
    completed_items = []

    def read_current(self):
        try:
            file = open(self.TASKS_FILE, "r")
            for line in file.readlines():
                item = line[:-1].split(" ")
                self.current_items[int(item[0])] = " ".join(item[1:])
            file.close()
        except Exception:
            pass

    def read_completed(self):
        try:
            file = open(self.COMPLETED_TASKS_FILE, "r")
            lines = file.readlines()
            file.close()
            return lines
        except Exception:
            pass

    def init(self):
        self.completed_items = self.read_completed() or []
        self.read_current()

    def write_current(self):
        with open(self.TASKS_FILE, "w+") as f:
            f.truncate(0)
            for key in sorted(self.current_items.keys()):
                f.write(f"{key} {self.current_items[key]}\n")

    def write_completed(self):
        with open(self.COMPLETED_TASKS_FILE, "w+") as f:
            f.truncate(0)
            for item in self.completed_items:
                f.write(f"{item}\n")

    def runserver(self):
        address = "127.0.0.1"
        port = 8000
        server_address = (address, port)
        httpd = HTTPServer(server_address, TasksServer)
        print(f"Started HTTP Server on http://{address}:{port}")
        httpd.serve_forever()

    def run(self, command, args):
        self.read_current()
        self.read_completed()
        if command == "add":
            self.add(args)
        elif command == "done":
            self.done(args)
        elif command == "delete":
            self.delete(args)
        elif command == "ls":
            self.ls()
        elif command == "report":
            self.report()
        elif command == "runserver":
            self.runserver()
        elif command == "help":
            self.help()

    def help(self):
        print(
            """Usage :-
$ python tasks.py add 2 hello world # Add a new item with priority 2 and text "hello world" to the list
$ python tasks.py ls # Show incomplete priority list items sorted by priority in ascending order
$ python tasks.py del PRIORITY_NUMBER # Delete the incomplete item with the given priority number
$ python tasks.py done PRIORITY_NUMBER # Mark the incomplete item with the given PRIORITY_NUMBER as complete
$ python tasks.py help # Show usage
$ python tasks.py report # Statistics
$ python tasks.py runserver # Starts the tasks management server"""
        )

    def add(self, args):
        [priority, text] = args
        cur_priority = int(priority)
        prev_task = text
        while True:
            if self.current_items.get(int(cur_priority)) == None:
                self.current_items[int(cur_priority)] = f"{prev_task}"
                break
            else:
                temp_prev_task = self.current_items[int(cur_priority)]
                self.current_items[int(cur_priority)] = prev_task
                prev_task = temp_prev_task
                cur_priority += 1
        print(f"Added task: \"{text}\" with priority {priority}")
        self.write_current()
        pass

    def done(self, args):
        priority = int(args[0])

        if priority < 1 or not self.current_items.get(priority):
            print(
                f"Error: no incomplete item with priority {priority} exists.")
            return

        self.completed_items.append(self.current_items[priority])

        del self.current_items[priority]
        self.write_current()
        self.write_completed()

        print("Marked item as done.")
        pass

    def delete(self, args):
        priority = int(args[0])

        if priority < 1 or not self.current_items.get(priority):
            print(
                f"Error: item with priority {priority} does not exist. Nothing deleted.")
            return

        del self.current_items[priority]
        self.write_current()

        print(f"Deleted item with priority {priority}")
        pass

    def ls(self):
        count = 1
        for priority in sorted(self.current_items):
            text = self.current_items[priority]
            print(f"{count}. {text} [{priority}]")
            count += 1
        pass

    def report(self):
        # Print pending
        print(f"Pending : {len(self.current_items)}")
        self.ls()
        print()

        # print completed
        print(f"Completed : {len(self.completed_items)}")
        self._print_completed()

    def _print_completed(self):
        count = 1
        for task in self.completed_items:
            print(f"{count}. {task}")
            count += 1
        pass

    def render_pending_tasks(self):
        # Complete this method to return all incomplete tasks as HTML
        pending_task_html = ""

        for priority in self.current_items:
            text = self.current_items[priority]
            pending_task_html += f"<li>{text} [{priority}]</li>"

        return f"""
        <div style="font-family:'Arial';" >
            <h1> Pending Tasks </h1>
            <ol style="font-size:1.5rem;">
                {pending_task_html}
            </ol>
        <div/>
        """

    def render_completed_tasks(self):
        # Complete this method to return all completed tasks as HTML
        completed_task_html = ""
        for text in self.completed_items:
            completed_task_html += f"<li>{text}</li>"

        return f"""
        <div style="font-family:'Arial';" >
            <h1> Completed Tasks </h1>
            <ol style="font-size:1.5rem;">
                {completed_task_html}
            </ol>
        <div/>
        """

    def render_home(self):
        return """
        <div style="font-family:'Arial';" >
            <h1>Todo Manager </h1>
            <h3> 
                <a href="/tasks">Show Pending Tasks</a> 
            </h3>
            <h3> 
                <a href="/completed">Show Completed Tasks</a> 
            </h3>
        </div>
        """


class TasksServer(TasksCommand, BaseHTTPRequestHandler):
    def do_GET(self):
        task_command_object = TasksCommand()
        task_command_object.init()
        if self.path == "/":
            content = task_command_object.render_home()
        elif self.path == "/tasks":
            content = task_command_object.render_pending_tasks()
        elif self.path == "/completed":
            content = task_command_object.render_completed_tasks()
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())
