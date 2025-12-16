#!/usr/bin/env python3
"""
TaskMaster CLI - A simple command-line task manager.
"""

import argparse
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

# Constants
TASKS_FILE = "tasks.json"
VERSION = "1.0.0"

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
    def __init__(self):
        self.tasks: List[Task] = []
        self.load_tasks()

    def add_task(self, title: str, priority: Priority = Priority.MEDIUM) -> Task:
        task_id = len(self.tasks) + 1
        task = Task(task_id, title, priority)
        self.tasks.append(task)
        self.save_tasks()
        return task

    def complete_task(self, task_id: int) -> bool:
        for task in self.tasks:
            if task.id == task_id and not task.completed:
                task.completed = True
                task.completed_at = datetime.now().isoformat()
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

    def list_tasks(self, show_completed: bool = False) -> List[Task]:
        if show_completed:
            return self.tasks
        return [task for task in self.tasks if not task.completed]

    def save_tasks(self) -> None:
        with open(TASKS_FILE, 'w') as f:
            json.dump([task.to_dict() for task in self.tasks], f, indent=2)

    def load_tasks(self) -> None:
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r') as f:
                try:
                    tasks_data = json.load(f)
                    self.tasks = [Task.from_dict(data) for data in tasks_data]
                except json.JSONDecodeError:
                    self.tasks = []
        else:
            self.tasks = []

def print_tasks(tasks: List[Task]) -> None:
    if not tasks:
        print("No tasks found.")
        return
    
    print("\nID  | Priority | Status    | Task")
    print("-" * 50)
    for task in tasks:
        status = "✓" if task.completed else " "
        print(f"{task.id:3d} | {task.priority.value.upper():<8} | [{status}]      | {task.title}")

def main():
    parser = argparse.ArgumentParser(description="TaskMaster CLI - A simple command-line task manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Task title")
    add_parser.add_argument("--priority", "-p", choices=[p.value for p in Priority], 
                           default=Priority.MEDIUM.value, help="Task priority")

    # List command
    list_parser = subparsers.add_parser("list", help="List all tasks")
    list_parser.add_argument("--all", "-a", action="store_true", 
                            help="Show all tasks including completed ones")

    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Mark a task as complete")
    complete_parser.add_argument("task_id", type=int, help="ID of the task to complete")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("task_id", type=int, help="ID of the task to delete")

    # Version
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")

    args = parser.parse_args()
    manager = TaskManager()

    if args.command == "add":
        task = manager.add_task(args.title, Priority(args.priority))
        print(f"Added task: {task.title} (Priority: {task.priority.value})")
    
    elif args.command == "list":
        tasks = manager.list_tasks(show_completed=args.all)
        print_tasks(tasks)
    
    elif args.command == "complete":
        if manager.complete_task(args.task_id):
            print(f"Task {args.task_id} marked as complete!")
        else:
            print(f"Task {args.task_id} not found or already completed.")
    
    elif args.command == "delete":
        if manager.delete_task(args.task_id):
            print(f"Task {args.task_id} deleted!")
        else:
            print(f"Task {args.task_id} not found.")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
