import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task:
    def __init__(self, id: int, title: str, priority: Priority = Priority.MEDIUM):
        self.id = id
        self.title = title
        self.priority = priority
        self.completed = False
        self.created_at = datetime.now().isoformat()
        self.completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority.value,
            "completed": self.completed,
            "created_at": self.created_at,
            "completed_at": self.completed_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        task = cls(data["id"], data["title"], Priority(data["priority"]))
        task.completed = data["completed"]
        task.created_at = data["created_at"]
        task.completed_at = data["completed_at"]
        return task

class TaskManager:
    def __init__(self, filename: str = "tasks.json"):
        self.filename = filename
        self.tasks: List[Task] = []
        self.load_tasks()

    def add_task(self, title: str, priority: Priority) -> Task:
        task_id = len(self.tasks) + 1
        task = Task(task_id, title, priority)
        self.tasks.append(task)
        self.save_tasks()
        return task

    def toggle_task(self, task_id: int) -> bool:
        for task in self.tasks:
            if task.id == task_id:
                task.completed = not task.completed
                task.completed_at = datetime.now().isoformat() if task.completed else None
                self.save_tasks()
                return True
        return False

    def delete_task(self, task_id: int) -> bool:
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                del self.tasks[i]
                self.save_tasks()
                return True
        return False

    def save_tasks(self) -> None:
        with open(self.filename, 'w') as f:
            json.dump([task.to_dict() for task in self.tasks], f, indent=2)

    def load_tasks(self) -> None:
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    tasks_data = json.load(f)
                    self.tasks = [Task.from_dict(data) for data in tasks_data]
            except (json.JSONDecodeError, FileNotFoundError):
                self.tasks = []
        else:
            self.tasks = []

class TaskMasterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TaskMaster")
        self.root.geometry("600x500")
        
        # Initialize task manager
        self.task_manager = TaskManager()
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._setup_styles()
        
        # Main container
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Task input frame
        self._create_task_input_frame()
        
        # Task list frame
        self._create_task_list_frame()
        
        # Load tasks
        self.refresh_task_list()

    def _setup_styles(self):
        self.style.configure('TButton', padding=5)
        self.style.configure('HighPriority.TLabel', foreground='red', font=('TkDefaultFont', 10, 'bold'))
        self.style.configure('MediumPriority.TLabel', foreground='orange')
        self.style.configure('LowPriority.TLabel', foreground='green')
        self.style.configure('Completed.TLabel', foreground='gray', font=('TkDefaultFont', 9, 'overstrike'))
        self.style.configure('Task.TFrame', padding=5, relief='groove', borderwidth=1)
        self.style.configure('Title.TLabel', font=('TkDefaultFont', 14, 'bold'))

    def _create_task_input_frame(self):
        input_frame = ttk.LabelFrame(self.main_frame, text="Add New Task", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Task entry
        ttk.Label(input_frame, text="Task:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.task_entry = ttk.Entry(input_frame, width=40)
        self.task_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.task_entry.bind('<Return>', lambda e: self.add_task())
        
        # Priority selection
        ttk.Label(input_frame, text="Priority:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.priority_var = tk.StringVar(value=Priority.MEDIUM.value)
        priority_menu = ttk.OptionMenu(input_frame, self.priority_var, 
                                     Priority.MEDIUM.value,
                                     *[p.value for p in Priority])
        priority_menu.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        # Add button
        add_btn = ttk.Button(input_frame, text="Add Task", command=self.add_task)
        add_btn.grid(row=0, column=4, padx=5, pady=5)
        
        # Configure grid weights
        input_frame.columnconfigure(1, weight=1)

    def _create_task_list_frame(self):
        list_frame = ttk.LabelFrame(self.main_frame, text="Tasks", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview with columns
        self.tree = ttk.Treeview(list_frame, columns=('id', 'task', 'priority', 'status'), 
                                show='headings', selectmode='browse')
        
        # Define headings
        self.tree.heading('id', text='ID')
        self.tree.heading('task', text='Task')
        self.tree.heading('priority', text='Priority')
        self.tree.heading('status', text='Status')
        
        # Configure columns
        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('task', width=300, anchor=tk.W)
        self.tree.column('priority', width=100, anchor=tk.CENTER)
        self.tree.column('status', width=100, anchor=tk.CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Configure grid weights
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Add context menu
        self._create_context_menu()
        
        # Bind double-click event
        self.tree.bind('<Double-1>', self.on_task_double_click)

    def _create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Toggle Complete", command=self.toggle_selected_task)
        self.context_menu.add_command(label="Delete", command=self.delete_selected_task)
        
        # Bind right-click
        self.tree.bind('<Button-3>', self.show_context_menu)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def add_task(self):
        title = self.task_entry.get().strip()
        if not title:
            messagebox.showwarning("Warning", "Task title cannot be empty!")
            return
            
        priority = Priority(self.priority_var.get())
        self.task_manager.add_task(title, priority)
        self.task_entry.delete(0, tk.END)
        self.refresh_task_list()

    def toggle_selected_task(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        task_id = int(self.tree.item(selected[0])['values'][0])
        self.task_manager.toggle_task(task_id)
        self.refresh_task_list()

    def delete_selected_task(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        task_id = int(self.tree.item(selected[0])['values'][0])
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
            self.task_manager.delete_task(task_id)
            self.refresh_task_list()

    def on_task_double_click(self, event):
        self.toggle_selected_task()

    def refresh_task_list(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add tasks to the treeview
        for task in self.task_manager.tasks:
            status = "✓" if task.completed else " "
            priority_style = f"{task.priority.value.capitalize()}Priority.TLabel"
            
            self.tree.insert('', 'end', values=(
                task.id,
                task.title,
                task.priority.value.capitalize(),
                status
            ))
            
            # Apply style to the row
            item_id = self.tree.get_children()[-1]
            
            if task.completed:
                self.tree.item(item_id, tags=('completed',))
                self.tree.tag_configure('completed', foreground='gray')

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskMasterApp(root)
    root.mainloop()
