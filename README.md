# Log File Processor

This is a python script that analyzes log files and generates statistics based on the provided input file(s). The script supports the following features:

- Most Frequent IP (MFIP)
- Least Frequent IP (LFIP)
- Events per Second (EPS)
- Total Bytes Exchanged

The script uses only standard python libraries and does not rely on any external dependencies.

## Requirements

- Python 3.11 or above
- Virtual environment (optional)

## Installation

1. Create a virtual environment: `python3 -m venv venv`
2. Activate the virtual environment: `source venv/bin/activate`
3. Install the tool: `pip install -e .`
4. Run the script: `usage: log_processor [-h] [--mfip] [--lfip] [--eps] [--bytes] [--format {json,text}] input [input ...] output`

## Usage

```
usage: log_processor [-h] [--mfip] [--lfip] [--eps] [--bytes] [--format {json,text}] input [input ...] output

Process log files and generate output in JSON format.

positional arguments:
  input                 Path to one or more input files.
  output                Path to a file to save output in plain text JSON format.

options:
  -h, --help            show this help message and exit
  --mfip                Most frequent IP
  --lfip                Least frequent IP
  --eps                 Events per second
  --bytes               Total amount of bytes exchanged
  --format {json,text}  Output format (default: json)
```

## Output

```
{
    "mfip": [
        "127.0.0.1",  # IP
        1422267       # Number of occurrences
    ],
    "lfip": [
        "210.10.215.171",
        1
    ],
    "eps": 0.01,
    "bytes": 3631264436
}
```
## Future Extensibility

The current implementation of the log processor is designed to be easily extensible. Here are some potential future improvements and extensions:

1. **Additional Metrics**: The script can be extended to include more metrics, such as the most frequent URL, the most frequent HTTP method, or the most frequent response type, handling cases where there are multiple entries with the same frequency.
2. **Parallel Processing**: The script can be modified to process log files in parallel, using a thread-based or a process-based approach, to improve performance on large log files.
3. **Debugging Mode**: A debugging mode can be added to the script, which would provide more detailed information about the parsing and processing of the log entries.
4. **File Management**: The script can be improved to handle file management, such as overwriting existing output files or handling errors when files cannot be accessed.
5. **Input Validation**: The script can be enhanced to perform more robust input validation, such as checking the correct format of the IPs, HTTP Request methods, etc.

## License

This project is licensed under the [MIT License](LICENSE).