# TaskMaster CLI

A simple command-line task manager to help you stay organized and productive.

## Features

- Add new tasks with priority levels
- List all tasks
- Mark tasks as complete
- Delete tasks
- Filter tasks by status
- Save tasks to a local file

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/taskmaster-cli.git
   cd taskmaster-cli
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
# Add a new task
python taskmaster.py add "Complete project documentation" --priority high

# List all tasks
python taskmaster.py list

# Mark a task as complete
python taskmaster.py complete 1

# Delete a task
python taskmaster.py delete 2
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT
